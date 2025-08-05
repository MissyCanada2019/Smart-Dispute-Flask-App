"""
Secure File Routes
Handles secure file upload, download, and management with access controls
"""

from flask import Blueprint, request, jsonify, send_file, abort, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.case import Case
from models.evidence import Evidence
from utils.db import db
from utils.secure_storage import SecureFileManager, require_file_access, get_client_ip
import os
import tempfile
from datetime import datetime

secure_file_bp = Blueprint('secure_files', __name__, url_prefix='/secure-files')

@secure_file_bp.route('/download/<int:file_id>')
@require_file_access
def download_secure_file(file_id):
    """Download a secure file"""
    try:
        file_manager = SecureFileManager()
        file_data = file_manager.get_file(file_id)
        return send_file(file_data, as_attachment=True, download_name=f"file_{file_id}.bin")
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('secure_files.manage_secure_files'))

@secure_file_bp.route('/view/<int:file_id>')
@require_file_access
def view_secure_file(file_id):
    """View file metadata"""
    file = Evidence.query.get(file_id)
    if not file:
        flash('File not found', 'error')
        return redirect(url_for('secure_files.manage_secure_files'))
    return render_template('files/view.html', file=file)

@secure_file_bp.route('/delete/<int:file_id>', methods=['POST'])
@require_file_access
def delete_secure_file(file_id):
    """Delete a secure file"""
    try:
        file_manager = SecureFileManager()
        file_manager.delete_file(file_id)
        flash('File deleted successfully', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('secure_files.manage_secure_files'))

@secure_file_bp.route('/manage')
@login_required
def manage_secure_files():
    """Manage user's secure files"""
    user_files = Evidence.query.filter_by(uploaded_by=current_user.id).all()
    return render_template('files/manage.html', files=user_files)