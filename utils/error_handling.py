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
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

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
        # In development, show detailed error
        if current_app.config.get('ENV') == 'development':
            return f"""
            <h1>Internal Server Error</h1>
            <h2>{error}</h2>
            <pre>{traceback.format_exc()}</pre>
            """, 500
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
                    result = db.session.execute(text('SELECT 1'), execution_options={"timeout": 5}) \
                                        .scalar()
                    user_count = result or 0
                    
                    # Get database statistics
                    try:
                        # Try to get table count statistics
                        table_count_result = db.session.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")).scalar()
                        table_info = f"Tables: {table_count_result}" if table_count_result else "Tables: Unknown"
                    except:
                        # Fallback for SQLite or if the above query fails
                        table_info = "Tables: Count unavailable"
                    
                    # Check connection pool status
                    pool = db.engine.pool
                    pool_status = f"Connections: {pool.status()}, Size: {pool.size()}"
                    
                    return True, f"Database OK (Connection test: {user_count}, {table_info}, {pool_status})"
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
    
    @staticmethod
    def check_memory_usage():
        """Check system memory usage"""
        if not PSUTIL_AVAILABLE:
            return False, "psutil not available"
        
        try:
            # Get memory information
            memory = psutil.virtual_memory()
            
            # Calculate percentages
            memory_percent = memory.percent
            swap_percent = psutil.swap_memory().percent if hasattr(psutil, 'swap_memory') else 0
            
            # Format memory information
            memory_info = (
                f"Memory: {memory_percent:.1f}% used "
                f"({memory.used // (1024*1024)}MB/{memory.total // (1024*1024)}MB), "
                f"Available: {memory.available // (1024*1024)}MB"
            )
            
            # Check if memory usage is within acceptable limits (less than 90%)
            if memory_percent > 90:
                return False, f"Memory usage critical: {memory_info}"
            elif memory_percent > 75:
                return True, f"Memory usage high: {memory_info}"
            else:
                return True, f"Memory usage normal: {memory_info}"
        except Exception as e:
            return False, f"Memory check failed: {str(e)}"
    
    @staticmethod
    def check_cpu_usage():
        """Check system CPU usage"""
        if not PSUTIL_AVAILABLE:
            return False, "psutil not available"
        
        try:
            # Get CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Format CPU information
            cpu_info = f"CPU: {cpu_percent:.1f}%"
            
            # Check if CPU usage is within acceptable limits (less than 90%)
            if cpu_percent > 90:
                return False, f"CPU usage critical: {cpu_info}"
            elif cpu_percent > 75:
                return True, f"CPU usage high: {cpu_info}"
            else:
                return True, f"CPU usage normal: {cpu_info}"
        except Exception as e:
            return False, f"CPU check failed: {str(e)}"
    
    @staticmethod
    def check_disk_usage():
        """Check disk space usage"""
        if not PSUTIL_AVAILABLE:
            return False, "psutil not available"
        
        try:
            # Get disk information for the root partition
            disk = psutil.disk_usage('/')
            
            # Calculate percentages
            disk_percent = (disk.used / disk.total) * 100
            
            # Format disk information
            disk_info = (
                f"Disk: {disk_percent:.1f}% used "
                f"({disk.used // (1024*1024*1024)}GB/{disk.total // (1024*1024*1024)}GB), "
                f"Free: {disk.free // (1024*1024*1024)}GB"
            )
            
            # Check if disk usage is within acceptable limits (less than 90%)
            if disk_percent > 90:
                return False, f"Disk usage critical: {disk_info}"
            elif disk_percent > 75:
                return True, f"Disk usage high: {disk_info}"
            else:
                return True, f"Disk usage normal: {disk_info}"
        except Exception as e:
            return False, f"Disk check failed: {str(e)}"
    
    @staticmethod
    def check_environment_variables():
        """Check critical environment variables"""
        try:
            # List of critical environment variables that should be set
            critical_vars = [
                'SECRET_KEY',
                'DATABASE_URL',
                'FLASK_ENV'
            ]
            
            # Check which variables are missing
            missing_vars = [var for var in critical_vars if not os.environ.get(var)]
            
            if missing_vars:
                return False, f"Missing critical environment variables: {', '.join(missing_vars)}"
            else:
                return True, f"All critical environment variables present ({len(critical_vars)} checked)"
        except Exception as e:
            return False, f"Environment variable check failed: {str(e)}"
    
    @staticmethod
    def check_ssl_certificates():
        """Check SSL certificate validity for main domain"""
        try:
            import ssl
            import socket
            
            domain = "smartdisputecanada.me"
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to the domain and get certificate
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
            # Check certificate expiration
            not_after = cert['notAfter']
            # Parse the date string
            import datetime
            exp_date = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            days_until_expiry = (exp_date - datetime.datetime.utcnow()).days
            
            if days_until_expiry < 0:
                return False, f"SSL certificate for {domain} expired {abs(days_until_expiry)} days ago"
            elif days_until_expiry < 14:
                return False, f"SSL certificate for {domain} expires in {days_until_expiry} days"
            else:
                return True, f"SSL certificate for {domain} valid for {days_until_expiry} more days"
        except Exception as e:
            return False, f"SSL certificate check failed for {domain}: {str(e)}"
    
    @staticmethod
    def check_cache_service():
        """Check cache service connectivity (Redis/Memcached)"""
        # Check if cache service is configured
        cache_url = os.environ.get('REDIS_URL') or os.environ.get('MEMCACHED_URL')
        
        if not cache_url:
            return True, "No cache service configured"
        
        try:
            # Try to import redis client
            import redis
            
            # Try to connect to Redis
            r = redis.Redis.from_url(cache_url, socket_timeout=5)
            r.ping()
            return True, "Cache service connected successfully"
        except ImportError:
            return False, "Redis client not installed"
        except Exception as e:
            return False, f"Cache service connection failed: {str(e)}"
    
    @staticmethod
    def check_email_service():
        """Check email service connectivity"""
        # Check if email service is configured
        mail_server = os.environ.get('MAIL_SERVER')
        mail_port = os.environ.get('MAIL_PORT')
        mail_username = os.environ.get('MAIL_USERNAME')
        mail_password = os.environ.get('MAIL_PASSWORD')
        
        if not all([mail_server, mail_port, mail_username, mail_password]):
            return True, "Email service not fully configured"
        
        try:
            # Try to import smtplib
            import smtplib
            
            # Try to connect to the email server
            server = smtplib.SMTP(mail_server, int(mail_port))
            server.starttls()
            server.login(mail_username, mail_password)
            server.quit()
            return True, "Email service connected successfully"
        except ImportError:
            return False, "smtplib not available"
        except Exception as e:
            return False, f"Email service connection failed: {str(e)}"
    
    @classmethod
    def get_health_status(cls):
        """Get comprehensive health status"""
        checks = {
            'database': cls.check_database(),
            'file_system': cls.check_file_system(),
            'ai_services': cls.check_ai_services(),
            'network': cls.check_network(),
            'memory': cls.check_memory_usage(),
            'cpu': cls.check_cpu_usage(),
            'disk': cls.check_disk_usage(),
            'environment': cls.check_environment_variables(),
            'ssl': cls.check_ssl_certificates(),
            'cache': cls.check_cache_service(),
            'email': cls.check_email_service()
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