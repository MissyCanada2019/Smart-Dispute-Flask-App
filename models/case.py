from utils.db import db
from datetime import datetime
from enum import Enum

class CaseType(Enum):
    CIVIL = 'Civil'
    CRIMINAL = 'Criminal'
    FAMILY = 'Family'
    LABOR = 'Labor'
    COMMERCIAL = 'Commercial'
    ADMINISTRATIVE = 'Administrative'
    CONSTITUTIONAL = 'Constitutional'
    OTHER = 'Other'

class CaseStatus(Enum):
    DRAFT = 'draft'
    FILED = 'filed'
    IN_PROGRESS = 'in_progress'
    CLOSED = 'closed'
    APPEALED = 'appealed'
    SETTLED = 'settled'

class Case(db.Model):
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    case_number = db.Column(db.String(50), unique=True)
    user_id = db.Column(db.Integer, nullable=False)
    case_type = db.Column(db.Enum(CaseType), nullable=False)
    status = db.Column(db.Enum(CaseStatus), default=CaseStatus.DRAFT)
    priority = db.Column(db.String(50), default='medium')
    province = db.Column(db.String(50), nullable=False)
    jurisdiction = db.Column(db.String(100))
    court_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    incident_date = db.Column(db.Date)
    filing_deadline = db.Column(db.Date)
    hearing_date = db.Column(db.DateTime)
    merit_score = db.Column(db.Float, default=0.0)
    merit_analysis = db.Column(db.Text)
    strength_indicators = db.Column(db.JSON)
    weakness_indicators = db.Column(db.JSON)
    metadata_json = db.Column(db.JSON)
    current_stage = db.Column(db.String(100))
    completion_percentage = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Case {self.case_number}: {self.title}>'

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
            'completion_percentage': self.completion_percentage,
            'metadata': self.metadata_json
        }