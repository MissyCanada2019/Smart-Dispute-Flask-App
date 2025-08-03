from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Date, Float, JSON, MetaData
from datetime import datetime

case_metadata = MetaData()

cases = Table('cases', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(200), nullable=False),
    Column('description', Text),
    Column('case_number', String(50), unique=True),
    Column('user_id', Integer, nullable=False),
    Column('case_type', String(50), nullable=False),
    Column('status', String(50), default='draft'),
    Column('priority', String(50), default='medium'),
    Column('province', String(50), nullable=False),
    Column('jurisdiction', String(100)),
    Column('court_name', String(200)),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    Column('incident_date', Date),
    Column('filing_deadline', Date),
    Column('hearing_date', DateTime),
    Column('merit_score', Float, default=0.0),
    Column('merit_analysis', Text),
    Column('strength_indicators', JSON),
    Column('weakness_indicators', JSON),
    Column('case_metadata', JSON),
    Column('current_stage', String(100)),
    Column('completion_percentage', Integer, default=0)
)

# Helper class for case operations
class Case:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.case_number = kwargs.get('case_number')
        self.user_id = kwargs.get('user_id')
        self.case_type = kwargs.get('case_type')
        self.status = kwargs.get('status')
        self.priority = kwargs.get('priority')
        self.province = kwargs.get('province')
        self.jurisdiction = kwargs.get('jurisdiction')
        self.court_name = kwargs.get('court_name')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.incident_date = kwargs.get('incident_date')
        self.filing_deadline = kwargs.get('filing_deadline')
        self.hearing_date = kwargs.get('hearing_date')
        self.merit_score = kwargs.get('merit_score')
        self.merit_analysis = kwargs.get('merit_analysis')
        self.strength_indicators = kwargs.get('strength_indicators')
        self.weakness_indicators = kwargs.get('weakness_indicators')
        self.case_metadata = kwargs.get('case_metadata')
        self.current_stage = kwargs.get('current_stage')
        self.completion_percentage = kwargs.get('completion_percentage')
    
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
            'completion_percentage': self.completion_percentage
        }