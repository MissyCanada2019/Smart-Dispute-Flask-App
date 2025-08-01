from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db
from models.case import Case
from models.court_form import FormTemplate, FormField, FormSubmission, SubmissionStatus
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
    # Get user's cases to show relevant forms
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    
    # Get all active form templates
    templates = FormTemplate.query.filter_by(is_active=True).order_by(FormTemplate.province, FormTemplate.name).all()
    
    # Group templates by province
    forms_by_province = {}
    for template in templates:
        if template.province not in forms_by_province:
            forms_by_province[template.province] = []
        forms_by_province[template.province].append(template)
    
    return render_template('forms/list.html', 
                         forms_by_province=forms_by_province, 
                         user_cases=user_cases)

@form_bp.route('/case/<int:case_id>')
@login_required
def forms_for_case(case_id):
    """Show suggested forms for a specific case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    # Get suggested forms for this case
    suggested_forms = get_form_suggestions_for_case(case)
    
    # Get existing form submissions for this case
    existing_submissions = FormSubmission.query.filter_by(case_id=case_id).order_by(FormSubmission.created_at.desc()).all()
    
    return render_template('forms/case_forms.html', 
                         case=case, 
                         suggested_forms=suggested_forms,
                         existing_submissions=existing_submissions)

@form_bp.route('/template/<int:template_id>')
@login_required
def view_template(template_id):
    """View form template details"""
    template = FormTemplate.query.get_or_404(template_id)
    fields = FormField.query.filter_by(template_id=template_id).order_by(FormField.order).all()
    
    return render_template('forms/template_detail.html', template=template, fields=fields)

@form_bp.route('/create/<int:template_id>')
@login_required
def create_form(template_id):
    """Create a new form submission from template"""
    template = FormTemplate.query.get_or_404(template_id)
    fields = FormField.query.filter_by(template_id=template_id).order_by(FormField.order).all()
    
    # Get user's cases that could be associated with this form
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    
    # Filter cases by province if template is province-specific
    if template.province:
        user_cases = [case for case in user_cases if case.province == template.province]
    
    return render_template('forms/create.html', 
                         template=template, 
                         fields=fields, 
                         user_cases=user_cases)

@form_bp.route('/create/<int:template_id>/case/<int:case_id>')
@login_required
def create_form_for_case(template_id, case_id):
    """Create a new form submission for a specific case"""
    template = FormTemplate.query.get_or_404(template_id)
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    fields = FormField.query.filter_by(template_id=template_id).order_by(FormField.order).all()
    
    return render_template('forms/create.html',
                         template=template,
                         fields=fields,
                         selected_case=case)

@form_bp.route('/create-prefilled/<int:template_id>/case/<int:case_id>')
@login_required
def create_prefilled_form(template_id, case_id):
    """Create a new form submission with AI pre-filled values"""
    template = FormTemplate.query.get_or_404(template_id)
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        # Initialize prefill manager
        prefill_manager = FormPrefillManager()
        
        # Create prefilled form submission
        submission = prefill_manager.create_prefilled_form_submission(
            case, template, current_user.id
        )
        
        if submission:
            flash('Form created with AI-powered pre-filled suggestions', 'success')
            return redirect(url_for('forms.edit_submission', submission_id=submission.id))
        else:
            flash('Could not create pre-filled form. Creating blank form instead.', 'warning')
            return redirect(url_for('forms.create_form_for_case',
                                  template_id=template_id, case_id=case_id))
        
    except Exception as e:
        flash(f'Error creating pre-filled form: {str(e)}', 'error')
        return redirect(url_for('forms.create_form_for_case',
                              template_id=template_id, case_id=case_id))

@form_bp.route('/submit/<int:template_id>', methods=['POST'])
@login_required
def submit_form(template_id):
    """Submit a new form"""
    template = FormTemplate.query.get_or_404(template_id)
    
    try:
        # Get form data
        form_data = {}
        for key, value in request.form.items():
            if key not in ['case_id', 'csrf_token']:
                form_data[key] = value
        
        # Validate form data
        validation_result = FormTemplateManager.validate_form_data(template_id, form_data)
        
        if not validation_result['valid']:
            for error in validation_result['errors']:
                flash(error, 'error')
            return redirect(request.url)
        
        # Get associated case
        case_id = request.form.get('case_id')
        case = None
        if case_id:
            case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
            if not case:
                flash('Invalid case selected', 'error')
                return redirect(request.url)
        
        # Create form submission
        submission = FormSubmission(
            template_id=template_id,
            case_id=case.id if case else None,
            user_id=current_user.id,
            form_data=json.dumps(form_data),
            status=SubmissionStatus.DRAFT
        )
        
        db.session.add(submission)
        db.session.commit()
        
        flash(f'Form "{template.name}" submitted successfully', 'success')
        
        # Redirect based on whether case was specified
        if case:
            return redirect(url_for('forms.forms_for_case', case_id=case.id))
        else:
            return redirect(url_for('forms.view_submission', submission_id=submission.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting form: {str(e)}', 'error')
        return redirect(request.url)

@form_bp.route('/submission/<int:submission_id>')
@login_required
def view_submission(submission_id):
    """View form submission details"""
    submission = FormSubmission.query.filter_by(id=submission_id, user_id=current_user.id).first_or_404()
    
    # Get template and fields
    template = FormTemplate.query.get(submission.template_id)
    fields = FormField.query.filter_by(template_id=submission.template_id).order_by(FormField.order).all()
    
    # Parse form data
    try:
        form_data = json.loads(submission.form_data) if submission.form_data else {}
    except json.JSONDecodeError:
        form_data = {}
    
    return render_template('forms/view_submission.html', 
                         submission=submission, 
                         template=template, 
                         fields=fields, 
                         form_data=form_data)

@form_bp.route('/submission/<int:submission_id>/edit')
@login_required
def edit_submission(submission_id):
    """Edit form submission"""
    submission = FormSubmission.query.filter_by(id=submission_id, user_id=current_user.id).first_or_404()
    
    # Only allow editing of draft submissions
    if submission.status != SubmissionStatus.DRAFT:
        flash('Only draft forms can be edited', 'error')
        return redirect(url_for('forms.view_submission', submission_id=submission_id))
    
    # Get template and fields
    template = FormTemplate.query.get(submission.template_id)
    fields = FormField.query.filter_by(template_id=submission.template_id).order_by(FormField.order).all()
    
    # Parse form data
    try:
        form_data = json.loads(submission.form_data) if submission.form_data else {}
    except json.JSONDecodeError:
        form_data = {}
    
    # Get user's cases for case selection
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    
    return render_template('forms/edit.html', 
                         submission=submission, 
                         template=template, 
                         fields=fields, 
                         form_data=form_data,
                         user_cases=user_cases)

@form_bp.route('/submission/<int:submission_id>/update', methods=['POST'])
@login_required
def update_submission(submission_id):
    """Update form submission"""
    submission = FormSubmission.query.filter_by(id=submission_id, user_id=current_user.id).first_or_404()
    
    # Only allow editing of draft submissions
    if submission.status != SubmissionStatus.DRAFT:
        flash('Only draft forms can be edited', 'error')
        return redirect(url_for('forms.view_submission', submission_id=submission_id))
    
    try:
        # Get form data
        form_data = {}
        for key, value in request.form.items():
            if key not in ['case_id', 'csrf_token']:
                form_data[key] = value
        
        # Validate form data
        validation_result = FormTemplateManager.validate_form_data(submission.template_id, form_data)
        
        if not validation_result['valid']:
            for error in validation_result['errors']:
                flash(error, 'error')
            return redirect(url_for('forms.edit_submission', submission_id=submission_id))
        
        # Update case association
        case_id = request.form.get('case_id')
        if case_id and case_id != str(submission.case_id):
            case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
            if case:
                submission.case_id = case.id
        
        # Update form data
        submission.form_data = json.dumps(form_data)
        submission.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Form updated successfully', 'success')
        return redirect(url_for('forms.view_submission', submission_id=submission_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating form: {str(e)}', 'error')
        return redirect(url_for('forms.edit_submission', submission_id=submission_id))

@form_bp.route('/submission/<int:submission_id>/finalize', methods=['POST'])
@login_required
def finalize_submission(submission_id):
    """Finalize form submission (make it read-only)"""
    submission = FormSubmission.query.filter_by(id=submission_id, user_id=current_user.id).first_or_404()
    
    if submission.status != SubmissionStatus.DRAFT:
        flash('Form is already finalized', 'warning')
        return redirect(url_for('forms.view_submission', submission_id=submission_id))
    
    try:
        # Validate form data one more time
        form_data = json.loads(submission.form_data) if submission.form_data else {}
        validation_result = FormTemplateManager.validate_form_data(submission.template_id, form_data)
        
        if not validation_result['valid']:
            flash('Form contains errors and cannot be finalized. Please fix the errors first.', 'error')
            return redirect(url_for('forms.edit_submission', submission_id=submission_id))
        
        # Update status
        submission.status = SubmissionStatus.COMPLETED
        submission.submitted_at = datetime.utcnow()
        
        db.session.commit()
        
        # Create notification for form completion
        try:
            template = FormTemplate.query.get(submission.template_id)
            case = Case.query.get(submission.case_id) if submission.case_id else None
            
            notification_manager.create_notification(
                user_id=current_user.id,
                case_id=submission.case_id,
                notification_type=NotificationType.FORM_UPDATE,
                title=f"Form Completed: {template.name if template else 'Court Form'}",
                message=f"Your {template.name if template else 'court form'} has been finalized and is ready for export or filing." + (f" Case: {case.title}" if case else ""),
                priority=NotificationPriority.MEDIUM,
                action_url=url_for('forms.view_submission', submission_id=submission.id)
            )
        except Exception as e:
            print(f"Error creating form completion notification: {str(e)}")
        
        flash('Form finalized successfully', 'success')
        return redirect(url_for('forms.view_submission', submission_id=submission_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error finalizing form: {str(e)}', 'error')
        return redirect(url_for('forms.view_submission', submission_id=submission_id))

@form_bp.route('/submission/<int:submission_id>/delete', methods=['POST'])
@login_required
def delete_submission(submission_id):
    """Delete form submission"""
    submission = FormSubmission.query.filter_by(id=submission_id, user_id=current_user.id).first_or_404()
    
    try:
        case_id = submission.case_id
        db.session.delete(submission)
        db.session.commit()
        
        flash('Form deleted successfully', 'success')
        
        if case_id:
            return redirect(url_for('forms.forms_for_case', case_id=case_id))
        else:
            return redirect(url_for('forms.list_forms'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting form: {str(e)}', 'error')
        return redirect(url_for('forms.view_submission', submission_id=submission_id))

@form_bp.route('/api/template/<int:template_id>/validate', methods=['POST'])
@login_required
def validate_form_data(template_id):
    """API endpoint to validate form data"""
    template = FormTemplate.query.get_or_404(template_id)
    
    try:
        form_data = request.get_json() or {}
        validation_result = FormTemplateManager.validate_form_data(template_id, form_data)
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [f'Validation error: {str(e)}']
        }), 500

@form_bp.route('/api/provinces')
@login_required
def get_provinces():
    """API endpoint to get list of Canadian provinces"""
    provinces = FormTemplateManager.get_available_provinces()
    return jsonify(provinces)

@form_bp.route('/api/forms/<province_code>')
@login_required
def get_forms_for_province(province_code):
    """API endpoint to get forms for a specific province"""
    forms = FormTemplateManager.get_forms_for_province(province_code)
    return jsonify(forms)

@form_bp.route('/api/template/<int:template_id>/case/<int:case_id>/prefill-suggestions')
@login_required
def get_prefill_suggestions(template_id, case_id):
    """API endpoint to get AI prefill suggestions for a form"""
    template = FormTemplate.query.get_or_404(template_id)
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        prefill_manager = FormPrefillManager()
        suggestions = prefill_manager.analyze_case_for_form_filling(case, template)
        
        return jsonify(suggestions)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@form_bp.route('/api/field-suggestions/<field_name>')
@login_required
def get_field_suggestions(field_name):
    """API endpoint to get smart suggestions for a specific field"""
    case_id = request.args.get('case_id')
    field_type = request.args.get('field_type', 'text')
    
    suggestions = []
    
    if case_id:
        try:
            case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
            if case:
                suggestions = get_smart_suggestions_for_field(field_name, field_type, case)
        except Exception as e:
            print(f"Error getting field suggestions: {str(e)}")
    
    return jsonify({
        'field_name': field_name,
        'suggestions': suggestions
    })

@form_bp.route('/api/submission/<int:submission_id>/refresh-suggestions', methods=['POST'])
@login_required
def refresh_prefill_suggestions(submission_id):
    """API endpoint to refresh AI suggestions for an existing form"""
    submission = FormSubmission.query.filter_by(id=submission_id, user_id=current_user.id).first_or_404()
    
    try:
        prefill_manager = FormPrefillManager()
        suggestions = prefill_manager.get_prefill_suggestions_for_existing_form(submission)
        
        return jsonify(suggestions)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@form_bp.route('/my-submissions')
@login_required
def my_submissions():
    """View all user's form submissions"""
    submissions = FormSubmission.query.filter_by(user_id=current_user.id).order_by(FormSubmission.created_at.desc()).all()
    
    # Group submissions by status
    submissions_by_status = {
        'draft': [],
        'completed': [],
        'submitted': []
    }
    
    for submission in submissions:
        status_key = submission.status.value
        if status_key not in submissions_by_status:
            submissions_by_status[status_key] = []
        submissions_by_status[status_key].append(submission)
    
    return render_template('forms/my_submissions.html', submissions_by_status=submissions_by_status)

