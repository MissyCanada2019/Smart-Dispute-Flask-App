from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from models.user import User
from models.case import Case
from models.evidence import Evidence
from models.court_form import FormTemplate, FormField, FormSubmission
from models.legal_journey import LegalJourney, JourneyStage, JourneyStep
from models.notification import Notification, NotificationPreference
