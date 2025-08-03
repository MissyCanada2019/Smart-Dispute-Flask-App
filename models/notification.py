from sqlalchemy import Table, Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean, MetaData
from datetime import datetime

metadata = MetaData()

notifications = Table('notifications', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('title', String(200), nullable=False),
    Column('message', Text, nullable=False),
    Column('notification_type', String(50), nullable=False),  # Using string instead of Enum
    Column('priority', String(50), default='medium'),  # Using string instead of Enum
    Column('status', String(50), default='unread'),  # Using string instead of Enum
    Column('case_id', Integer, ForeignKey('cases.id')),
    Column('evidence_id', Integer, ForeignKey('evidence.id')),
    Column('form_submission_id', Integer, ForeignKey('form_submissions.id')),
    Column('journey_step_id', Integer, ForeignKey('journey_steps.id')),
    Column('action_required', Boolean, default=False),
    Column('action_url', String(500)),
    Column('action_button_text', String(100)),
    Column('scheduled_for', DateTime),
    Column('expires_at', DateTime),
    Column('delivered_at', DateTime),
    Column('read_at', DateTime),
    Column('dismissed_at', DateTime),
    Column('context_data', JSON),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

# Helper class for notification operations
class Notification:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.title = kwargs.get('title')
        self.message = kwargs.get('message')
        self.notification_type = kwargs.get('notification_type')
        self.priority = kwargs.get('priority', 'medium')
        self.status = kwargs.get('status', 'unread')
        self.case_id = kwargs.get('case_id')
        self.evidence_id = kwargs.get('evidence_id')
        self.form_submission_id = kwargs.get('form_submission_id')
        self.journey_step_id = kwargs.get('journey_step_id')
        self.action_required = kwargs.get('action_required', False)
        self.action_url = kwargs.get('action_url')
        self.action_button_text = kwargs.get('action_button_text')
        self.scheduled_for = kwargs.get('scheduled_for')
        self.expires_at = kwargs.get('expires_at')
        self.delivered_at = kwargs.get('delivered_at')
        self.read_at = kwargs.get('read_at')
        self.dismissed_at = kwargs.get('dismissed_at')
        self.context_data = kwargs.get('context_data')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
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