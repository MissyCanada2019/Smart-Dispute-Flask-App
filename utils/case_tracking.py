"""
Case Tracking and Progress Monitoring System
Provides comprehensive case progress tracking, milestone management, and status monitoring
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from models.case import Case, CaseStatus
from models.legal_journey import LegalJourney, JourneyStage
from models.evidence import Evidence, EvidenceStatus
from models.court_form import CourtForm, FormStatus
from models.notification import Notification
from models import db
import json

class ProgressStage(Enum):
    """Case progress stages"""
    PREPARATION = "preparation"
    EVIDENCE_GATHERING = "evidence_gathering" 
    FORM_COMPLETION = "form_completion"
    REVIEW_SUBMISSION = "review_submission"
    COURT_PROCESS = "court_process"
    RESOLUTION = "resolution"

class MilestoneType(Enum):
    """Types of case milestones"""
    CASE_CREATED = "case_created"
    EVIDENCE_UPLOADED = "evidence_uploaded"
    FORM_COMPLETED = "form_completed"
    DOCUMENT_SUBMITTED = "document_submitted"
    COURT_DATE_SCHEDULED = "court_date_scheduled"
    HEARING_ATTENDED = "hearing_attended"
    DECISION_RECEIVED = "decision_received"
    CASE_RESOLVED = "case_resolved"
    CUSTOM = "custom"

class PriorityLevel(Enum):
    """Priority levels for tasks and milestones"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class CaseTracker:
    """Main case tracking and progress monitoring class"""
    
    def __init__(self):
        self.progress_weights = {
            ProgressStage.PREPARATION: 0.15,
            ProgressStage.EVIDENCE_GATHERING: 0.25,
            ProgressStage.FORM_COMPLETION: 0.25,
            ProgressStage.REVIEW_SUBMISSION: 0.15,
            ProgressStage.COURT_PROCESS: 0.15,
            ProgressStage.RESOLUTION: 0.05
        }
    
    def get_case_progress(self, case_id: int) -> Dict[str, Any]:
        """Calculate comprehensive case progress"""
        case = Case.query.get(case_id)
        if not case:
            return {'error': 'Case not found'}
        
        # Get related data
        evidence_list = Evidence.query.filter_by(case_id=case_id).all()
        court_forms = CourtForm.query.filter_by(case_id=case_id).all()
        legal_journey = LegalJourney.query.filter_by(case_id=case_id).first()
        
        # Calculate stage progress
        stage_progress = {}
        overall_progress = 0.0
        
        # Preparation stage
        prep_score = self._calculate_preparation_progress(case, legal_journey)
        stage_progress[ProgressStage.PREPARATION.value] = prep_score
        overall_progress += prep_score * self.progress_weights[ProgressStage.PREPARATION]
        
        # Evidence gathering stage
        evidence_score = self._calculate_evidence_progress(evidence_list)
        stage_progress[ProgressStage.EVIDENCE_GATHERING.value] = evidence_score
        overall_progress += evidence_score * self.progress_weights[ProgressStage.EVIDENCE_GATHERING]
        
        # Form completion stage
        form_score = self._calculate_form_progress(court_forms)
        stage_progress[ProgressStage.FORM_COMPLETION.value] = form_score
        overall_progress += form_score * self.progress_weights[ProgressStage.FORM_COMPLETION]
        
        # Review and submission stage
        review_score = self._calculate_review_progress(case, court_forms)
        stage_progress[ProgressStage.REVIEW_SUBMISSION.value] = review_score
        overall_progress += review_score * self.progress_weights[ProgressStage.REVIEW_SUBMISSION]
        
        # Court process stage
        court_score = self._calculate_court_progress(case)
        stage_progress[ProgressStage.COURT_PROCESS.value] = court_score
        overall_progress += court_score * self.progress_weights[ProgressStage.COURT_PROCESS]
        
        # Resolution stage
        resolution_score = self._calculate_resolution_progress(case)
        stage_progress[ProgressStage.RESOLUTION.value] = resolution_score
        overall_progress += resolution_score * self.progress_weights[ProgressStage.RESOLUTION]
        
        # Get current active stage
        current_stage = self._determine_current_stage(stage_progress)
        
        # Get next actions
        next_actions = self._get_next_actions(case, stage_progress, current_stage)
        
        # Get milestones
        milestones = self._get_case_milestones(case_id)
        
        return {
            'case_id': case_id,
            'overall_progress': round(overall_progress * 100, 1),
            'current_stage': current_stage,
            'stage_progress': {k: round(v * 100, 1) for k, v in stage_progress.items()},
            'next_actions': next_actions,
            'milestones': milestones,
            'estimated_completion': self._estimate_completion_date(case, overall_progress),
            'progress_trend': self._calculate_progress_trend(case_id),
            'blocking_issues': self._identify_blocking_issues(case, evidence_list, court_forms)
        }
    
    def _calculate_preparation_progress(self, case: Case, legal_journey: LegalJourney) -> float:
        """Calculate preparation stage progress"""
        score = 0.0
        total_items = 4
        
        # Case details completed
        if case.title and case.description and case.case_type and case.province:
            score += 0.3
        
        # Legal journey started
        if legal_journey:
            score += 0.3
            
            # Journey stages progress
            if legal_journey.current_stage_index > 0:
                score += 0.2
        
        # Initial assessment done (based on case analysis)
        if hasattr(case, 'merit_score') and case.merit_score:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_evidence_progress(self, evidence_list: List[Evidence]) -> float:
        """Calculate evidence gathering progress"""
        if not evidence_list:
            return 0.0
        
        total_evidence = len(evidence_list)
        analyzed_evidence = len([e for e in evidence_list if e.status == EvidenceStatus.ANALYZED])
        high_relevance = len([e for e in evidence_list if e.ai_relevance_score and e.ai_relevance_score >= 0.7])
        
        # Base score from having evidence
        base_score = min(total_evidence / 5, 0.6)  # Max 0.6 for having 5+ pieces of evidence
        
        # Analysis completion score
        analysis_score = (analyzed_evidence / total_evidence) * 0.3 if total_evidence > 0 else 0
        
        # Quality score (high relevance evidence)
        quality_score = min(high_relevance / max(total_evidence, 1), 0.5) * 0.1
        
        return min(base_score + analysis_score + quality_score, 1.0)
    
    def _calculate_form_progress(self, court_forms: List[CourtForm]) -> float:
        """Calculate form completion progress"""
        if not court_forms:
            return 0.0
        
        total_forms = len(court_forms)
        completed_forms = len([f for f in court_forms if f.status == FormStatus.COMPLETED])
        submitted_forms = len([f for f in court_forms if f.status == FormStatus.SUBMITTED])
        
        completion_score = (completed_forms / total_forms) * 0.7
        submission_score = (submitted_forms / total_forms) * 0.3
        
        return min(completion_score + submission_score, 1.0)
    
    def _calculate_review_progress(self, case: Case, court_forms: List[CourtForm]) -> float:
        """Calculate review and submission progress"""
        score = 0.0
        
        # Forms reviewed and ready
        if court_forms:
            ready_forms = len([f for f in court_forms if f.status in [FormStatus.COMPLETED, FormStatus.SUBMITTED]])
            score += (ready_forms / len(court_forms)) * 0.6
        
        # Case review completed (could be tracked as a case field)
        if hasattr(case, 'review_completed') and case.review_completed:
            score += 0.4
        
        return min(score, 1.0)
    
    def _calculate_court_progress(self, case: Case) -> float:
        """Calculate court process progress"""
        score = 0.0
        
        # Court dates scheduled
        if hasattr(case, 'court_date') and case.court_date:
            score += 0.4
        
        # Documents submitted to court
        if case.status in [CaseStatus.IN_PROGRESS, CaseStatus.AWAITING_HEARING]:
            score += 0.3
        
        # Hearing attended
        if case.status == CaseStatus.AWAITING_DECISION:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_resolution_progress(self, case: Case) -> float:
        """Calculate resolution progress"""
        if case.status in [CaseStatus.RESOLVED, CaseStatus.CLOSED]:
            return 1.0
        elif case.status == CaseStatus.AWAITING_DECISION:
            return 0.5
        return 0.0
    
    def _determine_current_stage(self, stage_progress: Dict[str, float]) -> str:
        """Determine the current active stage based on progress"""
        # Find the first incomplete stage or the most advanced stage
        for stage in ProgressStage:
            stage_score = stage_progress.get(stage.value, 0)
            if stage_score < 1.0:
                return stage.value
        
        return ProgressStage.RESOLUTION.value
    
    def _get_next_actions(self, case: Case, stage_progress: Dict[str, float], current_stage: str) -> List[Dict[str, Any]]:
        """Get recommended next actions based on current progress"""
        actions = []
        
        if current_stage == ProgressStage.PREPARATION.value:
            if not case.title or not case.description:
                actions.append({
                    'title': 'Complete Case Details',
                    'description': 'Fill in all basic case information',
                    'priority': PriorityLevel.HIGH.value,
                    'url': f'/cases/{case.id}/edit'
                })
            
            legal_journey = LegalJourney.query.filter_by(case_id=case.id).first()
            if not legal_journey:
                actions.append({
                    'title': 'Start Legal Journey',
                    'description': 'Begin the guided legal process',
                    'priority': PriorityLevel.HIGH.value,
                    'url': f'/journey/start/{case.id}'
                })
        
        elif current_stage == ProgressStage.EVIDENCE_GATHERING.value:
            evidence_count = Evidence.query.filter_by(case_id=case.id).count()
            if evidence_count < 3:
                actions.append({
                    'title': 'Upload More Evidence',
                    'description': 'Add supporting documents to strengthen your case',
                    'priority': PriorityLevel.HIGH.value,
                    'url': f'/evidence/upload?case_id={case.id}'
                })
            
            unanalyzed = Evidence.query.filter_by(
                case_id=case.id, 
                status=EvidenceStatus.UPLOADED
            ).count()
            if unanalyzed > 0:
                actions.append({
                    'title': 'Review Evidence Analysis',
                    'description': f'{unanalyzed} pieces of evidence need analysis',
                    'priority': PriorityLevel.MEDIUM.value,
                    'url': f'/evidence/review/{case.id}'
                })
        
        elif current_stage == ProgressStage.FORM_COMPLETION.value:
            incomplete_forms = CourtForm.query.filter_by(
                case_id=case.id,
                status=FormStatus.DRAFT
            ).count()
            if incomplete_forms > 0:
                actions.append({
                    'title': 'Complete Court Forms',
                    'description': f'{incomplete_forms} forms need to be completed',
                    'priority': PriorityLevel.HIGH.value,
                    'url': f'/forms/case/{case.id}'
                })
        
        # Add deadline-based actions
        deadline_actions = self._get_deadline_actions(case.id)
        actions.extend(deadline_actions)
        
        return actions[:5]  # Return top 5 actions
    
    def _get_deadline_actions(self, case_id: int) -> List[Dict[str, Any]]:
        """Get actions based on upcoming deadlines"""
        actions = []
        
        # Check for upcoming court dates, filing deadlines, etc.
        # This would integrate with a deadline/calendar system
        
        return actions
    
    def _get_case_milestones(self, case_id: int) -> List[Dict[str, Any]]:
        """Get case milestones and timeline"""
        case = Case.query.get(case_id)
        if not case:
            return []
        
        milestones = []
        
        # Case creation milestone
        milestones.append({
            'type': MilestoneType.CASE_CREATED.value,
            'title': 'Case Created',
            'description': f'Legal case "{case.title}" was created',
            'date': case.created_at.isoformat() if case.created_at else None,
            'completed': True,
            'icon': 'fas fa-plus-circle',
            'color': 'success'
        })
        
        # Evidence milestones
        evidence_list = Evidence.query.filter_by(case_id=case_id).order_by(Evidence.uploaded_at).all()
        for evidence in evidence_list[:3]:  # Show first 3 evidence uploads
            milestones.append({
                'type': MilestoneType.EVIDENCE_UPLOADED.value,
                'title': 'Evidence Uploaded',
                'description': f'Uploaded "{evidence.title}"',
                'date': evidence.uploaded_at.isoformat() if evidence.uploaded_at else None,
                'completed': True,
                'icon': 'fas fa-file-upload',
                'color': 'info'
            })
        
        # Form completion milestones
        court_forms = CourtForm.query.filter_by(case_id=case_id).all()
        for form in court_forms:
            if form.status in [FormStatus.COMPLETED, FormStatus.SUBMITTED]:
                milestones.append({
                    'type': MilestoneType.FORM_COMPLETED.value,
                    'title': 'Form Completed',
                    'description': f'Completed {form.form_name}',
                    'date': form.updated_at.isoformat() if form.updated_at else None,
                    'completed': True,
                    'icon': 'fas fa-check-circle',
                    'color': 'success'
                })
        
        # Future milestones based on case status
        if case.status not in [CaseStatus.RESOLVED, CaseStatus.CLOSED]:
            # Add upcoming milestones
            next_milestones = self._get_upcoming_milestones(case)
            milestones.extend(next_milestones)
        
        # Sort by date
        milestones.sort(key=lambda x: x['date'] or '9999-12-31')
        
        return milestones
    
    def _get_upcoming_milestones(self, case: Case) -> List[Dict[str, Any]]:
        """Get upcoming milestones based on case progress"""
        upcoming = []
        
        # Check what milestones are likely coming up
        incomplete_forms = CourtForm.query.filter_by(
            case_id=case.id,
            status=FormStatus.DRAFT
        ).count()
        
        if incomplete_forms > 0:
            upcoming.append({
                'type': MilestoneType.FORM_COMPLETED.value,
                'title': 'Complete Remaining Forms',
                'description': f'{incomplete_forms} forms to complete',
                'date': None,
                'completed': False,
                'icon': 'fas fa-clock',
                'color': 'warning'
            })
        
        if case.status == CaseStatus.DRAFT:
            upcoming.append({
                'type': MilestoneType.DOCUMENT_SUBMITTED.value,
                'title': 'Submit Documents',
                'description': 'Submit completed forms to court',
                'date': None,
                'completed': False,
                'icon': 'fas fa-paper-plane',
                'color': 'primary'
            })
        
        return upcoming
    
    def _estimate_completion_date(self, case: Case, overall_progress: float) -> Optional[str]:
        """Estimate case completion date based on progress"""
        if overall_progress >= 1.0:
            return None  # Already complete
        
        # Calculate estimated completion based on case type and progress
        days_created = (datetime.utcnow() - case.created_at).days if case.created_at else 30
        
        # Estimate based on case type
        estimated_total_days = {
            'family': 180,  # 6 months
            'civil': 240,   # 8 months
            'employment': 120,  # 4 months
            'landlord_tenant': 90,  # 3 months
            'small_claims': 60,  # 2 months
        }.get(case.case_type.value if case.case_type else 'civil', 180)
        
        # Adjust based on current progress
        if overall_progress > 0:
            remaining_days = (estimated_total_days - days_created) * (1 - overall_progress)
            estimated_completion = datetime.utcnow() + timedelta(days=int(remaining_days))
            return estimated_completion.isoformat()
        
        return None
    
    def _calculate_progress_trend(self, case_id: int) -> Dict[str, Any]:
        """Calculate progress trend over time"""
        # This would analyze historical progress data
        # For now, return a simple trend based on recent activity
        
        recent_activity = self._get_recent_activity_count(case_id, days=7)
        
        if recent_activity >= 3:
            trend = 'increasing'
        elif recent_activity >= 1:
            trend = 'steady'
        else:
            trend = 'stalled'
        
        return {
            'trend': trend,
            'recent_activity': recent_activity,
            'description': self._get_trend_description(trend)
        }
    
    def _get_recent_activity_count(self, case_id: int, days: int = 7) -> int:
        """Count recent activity for the case"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        evidence_count = Evidence.query.filter(
            Evidence.case_id == case_id,
            Evidence.uploaded_at >= cutoff_date
        ).count()
        
        form_count = CourtForm.query.filter(
            CourtForm.case_id == case_id,
            CourtForm.updated_at >= cutoff_date
        ).count()
        
        return evidence_count + form_count
    
    def _get_trend_description(self, trend: str) -> str:
        """Get human-readable trend description"""
        descriptions = {
            'increasing': 'Great progress! You\'ve been very active recently.',
            'steady': 'Steady progress. Keep up the good work.',
            'stalled': 'Progress has slowed. Consider taking the next recommended action.'
        }
        return descriptions.get(trend, 'Progress tracking available.')
    
    def _identify_blocking_issues(self, case: Case, evidence_list: List[Evidence], 
                                 court_forms: List[CourtForm]) -> List[Dict[str, Any]]:
        """Identify issues that might be blocking case progress"""
        issues = []
        
        # Check for evidence issues
        error_evidence = [e for e in evidence_list if e.status == EvidenceStatus.ERROR]
        if error_evidence:
            issues.append({
                'type': 'evidence_error',
                'title': 'Evidence Processing Errors',
                'description': f'{len(error_evidence)} pieces of evidence failed to process',
                'severity': 'medium',
                'action_url': f'/evidence/review/{case.id}'
            })
        
        # Check for low relevance evidence
        low_relevance = [e for e in evidence_list 
                        if e.ai_relevance_score and e.ai_relevance_score < 0.3]
        if len(low_relevance) > len(evidence_list) * 0.7 and evidence_list:
            issues.append({
                'type': 'low_relevance',
                'title': 'Evidence Quality Concerns',
                'description': 'Most evidence has low relevance scores',
                'severity': 'medium',
                'action_url': f'/evidence/upload?case_id={case.id}'
            })
        
        # Check for incomplete forms
        draft_forms = [f for f in court_forms if f.status == FormStatus.DRAFT]
        if draft_forms and len(draft_forms) == len(court_forms):
            issues.append({
                'type': 'incomplete_forms',
                'title': 'Incomplete Court Forms',
                'description': 'All court forms are still in draft status',
                'severity': 'high',
                'action_url': f'/forms/case/{case.id}'
            })
        
        return issues
    
    def record_milestone(self, case_id: int, milestone_type: MilestoneType, 
                        title: str, description: str = '', custom_data: Dict = None) -> bool:
        """Record a case milestone"""
        try:
            # This would be stored in a milestones table
            # For now, we can use the case's metadata or create a simple log
            
            case = Case.query.get(case_id)
            if not case:
                return False
            
            # Store milestone in case metadata
            if not hasattr(case, 'milestones') or not case.milestones:
                case.milestones = []
            
            milestone = {
                'type': milestone_type.value,
                'title': title,
                'description': description,
                'date': datetime.utcnow().isoformat(),
                'custom_data': custom_data or {}
            }
            
            # Add to milestones list (keep last 50)
            milestones = case.milestones or []
            milestones.append(milestone)
            case.milestones = milestones[-50:]  # Keep last 50 milestones
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Error recording milestone: {str(e)}")
            return False
    
    def get_case_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get overall case statistics for a user"""
        user_cases = Case.query.filter_by(user_id=user_id).all()
        
        if not user_cases:
            return {
                'total_cases': 0,
                'active_cases': 0,
                'completed_cases': 0,
                'average_progress': 0,
                'cases_by_stage': {},
                'recent_activity': 0
            }
        
        # Calculate statistics
        total_cases = len(user_cases)
        active_cases = len([c for c in user_cases if c.status not in [CaseStatus.RESOLVED, CaseStatus.CLOSED]])
        completed_cases = len([c for c in user_cases if c.status in [CaseStatus.RESOLVED, CaseStatus.CLOSED]])
        
        # Calculate average progress
        total_progress = 0
        cases_by_stage = {}
        
        for case in user_cases:
            progress_data = self.get_case_progress(case.id)
            total_progress += progress_data.get('overall_progress', 0)
            
            current_stage = progress_data.get('current_stage', 'preparation')
            cases_by_stage[current_stage] = cases_by_stage.get(current_stage, 0) + 1
        
        average_progress = total_progress / total_cases if total_cases > 0 else 0
        
        # Recent activity across all cases
        recent_activity = sum(self._get_recent_activity_count(case.id) for case in user_cases)
        
        return {
            'total_cases': total_cases,
            'active_cases': active_cases,
            'completed_cases': completed_cases,
            'average_progress': round(average_progress, 1),
            'cases_by_stage': cases_by_stage,
            'recent_activity': recent_activity,
            'completion_rate': round((completed_cases / total_cases) * 100, 1) if total_cases > 0 else 0
        }