"""
Case Management Dashboard System
Provides comprehensive dashboard data and analytics for user cases
"""

from typing import Dict, List, Any, Optional, Tuple
from models.case import Case
from models.evidence import Evidence
from models.court_form import FormSubmission
from models.legal_journey import JourneyStage, JourneyStep, StageStatus
from models.notification import Notification, NotificationType, NotificationPriority
from models import db
from utils.legal_journey import LegalJourneyManager
from utils.merit_scoring import calculate_case_merit
import json
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func

class DashboardManager:
    """Manages dashboard data aggregation and analytics"""
    
    def __init__(self):
        self.journey_manager = LegalJourneyManager()
    
    def get_user_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user"""
        try:
            # Get all user cases
            cases = Case.query.filter_by(user_id=user_id).order_by(Case.updated_at.desc()).all()
            
            # Aggregate dashboard metrics
            metrics = self._calculate_dashboard_metrics(cases)
            
            # Get recent activity
            recent_activity = self._get_recent_activity(user_id, limit=10)
            
            # Get upcoming deadlines
            upcoming_deadlines = self._get_upcoming_deadlines(cases)
            
            # Get priority cases
            priority_cases = self._get_priority_cases(cases)
            
            # Get journey progress summaries
            journey_summaries = self._get_journey_summaries(cases)
            
            # Get case summaries with enhanced data
            case_summaries = self._get_enhanced_case_summaries(cases)
            
            # Get actionable items
            actionable_items = self._get_actionable_items(cases, user_id)
            
            # Get recent notifications
            notifications = self._get_recent_notifications(user_id)
            
            return {
                'success': True,
                'metrics': metrics,
                'cases': case_summaries,
                'recent_activity': recent_activity,
                'upcoming_deadlines': upcoming_deadlines,
                'priority_cases': priority_cases,
                'journey_summaries': journey_summaries,
                'actionable_items': actionable_items,
                'notifications': notifications,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _calculate_dashboard_metrics(self, cases: List[Case]) -> Dict[str, Any]:
        """Calculate key dashboard metrics"""
        total_cases = len(cases)
        
        if total_cases == 0:
            return {
                'total_cases': 0,
                'active_cases': 0,
                'completed_cases': 0,
                'high_priority_cases': 0,
                'cases_with_deadlines': 0,
                'average_merit_score': 0,
                'completion_rate': 0
            }
        
        # Status breakdown
        active_cases = len([c for c in cases if c.status in [CaseStatus.INITIAL, CaseStatus.ACTIVE, CaseStatus.IN_PROGRESS]])
        completed_cases = len([c for c in cases if c.status == CaseStatus.COMPLETED])
        high_priority_cases = len([c for c in cases if c.priority == CasePriority.HIGH])
        cases_with_deadlines = len([c for c in cases if c.filing_deadline or c.hearing_date])
        
        # Merit score analysis
        merit_scores = [c.merit_score for c in cases if c.merit_score is not None]
        average_merit_score = sum(merit_scores) / len(merit_scores) if merit_scores else 0
        
        # Journey completion analysis
        cases_with_journeys = 0
        total_journey_progress = 0
        
        for case in cases:
            journey_progress = self.journey_manager.get_journey_progress(case)
            if journey_progress['total_stages'] > 0:
                cases_with_journeys += 1
                total_journey_progress += journey_progress['progress_percentage']
        
        average_journey_progress = total_journey_progress / cases_with_journeys if cases_with_journeys > 0 else 0
        
        return {
            'total_cases': total_cases,
            'active_cases': active_cases,
            'completed_cases': completed_cases,
            'high_priority_cases': high_priority_cases,
            'cases_with_deadlines': cases_with_deadlines,
            'average_merit_score': round(average_merit_score, 1),
            'average_journey_progress': round(average_journey_progress, 1),
            'completion_rate': round((completed_cases / total_cases) * 100, 1) if total_cases > 0 else 0,
            'cases_with_journeys': cases_with_journeys
        }
    
    def _get_recent_activity(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity across all user data"""
        activities = []
        
        try:
            # Recent cases
            recent_cases = Case.query.filter_by(user_id=user_id).order_by(Case.updated_at.desc()).limit(5).all()
            for case in recent_cases:
                activities.append({
                    'type': 'case_update',
                    'title': f'Case updated: {case.title}',
                    'description': f'Case "{case.title}" was last updated',
                    'timestamp': case.updated_at,
                    'case_id': case.id,
                    'icon': 'fas fa-briefcase',
                    'color': 'primary'
                })
            
            # Recent evidence uploads
            recent_evidence = db.session.query(Evidence).join(Case).filter(
                Case.user_id == user_id
            ).order_by(Evidence.created_at.desc()).limit(5).all()
            
            for evidence in recent_evidence:
                activities.append({
                    'type': 'evidence_upload',
                    'title': f'Evidence uploaded: {evidence.title}',
                    'description': f'New evidence added to case "{evidence.case.title}"',
                    'timestamp': evidence.created_at,
                    'case_id': evidence.case_id,
                    'evidence_id': evidence.id,
                    'icon': 'fas fa-file-upload',
                    'color': 'success'
                })
            
            # Recent form submissions
            recent_forms = db.session.query(FormSubmission).join(Case).filter(
                Case.user_id == user_id
            ).order_by(FormSubmission.created_at.desc()).limit(5).all()
            
            for form in recent_forms:
                activities.append({
                    'type': 'form_submission',
                    'title': f'Form created: {form.template.name}',
                    'description': f'New form submission for case "{form.case.title if form.case else "N/A"}"',
                    'timestamp': form.created_at,
                    'case_id': form.case_id,
                    'form_id': form.id,
                    'icon': 'fas fa-file-alt',
                    'color': 'info'
                })
            
            # Recent journey step completions
            recent_steps = db.session.query(JourneyStep).join(JourneyStage).join(Case).filter(
                and_(Case.user_id == user_id, JourneyStep.is_completed == True)
            ).order_by(JourneyStep.completed_at.desc()).limit(5).all()
            
            for step in recent_steps:
                activities.append({
                    'type': 'step_completion',
                    'title': f'Step completed: {step.name}',
                    'description': f'Journey step completed in case "{step.stage.case.title}"',
                    'timestamp': step.completed_at,
                    'case_id': step.stage.case_id,
                    'step_id': step.id,
                    'icon': 'fas fa-check-circle',
                    'color': 'success'
                })
            
            # Sort by timestamp and limit
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            print(f"Error getting recent activity: {str(e)}")
        
        return activities[:limit]
    
    def _get_upcoming_deadlines(self, cases: List[Case]) -> List[Dict[str, Any]]:
        """Get upcoming deadlines from cases"""
        deadlines = []
        now = datetime.now().date()
        
        for case in cases:
            # Filing deadlines
            if case.filing_deadline and case.filing_deadline >= now:
                days_until = (case.filing_deadline - now).days
                urgency = 'danger' if days_until <= 7 else 'warning' if days_until <= 30 else 'info'
                
                deadlines.append({
                    'type': 'filing_deadline',
                    'title': 'Filing Deadline',
                    'case_title': case.title,
                    'case_id': case.id,
                    'date': case.filing_deadline,
                    'days_until': days_until,
                    'urgency': urgency,
                    'description': f'Case "{case.title}" filing deadline'
                })
            
            # Hearing dates
            if case.hearing_date and case.hearing_date.date() >= now:
                days_until = (case.hearing_date.date() - now).days
                urgency = 'danger' if days_until <= 3 else 'warning' if days_until <= 14 else 'info'
                
                deadlines.append({
                    'type': 'hearing_date',
                    'title': 'Court Hearing',
                    'case_title': case.title,
                    'case_id': case.id,
                    'date': case.hearing_date.date(),
                    'time': case.hearing_date.time(),
                    'days_until': days_until,
                    'urgency': urgency,
                    'description': f'Court hearing for case "{case.title}"'
                })
        
        # Sort by date
        deadlines.sort(key=lambda x: x['date'])
        
        return deadlines[:10]  # Return next 10 deadlines
    
    def _get_priority_cases(self, cases: List[Case]) -> List[Dict[str, Any]]:
        """Get high priority cases that need attention"""
        priority_cases = []
        
        # High priority cases
        high_priority = [c for c in cases if c.priority == CasePriority.HIGH and c.status != CaseStatus.COMPLETED]
        
        # Cases with approaching deadlines
        now = datetime.now().date()
        urgent_deadline_cases = [
            c for c in cases 
            if (c.filing_deadline and (c.filing_deadline - now).days <= 14) or 
               (c.hearing_date and (c.hearing_date.date() - now).days <= 14)
        ]
        
        # Cases with low merit scores that need attention
        low_merit_cases = [c for c in cases if c.merit_score and c.merit_score < 40]
        
        # Combine and deduplicate
        all_priority_cases = set(high_priority + urgent_deadline_cases + low_merit_cases)
        
        for case in all_priority_cases:
            priority_reasons = []
            
            if case.priority == CasePriority.HIGH:
                priority_reasons.append('High Priority')
            
            if case.filing_deadline and (case.filing_deadline - now).days <= 14:
                priority_reasons.append('Approaching Filing Deadline')
            
            if case.hearing_date and (case.hearing_date.date() - now).days <= 14:
                priority_reasons.append('Upcoming Hearing')
            
            if case.merit_score and case.merit_score < 40:
                priority_reasons.append('Low Merit Score')
            
            priority_cases.append({
                'case': case,
                'reasons': priority_reasons,
                'urgency_score': len(priority_reasons)
            })
        
        # Sort by urgency score
        priority_cases.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return priority_cases[:5]  # Return top 5 priority cases
    
    def _get_journey_summaries(self, cases: List[Case]) -> List[Dict[str, Any]]:
        """Get journey progress summaries for cases"""
        summaries = []
        
        for case in cases:
            progress = self.journey_manager.get_journey_progress(case)
            if progress['total_stages'] > 0:
                current_stage_name = progress['current_stage'].name if progress['current_stage'] else 'Not Started'
                
                summaries.append({
                    'case': case,
                    'progress_percentage': progress['progress_percentage'],
                    'completed_stages': progress['completed_stages'],
                    'total_stages': progress['total_stages'],
                    'current_stage': current_stage_name,
                    'estimated_completion': progress['estimated_completion_date']
                })
        
        return summaries
    
    def _get_enhanced_case_summaries(self, cases: List[Case]) -> List[Dict[str, Any]]:
        """Get enhanced case summaries with additional metadata"""
        summaries = []
        
        for case in cases:
            # Evidence summary
            evidence_count = Evidence.query.filter_by(case_id=case.id).count()
            processed_evidence = Evidence.query.filter_by(
                case_id=case.id, 
                status=EvidenceStatus.ANALYZED
            ).count()
            
            # Form summary
            form_count = FormSubmission.query.filter_by(case_id=case.id).count()
            completed_forms = FormSubmission.query.filter_by(
                case_id=case.id, 
                status=SubmissionStatus.COMPLETED
            ).count()
            
            # Journey progress
            journey_progress = self.journey_manager.get_journey_progress(case)
            
            summaries.append({
                'case': case,
                'evidence_count': evidence_count,
                'processed_evidence': processed_evidence,
                'form_count': form_count,
                'completed_forms': completed_forms,
                'journey_progress': journey_progress['progress_percentage'],
                'current_stage': journey_progress['current_stage'].name if journey_progress['current_stage'] else None
            })
        
        return summaries
    
    def _get_actionable_items(self, cases: List[Case], user_id: int) -> List[Dict[str, Any]]:
        """Get actionable items across all cases"""
        items = []
        
        for case in cases:
            if case.status == CaseStatus.COMPLETED:
                continue
            
            # Next journey steps
            next_steps = self.journey_manager.get_next_steps(case, limit=2)
            for step in next_steps:
                items.append({
                    'type': 'journey_step',
                    'title': step.name,
                    'description': step.description,
                    'case_id': case.id,
                    'case_title': case.title,
                    'priority': 'high' if step.is_required else 'medium',
                    'action_url': f'/journey/step/{step.id}',
                    'icon': 'fas fa-tasks'
                })
            
            # Evidence to upload
            if Evidence.query.filter_by(case_id=case.id).count() == 0:
                items.append({
                    'type': 'upload_evidence',
                    'title': 'Upload Evidence',
                    'description': f'Add supporting evidence to strengthen case "{case.title}"',
                    'case_id': case.id,
                    'case_title': case.title,
                    'priority': 'high',
                    'action_url': f'/cases/{case.id}/evidence/upload',
                    'icon': 'fas fa-upload'
                })
            
            # Merit analysis
            if not case.merit_score:
                items.append({
                    'type': 'merit_analysis',
                    'title': 'Analyze Case Merit',
                    'description': f'Get AI-powered merit analysis for case "{case.title}"',
                    'case_id': case.id,
                    'case_title': case.title,
                    'priority': 'medium',
                    'action_url': f'/cases/{case.id}/analysis',
                    'icon': 'fas fa-chart-bar'
                })
            
            # Forms to complete
            if FormSubmission.query.filter_by(case_id=case.id).count() == 0:
                items.append({
                    'type': 'create_forms',
                    'title': 'Prepare Court Forms',
                    'description': f'Create required forms for case "{case.title}"',
                    'case_id': case.id,
                    'case_title': case.title,
                    'priority': 'medium',
                    'action_url': f'/forms/case/{case.id}',
                    'icon': 'fas fa-file-alt'
                })
        
        # Sort by priority
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        items.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return items[:15]  # Return top 15 actionable items
    
    def _get_recent_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recent notifications for the user"""
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id
            ).order_by(Notification.created_at.desc()).limit(10).all()
            
            notification_data = []
            for notification in notifications:
                notification_data.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type.value,
                    'priority': notification.priority.value,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at,
                    'case_id': notification.case_id
                })
            
            return notification_data
            
        except Exception as e:
            print(f"Error getting notifications: {str(e)}")
            return []
    
    def get_case_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get detailed analytics for user's cases"""
        try:
            cases = Case.query.filter_by(user_id=user_id).all()
            
            # Case type distribution
            case_types = {}
            for case in cases:
                case_type = case.case_type.value if case.case_type else 'unknown'
                case_types[case_type] = case_types.get(case_type, 0) + 1
            
            # Status distribution
            statuses = {}
            for case in cases:
                status = case.status.value if case.status else 'unknown'
                statuses[status] = statuses.get(status, 0) + 1
            
            # Merit score distribution
            merit_scores = [c.merit_score for c in cases if c.merit_score is not None]
            merit_distribution = {
                'high': len([s for s in merit_scores if s >= 80]),
                'medium': len([s for s in merit_scores if 60 <= s < 80]),
                'low': len([s for s in merit_scores if s < 60])
            }
            
            # Monthly case creation trends (last 12 months)
            monthly_trends = {}
            now = datetime.now()
            for i in range(12):
                month_date = now - timedelta(days=30*i)
                month_key = month_date.strftime('%Y-%m')
                monthly_trends[month_key] = 0
            
            for case in cases:
                if case.created_at:
                    month_key = case.created_at.strftime('%Y-%m')
                    if month_key in monthly_trends:
                        monthly_trends[month_key] += 1
            
            return {
                'success': True,
                'case_types': case_types,
                'statuses': statuses,
                'merit_distribution': merit_distribution,
                'monthly_trends': monthly_trends,
                'total_cases': len(cases)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as time ago string"""
    if not timestamp:
        return 'Unknown'
    
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        if diff.days == 1:
            return '1 day ago'
        elif diff.days < 30:
            return f'{diff.days} days ago'
        elif diff.days < 365:
            months = diff.days // 30
            return f'{months} month{"s" if months > 1 else ""} ago'
        else:
            years = diff.days // 365
            return f'{years} year{"s" if years > 1 else ""} ago'
    
    hours = diff.seconds // 3600
    if hours > 0:
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    
    minutes = diff.seconds // 60
    if minutes > 0:
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    
    return 'Just now'

def get_urgency_class(urgency: str) -> str:
    """Get Bootstrap CSS class for urgency level"""
    urgency_classes = {
        'danger': 'danger',
        'warning': 'warning',
        'info': 'info',
        'success': 'success'
    }
    return urgency_classes.get(urgency, 'secondary')