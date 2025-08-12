import functools
from flask import current_app, g, abort
from models.evidence import Evidence
from utils.db import db
import os
import logging
from cryptography.fernet import Fernet

# Initialize logger
logger = logging.getLogger(__name__)

class SecureFileManager:
    """Manages secure file storage with encryption and access control"""
    
    def __init__(self):
        self.encryption_key = current_app.config.get('ENCRYPTION_KEY')
        if not self.encryption_key:
            raise ValueError("Encryption key not configured")
        
        # Fernet key must be 32 url-safe base64-encoded bytes.
        # Environment variables are strings, so we need to encode it back to bytes.
        self.cipher = Fernet(self.encryption_key.encode('utf-8'))
    
    def encrypt_file(self, file_path):
        """Encrypt a file and store it securely"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            encrypted_data = self.cipher.encrypt(file_data)
            
            # Save encrypted file
            encrypted_path = os.path.join(
                current_app.config['ENCRYPTED_FOLDER'],
                os.path.basename(file_path) + '.enc'
            )
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
                
            return encrypted_path
        except Exception as e:
            logger.error(f"File encryption failed: {str(e)}")
            raise
    
    def decrypt_file(self, encrypted_path):
        """Decrypt a file for authorized access"""
        try:
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data
        except Exception as e:
            logger.error(f"File decryption failed: {str(e)}")
            raise

def require_file_access(func):
    """Decorator to check file access permissions with functools.wraps"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        file_id = kwargs.get('file_id')
        if not file_id:
            abort(400, "File ID required")
        
        file = Evidence.query.get(file_id)
        if not file:
            abort(404, "File not found")
        
        if file.uploaded_by != g.user.id:
            abort(403, "Access denied")
        
        return func(*args, **kwargs)
    return wrapper

def get_client_ip(request):
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']