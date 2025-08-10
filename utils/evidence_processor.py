from models.evidence import Evidence
from models.notification import Notification
import logging
from datetime import datetime
from utils.canadian_law_ai import canadian_law_ai

class EvidenceProcessor:
    """Processes evidence items with Canadian law AI analysis"""
    
    def process_evidence(self, evidence_id: int):
        """Process evidence with AI analysis"""
        evidence = Evidence.query.get(evidence_id)
        if not evidence:
            logging.error(f"Evidence {evidence_id} not found")
            return
        
        # Analyze evidence relevance using Canadian law AI
        try:
            case = evidence.case
            if case:
                # Get case type for context
                case_type = case.case_type if hasattr(case, 'case_type') else 'unknown'
                
                # Analyze evidence text (description or title)
                evidence_text = evidence.description or evidence.title or ""
                
                # Perform AI analysis
                analysis = canadian_law_ai.analyze_evidence_relevance(evidence_text, case_type)
                
                # Update evidence with AI analysis results
                evidence.ai_relevance_score = analysis.get("ai_relevance_score")
                evidence.analyzed_at = datetime.utcnow() if analysis.get("analyzed_at") else None
                
                logging.info(f"AI analysis completed for evidence {evidence_id}: {analysis.get('ai_relevance_score')}")
            else:
                logging.warning(f"No case found for evidence {evidence_id}")
        except Exception as e:
            logging.error(f"AI analysis failed for evidence {evidence_id}: {str(e)}")
            # Continue processing even if AI analysis fails
        
        # Simple processing: mark as reviewed
        evidence.status = "Reviewed"
        evidence.save()
        
        # Create notification
        notification = Notification(
            user_id=evidence.uploaded_by,
            message=f"Evidence {evidence_id} has been processed",
            notification_type="evidence_processed"
        )
        notification.save()
        return evidence