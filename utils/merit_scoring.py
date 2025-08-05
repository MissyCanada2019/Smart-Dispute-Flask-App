from models.evidence import Evidence

class MeritScorer:
    """Handles merit scoring for cases - AI functionality removed"""
    
    def calculate_merit_score(self, evidence_list) -> int:
        """Calculate merit score based on evidence - default implementation"""
        # Simple scoring based on evidence count
        return min(len(evidence_list) * 10, 100)  # Max 100 points