"""
Notification System for Smart Dispute Flask App
Manages notifications, reminders, deadlines, and user alerts
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from models.notification import Notification, NotificationType, NotificationPriority
from models.case import Case
from models.evidence import Evidence
from models.court_form import CourtForm
from models.legal_journey import LegalJourney
from models.user import User
from models import db
from utils.case_tracking import CaseTracker
import json

class NotificationTrigger(Enum):
    """Events that can trigger notifications"""
    CASE_CREATED = "case_created"
    EVIDENCE_UPLOADED = "evidence_uploaded"
    EVIDENCE_ANALYZED = "evidence_analyzed"
    FORM_COMPLETED = "form_completed"
    JOURNEY_STAGE_COMPLETED = "journey_stage_completed"
    DEADLINE_APPROACHING = "deadline_approaching"
    DEADLINE_OVERDUE = "deadline_overdue"
    PROGRESS_MILESTONE = "progress_milestone"
    BLOCKING_ISSUE = "blocking_issue"
    SYSTEM_UPDATE = "system_update"

class DeadlineType(Enum):
    """Types of deadlines that need tracking"""
    COURT_FILING = "court_filing"
    EVIDENCE_SUBMISSION = "evidence_submission"
    RESPONSE_DEADLINE = "response_deadline"
    HEARING_DATE = "hearing_date"
    APPEAL_DEADLINE = "appeal_deadline"
    DOCUMENT_SERVICE = "document_service"
    PAYMENT_DUE = "payment_due"
    CUSTOM = "custom"

class NotificationManager:
    """Main notification management system"""
    
    def __init__(self):
        self.reminder_intervals = {
            NotificationPriority.URGENT: [1, 3, 7],  # Days before deadline
            NotificationPriority.HIGH: [3, 7, 14],
            NotificationPriority.MEDIUM: [7, 14, 30],
            NotificationPriority.LOW: [14, 30]
        }
    
    def create_notification(self, user_id: int, notification_type: NotificationType,
                          title: str, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM,
                          case_id: int = None, action_url: str = None, 
                          scheduled_for: datetime = None, metadata: Dict = None) -> Notification:
        """Create a new notification"""
        try:
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                case_id=case_id,
                action_url=action_url,
                scheduled_for=scheduled_for or datetime.utcnow(),
                metadata=metadata or {}
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return notification
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating notification: {str(e)}")
            return None
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False,
                             limit: int = 50) -> List[Notification]:
        """Get notifications for a user"""
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id, 
                user_id=user_id
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            print(f"Error marking notification as read: {str(e)}")
            return False
    
    def mark_all_read(self, user_id: int) -> bool:
        """Mark all notifications as read for a user"""
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).all()
            
            for notification in notifications:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error marking all notifications as read: {str(e)}")
            return False
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                db.session.delete(notification)
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting notification: {str(e)}")
            return False
    
    def get_notification_summary(self, user_id: int) -> Dict[str, Any]:
        """Get notification summary for a user"""
        try:
            total_count = Notification.query.filter_by(user_id=user_id).count()
            unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
            
            # Count by priority
            priority_counts = {}
            for priority in NotificationPriority:
                count = Notification.query.filter_by(
                    user_id=user_id,
                    is_read=False,
                    priority=priority
                ).count()
                priority_counts[priority.value] = count
            
            # Count by type
            type_counts = {}
            for notif_type in NotificationType:
                count = Notification.query.filter_by(
                    user_id=user_id,
                    is_read=False,
                    notification_type=notif_type
                ).count()
                type_counts[notif_type.value] = count
            
            return {
                'total_count': total_count,
                'unread_count': unread_count,
                'priority_counts': priority_counts,
                'type_counts': type_counts
            }
            
        except Exception as e:
            print(f"Error getting notification summary: {str(e)}")
            return {
                'total_count': 0,
                'unread_count': 0,
                'priority_counts': {},
                'type_counts': {}
            }
    
    def trigger_notification(self, trigger: NotificationTrigger, 
                           user_id: int, case_id: int = None, **kwargs) -> bool:
        """Trigger notifications based on system events"""
        try:
            if trigger == NotificationTrigger.CASE_CREATED:
                return self._handle_case_created(user_id, case_id, **kwargs)
            
            elif trigger == NotificationTrigger.EVIDENCE_UPLOADED:
                return self._handle_evidence_uploaded(user_id, case_id, **kwargs)
            
            elif trigger == NotificationTrigger.EVIDENCE_ANALYZED:
                return self._handle_evidence_analyzed(user_id, case_id, **kwargs)
            
            elif trigger == NotificationTrigger.FORM_COMPLETED:
                return self._handle_form_completed(user_id, case_id, **kwargs)
            
            elif trigger == NotificationTrigger.JOURNEY_STAGE_COMPLETED:
                return self._handle_journey_stage_completed(user_id, case_id, **kwargs)
            
            elif trigger == NotificationTrigger.PROGRESS_MILESTONE:
                return self._handle_progress_milestone(user_id, case_id, **kwargs)
            
            elif trigger == NotificationTrigger.BLOCKING_ISSUE:
                return self._handle_blocking_issue(user_id, case_id, **kwargs)
            
            return False
            
        except Exception as e:
            print(f"Error triggering notification: {str(e)}")
            return False
    
    def _handle_case_created(self, user_id: int, case_id: int, **kwargs) -> bool:
        """Handle case creation notification"""
        case = Case.query.get(case_id)
        if not case:
            return False
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.CASE_UPDATE,
            title="New Case Created",
            message=f'Your case "{case.title}" has been successfully created. Start by uploading evidence or completing court forms.',
            priority=NotificationPriority.MEDIUM,
            case_id=case_id,
            action_url=f'/cases/{case_id}'
        ) is not None
    
    def _handle_evidence_uploaded(self, user_id: int, case_id: int, **kwargs) -> bool:
        """Handle evidence upload notification"""
        evidence_title = kwargs.get('evidence_title', 'New evidence')
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.EVIDENCE_UPDATE,
            title="Evidence Uploaded",
            message=f'"{evidence_title}" has been uploaded and is being processed.',
            priority=NotificationPriority.LOW,
            case_id=case_id,
            action_url=f'/evidence/review/{case_id}'
        ) is not None
    
    def _handle_evidence_analyzed(self, user_id: int, case_id: int, **kwargs) -> bool:
        """Handle evidence analysis completion"""
        evidence_title = kwargs.get('evidence_title', 'Evidence')
        relevance_score = kwargs.get('relevance_score', 0)
        
        if relevance_score >= 0.8:
            priority = NotificationPriority.HIGH
            message = f'"{evidence_title}" analysis complete! High relevance score ({int(relevance_score*100)}%). This could strengthen your case significantly.'
        elif relevance_score >= 0.5:
            priority = NotificationPriority.MEDIUM
            message = f'"{evidence_title}" analysis complete. Medium relevance score ({int(relevance_score*100)}%).'
        else:
            priority = NotificationPriority.LOW
            message = f'"{evidence_title}" analysis complete. Consider uploading additional supporting evidence.'
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.EVIDENCE_UPDATE,
            title="Evidence Analysis Complete",
            message=message,
            priority=priority,
            case_id=case_id,
            action_url=f'/evidence/review/{case_id}'
        ) is not None
    
    def _handle_form_completed(self, user_id: int, case_id: int, **kwargs) -> bool:
        """Handle form completion notification"""
        form_name = kwargs.get('form_name', 'Court form')
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.FORM_UPDATE,
            title="Form Completed",
            message=f'"{form_name}" has been completed. Review and submit when ready.',
            priority=NotificationPriority.MEDIUM,
            case_id=case_id,
            action_url=f'/forms/case/{case_id}'
        ) is not None
    
    def _handle_journey_stage_completed(self, user_id: int, case_id: int, **kwargs) -> bool:
        """Handle legal journey stage completion"""
        stage_name = kwargs.get('stage_name', 'Legal journey stage')
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.JOURNEY_UPDATE,
            title="Journey Stage Completed",
            message=f'You\'ve completed "{stage_name}". Continue to the next step in your legal journey.',
            priority=NotificationPriority.MEDIUM,
            case_id=case_id,
            action_url=f'/journey/case/{case_id}'
        ) is not None
    
    def _handle_progress_milestone(self, user_id: int, case_id: int, **kwargs) -> bool:
        """Handle progress milestone notifications"""
        milestone_percent = kwargs.get('milestone_percent', 0)
        case = Case.query.get(case_id)
        
        if milestone_percent in [25, 50, 75, 100]:
            return self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.PROGRESS_UPDATE,
                title=f"Progress Milestone: {milestone_percent}%",
                message=f'Great progress! "{case.title if case else "Your case"}" is now {milestone_percent}% complete.',
                priority=NotificationPriority.MEDIUM,
                case_id=case_id,
                action_url=f'/tracking/case/{case_id}'
            ) is not None
        
        return False
    
    def _handle_blocking_issue(self, user_id: int, case_id: int, **kwargs) -> bool:
        """Handle blocking issue notifications"""
        issue_title = kwargs.get('issue_title', 'Issue detected')
        issue_severity = kwargs.get('issue_severity', 'medium')
        
        priority_map = {
            'high': NotificationPriority.HIGH,
            'medium': NotificationPriority.MEDIUM,
            'low': NotificationPriority.LOW
        }
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.REMINDER,
            title="Action Required",
            message=f'{issue_title} needs your attention to keep your case progressing.',
            priority=priority_map.get(issue_severity, NotificationPriority.MEDIUM),
            case_id=case_id,
            action_url=f'/tracking/case/{case_id}'
        ) is not None
    
    def check_and_create_deadline_reminders(self) -> int:
        """Check for upcoming deadlines and create reminder notifications"""
        try:
            created_count = 0
            
            # This would typically check a deadlines table
            # For now, we'll check for cases that might have deadlines based on their progress
            
            # Get cases that might need deadline reminders
            active_cases = Case.query.filter(
                Case.status.in_(['draft', 'in_progress', 'awaiting_hearing'])
            ).all()
            
            for case in active_cases:
                # Check if case has been stagnant
                if case.updated_at:
                    days_since_update = (datetime.utcnow() - case.updated_at).days
                    
                    if days_since_update >= 7:  # Case hasn't been updated in 7 days
                        existing = Notification.query.filter_by(
                            user_id=case.user_id,
                            case_id=case.id,
                            notification_type=NotificationType.REMINDER,
                            title="Case Update Reminder"
                        ).filter(
                            Notification.created_at >= datetime.utcnow() - timedelta(days=7)
                        ).first()
                        
                        if not existing:
                            self.create_notification(
                                user_id=case.user_id,
                                notification_type=NotificationType.REMINDER,
                                title="Case Update Reminder",
                                message=f'Your case "{case.title}" hasn\'t been updated in {days_since_update} days. Consider taking the next recommended action.',
                                priority=NotificationPriority.MEDIUM,
                                case_id=case.id,
                                action_url=f'/tracking/case/{case.id}'
                            )
                            created_count += 1
            
            return created_count
            
        except Exception as e:
            print(f"Error checking deadline reminders: {str(e)}")
            return 0
    
    def create_custom_reminder(self, user_id: int, case_id: int, title: str,
                             message: str, remind_at: datetime, 
                             deadline_type: DeadlineType = DeadlineType.CUSTOM) -> bool:
        """Create a custom reminder/deadline"""
        try:
            return self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.DEADLINE,
                title=title,
                message=message,
                priority=NotificationPriority.HIGH,
                case_id=case_id,
                scheduled_for=remind_at,
                metadata={
                    'deadline_type': deadline_type.value,
                    'is_custom': True
                }
            ) is not None
            
        except Exception as e:
            print(f"Error creating custom reminder: {str(e)}")
            return False
    
    def get_upcoming_deadlines(self, user_id: int, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming deadlines for a user"""
        try:
            cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            deadlines = Notification.query.filter(
                Notification.user_id == user_id,
                Notification.notification_type == NotificationType.DEADLINE,
                Notification.scheduled_for <= cutoff_date,
                Notification.scheduled_for >= datetime.utcnow()
            ).order_by(Notification.scheduled_for).all()
            
            deadline_list = []
            for deadline in deadlines:
                days_until = (deadline.scheduled_for - datetime.utcnow()).days
                
                deadline_list.append({
                    'id': deadline.id,
                    'title': deadline.title,
                    'message': deadline.message,
                    'case_id': deadline.case_id,
                    'case_title': deadline.case.title if deadline.case else None,
                    'deadline_date': deadline.scheduled_for.isoformat(),
                    'days_until': days_until,
                    'priority': deadline.priority.value,
                    'is_overdue': days_until < 0,
                    'action_url': deadline.action_url
                })
            
            return deadline_list
            
        except Exception as e:
            print(f"Error getting upcoming deadlines: {str(e)}")
            return []
    
    def send_daily_digest(self, user_id: int) -> bool:
        """Send daily digest of notifications and upcoming items"""
        try:
            # Get unread notifications
            unread_notifications = self.get_user_notifications(user_id, unread_only=True, limit=10)
            
            # Get upcoming deadlines
            upcoming_deadlines = self.get_upcoming_deadlines(user_id, days_ahead=7)
            
            # Get case progress updates
            tracker = CaseTracker()
            user_cases = Case.query.filter_by(user_id=user_id).limit(5).all()
            
            urgent_actions = []
            for case in user_cases:
                progress_data = tracker.get_case_progress(case.id)
                next_actions = progress_data.get('next_actions', [])
                for action in next_actions:
                    if action.get('priority') in ['urgent', 'high']:
                        urgent_actions.append({
                            'case_title': case.title,
                            'action': action
                        })
            
            # Create digest if there's content
            if unread_notifications or upcoming_deadlines or urgent_actions:
                digest_content = self._format_daily_digest(
                    unread_notifications, upcoming_deadlines, urgent_actions
                )
                
                return self.create_notification(
                    user_id=user_id,
                    notification_type=NotificationType.SYSTEM,
                    title="Daily Legal Case Digest",
                    message=digest_content,
                    priority=NotificationPriority.LOW,
                    metadata={'is_digest': True}
                ) is not None
            
            return True
            
        except Exception as e:
            print(f"Error sending daily digest: {str(e)}")
            return False
    
    def _format_daily_digest(self, notifications: List[Notification], 
                           deadlines: List[Dict], urgent_actions: List[Dict]) -> str:
        """Format daily digest message"""
        digest_parts = []
        
        if notifications:
            digest_parts.append(f"You have {len(notifications)} unread notifications.")
        
        if deadlines:
            overdue = sum(1 for d in deadlines if d['is_overdue'])
            upcoming = len(deadlines) - overdue
            
            if overdue:
                digest_parts.append(f"{overdue} overdue deadline(s).")
            if upcoming:
                digest_parts.append(f"{upcoming} upcoming deadline(s).")
        
        if urgent_actions:
            digest_parts.append(f"{len(urgent_actions)} urgent action(s) need attention.")
        
        return " ".join(digest_parts)
    
    def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Clean up old read notifications"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            old_notifications = Notification.query.filter(
                Notification.is_read == True,
                Notification.read_at <= cutoff_date
            ).all()
            
            count = len(old_notifications)
            
            for notification in old_notifications:
                db.session.delete(notification)
            
            db.session.commit()
            
            return count
            
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up old notifications: {str(e)}")
            return 0


# Global notification manager instance
notification_manager = NotificationManager()


# Convenience functions for common notification scenarios
def notify_case_created(user_id: int, case_id: int):
    """Convenience function to notify about case creation"""
    return notification_manager.trigger_notification(
        NotificationTrigger.CASE_CREATED, user_id, case_id
    )

def notify_evidence_uploaded(user_id: int, case_id: int, evidence_title: str):
    """Convenience function to notify about evidence upload"""
    return notification_manager.trigger_notification(
        NotificationTrigger.EVIDENCE_UPLOADED, user_id, case_id,
        evidence_title=evidence_title
    )

def notify_evidence_analyzed(user_id: int, case_id: int, evidence_title: str, relevance_score: float):
    """Convenience function to notify about evidence analysis"""
    return notification_manager.trigger_notification(
        NotificationTrigger.EVIDENCE_ANALYZED, user_id, case_id,
        evidence_title=evidence_title, relevance_score=relevance_score
    )

def notify_progress_milestone(user_id: int, case_id: int, milestone_percent: int):
    """Convenience function to notify about progress milestones"""
    return notification_manager.trigger_notification(
        NotificationTrigger.PROGRESS_MILESTONE, user_id, case_id,
        milestone_percent=milestone_percent
    )