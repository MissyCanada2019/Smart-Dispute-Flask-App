import os
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import pytesseract
import PyPDF2
import io
import re
from datetime import datetime
from models import db
from models.evidence import Evidence, EvidenceStatus
from models.notification import Notification
from utils.ai_services import analyze_evidence_ai, ai_service_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvidenceProcessingError(Exception):
    """Custom exception for evidence processing errors"""
    pass

class EvidenceProcessor:
    """Handles processing of uploaded evidence files"""
    
    def __init__(self):
        # Configure OCR settings
        self.ocr_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6
        
        # Common legal keywords to identify
        self.legal_keywords = [
            'court', 'judge', 'hearing', 'defendant', 'plaintiff', 'respondent', 'applicant',
            'custody', 'access', 'support', 'maintenance', 'divorce', 'separation',
            'child protection', 'cps', 'cas', 'social services', 'welfare',
            'injunction', 'order', 'motion', 'application', 'affidavit', 'declaration',
            'evidence', 'witness', 'testimony', 'document', 'exhibit',
            'trial', 'settlement', 'mediation', 'arbitration', 'appeal',
            'lawyer', 'attorney', 'solicitor', 'barrister', 'counsel', 'legal aid'
        ]
        
        # Date patterns to extract
        self.date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD or YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',  # DD Month YYYY
        ]
        
        # Name patterns (simplified)
        self.name_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
            r'\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b',  # First M. Last
        ]

    def process_evidence_async(self, evidence_id: int) -> None:
        """Asynchronously process evidence (entry point for background processing)"""
        try:
            evidence = Evidence.query.get(evidence_id)
            if not evidence:
                logger.error(f"Evidence {evidence_id} not found")
                return
                
            logger.info(f"Starting processing for evidence {evidence_id}: {evidence.original_filename}")
            
            # Update status to processing
            evidence.status = EvidenceStatus.PROCESSING
            db.session.commit()
            
            # Process the file
            processing_result = self.process_evidence_file(evidence)
            
            # Update evidence with results
            self.update_evidence_with_results(evidence, processing_result)
            
            # Create notification for completion
            Notification.create_evidence_analysis_complete(
                evidence.user_id,
                evidence.case_id,
                evidence.id,
                processing_result.get('summary', 'Evidence processing completed')
            )
            
            db.session.commit()
            logger.info(f"Completed processing for evidence {evidence_id}")
            
        except Exception as e:
            logger.error(f"Error processing evidence {evidence_id}: {str(e)}")
            # Update status to error
            if evidence:
                evidence.status = EvidenceStatus.ERROR
                db.session.commit()

    def process_evidence_file(self, evidence: Evidence) -> Dict[str, Any]:
        """Process a single evidence file and extract information"""
        try:
            if not os.path.exists(evidence.file_path):
                raise EvidenceProcessingError(f"File not found: {evidence.file_path}")
            
            # Determine processing method based on file type
            if evidence.is_pdf:
                return self.process_pdf_file(evidence.file_path)
            elif evidence.is_image:
                return self.process_image_file(evidence.file_path)
            else:
                raise EvidenceProcessingError(f"Unsupported file type: {evidence.mime_type}")
                
        except Exception as e:
            logger.error(f"Error processing file {evidence.file_path}: {str(e)}")
            raise EvidenceProcessingError(f"Failed to process file: {str(e)}")

    def process_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """Extract text and information from PDF files"""
        try:
            extracted_text = ""
            metadata = {}
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'pages': len(pdf_reader.pages)
                    }
                
                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                        continue
            
            # Process extracted text
            processed_info = self.analyze_extracted_text(extracted_text)
            processed_info['metadata'] = metadata
            processed_info['extraction_method'] = 'pdf_text_extraction'
            
            return processed_info
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise EvidenceProcessingError(f"Failed to process PDF: {str(e)}")

    def process_image_file(self, file_path: str) -> Dict[str, Any]:
        """Extract text from image files using OCR"""
        try:
            # Open and process image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Perform OCR
                extracted_text = pytesseract.image_to_string(img, config=self.ocr_config)
                
                # Get OCR confidence data
                ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Image metadata
                metadata = {
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'ocr_confidence': round(avg_confidence, 2)
                }
            
            # Process extracted text
            processed_info = self.analyze_extracted_text(extracted_text)
            processed_info['metadata'] = metadata
            processed_info['extraction_method'] = 'ocr'
            
            return processed_info
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            raise EvidenceProcessingError(f"Failed to process image: {str(e)}")

    def analyze_extracted_text(self, text: str) -> Dict[str, Any]:
        """Analyze extracted text for legal information"""
        if not text or not text.strip():
            return {
                'extracted_text': '',
                'word_count': 0,
                'identified_dates': [],
                'identified_names': [],
                'legal_keywords': [],
                'summary': 'No text could be extracted from this file.',
                'relevance_indicators': []
            }
        
        # Clean and normalize text
        cleaned_text = self.clean_text(text)
        
        # Extract dates
        dates = self.extract_dates(cleaned_text)
        
        # Extract potential names
        names = self.extract_names(cleaned_text)
        
        # Find legal keywords
        found_keywords = self.find_legal_keywords(cleaned_text)
        
        # Generate summary
        summary = self.generate_text_summary(cleaned_text)
        
        # Identify relevance indicators
        relevance_indicators = self.identify_relevance_indicators(cleaned_text, found_keywords)
        
        return {
            'extracted_text': cleaned_text,
            'word_count': len(cleaned_text.split()),
            'identified_dates': dates,
            'identified_names': names,
            'legal_keywords': found_keywords,
            'summary': summary,
            'relevance_indicators': relevance_indicators
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-printable characters except newlines
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()

    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text using regex patterns"""
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        # Remove duplicates and sort
        unique_dates = list(set(dates))
        return unique_dates[:10]  # Limit to first 10 dates

    def extract_names(self, text: str) -> List[str]:
        """Extract potential names from text"""
        names = []
        for pattern in self.name_patterns:
            matches = re.findall(pattern, text)
            names.extend(matches)
        
        # Filter out common false positives
        filtered_names = []
        false_positives = ['Page Number', 'Date Time', 'Case Number', 'Court Order']
        
        for name in names:
            if name not in false_positives and len(name.split()) <= 3:
                filtered_names.append(name)
        
        # Remove duplicates
        unique_names = list(set(filtered_names))
        return unique_names[:10]  # Limit to first 10 names

    def find_legal_keywords(self, text: str) -> List[str]:
        """Find legal keywords in the text"""
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in self.legal_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords

    def generate_text_summary(self, text: str) -> str:
        """Generate a basic summary of the text content"""
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return "No readable text found in the document."
        elif word_count < 50:
            return f"Short document with {word_count} words. Contains basic text content."
        elif word_count < 200:
            return f"Medium-length document with {word_count} words. May contain relevant case information."
        else:
            return f"Substantial document with {word_count} words. Likely contains detailed information relevant to your case."

    def identify_relevance_indicators(self, text: str, legal_keywords: List[str]) -> List[str]:
        """Identify indicators of relevance to legal cases"""
        indicators = []
        
        if legal_keywords:
            indicators.append(f"Contains {len(legal_keywords)} legal terms")
        
        text_lower = text.lower()
        
        # Check for specific case types
        if any(term in text_lower for term in ['child', 'custody', 'access', 'support']):
            indicators.append("Appears related to family/child matters")
        
        if any(term in text_lower for term in ['court', 'hearing', 'judge', 'order']):
            indicators.append("Contains court-related content")
        
        if any(term in text_lower for term in ['social services', 'child protection', 'welfare']):
            indicators.append("May relate to child protection proceedings")
        
        if re.search(r'\$\d+|\d+\.\d{2}', text):
            indicators.append("Contains financial information")
        
        return indicators

    def update_evidence_with_results(self, evidence: Evidence, processing_result: Dict[str, Any]) -> None:
        """Update evidence record with processing results"""
        try:
            # Update extracted text and basic analysis
            evidence.extracted_text = processing_result.get('extracted_text', '')
            evidence.identified_dates = processing_result.get('identified_dates', [])
            evidence.identified_names = processing_result.get('identified_names', [])
            evidence.legal_keywords = processing_result.get('legal_keywords', [])
            
            # Store initial processing results
            evidence.ai_analysis = processing_result
            evidence.ai_summary = processing_result.get('summary', '')
            evidence.ai_relevance_score = self.calculate_relevance_score(processing_result)
            evidence.status = EvidenceStatus.PROCESSED
            evidence.processed_at = datetime.utcnow()
            
            logger.info(f"Updated evidence {evidence.id} with initial processing results")
            
            # Perform enhanced AI analysis if services are available
            self.perform_enhanced_ai_analysis(evidence)
            
        except Exception as e:
            logger.error(f"Error updating evidence {evidence.id}: {str(e)}")
            evidence.status = EvidenceStatus.ERROR

    def perform_enhanced_ai_analysis(self, evidence: Evidence) -> None:
        """Perform enhanced AI analysis using external AI services"""
        try:
            # Check if AI services are available
            if not (ai_service_manager.is_service_available('openai') or
                   ai_service_manager.is_service_available('anthropic')):
                logger.info(f"No AI services available for enhanced analysis of evidence {evidence.id}")
                return
            
            logger.info(f"Starting enhanced AI analysis for evidence {evidence.id}")
            
            # Perform AI analysis
            ai_result = analyze_evidence_ai(evidence, preferred_service='anthropic')
            
            if ai_result.get('success'):
                analysis_data = ai_result.get('analysis_result', {})
                
                # Update evidence with enhanced AI analysis
                if isinstance(analysis_data, str):
                    # If the result is a string, try to parse it or use as summary
                    evidence.ai_summary = analysis_data[:1000]  # Limit length
                else:
                    # If it's structured data, extract relevant information
                    evidence.ai_summary = analysis_data.get('summary', evidence.ai_summary)
                    
                    # Update relevance score if provided
                    if 'relevance_score' in analysis_data:
                        evidence.ai_relevance_score = min(1.0, analysis_data['relevance_score'] / 10.0)
                    
                    # Merge enhanced analysis with existing analysis
                    if evidence.ai_analysis:
                        evidence.ai_analysis.update({
                            'enhanced_ai_analysis': analysis_data,
                            'ai_service_used': ai_result.get('service_used'),
                            'enhanced_analysis_timestamp': ai_result.get('analyzed_at')
                        })
                    else:
                        evidence.ai_analysis = {
                            'enhanced_ai_analysis': analysis_data,
                            'ai_service_used': ai_result.get('service_used'),
                            'enhanced_analysis_timestamp': ai_result.get('analyzed_at')
                        }
                
                # Update status to fully analyzed
                evidence.status = EvidenceStatus.ANALYZED
                evidence.analyzed_at = datetime.utcnow()
                
                logger.info(f"Enhanced AI analysis completed for evidence {evidence.id}")
                
            else:
                logger.warning(f"Enhanced AI analysis failed for evidence {evidence.id}: {ai_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error performing enhanced AI analysis for evidence {evidence.id}: {str(e)}")
            # Don't change status on AI analysis failure - keep as PROCESSED

    def calculate_relevance_score(self, processing_result: Dict[str, Any]) -> float:
        """Calculate a basic relevance score based on processing results"""
        score = 0.0
        
        # Base score for having extractable text
        if processing_result.get('word_count', 0) > 0:
            score += 0.3
        
        # Score for legal keywords
        legal_keywords_count = len(processing_result.get('legal_keywords', []))
        if legal_keywords_count > 0:
            score += min(0.4, legal_keywords_count * 0.1)  # Max 0.4 for keywords
        
        # Score for dates (important in legal documents)
        dates_count = len(processing_result.get('identified_dates', []))
        if dates_count > 0:
            score += min(0.2, dates_count * 0.05)  # Max 0.2 for dates
        
        # Score for names (parties involved)
        names_count = len(processing_result.get('identified_names', []))
        if names_count > 0:
            score += min(0.1, names_count * 0.02)  # Max 0.1 for names
        
        # Ensure score is between 0 and 1
        return min(1.0, max(0.0, score))


# Global instance
evidence_processor = EvidenceProcessor()


# Convenience functions for async processing
async def process_evidence_background(evidence_id: int):
    """Process evidence in the background"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, evidence_processor.process_evidence_async, evidence_id)


def trigger_evidence_processing(evidence_id: int):
    """Trigger evidence processing (can be called from routes)"""
    try:
        # In a production environment, this would be sent to a task queue (Celery, RQ, etc.)
        # For now, we'll process synchronously but mark it as async
        evidence_processor.process_evidence_async(evidence_id)
        return True
    except Exception as e:
        logger.error(f"Failed to trigger processing for evidence {evidence_id}: {str(e)}")
        return False