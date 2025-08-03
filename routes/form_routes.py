from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from utils.db import Session  # Import Session object
from models.case import Case
from models.court_form import FormTemplate, FormField, FormSubmission  # Removed SubmissionStatus
from utils.form_templates import FormTemplateManager, get_form_suggestions_for_case
from utils.form_prefill import FormPrefillManager, get_smart_suggestions_for_field
import json
from datetime import datetime
from flask import send_file
from utils.pdf_export import pdf_export_manager
from utils.notification_system import notification_manager
from models.notification import NotificationType, NotificationPriority

form_bp = Blueprint('forms', __name__, url_prefix='/forms')

@form_bp.route('/')
@login_required
def list_forms():
    """List all available form templates"""
    session = Session()
    try:
        # Get user's cases to show relevant forms
        user_cases = session.query(Case).filter_by(user_id=current_user.id).all()
        
        # Get all active form templates
        templates = session.query(FormTemplate).filter_by(is_active=True).order_by(FormTemplate.province, FormTemplate.name).all()
        
        # Group templates by province
        forms_by_province = {}
        for template in templates:
            if template.province not in forms_by_province:
                forms_by_province[template.province] = []
            forms_by_province[template.province].append(template)
        
        return render_template('forms/list.html', 
                             forms_by_province=forms_by_province, 
                             user_cases=user_cases)
    finally:
        session.close()

@form_bp.route('/case/<int:case_id>')
@login_required
def forms_for_case(case_id):
    """Show suggested forms for a specific case"""
    session = Session()
    try:
        case = session.query(Case).filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            flash('Case not found', 'danger')
            return redirect(url_for('forms.list_forms'))
        
        # Get suggested forms for this case
        suggested_forms = get_form_suggestions_for_case(case)
        
        # Get existing form submissions for this case
        existing_submissions = session.query(FormSubmission).filter_by(case_id=case_id).order_by(FormSubmission.created_at.desc()).all()
        
        return render_template('forms/case_forms.html', 
                             case=case, 
                             suggested_forms=suggested_forms,
                             existing_submissions=existing_submissions)
    finally:
        session.close()

@form_bp.route('/template/<int:template_id>')
@login_required
def view_template(template_id):
    """View form template details"""
    session = Session()
    try:
        template = session.query(FormTemplate).get(template_id)
        if not template:
            flash('Form template not found', 'danger')
            return redirect(url_for('forms.list_forms'))
        
        fields = session.query(FormField).filter_by(template_id=template_id).order_by(FormField.order).all()
        return render_template('forms/view.html', template=template, fields=fields)
    finally:
        session.close()

# Other form routes would be implemented similarly
# For example:
@form_bp.route('/submit/<int:template_id>', methods=['GET', 'POST'])
@login_required
def submit_form(template_id):
    session = Session()
    try:
        template = session.query(FormTemplate).get(template_id)
        if not template:
            flash('Form template not found', 'danger')
            return redirect(url_for('forms.list_forms'))
        
        if request.method == 'POST':
            # Form submission logic
            pass
        
        return render_template('forms/submit.html', template=template)
    finally:
        session.close()