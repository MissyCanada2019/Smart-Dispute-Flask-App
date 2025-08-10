from models.evidence import Evidence
from utils.canadian_law_ai import canadian_law_ai

class MeritScorer:
    """Handles merit scoring for cases using Canadian law AI analysis"""
    
    def calculate_merit_score(self, evidence_list) -> int:
        """Calculate merit score based on evidence with AI analysis"""
        if not evidence_list:
            return 0
            
        total_score = 0
        ai_analyzed_count = 0
        
        # Calculate score based on AI relevance analysis
        for evidence in evidence_list:
            if hasattr(evidence, 'ai_relevance_score') and evidence.ai_relevance_score:
                # Use AI relevance score (0-100)
                total_score += evidence.ai_relevance_score
                ai_analyzed_count += 1
            else:
                # Fallback to simple scoring
                total_score += 10
                
        # Average the scores and cap at 100
        if evidence_list:
            avg_score = total_score / len(evidence_list)
            return min(int(avg_score), 100)
        else:
            return 0