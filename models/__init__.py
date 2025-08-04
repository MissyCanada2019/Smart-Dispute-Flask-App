from .user import User
from .case import Case
from .court_form import FormTemplate, FormField, FormSubmission
from .evidence import Evidence
from .legal_journey import LegalJourney
from .notification import Notification

# Explicitly import and export db for better accessibility
from utils.db import db

# Explicitly import db for better accessibility
from utils.db import db
