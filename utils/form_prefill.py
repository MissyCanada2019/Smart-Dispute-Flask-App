"""
AI-Powered Form Pre-filling System
Analyzes case data and evidence to automatically populate court form fields
"""

from typing import Dict, List, Any, Optional, Tuple
from models.case import Case
from models.evidence import Evidence
from models.court_form import FormTemplate, FormField, FormSubmission, SubmissionStatus
from models import db
from utils.ai_services import AIServiceManager
from utils.form_templates import FormTemplateManager
import json
import re
from datetime import datetime, date

class FormPrefillManager:
    """Manages AI-powered form pre-filling functionality"""
    
    def __init__(self):
        self.ai_service = AIServiceManager()
    
    def analyze_case_for_form_filling(self, case: Case, template: FormTemplate) -> Dict[str, Any]:
        """Analyze case data and evidence to generate form field suggestions"""
        try:
            # Gather all available case data
            case_data = self._extract_case_data(case)
            evidence_data = self._extract_evidence_data(case)
            
            # Get form field definitions
            form_fields = FormField.query.filter_by(template_id=template.id).all()
            field_definitions = {}
            for field in form_fields:
                field_definitions[field.name] = {
                    'label': field.label,
                    'type': field.field_type.value,
                    'required': field.required,
                    'placeholder': field.placeholder
                }
            
            # Use AI to analyze and suggest form values
            ai_suggestions = self._get_ai_form_suggestions(
                case_data, 
                evidence_data, 
                field_definitions, 
                template
            )
            
            # Process and validate suggestions
            processed_suggestions = self._process_ai_suggestions(
                ai_suggestions, 
                field_definitions,
                case
            )
            
            return {
                'success': True,
                'suggestions': processed_suggestions,
                'confidence_scores': ai_suggestions.get('confidence_scores', {}),
                'data_sources': ai_suggestions.get('data_sources', {}),
                'analysis_summary': ai_suggestions.get('analysis_summary', '')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'suggestions': {}
            }
    
    def _extract_case_data(self, case: Case) -> Dict[str, Any]:
        """Extract structured data from case object"""
        return {
            'title': case.title,
            'description': case.description,
            'case_number': case.case_number,
            'case_type': case.case_type.value if case.case_type else None,
            'province': case.province,
            'jurisdiction': case.jurisdiction,
            'court_name': case.court_name,
            'priority': case.priority.value if case.priority else None,
            'status': case.status.value if case.status else None,
            'incident_date': case.incident_date.isoformat() if case.incident_date else None,
            'filing_deadline': case.filing_deadline.isoformat() if case.filing_deadline else None,
            'hearing_date': case.hearing_date.isoformat() if case.hearing_date else None,
            'created_at': case.created_at.isoformat() if case.created_at else None,
            'current_stage': case.current_stage,
            'parties_involved': case.parties_involved,
            'legal_issues': case.legal_issues
        }
    
    def _extract_evidence_data(self, case: Case) -> List[Dict[str, Any]]:
        """Extract data from case evidence"""
        evidence_list = Evidence.query.filter_by(case_id=case.id).all()
        evidence_data = []
        
        for evidence in evidence_list:
            evidence_info = {
                'title': evidence.title,
                'description': evidence.description,
                'filename': evidence.original_filename,
                'evidence_type': evidence.evidence_type.value,
                'extracted_text': evidence.extracted_text,
                'ai_analysis': evidence.ai_analysis,
                'key_points': evidence.key_points,
                'created_at': evidence.created_at.isoformat()
            }
            evidence_data.append(evidence_info)
        
        return evidence_data
    
    def _get_ai_form_suggestions(self, case_data: Dict, evidence_data: List[Dict], 
                               field_definitions: Dict, template: FormTemplate) -> Dict[str, Any]:
        """Use AI to analyze case and suggest form field values"""
        
        # Prepare context for AI analysis
        context = f"""
        You are an AI assistant helping to pre-fill a Canadian court form based on case information and evidence.
        
        FORM INFORMATION:
        Form Name: {template.name}
        Form Description: {template.description}
        Province: {template.province}
        Category: {template.category}
        
        CASE INFORMATION:
        {json.dumps(case_data, indent=2)}
        
        EVIDENCE SUMMARY:
        {self._summarize_evidence_for_ai(evidence_data)}
        
        FORM FIELDS TO FILL:
        {json.dumps(field_definitions, indent=2)}
        
        INSTRUCTIONS:
        1. Analyze the case information and evidence
        2. For each form field, suggest an appropriate value if the information is available
        3. Only suggest values you are confident about based on the provided information
        4. For each suggestion, provide a confidence score (0-100) and data source
        5. Include an analysis summary explaining your reasoning
        
        Please respond in JSON format with the following structure:
        {{
            "field_suggestions": {{
                "field_name": {{
                    "value": "suggested_value",
                    "confidence": 85,
                    "source": "case_data|evidence|inference",
                    "reasoning": "explanation of why this value was chosen"
                }}
            }},
            "confidence_scores": {{"field_name": confidence_score}},
            "data_sources": {{"field_name": "source_description"}},
            "analysis_summary": "Overall analysis of available information and form filling strategy"
        }}
        """
        
        try:
            # Use AI service to analyze and suggest values
            ai_response = self.ai_service.analyze_text_with_claude(
                context,
                max_tokens=2000,
                temperature=0.3  # Lower temperature for more consistent suggestions
            )
            
            if ai_response and 'analysis' in ai_response:
                # Try to parse JSON response
                try:
                    return json.loads(ai_response['analysis'])
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract suggestions using regex
                    return self._parse_ai_response_fallback(ai_response['analysis'])
            
        except Exception as e:
            print(f"Error getting AI form suggestions: {str(e)}")
        
        return {
            'field_suggestions': {},
            'confidence_scores': {},
            'data_sources': {},
            'analysis_summary': 'AI analysis was not available'
        }
    
    def _summarize_evidence_for_ai(self, evidence_data: List[Dict]) -> str:
        """Create a concise summary of evidence for AI analysis"""
        if not evidence_data:
            return "No evidence files have been uploaded yet."
        
        summary = f"Evidence Summary ({len(evidence_data)} files):\n"
        
        for i, evidence in enumerate(evidence_data, 1):
            summary += f"\n{i}. {evidence['title']} ({evidence['evidence_type']})\n"
            if evidence['description']:
                summary += f"   Description: {evidence['description']}\n"
            
            # Include key extracted information
            if evidence['key_points']:
                try:
                    key_points = json.loads(evidence['key_points']) if isinstance(evidence['key_points'], str) else evidence['key_points']
                    if key_points:
                        summary += f"   Key Points: {', '.join(key_points[:3])}{'...' if len(key_points) > 3 else ''}\n"
                except:
                    pass
            
            # Include snippet of extracted text
            if evidence['extracted_text'] and len(evidence['extracted_text']) > 50:
                snippet = evidence['extracted_text'][:200] + "..." if len(evidence['extracted_text']) > 200 else evidence['extracted_text']
                summary += f"   Content: {snippet}\n"
        
        return summary
    
    def _parse_ai_response_fallback(self, response_text: str) -> Dict[str, Any]:
        """Fallback method to parse AI response if JSON parsing fails"""
        # This is a simplified fallback - in production, you'd want more robust parsing
        return {
            'field_suggestions': {},
            'confidence_scores': {},
            'data_sources': {},
            'analysis_summary': response_text[:500] + "..." if len(response_text) > 500 else response_text
        }
    
    def _process_ai_suggestions(self, ai_suggestions: Dict, field_definitions: Dict, 
                              case: Case) -> Dict[str, Any]:
        """Process and validate AI suggestions"""
        processed = {}
        field_suggestions = ai_suggestions.get('field_suggestions', {})
        
        for field_name, suggestion in field_suggestions.items():
            if field_name not in field_definitions:
                continue
            
            field_def = field_definitions[field_name]
            suggested_value = suggestion.get('value', '')
            confidence = suggestion.get('confidence', 0)
            
            # Only include suggestions with reasonable confidence
            if confidence >= 60:  # Configurable threshold
                # Validate and format the suggested value
                validated_value = self._validate_field_value(
                    suggested_value, 
                    field_def['type'],
                    field_name
                )
                
                if validated_value is not None:
                    processed[field_name] = {
                        'value': validated_value,
                        'confidence': confidence,
                        'source': suggestion.get('source', 'ai_analysis'),
                        'reasoning': suggestion.get('reasoning', ''),
                        'editable': True,  # Always allow user to edit
                        'auto_filled': True
                    }
        
        # Add some standard mappings based on case data
        processed.update(self._add_standard_mappings(case, field_definitions))
        
        return processed
    
    def _validate_field_value(self, value: str, field_type: str, field_name: str) -> Optional[str]:
        """Validate and format field value based on field type"""
        if not value or str(value).strip() == '':
            return None
        
        value = str(value).strip()
        
        try:
            if field_type == 'email':
                # Basic email validation
                if '@' in value and '.' in value.split('@')[1]:
                    return value.lower()
                return None
            
            elif field_type == 'date':
                # Try to parse and format date
                try:
                    # Handle various date formats
                    if '-' in value:
                        parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
                    elif '/' in value:
                        parsed_date = datetime.strptime(value, '%m/%d/%Y').date()
                    else:
                        return None
                    return parsed_date.isoformat()
                except ValueError:
                    return None
            
            elif field_type == 'select':
                # For select fields, return the value as-is (validation handled by form)
                return value
            
            elif field_type in ['text', 'textarea']:
                # Limit text length
                max_length = 1000 if field_type == 'textarea' else 200
                return value[:max_length]
            
            else:
                return value
                
        except Exception:
            return None
    
    def _add_standard_mappings(self, case: Case, field_definitions: Dict) -> Dict[str, Any]:
        """Add standard field mappings based on case data"""
        mappings = {}
        
        # Standard field mappings
        field_mappings = {
            'case_number': case.case_number,
            'court_location': case.court_name or case.jurisdiction,
            'matter_description': case.description,
            'date_of_incident': case.incident_date.isoformat() if case.incident_date else None,
            'applicant_name': None,  # Would need to be extracted from user profile
            'relief_sought': None  # Could be extracted from case description or evidence
        }
        
        for field_name, case_value in field_mappings.items():
            if field_name in field_definitions and case_value:
                # Only add if not already suggested by AI with higher confidence
                mappings[field_name] = {
                    'value': str(case_value),
                    'confidence': 90,  # High confidence for direct case data
                    'source': 'case_data',
                    'reasoning': 'Directly mapped from case information',
                    'editable': True,
                    'auto_filled': True
                }
        
        return mappings
    
    def create_prefilled_form_submission(self, case: Case, template: FormTemplate, 
                                       user_id: int) -> Optional[FormSubmission]:
        """Create a new form submission with AI-suggested pre-filled values"""
        try:
            # Get AI suggestions for form filling
            prefill_result = self.analyze_case_for_form_filling(case, template)
            
            if not prefill_result['success']:
                return None
            
            suggestions = prefill_result['suggestions']
            
            # Convert suggestions to form data format
            form_data = {}
            prefill_metadata = {
                'auto_filled_fields': [],
                'confidence_scores': {},
                'data_sources': {},
                'analysis_summary': prefill_result.get('analysis_summary', ''),
                'prefill_timestamp': datetime.utcnow().isoformat()
            }
            
            for field_name, suggestion in suggestions.items():
                form_data[field_name] = suggestion['value']
                prefill_metadata['auto_filled_fields'].append(field_name)
                prefill_metadata['confidence_scores'][field_name] = suggestion['confidence']
                prefill_metadata['data_sources'][field_name] = suggestion['source']
            
            # Create form submission
            submission = FormSubmission(
                template_id=template.id,
                case_id=case.id,
                user_id=user_id,
                form_data=json.dumps(form_data),
                metadata=json.dumps(prefill_metadata),
                status=SubmissionStatus.DRAFT
            )
            
            db.session.add(submission)
            db.session.commit()
            
            return submission
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating prefilled form submission: {str(e)}")
            return None
    
    def get_prefill_suggestions_for_existing_form(self, submission: FormSubmission) -> Dict[str, Any]:
        """Get AI suggestions for an existing form submission"""
        try:
            template = FormTemplate.query.get(submission.template_id)
            case = Case.query.get(submission.case_id) if submission.case_id else None
            
            if not template or not case:
                return {'success': False, 'error': 'Template or case not found'}
            
            # Get current form data
            current_data = {}
            if submission.form_data:
                try:
                    current_data = json.loads(submission.form_data)
                except json.JSONDecodeError:
                    pass
            
            # Get AI suggestions
            prefill_result = self.analyze_case_for_form_filling(case, template)
            
            if prefill_result['success']:
                suggestions = prefill_result['suggestions']
                
                # Filter out fields that already have values (unless user wants to overwrite)
                new_suggestions = {}
                for field_name, suggestion in suggestions.items():
                    if not current_data.get(field_name) or current_data[field_name].strip() == '':
                        new_suggestions[field_name] = suggestion
                
                prefill_result['suggestions'] = new_suggestions
            
            return prefill_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

