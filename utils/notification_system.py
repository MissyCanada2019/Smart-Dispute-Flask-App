"""
Notification System for Smart Dispute Flask App
Manages notifications, reminders, deadlines, and user alerts
"""

from typing import Dict, List, Any, Optional
from flask import current_app
from models.notification import Notification  # Using the helper class
from utils.db import db
from datetime import datetime, timedelta

class NotificationManager:
    """Main notification management system"""
    
    def __init__(self):
        self.session = db.session
        self.reminder_intervals = {
            'urgent': [1, 3, 7],  # Days before deadline
            'high': [3, 7, 14],
            'medium': [7, 14, 30],
            'low': [14, 30]
        }
    
    def create_notification(self, user_id: int, title: str, message: str, 
                           notification_type: str, priority: str = 'medium',
                           case_id: int = None, action_url: str = None, 
                           scheduled_for: datetime = None, metadata: Dict = None) -> Notification:
        """Create a new notification using string-based types"""
        try:
            # Create notification object
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                case_id=case_id,
                action_url=action_url,
                scheduled_for=scheduled_for,
                context_data=metadata or {}
            )
            
            # Save to database
            self.session.add(notification)
            self.session.commit()
            return notification
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {str(e)}")
            self.session.rollback()
            raise
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user"""
        try:
            query = self.session.query(Notification).filter_by(user_id=user_id)
            if unread_only:
                query = query.filter_by(status='unread')
            return query.order_by(Notification.created_at.desc()).all()
        except Exception as e:
            current_app.logger.error(f"Error fetching notifications: {str(e)}")
            return []
    
    def send_deadline_reminder(self, user_id: int, deadline_type: str, deadline_date: datetime, case_id: int):
        """Send a deadline reminder notification"""
        title = f"Deadline Reminder: {deadline_type}"
        message = f"Your deadline for {deadline_type} is approaching on {deadline_date.strftime('%Y-%m-%d')}"
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type='deadline_reminder',
            priority='high',
            case_id=case_id,
            action_url=f"/cases/{case_id}"
        )
    
    # Other notification methods would be implemented similarly
    # using string-based types instead of enums

notification_manager = NotificationManager()