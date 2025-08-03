from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Import all models to ensure they are registered with SQLAlchemy
from models.case import Case
from models.evidence import Evidence
from models.court_form import FormTemplate, FormField, FormSubmission
from models.legal_journey import LegalJourney, JourneyStage, JourneyStep
from models.notification import Notification, NotificationPreference
