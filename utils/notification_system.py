from utils.db import db
from models.notification import Notification, NotificationType, NotificationPriority
from datetime import datetime, timedelta
from enum import Enum as PyEnum

class DeadlineType(PyEnum):  # Added enum
    """Types of deadlines for notifications"""
    FORM_SUBMISSION = "form_submission"
    HEARING = "hearing"
    PAYMENT = "payment"
    EVIDENCE_SUBMISSION = "evidence_submission"
    CASE_MILESTONE = "case_milestone"

class NotificationManager:
    """Manages notification creation and delivery"""
    
    def create_notification(self, user_id, title, message, notif_type, priority=NotificationPriority.MEDIUM, case_id=None):
        """Create and save a notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notif_type,
            priority=priority,
            related_case_id=case_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    def send_reminder(self, user_id, deadline_type, deadline_date, case_id=None):
        """Send deadline reminder notification"""
        title = f"Reminder: {deadline_type.value.replace('_', ' ').title()}"
        message = f"Upcoming deadline on {deadline_date.strftime('%Y-%m-%d')}"
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notif_type=NotificationType.HEARING_REMINDER,
            priority=NotificationPriority.HIGH,
            case_id=case_id
        )
    
    def mark_as_read(self, notification_id):
        """Mark notification as read"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False

# Global notification manager instance
notification_manager = NotificationManager()