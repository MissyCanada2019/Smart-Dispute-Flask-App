"""
Secure File Storage and Access Control System
Implements security measures for protecting sensitive legal documents
"""

import os
import hashlib
import hmac
import secrets
import tempfile
from typing import Dict, List, Any, Optional, Tuple, BinaryIO
from werkzeug.utils import secure_filename
from models.case import Case
from models.evidence import Evidence
from models.user import User
from models import db
from flask import current_app, request, abort
from flask_login import current_user
from datetime import datetime, timedelta
import mimetypes
import uuid
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecureFileManager:
    """Manages secure file storage with encryption and access controls"""
    
    def __init__(self):
        self.upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        self.max_file_size = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
        self.allowed_extensions = {
            'pdf', 'doc', 'docx', 'txt', 'rtf',  # Documents
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',  # Images
            'mp3', 'wav', 'm4a',  # Audio
            'mp4', 'avi', 'mov'   # Video (limited)
        }
        self.encryption_key = self._get_or_create_encryption_key()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create file encryption key"""
        key_file = os.path.join(self.upload_folder, '.encryption_key')
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                
                # Ensure upload folder exists
                os.makedirs(self.upload_folder, exist_ok=True)
                
                # Save key securely
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                
                return key
        except Exception as e:
            print(f"Error handling encryption key: {str(e)}")
            # Return a temporary key for development
            return Fernet.generate_key()
    
    def validate_file_upload(self, file, user_id: int) -> Dict[str, Any]:
        """Validate file upload for security"""
        if not file or not file.filename:
            return {'valid': False, 'error': 'No file provided'}
        
        # Check file extension
        filename = secure_filename(file.filename)
        if '.' not in filename:
            return {'valid': False, 'error': 'File must have an extension'}
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in self.allowed_extensions:
            return {'valid': False, 'error': f'File type "{ext}" is not allowed'}
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset position
        
        if file_size > self.max_file_size:
            return {'valid': False, 'error': 'File too large'}
        
        if file_size == 0:
            return {'valid': False, 'error': 'Empty file'}
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            return {'valid': False, 'error': 'Could not determine file type'}
        
        # Additional security checks
        security_check = self._security_scan_file(file)
        if not security_check['safe']:
            return {'valid': False, 'error': security_check['reason']}
        
        return {
            'valid': True,
            'filename': filename,
            'size': file_size,
            'mime_type': mime_type,
            'extension': ext
        }
    
    def _security_scan_file(self, file) -> Dict[str, Any]:
        """Basic security scanning of uploaded files"""
        try:
            # Read first few bytes to check for malicious patterns
            file.seek(0)
            header = file.read(1024)
            file.seek(0)
            
            # Check for suspicious patterns
            suspicious_patterns = [
                b'<script',
                b'javascript:',
                b'<?php',
                b'<%',
                b'<html',
                b'<!DOCTYPE',
            ]
            
            header_lower = header.lower()
            for pattern in suspicious_patterns:
                if pattern in header_lower:
                    return {
                        'safe': False,
                        'reason': 'File contains potentially malicious content'
                    }
            
            return {'safe': True}
            
        except Exception as e:
            return {
                'safe': False,
                'reason': f'Error scanning file: {str(e)}'
            }
    
    def store_file_securely(self, file, case_id: int, user_id: int, 
                          evidence_title: str = None, evidence_description: str = None) -> Dict[str, Any]:
        """Store file securely with encryption and access controls"""
        try:
            # Validate file
            validation = self.validate_file_upload(file, user_id)
            if not validation['valid']:
                return validation
            
            # Generate unique file identifier
            file_id = str(uuid.uuid4())
            
            # Create secure directory structure
            user_dir = os.path.join(self.upload_folder, f'user_{user_id}')
            case_dir = os.path.join(user_dir, f'case_{case_id}')
            os.makedirs(case_dir, exist_ok=True)
            
            # Set restrictive permissions
            os.chmod(user_dir, 0o700)
            os.chmod(case_dir, 0o700)
            
            # Generate secure filename
            ext = validation['extension']
            encrypted_filename = f"{file_id}.{ext}.enc"
            file_path = os.path.join(case_dir, encrypted_filename)
            
            # Encrypt and store file
            file.seek(0)
            file_data = file.read()
            
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(file_data)
            
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Set file permissions
            os.chmod(file_path, 0o600)
            
            # Generate file hash for integrity checking
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Create evidence record
            evidence = Evidence(
                filename=encrypted_filename,
                original_filename=validation['filename'],
                file_path=file_path,
                file_size=validation['size'],
                mime_type=validation['mime_type'],
                file_hash=file_hash,
                title=evidence_title or validation['filename'],
                description=evidence_description or '',
                case_id=case_id,
                user_id=user_id,
                storage_encrypted=True
            )
            
            db.session.add(evidence)
            db.session.commit()
            
            return {
                'success': True,
                'evidence_id': evidence.id,
                'file_id': file_id,
                'file_path': file_path,
                'file_hash': file_hash
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Error storing file: {str(e)}'
            }
    
    def retrieve_file_securely(self, evidence_id: int, user_id: int) -> Tuple[Optional[BinaryIO], Optional[Dict[str, Any]]]:
        """Retrieve and decrypt file with access control checks"""
        try:
            # Get evidence record
            evidence = Evidence.query.get(evidence_id)
            if not evidence:
                return None, {'error': 'Evidence not found'}
            
            # Check access permissions
            access_check = self.check_file_access(evidence_id, user_id)
            if not access_check['allowed']:
                return None, {'error': access_check['reason']}
            
            # Check if file exists
            if not os.path.exists(evidence.file_path):
                return None, {'error': 'File not found on disk'}
            
            # Read and decrypt file
            with open(evidence.file_path, 'rb') as f:
                encrypted_data = f.read()
            
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Verify file integrity
            file_hash = hashlib.sha256(decrypted_data).hexdigest()
            if evidence.file_hash and file_hash != evidence.file_hash:
                return None, {'error': 'File integrity check failed'}
            
            # Create temporary file for serving
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(decrypted_data)
            temp_file.seek(0)
            
            file_info = {
                'filename': evidence.original_filename,
                'mime_type': evidence.mime_type,
                'size': evidence.file_size,
                'temp_path': temp_file.name
            }
            
            return temp_file, file_info
            
        except Exception as e:
            return None, {'error': f'Error retrieving file: {str(e)}'}
    
    def check_file_access(self, evidence_id: int, user_id: int) -> Dict[str, Any]:
        """Check if user has access to a specific file"""
        try:
            evidence = Evidence.query.get(evidence_id)
            if not evidence:
                return {'allowed': False, 'reason': 'Evidence not found'}
            
            # Owner has full access
            if evidence.user_id == user_id:
                return {'allowed': True, 'access_level': 'owner'}
            
            # Check if user owns the case
            case = Case.query.get(evidence.case_id)
            if case and case.user_id == user_id:
                return {'allowed': True, 'access_level': 'case_owner'}
            
            # Check for shared access (future feature)
            # This could include lawyers, family members, etc.
            
            return {'allowed': False, 'reason': 'Access denied'}
            
        except Exception as e:
            return {'allowed': False, 'reason': f'Error checking access: {str(e)}'}
    
    def delete_file_securely(self, evidence_id: int, user_id: int) -> Dict[str, Any]:
        """Securely delete file and evidence record"""
        try:
            evidence = Evidence.query.get(evidence_id)
            if not evidence:
                return {'success': False, 'error': 'Evidence not found'}
            
            # Check access permissions
            access_check = self.check_file_access(evidence_id, user_id)
            if not access_check['allowed']:
                return {'success': False, 'error': access_check['reason']}
            
            # Securely delete physical file
            if os.path.exists(evidence.file_path):
                # Overwrite file with random data before deletion
                file_size = os.path.getsize(evidence.file_path)
                with open(evidence.file_path, 'wb') as f:
                    f.write(secrets.token_bytes(file_size))
                
                # Delete file
                os.remove(evidence.file_path)
            
            # Delete database record
            db.session.delete(evidence)
            db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error deleting file: {str(e)}'}
    
    def generate_secure_download_token(self, evidence_id: int, user_id: int, 
                                     expires_in: int = 3600) -> Optional[str]:
        """Generate secure token for file downloads"""
        try:
            # Check access first
            access_check = self.check_file_access(evidence_id, user_id)
            if not access_check['allowed']:
                return None
            
            # Create token payload
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            payload = f"{evidence_id}:{user_id}:{int(expires_at.timestamp())}"
            
            # Sign token
            secret_key = current_app.config.get('SECRET_KEY', 'fallback-key')
            signature = hmac.new(
                secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            token = f"{base64.b64encode(payload.encode()).decode()}:{signature}"
            
            return token
            
        except Exception as e:
            print(f"Error generating download token: {str(e)}")
            return None
    
    def verify_download_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify secure download token"""
        try:
            if ':' not in token:
                return None
            
            payload_b64, signature = token.rsplit(':', 1)
            payload = base64.b64decode(payload_b64).decode()
            
            # Verify signature
            secret_key = current_app.config.get('SECRET_KEY', 'fallback-key')
            expected_signature = hmac.new(
                secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Parse payload
            evidence_id_str, user_id_str, expires_at_str = payload.split(':')
            evidence_id = int(evidence_id_str)
            user_id = int(user_id_str)
            expires_at = datetime.utcfromtimestamp(int(expires_at_str))
            
            # Check expiration
            if datetime.utcnow() > expires_at:
                return None
            
            return {
                'evidence_id': evidence_id,
                'user_id': user_id,
                'expires_at': expires_at
            }
            
        except Exception as e:
            print(f"Error verifying download token: {str(e)}")
            return None
    
    def audit_file_access(self, evidence_id: int, user_id: int, action: str, 
                         ip_address: str = None, user_agent: str = None):
        """Log file access for security auditing"""
        try:
            # Create audit log entry
            audit_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'evidence_id': evidence_id,
                'user_id': user_id,
                'action': action,  # 'view', 'download', 'delete', 'upload'
                'ip_address': ip_address or (request.remote_addr if request else None),
                'user_agent': user_agent or (request.headers.get('User-Agent') if request else None)
            }
            
            # For now, log to file (in production, use proper logging service)
            audit_log_path = os.path.join(self.upload_folder, 'audit.log')
            with open(audit_log_path, 'a') as f:
                f.write(f"{audit_entry}\n")
                
        except Exception as e:
            print(f"Error logging file access: {str(e)}")
    
    def get_file_access_stats(self, user_id: int) -> Dict[str, Any]:
        """Get file access statistics for user"""
        try:
            user_cases = Case.query.filter_by(user_id=user_id).all()
            case_ids = [case.id for case in user_cases]
            
            # Get evidence counts
            total_files = Evidence.query.filter(Evidence.case_id.in_(case_ids)).count()
            encrypted_files = Evidence.query.filter(
                Evidence.case_id.in_(case_ids),
                Evidence.storage_encrypted == True
            ).count()
            
            # Calculate total storage used
            evidence_list = Evidence.query.filter(Evidence.case_id.in_(case_ids)).all()
            total_storage = sum(e.file_size or 0 for e in evidence_list)
            
            return {
                'total_files': total_files,
                'encrypted_files': encrypted_files,
                'total_storage_bytes': total_storage,
                'total_storage_mb': round(total_storage / (1024 * 1024), 2),
                'encryption_rate': round((encrypted_files / total_files) * 100, 1) if total_files > 0 else 0
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_files': 0,
                'encrypted_files': 0,
                'total_storage_bytes': 0,
                'total_storage_mb': 0,
                'encryption_rate': 0
            }

# Security decorators and utilities
def require_file_access(evidence_id_param='evidence_id'):
    """Decorator to require file access permissions"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            evidence_id = kwargs.get(evidence_id_param)
            if not evidence_id:
                abort(400)
            
            secure_manager = SecureFileManager()
            access_check = secure_manager.check_file_access(evidence_id, current_user.id)
            
            if not access_check['allowed']:
                abort(403)
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

def get_client_ip():
    """Get client IP address safely"""
    if request:
        return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for secure storage"""
    # Remove potentially dangerous characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
    sanitized = ''.join(c for c in filename if c in safe_chars)
    
    # Ensure reasonable length
    if len(sanitized) > 100:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:95] + ext
    
    return sanitized or 'unnamed_file'