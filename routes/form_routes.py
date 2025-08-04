from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from utils.db import db
from models.case import Case
from models.court_form import FormTemplate, FormField, FormSubmission
from utils.form_templates import FormTemplateManager, get_form_suggestions_for_case
from utils.form_prefill import FormPrefillManager, get_smart_suggestions_for_field
import json
from datetime import datetime
from flask import send_file
from utils.pdf_export import pdf_export_manager
from utils.notification_system import notification_manager
from models.notification import Notification

form_bp = Blueprint('forms', __name__, url_prefix='/forms')

@form_bp.route('/')
@login_required
def list_forms():
    """List all available form templates"""
    try:
        user_cases = db.session.query(Case).filter_by(user_id=current_user.id).all()
        templates = db.session.query(FormTemplate).filter_by(is_active=True).order_by(FormTemplate.province, FormTemplate.name).all()
        
        forms_by_province = {}
        for template in templates:
            if template.province not in forms_by_province:
                forms_by_province[template.province] = []
            forms_by_province[template.province].append(template)
        
        return render_template('forms/list.html', 
                             forms_by_province=forms_by_province, 
                             user_cases=user_cases)
    except Exception as e:
        current_app.logger.error(f"Error listing forms: {str(e)}")
        flash('Error loading forms. Please try again later.', 'danger')
        return redirect(url_for('dashboard.main'))

@form_bp.route('/case/<int:case_id>')
@login_required
def forms_for_case(case_id):
    """Show suggested forms for a specific case"""
    try:
        case = db.session.query(Case).filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            flash('Case not found', 'danger')
            return redirect(url_for('forms.list_forms'))
        
        suggested_forms = get_form_suggestions_for_case(case)
        existing_submissions = db.session.query(FormSubmission).filter_by(case_id=case_id).order_by(FormSubmission.created_at.desc()).all()
        
        return render_template('forms/case_forms.html', 
                             case=case, 
                             suggested_forms=suggested_forms,
                             existing_submissions=existing_submissions)
    except Exception as e:
        current_app.logger.error(f"Error loading forms for case: {str(e)}")
        flash('Error loading forms. Please try again later.', 'danger')
        return redirect(url_for('case.list_cases'))

@form_bp.route('/template/<int:template_id>')
@login_required
def view_template(template_id):
    """View form template details"""
    try:
        template = db.session.query(FormTemplate).get(template_id)
        if not template:
            flash('Form template not found', 'danger')
            return redirect(url_for('forms.list_forms'))
        
        fields = db.session.query(FormField).filter_by(template_id=template_id).order_by(FormField.order_index).all()
        return render_template('forms/view.html', template=template, fields=fields)
    except Exception as e:
        current_app.logger.error(f"Error viewing form template: {str(e)}")
        flash('Error loading form template. Please try again later.', 'danger')
        return redirect(url_for('forms.list_forms'))

@form_bp.route('/submit/<int:template_id>', methods=['GET', 'POST'])
@login_required
def submit_form(template_id):
    try:
        template = db.session.query(FormTemplate).get(template_id)
        if not template:
            flash('Form template not found', 'danger')
            return redirect(url_for('forms.list_forms'))
        
        if request.method == 'POST':
            # Form submission logic
            pass
        
        return render_template('forms/submit.html', template=template)
    except Exception as e:
        current_app.logger.error(f"Error submitting form: {str(e)}")
        flash('Error submitting form. Please try again later.', 'danger')
        return redirect(url_for('forms.list_forms'))
