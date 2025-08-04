from datetime import datetime
from utils.db import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50), default='medium')
    status = db.Column(db.String(50), default='unread')
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence.id'))
    form_submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id'))
    journey_step_id = db.Column(db.Integer, db.ForeignKey('journey_steps.id'))
    action_required = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(500))
    action_button_text = db.Column(db.String(100))
    scheduled_for = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    context_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def dismiss(self):
        """Dismiss notification"""
        self.status = 'dismissed'
        self.dismissed_at = datetime.utcnow()
        db.session.commit()
    
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