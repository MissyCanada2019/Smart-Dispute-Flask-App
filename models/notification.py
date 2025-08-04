from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base
from utils.db import db

Base = declarative_base()

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    priority = Column(String(50), default='medium')
    status = Column(String(50), default='unread')
    case_id = Column(Integer, ForeignKey('cases.id'))
    evidence_id = Column(Integer, ForeignKey('evidence.id'))
    form_submission_id = Column(Integer, ForeignKey('form_submissions.id'))
    journey_step_id = Column(Integer, ForeignKey('journey_steps.id'))
    action_required = Column(Boolean, default=False)
    action_url = Column(String(500))
    action_button_text = Column(String(100))
    scheduled_for = Column(DateTime)
    expires_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    dismissed_at = Column(DateTime)
    context_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = datetime.utcnow()

    def dismiss(self):
        """Dismiss notification"""
        self.status = 'dismissed'
        self.dismissed_at = datetime.utcnow()
    
    def is_expired(self):
        """Check if notification has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def should_be_shown(self):
        """Check if notification should be shown now"""
        now = datetime.utcnow()
        
        # Don't show if expired
        if self.is_expired():
            return False
        
        # Don't show if scheduled for future
        if self.scheduled_for and now < self.scheduled_for:
            return False
            
        # Don't show if already read or dismissed
        if self.status in ['read', 'dismissed']:
            return False
            
        return True