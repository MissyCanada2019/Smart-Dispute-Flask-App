from utils.db import db
from datetime import datetime, timedelta
from enum import Enum

class StageStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"

class StepType(Enum):
    INFORMATION_GATHERING = "information_gathering"
    EVIDENCE_COLLECTION = "evidence_collection"
    FORM_COMPLETION = "form_completion"
    DOCUMENT_REVIEW = "document_review"
    FILING = "filing"
    HEARING_PREPARATION = "hearing_preparation"
    FOLLOW_UP = "follow_up"
    DEADLINE = "deadline"

class UrgencyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LegalJourney(db.Model):
    __tablename__ = 'legal_journeys'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    
    journey_type = db.Column(db.String(100), nullable=False)
    current_stage_id = db.Column(db.Integer, db.ForeignKey('journey_stages.id'))
    current_step_id = db.Column(db.Integer, db.ForeignKey('journey_steps.id'))
    
    total_stages = db.Column(db.Integer, default=0)
    completed_stages = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=0)
    completed_steps = db.Column(db.Integer, default=0)
    overall_progress = db.Column(db.Integer, default=0)
    
    estimated_completion_date = db.Column(db.Date)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    ai_recommendations = db.Column(db.JSON)
    risk_factors = db.Column(db.JSON)
    next_actions = db.Column(db.JSON)
    
    user_notes = db.Column(db.Text)
    custom_deadlines = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    stages = db.relationship('JourneyStage', backref='journey', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LegalJourney {self.id}: {self.journey_type}>'

class JourneyStage(db.Model):
    __tablename__ = 'journey_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    journey_id = db.Column(db.Integer, db.ForeignKey('legal_journeys.id'), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_order = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(StageStatus), default=StageStatus.NOT_STARTED)
    
    prerequisites = db.Column(db.JSON)
    dependencies = db.Column(db.JSON)
    
    estimated_duration_days = db.Column(db.Integer)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    total_steps = db.Column(db.Integer, default=0)
    completed_steps = db.Column(db.Integer, default=0)
    
    instructions = db.Column(db.Text)
    tips = db.Column(db.JSON)
    common_pitfalls = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    steps = db.relationship('JourneyStep', backref='stage', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<JourneyStage {self.stage_order}: {self.name}>'

class JourneyStep(db.Model):
    __tablename__ = 'journey_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(db.Integer, db.ForeignKey('journey_stages.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    step_order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.Enum(StepType), nullable=False)
    status = db.Column(db.Enum(StageStatus), default=StageStatus.NOT_STARTED)
    
    is_mandatory = db.Column(db.Boolean, default=True)
    prerequisites = db.Column(db.JSON)
    
    estimated_duration_hours = db.Column(db.Integer)
    deadline = db.Column(db.DateTime)
    urgency = db.Column(db.Enum(UrgencyLevel), default=UrgencyLevel.MEDIUM)
    
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    form_template_id = db.Column(db.Integer, db.ForeignKey('form_templates.id'))
    evidence_requirements = db.Column(db.JSON)
    external_links = db.Column(db.JSON)
    
    detailed_instructions = db.Column(db.Text)
    checklist_items = db.Column(db.JSON)
    success_criteria = db.Column(db.JSON)
    
    ai_assistance_available = db.Column(db.Boolean, default=False)
    ai_prompt_template = db.Column(db.Text)
    
    user_notes = db.Column(db.Text)
    user_questions = db.Column(db.JSON)
    completion_confirmation = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JourneyStep {self.step_order}: {self.title}>'