from models.case import Case
from models.evidence import Evidence
from utils.db import db
import json
from utils.canadian_law_ai import canadian_law_ai

class FormPrefill:
    """Handles form pre-filling based on case data with AI assistance"""
    
    def get_case_form_data(self, case_id: int, form_type: str) -> dict:
        """Get prefill data for case-related forms with AI guidance"""
        case = Case.query.get(case_id)
        if not case:
            return {}
        
        # Get AI guidance for form prefilling
        case_summary = f"{case.case_type} case: {case.title}"
        ai_advice = canadian_law_ai.get_legal_advice(case_summary)
        
        # Basic form data structure with AI guidance
        form_data = {
            "case_id": case_id,
            "case_type": case.case_type,
            "parties": [p.name for p in case.parties] if hasattr(case, 'parties') else [],
            "form_type": form_type,
            "ai_guidance": ai_advice
        }
        
        # Add evidence-based prefilling if available
        if hasattr(case, 'evidence'):
            evidence_list = case.evidence
            relevant_evidence = []
            for evidence in evidence_list:
                if hasattr(evidence, 'ai_relevance_score') and evidence.ai_relevance_score and evidence.ai_relevance_score > 50:
                    relevant_evidence.append({
                        "id": evidence.id,
                        "title": evidence.title,
                        "description": evidence.description,
                        "relevance_score": evidence.ai_relevance_score
                    })
            form_data["relevant_evidence"] = relevant_evidence
            
        return form_data