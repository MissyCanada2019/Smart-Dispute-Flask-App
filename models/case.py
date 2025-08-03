from utils.db import db  # Import centralized db instance
from sqlalchemy import Enum
from datetime import datetime
from enum import Enum as PyEnum

class CaseType(PyEnum):
    CHILD_PROTECTION = "child_protection"
    FAMILY_COURT = "family_court"
    PARENTAL_RIGHTS = "parental_rights"
    TRIBUNAL = "tribunal"
    OTHER = "other"

class CaseStatus(PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    AWAITING_HEARING = "awaiting_hearing"
    COMPLETED = "completed"
    CLOSED = "closed"

class CasePriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Case(db.Model):  # Inherit from db.Model
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    case_number = db.Column(db.String(50), unique=True)
    
    # User relationship
    user_id = db.Column(db.Integer, nullable=False)
    
    # Case details
    case_type = db.Column(db.Enum(CaseType), nullable=False)
    status = db.Column(db.Enum(CaseStatus), default=CaseStatus.DRAFT)
    priority = db.Column(db.Enum(CasePriority), default=CasePriority.MEDIUM)
    
    # Location (Canadian province/territory)
    province = db.Column(db.String(50), nullable=False)
    jurisdiction = db.Column(db.String(100))
    court_name = db.Column(db.String(200))
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    incident_date = db.Column(db.Date)
    filing_deadline = db.Column(db.Date)
    hearing_date = db.Column(db.DateTime)
    
    # Merit scoring
    merit_score = db.Column(db.Float, default=0.0)
    merit_analysis = db.Column(db.Text)
    strength_indicators = db.Column(db.JSON)
    weakness_indicators = db.Column(db.JSON)
    
    # Additional case data
    case_metadata = db.Column(db.JSON)
    
    # Legal journey tracking
    current_stage = db.Column(db.String(100))
    completion_percentage = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Case {self.case_number}: {self.title}>'
    
    @property
    def metadata(self):
        return self.case_metadata
    
    @metadata.setter
    def metadata(self, value):
        self.case_metadata = value
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'case_number': self.case_number,
            'case_type': self.case_type.value if self.case_type else None,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'province': self.province,
            'jurisdiction': self.jurisdiction,
            'court_name': self.court_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'filing_deadline': self.filing_deadline.isoformat() if self.filing_deadline else None,
            'hearing_date': self.hearing_date.isoformat() if self.hearing_date else None,
            'merit_score': self.merit_score,
            'current_stage': self.current_stage,
            'completion_percentage': self.completion_percentage
        }