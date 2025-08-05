from main import create_app
app = create_app()

with app.app_context():
    from utils.db import db
    # Import all models to ensure they're registered with SQLAlchemy
    from models.court_form import CourtForm
    from models.legal_journey import LegalJourney, JourneyStep
    from models.case import Case
    from models.evidence import Evidence
    from models.user import User
    from models.notification import Notification, NotificationType
    from models.payment import Payment, PaymentStatus
    
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")