# Admin routes for form template management
@form_bp.route('/admin/initialize-templates', methods=['POST'])
@login_required
def initialize_templates():
    """Initialize default form templates (admin function)"""
    # Note: In a real app, you'd want proper admin authentication
    if not current_user.is_authenticated:
        flash('Access denied', 'error')
        return redirect(url_for('forms.list_forms'))
    
    try:
        created_count = FormTemplateManager.initialize_default_templates()
        flash(f'Successfully initialized {created_count} form templates', 'success')
        
    except Exception as e:
        flash(f'Error initializing templates: {str(e)}', 'error')
    
    return redirect(url_for('forms.list_forms'))

@form_bp.route('/submission/<int:submission_id>/export-pdf')
@login_required
def export_submission_pdf(submission_id):
    """Export form submission as PDF"""
    try:
        # Generate PDF
        pdf_buffer = pdf_export_manager.export_form_submission(submission_id, current_user.id)
        
        if not pdf_buffer:
            flash('Form not found or access denied', 'error')
            return redirect(url_for('forms.my_submissions'))
        
        # Get filename
        filename = pdf_export_manager.get_export_filename(submission_id, current_user.id)
        
        # Create download notification
        try:
            submission = FormSubmission.query.filter_by(id=submission_id, user_id=current_user.id).first()
            if submission:
                template = FormTemplate.query.get(submission.template_id)
                notification_manager.create_notification(
                    user_id=current_user.id,
                    case_id=submission.case_id,
                    notification_type=NotificationType.FORM_UPDATE,
                    title="Form PDF Downloaded",
                    message=f"PDF export downloaded for {template.name if template else 'court form'}. Remember to review before filing with the court.",
                    priority=NotificationPriority.LOW,
                    action_url=url_for('forms.view_submission', submission_id=submission.id)
                )
        except Exception as e:
            print(f"Error creating PDF download notification: {str(e)}")
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error exporting PDF: {str(e)}', 'error')
        return redirect(url_for('forms.view_submission', submission_id=submission_id))

