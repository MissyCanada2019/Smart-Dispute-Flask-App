from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.exceptions import RequestEntityTooLarge
from models import db
from models.case import Case, CaseType, CaseStatus, CasePriority
from models.evidence import Evidence, EvidenceType, EvidenceStatus
from models.user import User
from utils.file_upload import save_evidence_file, FileUploadError, file_upload_handler
from utils.evidence_processor import trigger_evidence_processing
from utils.merit_scoring import calculate_case_merit, update_case_merit_score
import os
from datetime import datetime

case_bp = Blueprint('cases', __name__, url_prefix='/cases')

@case_bp.route('/')
@login_required
def list_cases():
    """List all cases for the current user"""
    cases = Case.query.filter_by(user_id=current_user.id).order_by(Case.created_at.desc()).all()
    return render_template('cases/list.html', cases=cases)

@case_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_case():
    """Create a new case"""
    if request.method == 'POST':
        try:
            # Validate required fields
            title = request.form.get('title', '').strip()
            case_type = request.form.get('case_type')
            province = request.form.get('province', '').strip()
            
            if not title:
                flash('Case title is required', 'error')
                return render_template('cases/create.html')
            
            if not case_type or case_type not in [t.value for t in CaseType]:
                flash('Valid case type is required', 'error')
                return render_template('cases/create.html')
            
            if not province:
                flash('Province is required', 'error')
                return render_template('cases/create.html')
            
            # Generate unique case number
            case_number = f"SDC-{datetime.now().strftime('%Y%m%d')}-{current_user.id:04d}-{Case.query.count() + 1:04d}"
            
            # Create new case
            new_case = Case(
                title=title,
                description=request.form.get('description', '').strip(),
                case_number=case_number,
                user_id=current_user.id,
                case_type=CaseType(case_type),
                province=province,
                jurisdiction=request.form.get('jurisdiction', '').strip(),
                court_name=request.form.get('court_name', '').strip(),
                priority=CasePriority(request.form.get('priority', 'medium'))
            )
            
            # Set dates if provided
            incident_date_str = request.form.get('incident_date')
            if incident_date_str:
                new_case.incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d').date()
            
            filing_deadline_str = request.form.get('filing_deadline')
            if filing_deadline_str:
                new_case.filing_deadline = datetime.strptime(filing_deadline_str, '%Y-%m-%d').date()
            
            db.session.add(new_case)
            db.session.commit()
            
            flash(f'Case "{title}" created successfully with case number {case_number}', 'success')
            return redirect(url_for('cases.view_case', case_id=new_case.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating case: {str(e)}', 'error')
            return render_template('cases/create.html')
    
    # GET request - show create form
    return render_template('cases/create.html')

@case_bp.route('/<int:case_id>')
@login_required
def view_case(case_id):
    """View case details"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    # Get recent evidence
    recent_evidence = Evidence.query.filter_by(case_id=case_id).order_by(Evidence.created_at.desc()).limit(5).all()
    
    return render_template('cases/view.html', case=case, recent_evidence=recent_evidence)

@case_bp.route('/<int:case_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_case(case_id):
    """Edit case details"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Update case fields
            case.title = request.form.get('title', '').strip()
            case.description = request.form.get('description', '').strip()
            case.province = request.form.get('province', '').strip()
            case.jurisdiction = request.form.get('jurisdiction', '').strip()
            case.court_name = request.form.get('court_name', '').strip()
            
            # Update case type and priority
            case_type = request.form.get('case_type')
            if case_type and case_type in [t.value for t in CaseType]:
                case.case_type = CaseType(case_type)
            
            priority = request.form.get('priority')
            if priority and priority in [p.value for p in CasePriority]:
                case.priority = CasePriority(priority)
            
            # Update dates
            incident_date_str = request.form.get('incident_date')
            if incident_date_str:
                case.incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d').date()
            
            filing_deadline_str = request.form.get('filing_deadline')
            if filing_deadline_str:
                case.filing_deadline = datetime.strptime(filing_deadline_str, '%Y-%m-%d').date()
            
            hearing_date_str = request.form.get('hearing_date')
            if hearing_date_str:
                case.hearing_date = datetime.strptime(hearing_date_str, '%Y-%m-%dT%H:%M')
            
            db.session.commit()
            flash('Case updated successfully', 'success')
            return redirect(url_for('cases.view_case', case_id=case.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating case: {str(e)}', 'error')
    
    return render_template('cases/edit.html', case=case)

@case_bp.route('/<int:case_id>/evidence')
@login_required
def view_evidence(case_id):
    """View all evidence for a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    evidence_list = Evidence.query.filter_by(case_id=case_id).order_by(Evidence.created_at.desc()).all()
    
    return render_template('cases/evidence.html', case=case, evidence_list=evidence_list)

@case_bp.route('/<int:case_id>/evidence/upload', methods=['GET', 'POST'])
@login_required
def upload_evidence(case_id):
    """Upload evidence for a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'evidence_file' not in request.files:
                flash('No file selected', 'error')
                return render_template('cases/upload_evidence.html', case=case)
            
            file = request.files['evidence_file']
            if file.filename == '':
                flash('No file selected', 'error')
                return render_template('cases/upload_evidence.html', case=case)
            
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            evidence_type = request.form.get('evidence_type', 'document')
            
            # Use filename as title if not provided
            if not title:
                title = file.filename
            
            # Save file securely
            file_path, file_info = save_evidence_file(file)
            
            # Determine evidence type based on file
            if file_info['is_pdf']:
                evidence_type_enum = EvidenceType.DOCUMENT
            elif file_info['is_image']:
                evidence_type_enum = EvidenceType.IMAGE
            else:
                evidence_type_enum = EvidenceType.OTHER
            
            # Create evidence record
            evidence = Evidence(
                filename=file_info['secure_filename'],
                original_filename=file_info['original_filename'],
                file_path=file_path,
                file_size=file_info['file_size'],
                mime_type=file_info['mime_type'],
                title=title,
                description=description,
                evidence_type=evidence_type_enum,
                case_id=case_id,
                user_id=current_user.id
            )
            
            db.session.add(evidence)
            db.session.commit()
            
            # Trigger evidence processing in the background
            try:
                trigger_evidence_processing(evidence.id)
                flash(f'Evidence "{title}" uploaded successfully and is being processed', 'success')
            except Exception as e:
                flash(f'Evidence uploaded but processing failed to start: {str(e)}', 'warning')
            
            return redirect(url_for('cases.view_evidence', case_id=case_id))
            
        except FileUploadError as e:
            flash(str(e), 'error')
        except RequestEntityTooLarge:
            flash('File too large. Please upload a smaller file.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading evidence: {str(e)}', 'error')
    
    return render_template('cases/upload_evidence.html', case=case)

@case_bp.route('/<int:case_id>/evidence/<int:evidence_id>')
@login_required
def view_evidence_detail(case_id, evidence_id):
    """View detailed evidence information"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    evidence = Evidence.query.filter_by(id=evidence_id, case_id=case_id).first_or_404()
    
    return render_template('cases/evidence_detail.html', case=case, evidence=evidence)

@case_bp.route('/<int:case_id>/evidence/<int:evidence_id>/delete', methods=['POST'])
@login_required
def delete_evidence(case_id, evidence_id):
    """Delete evidence"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    evidence = Evidence.query.filter_by(id=evidence_id, case_id=case_id).first_or_404()
    
    try:
        # Delete physical file
        if os.path.exists(evidence.file_path):
            os.remove(evidence.file_path)
        
        # Delete database record
        db.session.delete(evidence)
        db.session.commit()
        
        flash('Evidence deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting evidence: {str(e)}', 'error')
    
    return redirect(url_for('cases.view_evidence', case_id=case_id))

@case_bp.route('/api/<int:case_id>/evidence/<int:evidence_id>/process', methods=['POST'])
@login_required
def process_evidence_api(case_id, evidence_id):
    """API endpoint to trigger evidence processing"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    evidence = Evidence.query.filter_by(id=evidence_id, case_id=case_id).first_or_404()
    
    try:
        # Update status to processing
        evidence.status = EvidenceStatus.PROCESSING
        db.session.commit()
        
        # Trigger evidence processing
        processing_started = trigger_evidence_processing(evidence_id)
        if not processing_started:
            return jsonify({
                'success': False,
                'error': 'Failed to start evidence processing'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Evidence processing started',
            'evidence_id': evidence_id,
            'status': evidence.status.value
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@case_bp.route('/api/<int:case_id>/stats')
@login_required
def get_case_stats(case_id):
    """Get case statistics"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    evidence_count = Evidence.query.filter_by(case_id=case_id).count()
    processed_evidence = Evidence.query.filter_by(case_id=case_id, status=EvidenceStatus.ANALYZED).count()
    
    stats = {
        'case_id': case_id,
        'evidence_count': evidence_count,
        'processed_evidence': processed_evidence,
        'processing_progress': int((processed_evidence / evidence_count * 100)) if evidence_count > 0 else 0,
        'merit_score': case.merit_score or 0,
        'completion_percentage': case.completion_percentage or 0,
        'current_stage': case.current_stage or 'Getting Started'
    }
    
    return jsonify(stats)

@case_bp.route('/api/<int:case_id>/merit-analysis', methods=['POST'])
@login_required
def calculate_merit_analysis(case_id):
    """Calculate comprehensive merit analysis for a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        # Calculate merit score
        merit_result = calculate_case_merit(case)
        
        if 'error' not in merit_result:
            # Update case with new merit data
            success = update_case_merit_score(case)
            
            return jsonify({
                'success': True,
                'merit_analysis': merit_result,
                'case_updated': success
            })
        else:
            return jsonify({
                'success': False,
                'error': merit_result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@case_bp.route('/api/<int:case_id>/merit-score')
@login_required
def get_merit_score(case_id):
    """Get current merit score and analysis for a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    # Get evidence count and processing status
    evidence_list = Evidence.query.filter_by(case_id=case_id).all()
    processed_evidence_count = len([e for e in evidence_list if e.status in [EvidenceStatus.PROCESSED, EvidenceStatus.ANALYZED]])
    
    return jsonify({
        'case_id': case_id,
        'merit_score': case.merit_score or 0,
        'merit_analysis': case.merit_analysis or {},
        'strength_indicators': case.strength_indicators or [],
        'weakness_indicators': case.weakness_indicators or [],
        'evidence_count': len(evidence_list),
        'processed_evidence_count': processed_evidence_count,
        'analysis_available': case.merit_score is not None,
        'last_updated': case.updated_at.isoformat() if case.updated_at else None
    })

@case_bp.route('/<int:case_id>/analysis')
@login_required
def view_case_analysis(case_id):
    """View detailed case analysis page"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    evidence_list = Evidence.query.filter_by(case_id=case_id).order_by(Evidence.created_at.desc()).all()
    
    # Calculate fresh merit analysis if needed
    if not case.merit_score:
        try:
            update_case_merit_score(case)
        except Exception as e:
            flash(f'Error calculating merit score: {str(e)}', 'warning')
    
    return render_template('cases/analysis.html', case=case, evidence_list=evidence_list)

# Error handlers for file upload
@case_bp.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash('File too large. Please upload a smaller file.', 'error')
    return redirect(request.url)

@case_bp.errorhandler(413)
def handle_payload_too_large(e):
    flash('File too large. Please upload a smaller file.', 'error')
    return redirect(request.url)