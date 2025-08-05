from utils.db import db
from datetime import datetime
from enum import Enum as PyEnum

class NotificationType(PyEnum):
    """Types of notifications"""
    CASE_UPDATE = "case_update"
    FORM_SUBMISSION = "form_submission"
    PAYMENT_RECEIVED = "payment_received"
    HEARING_REMINDER = "hearing_reminder"
    DOCUMENT_UPLOAD = "document_upload"
    SYSTEM_ALERT = "system_alert"

class NotificationPriority(PyEnum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.Enum(NotificationType), nullable=False)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    action_url = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'