@form_bp.route('/case/<int:case_id>/export-forms-pdf')
@login_required
def export_case_forms_pdf(case_id):
    """Export all completed forms for a case as PDF"""
    try:
        # Verify case ownership
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            flash('Case not found or access denied', 'error')
            return redirect(url_for('cases.list_cases'))
        
        # Generate combined PDF
        pdf_buffer = pdf_export_manager.export_case_forms(case_id, current_user.id)
        
        if not pdf_buffer:
            flash('No completed forms found for this case', 'warning')
            return redirect(url_for('forms.forms_for_case', case_id=case_id))
        
        # Create filename
        safe_case_title = ''.join(c for c in case.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_case_title = safe_case_title.replace(' ', '_')
        filename = f"Case_Forms_{safe_case_title}_ID{case_id}.pdf"
        
        # Create notification
        try:
            notification_manager.create_notification(
                user_id=current_user.id,
                case_id=case_id,
                notification_type=NotificationType.CASE_UPDATE,
                title="Case Forms PDF Downloaded",
                message=f"All completed forms for '{case.title}' have been exported to PDF. Review all documents before court filing.",
                priority=NotificationPriority.MEDIUM,
                action_url=url_for('forms.forms_for_case', case_id=case_id)
            )
        except Exception as e:
            print(f"Error creating case forms PDF notification: {str(e)}")
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error exporting case forms PDF: {str(e)}', 'error')
        return redirect(url_for('forms.forms_for_case', case_id=case_id))

@form_bp.route('/export-summary-pdf')
@login_required
def export_user_forms_summary_pdf():
    """Export summary of all user's forms as PDF"""
    try:
        pdf_buffer = pdf_export_manager.export_user_forms_summary(current_user.id)
        
        if not pdf_buffer:
            flash('No forms found to export', 'warning')
            return redirect(url_for('forms.my_submissions'))
        
        filename = f"Forms_Summary_{current_user.email.split('@')[0]}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error exporting forms summary: {str(e)}', 'error')
        return redirect(url_for('forms.my_submissions'))

@form_bp.route('/api/submission/<int:submission_id>/pdf-preview')
@login_required
def api_pdf_preview(submission_id):
    """API endpoint to preview PDF generation (returns PDF info)"""
    try:
        submission = FormSubmission.query.filter_by(
            id=submission_id,
            user_id=current_user.id
        ).first()
        
        if not submission:
            return jsonify({'error': 'Form not found or access denied'}), 404
        
        template = FormTemplate.query.get(submission.template_id)
        case = Case.query.get(submission.case_id) if submission.case_id else None
        
        # Parse form data for preview
        try:
            form_data = json.loads(submission.form_data) if submission.form_data else {}
        except json.JSONDecodeError:
            form_data = {}
        
        preview_info = {
            'form_name': template.name if template else 'Unknown Form',
            'form_description': template.description if template else '',
            'case_title': case.title if case else None,
            'case_number': case.case_number if case else None,
            'status': submission.status.value,
            'created_date': submission.created_at.strftime('%Y-%m-%d'),
            'submitted_date': submission.submitted_at.strftime('%Y-%m-%d') if submission.submitted_at else None,
            'field_count': len(form_data),
            'completed_fields': len([k for k, v in form_data.items() if v and str(v).strip()]),
            'filename': pdf_export_manager.get_export_filename(submission_id, current_user.id)
        }
        
        return jsonify(preview_info)
        
    except Exception as e:
        return jsonify({'error': f'Error generating preview: {str(e)}'}), 500

@form_bp.route('/api/case/<int:case_id>/forms-export-info')
@login_required
def api_case_forms_export_info(case_id):
    """API endpoint to get export information for case forms"""
    try:
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found or access denied'}), 404
        
        # Get completed forms for the case
        submissions = FormSubmission.query.filter_by(
            case_id=case_id,
            user_id=current_user.id
        ).filter(FormSubmission.status.in_(['completed', 'submitted'])).all()
        
        forms_info = []
        for submission in submissions:
            template = FormTemplate.query.get(submission.template_id)
            forms_info.append({
                'id': submission.id,
                'name': template.name if template else 'Unknown Form',
                'status': submission.status.value,
                'created_date': submission.created_at.strftime('%Y-%m-%d'),
                'submitted_date': submission.submitted_at.strftime('%Y-%m-%d') if submission.submitted_at else None
            })
        
        export_info = {
            'case_title': case.title,
            'case_number': case.case_number,
            'total_forms': len(forms_info),
            'forms': forms_info,
            'can_export': len(forms_info) > 0
        }
        
        return jsonify(export_info)
        
    except Exception as e:
        return jsonify({'error': f'Error getting export info: {str(e)}'}), 500