def get_smart_suggestions_for_field(field_name: str, field_type: str, case: Case, 
                                  evidence_data: List[Dict] = None) -> List[str]:
    """Get smart suggestions for a specific form field based on case and evidence"""
    suggestions = []
    
    try:
        # Field-specific suggestion logic
        if field_name.lower() in ['relief_sought', 'relief', 'remedy']:
            # Suggest common relief types based on case type
            case_type_reliefs = {
                'family_court': [
                    'Sole custody of the child',
                    'Joint custody arrangement',
                    'Child support payments',
                    'Spousal support',
                    'Division of matrimonial property'
                ],
                'child_protection': [
                    'Return of child to parent',
                    'Supervised access to child',
                    'Termination of protection order',
                    'Alternative care arrangement'
                ],
                'tribunal': [
                    'Compensation for damages',
                    'Reinstatement of benefits',
                    'Reversal of decision',
                    'Order for compliance'
                ]
            }
            
            if case.case_type and case.case_type.value in case_type_reliefs:
                suggestions.extend(case_type_reliefs[case.case_type.value])
        
        elif field_name.lower() in ['court_location', 'court', 'location']:
            if case.court_name:
                suggestions.append(case.court_name)
            if case.jurisdiction:
                suggestions.append(case.jurisdiction)
        
        elif field_name.lower() in ['matter_description', 'description', 'matter']:
            if case.description:
                suggestions.append(case.description)
        
        # Remove duplicates and empty suggestions
        suggestions = list(set([s for s in suggestions if s and s.strip()]))
        
    except Exception:
        pass
    
    return suggestions[:5]  # Return top 5 suggestions