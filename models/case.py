from models import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, JSON, ForeignKey
from datetime import datetime
from enum import Enum

class CaseType(Enum):
    CHILD_PROTECTION = "child_protection"
    FAMILY_COURT = "family_court"
    PARENTAL_RIGHTS = "parental_rights"
    TRIBUNAL = "tribunal"
    OTHER = "other"

class CaseStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    AWAITING_HEARING = "awaiting_hearing"
    COMPLETED = "completed"
    CLOSED = "closed"

class CasePriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Case(Base):
    __tablename__ = 'cases'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    case_number = Column(String(50), unique=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Case details
    case_type = Column(String(50), nullable=False)  # Using String instead of Enum for simplicity
    status = Column(String(50), default=CaseStatus.DRAFT.value)
    priority = Column(String(50), default=CasePriority.MEDIUM.value)
    
    # Location (Canadian province/territory)
    province = Column(String(50), nullable=False)
    jurisdiction = Column(String(100))
    court_name = Column(String(200))
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    incident_date = Column(Date)
    filing_deadline = Column(Date)
    hearing_date = Column(DateTime)
    
    # Merit scoring
    merit_score = Column(Float, default=0.0)
    merit_analysis = Column(Text)
    strength_indicators = Column(JSON)  # Store array of strength factors
    weakness_indicators = Column(JSON)  # Store array of weakness factors
    
    # Additional case data
    case_metadata = Column(JSON)  # Additional case context data
    
    # Legal journey tracking
    current_stage = Column(String(100))
    completion_percentage = Column(Integer, default=0)
    
    def __repr__(self):
        return f'<Case {self.case_number}: {self.title}>'
    
    @property
    def metadata(self):
        """Backwards compatibility property for case_metadata"""
        return self.case_metadata
    
    @metadata.setter
    def metadata(self, value):
        """Backwards compatibility setter for case_metadata"""
        self.case_metadata = value
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'case_number': self.case_number,
            'case_type': self.case_type,
            'status': self.status,
            'priority': self.priority,
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