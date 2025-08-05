"""
Security Configuration for Smart Dispute Flask App
Centralizes security settings and constants
"""

import os
from datetime import timedelta

class SecurityConfig:
    """Security configuration constants"""
    
    # File upload security
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'txt', 'rtf',  # Documents
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',  # Images
        'mp3', 'wav', 'm4a',  # Audio
        'mp4', 'avi', 'mov'   # Video (limited)
    }
    
    # File storage paths
    UPLOAD_FOLDER = 'uploads'
    ENCRYPTED_FOLDER = 'encrypted'
    TEMP_FOLDER = 'temp'
    
    # Security scanning patterns
    MALICIOUS_PATTERNS = [
        b'<script',
        b'javascript:',
        b'<?php',
        b'<%',
        b'<html',
        b'<!DOCTYPE',
        b'vbscript:',
        b'data:text/html'
    ]
    
    # Access control
    DEFAULT_FILE_PERMISSIONS = 0o600  # Owner read/write only
    DEFAULT_DIR_PERMISSIONS = 0o700   # Owner full access only
    
    # Token security
    DOWNLOAD_TOKEN_EXPIRY = timedelta(hours=1)  # 1 hour default
    SHARE_TOKEN_EXPIRY = timedelta(days=7)      # 7 days for sharing
    
    # Justice-bot.com integration
    JUSTICE_BOT_DOMAIN = os.getenv("APP_DOMAIN", "justice-bot.com")
    AUTH_ENDPOINT = f"https://auth.{JUSTICE_BOT_DOMAIN}/oauth2"
    API_ENDPOINT = f"https://api.{JUSTICE_BOT_DOMAIN}/v1"
    
    # Alert destinations
    SECURITY_ALERT_EMAIL = os.getenv('SECURITY_ALERT_EMAIL')
    ADMIN_ALERT_EMAIL = os.getenv('ADMIN_ALERT_EMAIL')