from utils.db import db  # Corrected import
from models.case import Case
from models.legal_journey import LegalJourney
from datetime import datetime
import json

class LegalJourneyGenerator:
    """Generates legal journeys - simplified without AI"""
    
    def create_initial_journey(self, case_id):
        """Create initial journey for a case"""
        journey = LegalJourney(
            case_id=case_id,
            journey_data=json.dumps({
                "stages": [
                    {"name": "Initial Consultation", "status": "completed", "date": str(datetime.utcnow())},
                    {"name": "Evidence Gathering", "status": "in_progress", "date": None},
                    {"name": "Form Submission", "status": "pending", "date": None},
                    {"name": "Hearing Preparation", "status": "pending", "date": None},
                    {"name": "Resolution", "status": "pending", "date": None}
                ]
            })
        )
        db.session.add(journey)
        db.session.commit()
        return journey