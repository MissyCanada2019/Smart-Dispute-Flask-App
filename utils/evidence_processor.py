from models.evidence import Evidence
from models.notification import Notification
import logging

class EvidenceProcessor:
    """Processes evidence items - AI functionality removed"""
    
    def process_evidence(self, evidence_id: int):
        """Process evidence - default implementation without AI"""
        evidence = Evidence.query.get(evidence_id)
        if not evidence:
            logging.error(f"Evidence {evidence_id} not found")
            return
        
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