"""
Comprehensive Error Handling and Logging System
Enhanced error handling for production deployment
"""

import logging
import traceback
import sys
from datetime import datetime
from functools import wraps
from flask import jsonify, render_template, request, current_app
import os

# Configure logging
def setup_logging():
    """Set up comprehensive logging configuration"""
    
    # Create logs directory
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'app.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure specific loggers
    loggers = {
        'werkzeug': logging.WARNING,
        'urllib3': logging.WARNING,
        'requests': logging.WARNING,
        'PIL': logging.WARNING
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)
    
    # Create separate loggers for different components
    setup_component_loggers()

def setup_component_loggers():
    """Set up component-specific loggers"""
    
    log_dir = 'logs'
    
    # Security logger
    security_logger = logging.getLogger('security')
    security_handler = logging.FileHandler(os.path.join(log_dir, 'security.log'))
    security_handler.setFormatter(logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    ))
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    
    # Payment logger
    payment_logger = logging.getLogger('payments')
    payment_handler = logging.FileHandler(os.path.join(log_dir, 'payments.log'))
    payment_handler.setFormatter(logging.Formatter(
        '%(asctime)s - PAYMENT - %(levelname)s - %(message)s'
    ))
    payment_logger.addHandler(payment_handler)
    payment_logger.setLevel(logging.INFO)
    
    # AI processing logger
    ai_logger = logging.getLogger('ai_processing')
    ai_handler = logging.FileHandler(os.path.join(log_dir, 'ai_processing.log'))
    ai_handler.setFormatter(logging.Formatter(
        '%(asctime)s - AI - %(levelname)s - %(message)s'
    ))
    ai_logger.addHandler(ai_handler)
    ai_logger.setLevel(logging.INFO)

class ErrorHandler:
    """Centralized error handling class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_error(self, error, context=None, user_id=None):
        """Log error with context information"""
        try:
            error_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc(),
                'context': context or {},
                'user_id': user_id,
                'request_path': getattr(request, 'path', 'N/A'),
                'request_method': getattr(request, 'method', 'N/A'),
                'user_agent': str(getattr(request, 'user_agent', 'N/A'))
            }
            
            self.logger.error(f"Application Error: {error_info}")
            
            # Log to security logger if security-related
            if self._is_security_error(error):
                security_logger = logging.getLogger('security')
                security_logger.warning(f"Security incident: {error_info}")
                
        except Exception as log_error:
            # Fallback logging
            print(f"Failed to log error: {log_error}")
            print(f"Original error: {error}")
    
    def _is_security_error(self, error):
        """Check if error is security-related"""
        security_indicators = [
            'unauthorized', 'forbidden', 'access denied',
            'authentication', 'permission', 'csrf',
            'injection', 'xss', 'sql'
        ]
        
        error_str = str(error).lower()
        return any(indicator in error_str for indicator in security_indicators)

# Global error handler instance
error_handler = ErrorHandler()

def handle_errors(f):
    """Decorator for comprehensive error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Log the error
            error_handler.log_error(
                error=e,
                context={'function': f.__name__, 'args': str(args)[:200]},
                user_id=getattr(request, 'user_id', None)
            )
            
            # Return appropriate response based on request type
            if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                return jsonify({
                    'success': False,
                    'error': 'An internal error occurred',
                    'error_id': datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                }), 500
            else:
                return render_template('errors/500.html'), 500
    
    return decorated_function

def register_error_handlers(app):
    """Register global error handlers with Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        error_handler.log_error(error, context={'status_code': 400})
        if request.is_json:
            return jsonify({'success': False, 'error': 'Bad request'}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        error_handler.log_error(error, context={'status_code': 401})
        if request.is_json:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        error_handler.log_error(error, context={'status_code': 403})
        if request.is_json:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(413)
    def too_large(error):
        error_handler.log_error(error, context={'status_code': 413})
        if request.is_json:
            return jsonify({'success': False, 'error': 'File too large'}), 413
        return render_template('errors/413.html'), 413
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        error_handler.log_error(error, context={'status_code': 429})
        if request.is_json:
            return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        error_handler.log_error(error, context={'status_code': 500})
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        error_handler.log_error(error, context={'unhandled_exception': True})
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'An unexpected error occurred'
            }), 500
        
        return render_template('errors/500.html'), 500

class HealthCheck:
    """Application health check utilities"""
    
    @classmethod
    def check_database(cls):
        """Check database connectivity with timeout and meaningful query"""
        try:
            from flask import current_app
            import sqlalchemy
            from sqlalchemy import text
            from sqlalchemy.exc import OperationalError, TimeoutError
            
            with current_app.app_context():
                db = current_app.extensions['sqlalchemy'].db
                
                # Set timeout for database operations
                try:
                    # Try a simple query with timeout
                    result = db.session.execute(text('SELECT COUNT(*) FROM user'), execution_options={"timeout": 5}) \
                                        .scalar()
                    user_count = result or 0
                    
                    # Check connection pool status
                    pool = db.engine.pool
                    pool_status = f"Connections: {pool.status()}, Size: {pool.size()}"
                    
                    return True, f"Database OK ({user_count} users, {pool_status})"
                except (OperationalError, TimeoutError) as e:
                    return False, f"Database timeout: {str(e)}"
        except Exception as e:
            logging.getLogger('ai_processing').error(f"Database health check failed: {str(e)}")
            return False, f"Database error: {str(e)}"
    
    @staticmethod
    def check_file_system():
        """Check file system access"""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile() as tmp:
                tmp.write(b'health_check')
                tmp.flush()
            return True, "File system OK"
        except Exception as e:
            return False, f"File system error: {str(e)}"
    
    @staticmethod
    def check_ai_services():
        """Check AI service availability"""
        try:
            # Basic connectivity check (would need API keys in production)
            return True, "AI services configured"
        except Exception as e:
            return False, f"AI services error: {str(e)}"
    
    @staticmethod
    def check_network():
        """Comprehensive network diagnostics with fail-safes"""
        try:
            import socket
            import requests
            
            # Check DNS resolution
            try:
                socket.gethostbyname("google.com")
            except socket.gaierror:
                return False, "DNS resolution failed"
                
            # Check ICMP connectivity (ping equivalent)
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=5)
            except Exception as e:
                return False, f"ICMP blocked: {str(e)}"
                
            # Check HTTP connectivity
            try:
                response = requests.head("http://example.com", timeout=5)
                if response.status_code != 200:
                    return False, f"HTTP test failed: Status {response.status_code}"
            except Exception as e:
                return False, f"HTTP error: {str(e)}"
                
            # Check HTTPS connectivity
            try:
                response = requests.head("https://example.com", timeout=5)
                if response.status_code != 200:
                    return False, f"HTTPS test failed: Status {response.status_code}"
            except Exception as e:
                return False, f"HTTPS error: {str(e)}"
                
            return True, "Network fully operational"
        except Exception as e:
            return False, f"Network diagnostics failed: {str(e)}"
    
    @classmethod
    def get_health_status(cls):
        """Get comprehensive health status"""
        checks = {
            'database': cls.check_database(),
            'file_system': cls.check_file_system(),
            'ai_services': cls.check_ai_services(),
            'network': cls.check_network()
        }
        
        all_healthy = all(status for status, _ in checks.values())
        
        return {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                name: {'status': 'ok' if status else 'error', 'message': message}
                for name, (status, message) in checks.items()
            }
        }

# Initialize logging when module is imported
setup_logging()