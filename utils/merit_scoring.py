from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from models import db
from models.case import Case, CaseType, CaseStatus, CasePriority
from models.evidence import Evidence, EvidenceStatus
from utils.ai_services import calculate_case_merit_ai, ai_service_manager

logger = logging.getLogger(__name__)

class MeritScoringEngine:
    """
    Comprehensive merit scoring system for legal cases
    Combines rule-based analysis with AI-powered assessment
    """
    
    def __init__(self):
        # Scoring weights for different factors
        self.scoring_weights = {
            'evidence_quality': 0.30,      # Quality and relevance of evidence
            'evidence_quantity': 0.15,     # Amount of supporting evidence
            'case_completeness': 0.20,     # How complete the case information is
            'legal_strength': 0.25,        # AI-assessed legal strength
            'procedural_factors': 0.10     # Deadlines, jurisdiction, etc.
        }
        
        # Evidence type importance weights
        self.evidence_type_weights = {
            'document': 1.0,     # Official documents are most important
            'image': 0.8,        # Images/photos are strong evidence
            'email': 0.9,        # Email communications are valuable
            'text': 0.6,         # Text notes are supportive
            'audio': 0.9,        # Audio recordings are strong
            'video': 0.95,       # Video evidence is very strong
            'other': 0.5         # Other evidence has base value
        }
        
        # Case type difficulty multipliers
        self.case_complexity_multipliers = {
            'child_protection': 0.9,  # Complex but well-defined processes
            'family_court': 0.8,      # Generally well-established procedures
            'parental_rights': 0.85,  # Emotionally complex but structured
            'tribunal': 0.95,         # More straightforward procedures
            'other': 0.7             # Unknown complexity
        }

    def calculate_comprehensive_merit_score(self, case: Case) -> Dict[str, Any]:
        """
        Calculate comprehensive merit score for a case
        
        Returns:
            Dictionary with detailed scoring breakdown
        """
        try:
            logger.info(f"Starting comprehensive merit analysis for case {case.id}")
            
            # Get all evidence for the case
            evidence_list = Evidence.query.filter_by(case_id=case.id).all()
            
            # Calculate individual score components
            evidence_quality_score = self._calculate_evidence_quality_score(evidence_list)
            evidence_quantity_score = self._calculate_evidence_quantity_score(evidence_list)
            case_completeness_score = self._calculate_case_completeness_score(case)
            legal_strength_score = self._calculate_legal_strength_score(case, evidence_list)
            procedural_score = self._calculate_procedural_factors_score(case)
            
            # Calculate weighted overall score
            overall_score = (
                evidence_quality_score * self.scoring_weights['evidence_quality'] +
                evidence_quantity_score * self.scoring_weights['evidence_quantity'] +
                case_completeness_score * self.scoring_weights['case_completeness'] +
                legal_strength_score * self.scoring_weights['legal_strength'] +
                procedural_score * self.scoring_weights['procedural_factors']
            )
            
            # Apply case complexity multiplier
            complexity_multiplier = self.case_complexity_multipliers.get(
                case.case_type.value if case.case_type else 'other', 0.7
            )
            
            adjusted_score = overall_score * complexity_multiplier
            final_score = min(100, max(0, adjusted_score))
            
            # Generate detailed analysis
            analysis_result = {
                'overall_score': round(final_score, 1),
                'score_breakdown': {
                    'evidence_quality': round(evidence_quality_score, 1),
                    'evidence_quantity': round(evidence_quantity_score, 1),
                    'case_completeness': round(case_completeness_score, 1),
                    'legal_strength': round(legal_strength_score, 1),
                    'procedural_factors': round(procedural_score, 1)
                },
                'complexity_multiplier': complexity_multiplier,
                'strength_indicators': self._identify_strength_indicators(case, evidence_list),
                'weakness_indicators': self._identify_weakness_indicators(case, evidence_list),
                'recommendations': self._generate_recommendations(case, evidence_list, final_score),
                'confidence_level': self._calculate_confidence_level(case, evidence_list),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'evidence_count': len(evidence_list),
                'processed_evidence_count': len([e for e in evidence_list if e.status in [EvidenceStatus.PROCESSED, EvidenceStatus.ANALYZED]])
            }
            
            logger.info(f"Merit analysis completed for case {case.id}: score {final_score}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error calculating merit score for case {case.id}: {str(e)}")
            return {
                'overall_score': 0,
                'error': str(e),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }

    def _calculate_evidence_quality_score(self, evidence_list: List[Evidence]) -> float:
        """Calculate score based on evidence quality and relevance"""
        if not evidence_list:
            return 0
        
        total_quality_score = 0
        total_weight = 0
        
        for evidence in evidence_list:
            # Base quality score from AI relevance
            ai_relevance = evidence.ai_relevance_score or 0.5
            quality_score = ai_relevance * 100
            
            # Apply evidence type weight
            type_weight = self.evidence_type_weights.get(
                evidence.evidence_type.value if evidence.evidence_type else 'other', 0.5
            )
            
            # Bonus for processed evidence
            processing_bonus = 1.2 if evidence.status == EvidenceStatus.ANALYZED else 1.0
            
            weighted_score = quality_score * type_weight * processing_bonus
            total_quality_score += weighted_score
            total_weight += type_weight
        
        return min(100, total_quality_score / total_weight if total_weight > 0 else 0)

    def _calculate_evidence_quantity_score(self, evidence_list: List[Evidence]) -> float:
        """Calculate score based on quantity and diversity of evidence"""
        evidence_count = len(evidence_list)
        
        if evidence_count == 0:
            return 0
        elif evidence_count <= 2:
            base_score = evidence_count * 25  # 25 points per piece up to 2
        elif evidence_count <= 5:
            base_score = 50 + (evidence_count - 2) * 15  # Additional 15 points each
        else:
            base_score = 95  # Maximum for quantity
        
        # Bonus for evidence diversity
        evidence_types = set()
        for evidence in evidence_list:
            if evidence.evidence_type:
                evidence_types.add(evidence.evidence_type.value)
        
        diversity_bonus = min(10, len(evidence_types) * 2.5)  # Up to 10 points for diversity
        
        return min(100, base_score + diversity_bonus)

    def _calculate_case_completeness_score(self, case: Case) -> float:
        """Calculate score based on how complete the case information is"""
        completeness_factors = []
        
        # Basic case information
        completeness_factors.append(1 if case.title and case.title.strip() else 0)
        completeness_factors.append(1 if case.description and len(case.description.strip()) > 20 else 0)
        completeness_factors.append(1 if case.case_type else 0)
        completeness_factors.append(1 if case.province else 0)
        
        # Dates and deadlines
        completeness_factors.append(1 if case.incident_date else 0)
        completeness_factors.append(0.5 if case.filing_deadline else 0)  # Optional but valuable
        completeness_factors.append(0.5 if case.hearing_date else 0)     # Optional but valuable
        
        # Jurisdiction information
        completeness_factors.append(0.5 if case.jurisdiction else 0)
        completeness_factors.append(0.5 if case.court_name else 0)
        
        # Calculate percentage
        total_possible = len(completeness_factors)
        actual_score = sum(completeness_factors)
        
        return (actual_score / total_possible) * 100 if total_possible > 0 else 0

    def _calculate_legal_strength_score(self, case: Case, evidence_list: List[Evidence]) -> float:
        """Calculate legal strength using AI analysis if available"""
        try:
            # Try to get AI-powered assessment
            if ai_service_manager.is_service_available('anthropic') or ai_service_manager.is_service_available('openai'):
                ai_result = calculate_case_merit_ai(case, evidence_list)
                
                if ai_result.get('success'):
                    ai_score = ai_result.get('merit_score', 50)
                    confidence = ai_result.get('confidence_level', 3)
                    
                    # Adjust score based on AI confidence
                    confidence_multiplier = 0.6 + (confidence / 5) * 0.4  # 0.6 to 1.0
                    return min(100, ai_score * confidence_multiplier)
            
            # Fallback to rule-based assessment
            return self._rule_based_legal_strength(case, evidence_list)
            
        except Exception as e:
            logger.warning(f"AI legal strength analysis failed for case {case.id}: {str(e)}")
            return self._rule_based_legal_strength(case, evidence_list)

    def _rule_based_legal_strength(self, case: Case, evidence_list: List[Evidence]) -> float:
        """Fallback rule-based legal strength assessment"""
        base_score = 50  # Neutral starting point
        
        # Adjust based on case type (some are easier to prove)
        case_type_adjustments = {
            'tribunal': 10,        # Generally more straightforward
            'family_court': 5,     # Well-established procedures
            'child_protection': 0, # Neutral
            'parental_rights': -5, # Can be more complex
            'other': -10           # Unknown complexity
        }
        
        case_type = case.case_type.value if case.case_type else 'other'
        base_score += case_type_adjustments.get(case_type, 0)
        
        # Adjust based on evidence with legal keywords
        legal_evidence_count = 0
        for evidence in evidence_list:
            if evidence.legal_keywords and len(evidence.legal_keywords) > 0:
                legal_evidence_count += 1
        
        if legal_evidence_count > 0:
            base_score += min(20, legal_evidence_count * 5)
        
        # Adjust based on timeliness
        if case.incident_date:
            days_since_incident = (datetime.utcnow().date() - case.incident_date).days
            if days_since_incident < 30:
                base_score += 10  # Recent incidents are good
            elif days_since_incident > 365:
                base_score -= 10  # Old incidents may have limitations issues
        
        return min(100, max(0, base_score))

    def _calculate_procedural_factors_score(self, case: Case) -> float:
        """Calculate score based on procedural and timing factors"""
        score = 50  # Base score
        
        # Deadline factors
        if case.filing_deadline:
            days_until_deadline = (case.filing_deadline - datetime.utcnow().date()).days
            
            if days_until_deadline < 0:
                score -= 30  # Past deadline is very bad
            elif days_until_deadline < 7:
                score -= 15  # Very urgent
            elif days_until_deadline < 30:
                score += 10  # Good timing
            else:
                score += 20  # Plenty of time
        
        # Jurisdiction factors
        if case.province and case.jurisdiction:
            score += 15  # Good jurisdictional clarity
        elif case.province:
            score += 10  # Some jurisdictional info
        
        # Case age factors
        if case.created_at:
            case_age_days = (datetime.utcnow() - case.created_at).days
            if case_age_days < 7:
                score += 5   # Fresh case
            elif case_age_days > 180:
                score -= 10  # Case getting stale
        
        return min(100, max(0, score))

    def _identify_strength_indicators(self, case: Case, evidence_list: List[Evidence]) -> List[str]:
        """Identify positive factors in the case"""
        strengths = []
        
        # Evidence strengths
        analyzed_evidence = [e for e in evidence_list if e.status == EvidenceStatus.ANALYZED]
        if len(analyzed_evidence) > 0:
            strengths.append(f"{len(analyzed_evidence)} pieces of evidence have been AI-analyzed")
        
        high_relevance_evidence = [e for e in evidence_list if (e.ai_relevance_score or 0) > 0.7]
        if len(high_relevance_evidence) > 0:
            strengths.append(f"{len(high_relevance_evidence)} highly relevant evidence items")
        
        # Case information strengths
        if case.description and len(case.description) > 100:
            strengths.append("Detailed case description provided")
        
        if case.incident_date:
            days_since = (datetime.utcnow().date() - case.incident_date).days
            if days_since < 90:
                strengths.append("Recent incident date supports case timeliness")
        
        if case.filing_deadline:
            days_until = (case.filing_deadline - datetime.utcnow().date()).days
            if days_until > 30:
                strengths.append("Sufficient time before filing deadline")
        
        # Evidence diversity
        evidence_types = set(e.evidence_type.value for e in evidence_list if e.evidence_type)
        if len(evidence_types) > 2:
            strengths.append(f"Diverse evidence types ({len(evidence_types)} different types)")
        
        return strengths

    def _identify_weakness_indicators(self, case: Case, evidence_list: List[Evidence]) -> List[str]:
        """Identify areas needing improvement"""
        weaknesses = []
        
        # Evidence weaknesses
        if len(evidence_list) < 3:
            weaknesses.append("Limited evidence - consider gathering more supporting documents")
        
        unprocessed_evidence = [e for e in evidence_list if e.status == EvidenceStatus.UPLOADED]
        if len(unprocessed_evidence) > 0:
            weaknesses.append(f"{len(unprocessed_evidence)} evidence items not yet processed")
        
        low_relevance_evidence = [e for e in evidence_list if (e.ai_relevance_score or 0) < 0.3]
        if len(low_relevance_evidence) > len(evidence_list) / 2:
            weaknesses.append("Several evidence items have low relevance scores")
        
        # Case information gaps
        if not case.description or len(case.description.strip()) < 50:
            weaknesses.append("Case description needs more detail")
        
        if not case.incident_date:
            weaknesses.append("Incident date not specified")
        
        if not case.jurisdiction or not case.court_name:
            weaknesses.append("Jurisdiction or court information incomplete")
        
        # Timing issues
        if case.filing_deadline:
            days_until = (case.filing_deadline - datetime.utcnow().date()).days
            if days_until < 14:
                weaknesses.append("Approaching filing deadline - urgent action needed")
            elif days_until < 0:
                weaknesses.append("Filing deadline has passed")
        
        return weaknesses

    def _generate_recommendations(self, case: Case, evidence_list: List[Evidence], score: float) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if score < 30:
            recommendations.append("Case needs significant strengthening before proceeding")
            recommendations.append("Consider consulting with a legal professional")
        elif score < 50:
            recommendations.append("Case has potential but needs improvement in key areas")
        elif score < 70:
            recommendations.append("Good foundation - focus on strengthening weak areas")
        else:
            recommendations.append("Strong case - ready for next steps in legal process")
        
        # Evidence-specific recommendations
        if len(evidence_list) < 5:
            recommendations.append("Gather additional supporting evidence to strengthen your case")
        
        unprocessed = [e for e in evidence_list if e.status == EvidenceStatus.UPLOADED]
        if unprocessed:
            recommendations.append("Process remaining uploaded evidence for complete analysis")
        
        # Case information recommendations
        if not case.description or len(case.description) < 100:
            recommendations.append("Expand case description with more specific details")
        
        if not case.incident_date:
            recommendations.append("Add the incident date to establish timeline")
        
        # Deadline recommendations
        if case.filing_deadline:
            days_until = (case.filing_deadline - datetime.utcnow().date()).days
            if days_until < 30:
                recommendations.append("Prioritize case preparation due to approaching deadline")
        
        return recommendations

    def _calculate_confidence_level(self, case: Case, evidence_list: List[Evidence]) -> int:
        """Calculate confidence level in the analysis (1-5 scale)"""
        confidence = 3  # Base confidence
        
        # Increase confidence with more evidence
        if len(evidence_list) >= 5:
            confidence += 1
        elif len(evidence_list) < 2:
            confidence -= 1
        
        # Increase confidence with AI analysis
        analyzed_count = len([e for e in evidence_list if e.status == EvidenceStatus.ANALYZED])
        if analyzed_count > len(evidence_list) * 0.8:
            confidence += 1
        
        # Decrease confidence for incomplete case info
        if not case.description or not case.incident_date:
            confidence -= 1
        
        return max(1, min(5, confidence))


# Global instance
merit_scoring_engine = MeritScoringEngine()


def calculate_case_merit(case: Case) -> Dict[str, Any]:
    """Convenience function to calculate case merit score"""
    return merit_scoring_engine.calculate_comprehensive_merit_score(case)


def update_case_merit_score(case: Case) -> bool:
    """Update case merit score and save to database"""
    try:
        merit_result = calculate_case_merit(case)
        
        if 'error' not in merit_result:
            case.merit_score = merit_result['overall_score']
            case.merit_analysis = merit_result.get('score_breakdown', {})
            case.strength_indicators = merit_result.get('strength_indicators', [])
            case.weakness_indicators = merit_result.get('weakness_indicators', [])
            
            db.session.commit()
            logger.info(f"Updated merit score for case {case.id}: {case.merit_score}")
            return True
        else:
            logger.error(f"Merit calculation failed for case {case.id}: {merit_result['error']}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating merit score for case {case.id}: {str(e)}")
        db.session.rollback()
        return False