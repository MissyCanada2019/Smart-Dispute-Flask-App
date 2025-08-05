from flask import current_app
from models.case import Case
from models.evidence import Evidence
from models.court_form import FormSubmission
from models.notification import Notification
from utils.db import db
from datetime import datetime, timedelta

def format_time_ago(dt):
    """Format datetime as time ago string"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        mins = diff.seconds // 60
        return f"{mins} minute{'s' if mins > 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days > 1 else ''} ago"

def get_urgency_class(dt):
    """Get urgency class based on datetime"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff < timedelta(hours=24):
        return "urgent"
    elif diff < timedelta(days=3):
        return "warning"
    else:
        return "normal"

class DashboardManager:
    """Manages dashboard data - simplified without journey management"""
    
    def get_user_dashboard(self, user_id):
        """Get dashboard data for user"""
        cases = Case.query.filter_by(user_id=user_id).order_by(Case.created_at.desc()).limit(5).all()
        recent_evidence = Evidence.query.filter_by(uploaded_by=user_id).order_by(Evidence.uploaded_at.desc()).limit(5).all()
        recent_forms = FormSubmission.query.filter_by(submitted_by=user_id).order_by(FormSubmission.created_at.desc()).limit(5).all()
        notifications = Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc()).limit(10).all()
        
        return {
            "cases": cases,
            "recent_evidence": recent_evidence,
            "recent_forms": recent_forms,
            "notifications": notifications
        }