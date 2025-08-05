from models.case import Case
from models.evidence import Evidence
from utils.db import db
import json

class FormPrefill:
    """Handles form pre-filling based on case data"""
    
    def get_case_form_data(self, case_id: int, form_type: str) -> dict:
        """Get prefill data for case-related forms"""
        case = Case.query.get(case_id)
        if not case:
            return {}
        
        # Basic form data structure
        return {
            "case_id": case_id,
            "case_type": case.case_type,
            "parties": [p.name for p in case.parties],
            "form_type": form_type
        }