from flask import Blueprint, render_template
from flask_login import login_required, current_user
from utils.db import db  # Corrected import
from models.case import Case
from models.evidence import Evidence
from models.court_form import FormSubmission
from models.notification import Notification
from utils.dashboard import DashboardManager

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def main_dashboard():
    """Main dashboard view"""
    manager = DashboardManager()
    dashboard_data = manager.get_user_dashboard(current_user.id)
    return render_template('dashboard/main.html', **dashboard_data)