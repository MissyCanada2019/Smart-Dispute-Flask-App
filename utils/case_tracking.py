from utils.db import db  # Corrected import
from models.case import Case
from models.evidence import Evidence
from models.court_form import FormSubmission
from models.legal_journey import LegalJourney
from datetime import datetime, timedelta
from enum import Enum

class MilestoneType(Enum):
    """Types of case milestones"""
    EVIDENCE_SUBMITTED = "evidence_submitted"
    FORM_FILED = "form_filed"
    HEARING_SCHEDULED = "hearing_scheduled"
    DECISION_RENDERED = "decision_rendered"
    PAYMENT_MADE = "payment_made"

class CaseTracker:
    """Tracks case progress and milestones - simplified without AI"""
    
    def record_milestone(self, case_id, milestone_type, description=""):
        """Record a new milestone for a case"""
        milestone = {
            "type": milestone_type.value,
            "date": datetime.utcnow(),
            "description": description
        }
        
        case = Case.query.get(case_id)
        if not case:
            return False
        
        if not case.milestones:
            case.milestones = []
        
        case.milestones.append(milestone)
        db.session.commit()
        return True
    
    def get_case_progress(self, case_id):
        """Get progress overview for a case"""
        case = Case.query.get(case_id)
        if not case:
            return None
        
        # Simplified progress calculation
        total_milestones = 5  # Predefined milestones
        completed = len(case.milestones) if case.milestones else 0
        progress = min(100, int((completed / total_milestones) * 100))
        
        return {
            "case_id": case_id,
            "progress": progress,
            "completed_milestones": completed,
            "total_milestones": total_milestones,
            "last_milestone": case.milestones[-1] if case.milestones else None
        }