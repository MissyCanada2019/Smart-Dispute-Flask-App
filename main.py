from flask import Flask, render_template
from models import db
from flask_login import LoginManager
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
import os
from dotenv import load_dotenv
from utils.error_handling import register_error_handlers, HealthCheck

# Load environment variables
load_dotenv()

def create_app():
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
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
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
    @app.route('/')
    def index():
        return render_template('onboarding/welcome.html')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check route
    @app.route('/health')
    def health_check():
        return HealthCheck.get_health_status()

    with app.app_context():
        db.create_all()
        
        # Auto-initialize database if empty (fixes Railway deployment)
        try:
            from models.user import User
            if User.query.count() == 0:
                print("Auto-initializing database for first deployment...")
                
                # Create admin user
                admin_user = User(
                    email='admin@smartdispute.ca',
                    is_admin=True,
                    is_active=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                
                # Create test user
                test_user = User(
                    email='test@smartdispute.ca',
                    is_admin=False,
                    is_active=True
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                
                db.session.commit()
                print("Database auto-initialized with default users")
                print("Admin: admin@smartdispute.ca / admin123")
                print("Test: test@smartdispute.ca / test123")
        except Exception as e:
            print(f"Auto-initialization failed: {str(e)}")

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
