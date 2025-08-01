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
    
    # Encryption settings
    ENCRYPTION_ALGORITHM = 'Fernet'  # AES-128 in CBC mode with HMAC
    KEY_DERIVATION_ITERATIONS = 100000
    
    # Audit logging
    AUDIT_LOG_RETENTION_DAYS = 365  # Keep audit logs for 1 year
    LOG_SENSITIVE_OPERATIONS = True
    LOG_FILE_ACCESS = True
    
    # Rate limiting (files per user per hour)
    UPLOAD_RATE_LIMIT = 50
    DOWNLOAD_RATE_LIMIT = 100
    
    # File integrity
    HASH_ALGORITHM = 'sha256'
    VERIFY_INTEGRITY_ON_ACCESS = True
    
    # Access restrictions
    MAX_FAILED_ACCESS_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    
    @classmethod
    def get_secure_headers(cls):
        """Get security headers for HTTP responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data: https:;",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    @classmethod
    def is_allowed_file_type(cls, filename):
        """Check if file type is allowed"""
        if '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def get_upload_path(cls, user_id, case_id=None):
        """Get secure upload path for user"""
        base_path = os.path.join(cls.UPLOAD_FOLDER, f'user_{user_id}')
        if case_id:
            return os.path.join(base_path, f'case_{case_id}')
        return base_path
    
    @classmethod
    def sanitize_filename(cls, filename):
        """Sanitize filename for secure storage"""
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Remove potentially dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        sanitized = ''.join(c for c in filename if c in safe_chars)
        
        # Ensure reasonable length
        if len(sanitized) > 100:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:95] + ext
        
        return sanitized or 'unnamed_file'

# Canadian legal data protection compliance
class PrivacyConfig:
    """Privacy and data protection settings"""
    
    # Data retention
    CASE_DATA_RETENTION_YEARS = 7  # Legal requirement in Canada
    EVIDENCE_RETENTION_YEARS = 10  # Extended for legal evidence
    AUDIT_LOG_RETENTION_YEARS = 1
    
    # Data classification
    SENSITIVE_DATA_TYPES = [
        'personal_information',
        'financial_records',
        'medical_records',
        'legal_documents',
        'court_orders'
    ]
    
    # Consent management
    REQUIRE_EXPLICIT_CONSENT = True
    CONSENT_EXPIRY_MONTHS = 24
    
    # Data subject rights (PIPEDA compliance)
    ENABLE_DATA_PORTABILITY = True
    ENABLE_RIGHT_TO_DELETION = True
    ENABLE_ACCESS_REQUESTS = True
    
    @classmethod
    def get_retention_period(cls, data_type):
        """Get data retention period based on type"""
        retention_map = {
            'case_data': cls.CASE_DATA_RETENTION_YEARS,
            'evidence': cls.EVIDENCE_RETENTION_YEARS,
            'audit_logs': cls.AUDIT_LOG_RETENTION_YEARS,
            'user_data': cls.CASE_DATA_RETENTION_YEARS
        }
        return retention_map.get(data_type, cls.CASE_DATA_RETENTION_YEARS)

# Security monitoring and alerting
class MonitoringConfig:
    """Security monitoring configuration"""
    
    # Alert thresholds
    FAILED_LOGIN_THRESHOLD = 5
    SUSPICIOUS_FILE_ACCESS_THRESHOLD = 10
    UNUSUAL_DOWNLOAD_THRESHOLD = 20
    
    # Monitoring intervals
    SECURITY_SCAN_INTERVAL_HOURS = 24
    ACCESS_PATTERN_ANALYSIS_HOURS = 1
    
    # Alert destinations
    SECURITY_ALERT_EMAIL = os.getenv('SECURITY_ALERT_EMAIL')
    ADMIN_ALERT_EMAIL = os.getenv('ADMIN_ALERT_EMAIL')
    
    # Threat detection
    ENABLE_ANOMALY_DETECTION = True
    ENABLE_THREAT_INTELLIGENCE = False  # Would require external service
    
    @classmethod
    def should_alert(cls, event_type, count):
        """Determine if security event should trigger alert"""
        thresholds = {
            'failed_login': cls.FAILED_LOGIN_THRESHOLD,
            'suspicious_access': cls.SUSPICIOUS_FILE_ACCESS_THRESHOLD,
            'unusual_download': cls.UNUSUAL_DOWNLOAD_THRESHOLD
        }
        return count >= thresholds.get(event_type, 5)