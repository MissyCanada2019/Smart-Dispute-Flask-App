from utils.db import db  # Corrected import
from models.case import Case
from models.legal_journey import LegalJourney
from datetime import datetime
import json
from utils.canadian_law_ai import canadian_law_ai

class LegalJourneyGenerator:
    """Generates legal journeys with Canadian law AI guidance"""
    
    def create_initial_journey(self, case_id):
        """Create initial journey for a case with AI guidance"""
        case = Case.query.get(case_id)
        if not case:
            return None
            
        # Get AI guidance for case type
        case_summary = f"{case.case_type} case: {case.title}"
        ai_advice = canadian_law_ai.get_legal_advice(case_summary)
        
        journey = LegalJourney(
            case_id=case_id,
            journey_data=json.dumps({
                "stages": [
                    {"name": "Initial Consultation", "status": "completed", "date": str(datetime.utcnow())},
                    {"name": "Evidence Gathering", "status": "in_progress", "date": None},
                    {"name": "Form Submission", "status": "pending", "date": None},
                    {"name": "Hearing Preparation", "status": "pending", "date": None},
                    {"name": "Resolution", "status": "pending", "date": None}
                ],
                "ai_guidance": ai_advice
            })
        )
        db.session.add(journey)
        db.session.commit()
        return journey