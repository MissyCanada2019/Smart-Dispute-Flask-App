from flask import Flask
from flask_login import LoginManager
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from utils.error_handling import register_error_handlers, HealthCheck
from utils.db import db

def create_app():
    # Load environment variables based on deployment environment
    if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
        load_dotenv('.env.production')
    else:
        load_dotenv('.env.development')

    app = Flask(__name__)
    
    # Use environment variable for secret key, with fallback
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database configuration with Railway support
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Railway PostgreSQL
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Local SQLite fallback
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
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
    
    # Health check route
    @app.route('/health')
    def health_check():
        return HealthCheck.get_health_status()

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)