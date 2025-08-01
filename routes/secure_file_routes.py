"""
Secure File Routes
Handles secure file upload, download, and management with access controls
"""

from flask import Blueprint, request, jsonify, send_file, abort, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.case import Case
from models.evidence import Evidence
from models import db
from utils.secure_storage import SecureFileManager, require_file_access, get_client_ip
import os
import tempfile
from datetime import datetime

secure_file_bp = Blueprint('secure_files', __name__, url_prefix='/secure-files')

@secure_file_bp.route('/manage')
@login_required
def manage_files():
    """Render secure file management page"""
    return render_template('files/manage.html')

@secure_file_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle secure file upload"""
    try:
        # Get form data
        case_id = request.form.get('case_id', type=int)
        evidence_title = request.form.get('title', '').strip()
        evidence_description = request.form.get('description', '').strip()
        
        if not case_id:
            return jsonify({'success': False, 'error': 'Case ID is required'}), 400
        
        # Verify user owns the case
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            return jsonify({'success': False, 'error': 'Case not found or access denied'}), 404
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Use secure storage manager
        secure_manager = SecureFileManager()
        result = secure_manager.store_file_securely(
            file=file,
            case_id=case_id,
            user_id=current_user.id,
            evidence_title=evidence_title,
            evidence_description=evidence_description
        )
        
        if result.get('success'):
            # Log successful upload
            secure_manager.audit_file_access(
                evidence_id=result['evidence_id'],
                user_id=current_user.id,
                action='upload',
                ip_address=get_client_ip()
            )
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'evidence_id': result['evidence_id']
            })
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@secure_file_bp.route('/download/<int:evidence_id>')
@login_required
@require_file_access('evidence_id')
def download_file(evidence_id):
    """Handle secure file download"""
    try:
        secure_manager = SecureFileManager()
        
        # Retrieve file securely
        temp_file, file_info = secure_manager.retrieve_file_securely(evidence_id, current_user.id)
        
        if not temp_file:
            flash(file_info.get('error', 'File not found'), 'error')
            return redirect(url_for('cases.list_cases'))
        
        # Log download
        secure_manager.audit_file_access(
            evidence_id=evidence_id,
            user_id=current_user.id,
            action='download',
            ip_address=get_client_ip()
        )
        
        # Serve file
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=file_info['filename'],
            mimetype=file_info['mime_type']
        )
        
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('cases.list_cases'))

@secure_file_bp.route('/download-token/<int:evidence_id>')
@login_required
@require_file_access('evidence_id')
def generate_download_token(evidence_id):
    """Generate secure download token"""
    try:
        secure_manager = SecureFileManager()
        token = secure_manager.generate_secure_download_token(evidence_id, current_user.id)
        
        if token:
            return jsonify({
                'success': True,
                'token': token,
                'download_url': url_for('secure_files.download_with_token', token=token, _external=True)
            })
        else:
            return jsonify({'success': False, 'error': 'Could not generate download token'}), 403
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@secure_file_bp.route('/download-token/<token>')
def download_with_token(token):
    """Download file using secure token"""
    try:
        secure_manager = SecureFileManager()
        token_data = secure_manager.verify_download_token(token)
        
        if not token_data:
            abort(403)
        
        evidence_id = token_data['evidence_id']
        user_id = token_data['user_id']
        
        # Retrieve file securely
        temp_file, file_info = secure_manager.retrieve_file_securely(evidence_id, user_id)
        
        if not temp_file:
            abort(404)
        
        # Log download
        secure_manager.audit_file_access(
            evidence_id=evidence_id,
            user_id=user_id,
            action='token_download',
            ip_address=get_client_ip()
        )
        
        # Serve file
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=file_info['filename'],
            mimetype=file_info['mime_type']
        )
        
    except Exception as e:
        abort(500)

@secure_file_bp.route('/view/<int:evidence_id>')
@login_required
@require_file_access('evidence_id')
def view_file(evidence_id):
    """View file in browser (for supported formats)"""
    try:
        evidence = Evidence.query.get_or_404(evidence_id)
        secure_manager = SecureFileManager()
        
        # Check if file type is viewable in browser
        viewable_types = {
            'application/pdf',
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'text/plain', 'text/html'
        }
        
        if evidence.mime_type not in viewable_types:
            flash('This file type cannot be viewed in browser. Please download instead.', 'info')
            return redirect(url_for('secure_files.download_file', evidence_id=evidence_id))
        
        # Retrieve file securely
        temp_file, file_info = secure_manager.retrieve_file_securely(evidence_id, current_user.id)
        
        if not temp_file:
            flash(file_info.get('error', 'File not found'), 'error')
            return redirect(url_for('cases.list_cases'))
        
        # Log view
        secure_manager.audit_file_access(
            evidence_id=evidence_id,
            user_id=current_user.id,
            action='view',
            ip_address=get_client_ip()
        )
        
        # Serve file for viewing
        return send_file(
            temp_file.name,
            mimetype=file_info['mime_type'],
            as_attachment=False
        )
        
    except Exception as e:
        flash(f'Error viewing file: {str(e)}', 'error')
        return redirect(url_for('cases.list_cases'))

@secure_file_bp.route('/delete/<int:evidence_id>', methods=['POST'])
@login_required
@require_file_access('evidence_id')
def delete_file(evidence_id):
    """Securely delete file"""
    try:
        secure_manager = SecureFileManager()
        result = secure_manager.delete_file_securely(evidence_id, current_user.id)
        
        if result['success']:
            # Log deletion
            secure_manager.audit_file_access(
                evidence_id=evidence_id,
                user_id=current_user.id,
                action='delete',
                ip_address=get_client_ip()
            )
            
            flash('File deleted successfully', 'success')
        else:
            flash(result['error'], 'error')
            
        return redirect(request.referrer or url_for('cases.list_cases'))
        
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'error')
        return redirect(url_for('cases.list_cases'))

@secure_file_bp.route('/info/<int:evidence_id>')
@login_required
@require_file_access('evidence_id')
def file_info(evidence_id):
    """Get file information"""
    try:
        evidence = Evidence.query.get_or_404(evidence_id)
        secure_manager = SecureFileManager()
        
        # Check access
        access_check = secure_manager.check_file_access(evidence_id, current_user.id)
        if not access_check['allowed']:
            return jsonify({'error': 'Access denied'}), 403
        
        file_info = {
            'id': evidence.id,
            'title': evidence.title,
            'description': evidence.description,
            'original_filename': evidence.original_filename,
            'file_size': evidence.file_size,
            'file_size_mb': round(evidence.file_size / (1024 * 1024), 2) if evidence.file_size else 0,
            'mime_type': evidence.mime_type,
            'uploaded_at': evidence.uploaded_at.isoformat() if evidence.uploaded_at else None,
            'is_encrypted': evidence.storage_encrypted,
            'access_level': access_check['access_level']
        }
        
        return jsonify(file_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@secure_file_bp.route('/list/<int:case_id>')
@login_required
def list_case_files(case_id):
    """List all files for a case"""
    try:
        # Verify user owns the case
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found or access denied'}), 404
        
        # Get all evidence for the case
        evidence_list = Evidence.query.filter_by(case_id=case_id).order_by(Evidence.uploaded_at.desc()).all()
        
        files = []
        for evidence in evidence_list:
            files.append({
                'id': evidence.id,
                'title': evidence.title,
                'description': evidence.description,
                'original_filename': evidence.original_filename,
                'file_size': evidence.file_size,
                'file_size_mb': round(evidence.file_size / (1024 * 1024), 2) if evidence.file_size else 0,
                'mime_type': evidence.mime_type,
                'uploaded_at': evidence.uploaded_at.isoformat() if evidence.uploaded_at else None,
                'is_encrypted': evidence.storage_encrypted,
                'download_url': url_for('secure_files.download_file', evidence_id=evidence.id),
                'view_url': url_for('secure_files.view_file', evidence_id=evidence.id),
                'delete_url': url_for('secure_files.delete_file', evidence_id=evidence.id)
            })
        
        return jsonify({
            'case_id': case_id,
            'case_title': case.title,
            'files': files,
            'total_files': len(files)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@secure_file_bp.route('/storage-stats')
@login_required
def storage_stats():
    """Get user's file storage statistics"""
    try:
        secure_manager = SecureFileManager()
        stats = secure_manager.get_file_access_stats(current_user.id)
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@secure_file_bp.route('/validate-upload', methods=['POST'])
@login_required
def validate_upload():
    """Validate file before upload (for AJAX validation)"""
    try:
        if 'file' not in request.files:
            return jsonify({'valid': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'valid': False, 'error': 'No file selected'})
        
        secure_manager = SecureFileManager()
        validation = secure_manager.validate_file_upload(file, current_user.id)
        
        return jsonify(validation)
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@secure_file_bp.route('/batch-delete', methods=['POST'])
@login_required
def batch_delete_files():
    """Delete multiple files at once"""
    try:
        evidence_ids = request.json.get('evidence_ids', [])
        if not evidence_ids:
            return jsonify({'success': False, 'error': 'No files selected'}), 400
        
        secure_manager = SecureFileManager()
        results = []
        
        for evidence_id in evidence_ids:
            result = secure_manager.delete_file_securely(evidence_id, current_user.id)
            results.append({
                'evidence_id': evidence_id,
                'success': result['success'],
                'error': result.get('error')
            })
            
            if result['success']:
                # Log deletion
                secure_manager.audit_file_access(
                    evidence_id=evidence_id,
                    user_id=current_user.id,
                    action='batch_delete',
                    ip_address=get_client_ip()
                )
        
        successful_deletions = sum(1 for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'message': f'{successful_deletions} files deleted successfully',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers for secure file routes
@secure_file_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access denied'}), 403

@secure_file_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'File not found'}), 404

@secure_file_bp.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large'}), 413