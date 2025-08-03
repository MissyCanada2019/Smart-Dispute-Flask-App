from models import db
from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    DEADLINE_REMINDER = "deadline_reminder"
    FORM_COMPLETION = "form_completion"
    EVIDENCE_ANALYSIS = "evidence_analysis"
    CASE_UPDATE = "case_update"
    SYSTEM_ALERT = "system_alert"
    AI_RECOMMENDATION = "ai_recommendation"
    COURT_DATE = "court_date"
    FILING_CONFIRMATION = "filing_confirmation"

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(Enum):
    UNREAD = "unread"
    READ = "read"
    DISMISSED = "dismissed"
    ARCHIVED = "archived"

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Recipient
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.Enum(NotificationType), nullable=False)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    status = db.Column(db.Enum(NotificationStatus), default=NotificationStatus.UNREAD)
    
    # Context and links
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence.id'))
    form_submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id'))
    journey_step_id = db.Column(db.Integer, db.ForeignKey('journey_steps.id'))
    
    # Action required
    action_required = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(500))  # URL to take action
    action_button_text = db.Column(db.String(100))  # Text for action button
    
    # Scheduling
    scheduled_for = db.Column(db.DateTime)  # When to show notification
    expires_at = db.Column(db.DateTime)  # When notification becomes irrelevant
    
    # Delivery tracking
    delivered_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    
    # Additional context data
    context_data = db.Column(db.JSON)  # Additional context data (renamed from metadata to avoid SQLAlchemy conflict)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == NotificationStatus.UNREAD:
            self.status = NotificationStatus.READ
            self.read_at = datetime.utcnow()
    
    def dismiss(self):
        """Dismiss notification"""
        self.status = NotificationStatus.DISMISSED
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
        
        # Don't show if dismissed or archived
        if self.status in [NotificationStatus.DISMISSED, NotificationStatus.ARCHIVED]:
            return False
        
        # Don't show if scheduled for future
        if self.scheduled_for and now < self.scheduled_for:
            return False
        
        return True
    
    @staticmethod
    def create_deadline_reminder(user_id, case_id, deadline_date, title, message, journey_step_id=None):
        """Create a deadline reminder notification"""
        # Schedule notification 3 days before deadline
        scheduled_time = deadline_date - datetime.timedelta(days=3)
        
        notification = Notification(
            user_id=user_id,
            case_id=case_id,
            journey_step_id=journey_step_id,
            title=title,
            message=message,
            notification_type=NotificationType.DEADLINE_REMINDER,
            priority=NotificationPriority.HIGH,
            scheduled_for=scheduled_time,
            expires_at=deadline_date,
            action_required=True,
            action_url=f"/cases/{case_id}/journey",
            action_button_text="View Case"
        )
        
        db.session.add(notification)
        return notification
    
    @staticmethod
    def create_evidence_analysis_complete(user_id, case_id, evidence_id, ai_summary):
        """Create notification when evidence analysis is complete"""
        notification = Notification(
            user_id=user_id,
            case_id=case_id,
            evidence_id=evidence_id,
            title="Evidence Analysis Complete",
            message=f"AI analysis of your evidence is ready. {ai_summary[:100]}...",
            notification_type=NotificationType.EVIDENCE_ANALYSIS,
            priority=NotificationPriority.MEDIUM,
            action_required=True,
            action_url=f"/cases/{case_id}/evidence/{evidence_id}",
            action_button_text="Review Analysis"
        )
        
        db.session.add(notification)
        return notification
    
    @staticmethod
    def create_form_ready_notification(user_id, case_id, form_name):
        """Create notification when a form is ready to be filled"""
        notification = Notification(
            user_id=user_id,
            case_id=case_id,
            title="Court Form Ready",
            message=f"Based on your case analysis, we've prepared the {form_name} form for you to review and complete.",
            notification_type=NotificationType.FORM_COMPLETION,
            priority=NotificationPriority.HIGH,
            action_required=True,
            action_url=f"/cases/{case_id}/forms",
            action_button_text="Complete Form"
        )
        
        db.session.add(notification)
        return notification
    
    @staticmethod
    def create_ai_recommendation(user_id, case_id, recommendation_title, recommendation_text):
        """Create AI recommendation notification"""
        notification = Notification(
            user_id=user_id,
            case_id=case_id,
            title=f"AI Recommendation: {recommendation_title}",
            message=recommendation_text,
            notification_type=NotificationType.AI_RECOMMENDATION,
            priority=NotificationPriority.MEDIUM,
            action_required=False,
            action_url=f"/cases/{case_id}",
            action_button_text="View Case"
        )
        
        db.session.add(notification)
        return notification
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'case_id': self.case_id,
            'evidence_id': self.evidence_id,
            'form_submission_id': self.form_submission_id,
            'action_required': self.action_required,
            'action_url': self.action_url,
            'action_button_text': self.action_button_text,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired(),
            'should_be_shown': self.should_be_shown(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification type preferences
    deadline_reminders = db.Column(db.Boolean, default=True)
    evidence_analysis_updates = db.Column(db.Boolean, default=True)
    form_completion_reminders = db.Column(db.Boolean, default=True)
    ai_recommendations = db.Column(db.Boolean, default=True)
    case_updates = db.Column(db.Boolean, default=True)
    system_alerts = db.Column(db.Boolean, default=True)
    
    # Timing preferences
    reminder_days_before_deadline = db.Column(db.Integer, default=3)
    daily_digest_enabled = db.Column(db.Boolean, default=False)
    daily_digest_time = db.Column(db.Time)  # What time to send daily digest
    
    # Delivery preferences
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    push_notifications = db.Column(db.Boolean, default=True)
    
    # Contact information
    email_address = db.Column(db.String(255))
    phone_number = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<NotificationPreference for User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'deadline_reminders': self.deadline_reminders,
            'evidence_analysis_updates': self.evidence_analysis_updates,
            'form_completion_reminders': self.form_completion_reminders,
            'ai_recommendations': self.ai_recommendations,
            'case_updates': self.case_updates,
            'reminder_days_before_deadline': self.reminder_days_before_deadline,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'push_notifications': self.push_notifications
        }