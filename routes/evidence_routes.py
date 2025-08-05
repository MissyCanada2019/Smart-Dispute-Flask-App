from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.evidence import Evidence
from models.case import Case
from utils.db import db
from utils.file_upload import get_file_upload_handler

evidence_bp = Blueprint('evidence', __name__, url_prefix='/evidence')

@evidence_bp.route('/upload/<int:case_id>', methods=['GET', 'POST'])
@login_required
def upload_evidence(case_id):
    """Upload evidence for a case"""
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash('You do not have permission to upload evidence for this case', 'danger')
        return redirect(url_for('case.list_cases'))
    
    if request.method == 'POST':
        file = request.files.get('evidence_file')
        if not file or file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        try:
            handler = get_file_upload_handler()
            file_path = handler.upload_file(file, case_id, current_user.id)
            
            evidence = Evidence(
                case_id=case_id,
                file_path=file_path,
                description=request.form.get('description', ''),
                uploaded_by=current_user.id
            )
            db.session.add(evidence)
            db.session.commit()
            
            flash('Evidence uploaded successfully', 'success')
            return redirect(url_for('case.view_case', case_id=case_id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading evidence: {str(e)}', 'danger')
    
    return render_template('evidence/upload.html', case=case)

@evidence_bp.route('/review/<int:evidence_id>')
@login_required
def review_evidence(evidence_id):
    """Review evidence details"""
    evidence = Evidence.query.get_or_404(evidence_id)
    if evidence.case.user_id != current_user.id:
        flash('You do not have permission to view this evidence', 'danger')
        return redirect(url_for('case.list_cases'))
    
    return render_template('evidence/review.html', evidence=evidence)

@evidence_bp.route('/delete/<int:evidence_id>', methods=['POST'])
@login_required
def delete_evidence(evidence_id):
    """Delete evidence"""
    evidence = Evidence.query.get_or_404(evidence_id)
    if evidence.case.user_id != current_user.id:
        flash('You do not have permission to delete this evidence', 'danger')
        return redirect(url_for('case.list_cases'))
    
    try:
        handler = get_file_upload_handler()
        handler.delete_file(evidence.file_path)
        db.session.delete(evidence)
        db.session.commit()
        flash('Evidence deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting evidence: {str(e)}', 'danger')
    
    return redirect(url_for('case.view_case', case_id=evidence.case_id))