from flask import Flask
from flask_login import LoginManager
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from utils.error_handling import register_error_handlers, HealthCheck
from utils.db import db

def create_app():
    # Load environment variables from .env file
    load_dotenv('.env')

    app = Flask(__name__)
    
    # Use environment variable for secret key, with fallback
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database configuration with production-grade validation
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    # Handle placeholder values with case-insensitive check
    placeholder_patterns = [
        '<your_railway_postgres_url>',
        'your-database-url-here',
        'placeholder',
        'example.com'
    ]
    
    # PostgreSQL-specific validation
    is_postgres = 'postgres' in database_url.lower()
    
    if any(pattern.lower() in database_url.lower() for pattern in placeholder_patterns):
        app.logger.error(f"Critical error: Database URL placeholder detected!")
        app.logger.error("Please set a valid DATABASE_URL environment variable")
        app.logger.warning("Using SQLite fallback database for local development")
        database_url = 'sqlite:///app.db'
    elif is_postgres and not database_url.startswith('postgresql://'):
        app.logger.warning("PostgreSQL URL should use 'postgresql://' prefix. Attempting to fix...")
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Validate URL format with detailed error reporting
    try:
        from sqlalchemy.engine import make_url
        parsed_url = make_url(database_url)
        
        # Additional PostgreSQL checks
        if is_postgres:
            if not parsed_url.drivername.startswith('postgresql'):
                raise ValueError("Invalid PostgreSQL URL format")
            if not parsed_url.host or not parsed_url.port:
                raise ValueError("PostgreSQL URL requires host and port")
                
        app.logger.info(f"Using database: {parsed_url}")
    except Exception as e:
        app.logger.error(f"Invalid database URL format: {str(e)}")
        app.logger.error(f"Offending URL: {database_url}")
        app.logger.warning("Using SQLite fallback database")
        database_url = 'sqlite:///app.db'
        parsed_url = make_url(database_url)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    db.init_app(app)

    # Configure logging
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')
    
    handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return db.session.query(User).get(int(user_id))

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.case_routes import case_bp
    from routes.form_routes import form_bp
    from routes.journey_routes import journey_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.secure_file_routes import secure_file_bp
    from routes.evidence_routes import evidence_bp
    from routes.tracking_routes import tracking_bp
    from routes.notification_routes import notification_bp
    from routes.payment_routes import payment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(case_bp)
    app.register_blueprint(form_bp)
    app.register_blueprint(journey_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(secure_file_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(payment_bp)

    # Root route - Welcome/onboarding page
    from flask import render_template
    @app.route('/')
    def index():
        return render_template('onboarding/welcome.html')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check route with detailed logging
    @app.route('/health')
    def health_check():
        import time
        from flask import current_app
        
        start_time = time.time()
        health_status = HealthCheck.get_health_status()
        duration = round((time.time() - start_time) * 1000, 2)
        
        # Log health check results
        if health_status['status'] == 'healthy':
            current_app.logger.info(f"Health check passed in {duration}ms")
        else:
            error_details = {k: v for k,v in health_status['checks'].items() if v['status'] == 'error'}
            current_app.logger.error(
                f"Health check FAILED in {duration}ms. Errors: {error_details}"
            )
        
        return health_status

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    # Explicitly bind to all interfaces and handle port binding
    # Explicitly bind to port 8080 with fallback to 5000
    try:
        from werkzeug.serving import run_simple
        app.logger.info("Starting web server on port 8080")
        run_simple('0.0.0.0', 8080, app, use_reloader=False)
    except OSError as e:
        app.logger.error(f"Error binding to port 8080: {str(e)}")
        app.logger.warning("Trying alternative port 5000")
        try:
            run_simple('0.0.0.0', 5000, app, use_reloader=False)
        except OSError as e2:
            app.logger.critical(f"Failed to bind to port 5000: {str(e2)}")
            app.logger.error("Application failed to start")