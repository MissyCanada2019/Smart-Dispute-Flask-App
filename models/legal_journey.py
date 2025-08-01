from models import db
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
    
    # Journey metadata
    journey_type = db.Column(db.String(100), nullable=False)  # e.g., "child_protection_response"
    current_stage_id = db.Column(db.Integer, db.ForeignKey('journey_stages.id'))
    current_step_id = db.Column(db.Integer, db.ForeignKey('journey_steps.id'))
    
    # Progress tracking
    total_stages = db.Column(db.Integer, default=0)
    completed_stages = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=0)
    completed_steps = db.Column(db.Integer, default=0)
    overall_progress = db.Column(db.Integer, default=0)  # Percentage
    
    # Timeline
    estimated_completion_date = db.Column(db.Date)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # AI guidance
    ai_recommendations = db.Column(db.JSON)  # Current AI suggestions
    risk_factors = db.Column(db.JSON)  # Identified risks and warnings
    next_actions = db.Column(db.JSON)  # Recommended next steps
    
    # User customization
    user_notes = db.Column(db.Text)
    custom_deadlines = db.Column(db.JSON)  # User-set custom deadlines
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stages = db.relationship('JourneyStage', backref='journey', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LegalJourney {self.id}: {self.journey_type}>'
    
    def calculate_progress(self):
        """Calculate and update overall progress"""
        if self.total_steps == 0:
            return 0
        
        progress = int((self.completed_steps / self.total_steps) * 100)
        self.overall_progress = progress
        return progress
    
    def get_current_stage(self):
        """Get the current active stage"""
        return JourneyStage.query.get(self.current_stage_id) if self.current_stage_id else None
    
    def get_current_step(self):
        """Get the current active step"""
        return JourneyStep.query.get(self.current_step_id) if self.current_step_id else None
    
    def get_upcoming_deadlines(self, days_ahead=30):
        """Get upcoming deadlines within specified days"""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        return JourneyStep.query.join(JourneyStage).filter(
            JourneyStage.journey_id == self.id,
            JourneyStep.deadline.isnot(None),
            JourneyStep.deadline <= cutoff_date,
            JourneyStep.status != StageStatus.COMPLETED
        ).order_by(JourneyStep.deadline).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'journey_type': self.journey_type,
            'total_stages': self.total_stages,
            'completed_stages': self.completed_stages,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'overall_progress': self.overall_progress,
            'estimated_completion_date': self.estimated_completion_date.isoformat() if self.estimated_completion_date else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'ai_recommendations': self.ai_recommendations,
            'next_actions': self.next_actions
        }

class JourneyStage(db.Model):
    __tablename__ = 'journey_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    journey_id = db.Column(db.Integer, db.ForeignKey('legal_journeys.id'), nullable=False)
    
    # Stage details
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_order = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(StageStatus), default=StageStatus.NOT_STARTED)
    
    # Prerequisites and dependencies
    prerequisites = db.Column(db.JSON)  # Required previous stages
    dependencies = db.Column(db.JSON)  # External dependencies
    
    # Timeline
    estimated_duration_days = db.Column(db.Integer)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Progress tracking
    total_steps = db.Column(db.Integer, default=0)
    completed_steps = db.Column(db.Integer, default=0)
    
    # Guidance
    instructions = db.Column(db.Text)
    tips = db.Column(db.JSON)  # Array of helpful tips
    common_pitfalls = db.Column(db.JSON)  # Array of things to avoid
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    steps = db.relationship('JourneyStep', backref='stage', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<JourneyStage {self.stage_order}: {self.name}>'
    
    def calculate_progress(self):
        """Calculate progress for this stage"""
        if self.total_steps == 0:
            return 0
        return int((self.completed_steps / self.total_steps) * 100)
    
    def can_start(self):
        """Check if this stage can be started based on prerequisites"""
        if not self.prerequisites:
            return True
        
        # Check if all prerequisite stages are completed
        for prereq_id in self.prerequisites:
            prereq_stage = JourneyStage.query.get(prereq_id)
            if not prereq_stage or prereq_stage.status != StageStatus.COMPLETED:
                return False
        
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage_order': self.stage_order,
            'status': self.status.value if self.status else None,
            'progress': self.calculate_progress(),
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'can_start': self.can_start(),
            'instructions': self.instructions,
            'tips': self.tips
        }

class JourneyStep(db.Model):
    __tablename__ = 'journey_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(db.Integer, db.ForeignKey('journey_stages.id'), nullable=False)
    
    # Step details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    step_order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.Enum(StepType), nullable=False)
    status = db.Column(db.Enum(StageStatus), default=StageStatus.NOT_STARTED)
    
    # Requirements
    is_mandatory = db.Column(db.Boolean, default=True)
    prerequisites = db.Column(db.JSON)  # Required previous steps
    
    # Timeline and urgency
    estimated_duration_hours = db.Column(db.Integer)
    deadline = db.Column(db.DateTime)
    urgency = db.Column(db.Enum(UrgencyLevel), default=UrgencyLevel.MEDIUM)
    
    # Progress tracking
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Linked resources
    form_template_id = db.Column(db.Integer, db.ForeignKey('form_templates.id'))
    evidence_requirements = db.Column(db.JSON)  # What evidence is needed
    external_links = db.Column(db.JSON)  # Helpful external resources
    
    # Guidance and instructions
    detailed_instructions = db.Column(db.Text)
    checklist_items = db.Column(db.JSON)  # Sub-tasks within this step
    success_criteria = db.Column(db.JSON)  # How to know step is complete
    
    # AI assistance
    ai_assistance_available = db.Column(db.Boolean, default=False)
    ai_prompt_template = db.Column(db.Text)  # Template for AI assistance
    
    # User interaction
    user_notes = db.Column(db.Text)
    user_questions = db.Column(db.JSON)  # Questions user has asked
    completion_confirmation = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JourneyStep {self.step_order}: {self.title}>'
    
    def can_start(self):
        """Check if this step can be started"""
        if not self.prerequisites:
            return True
        
        # Check if all prerequisite steps are completed
        for prereq_id in self.prerequisites:
            prereq_step = JourneyStep.query.get(prereq_id)
            if not prereq_step or prereq_step.status != StageStatus.COMPLETED:
                return False
        
        return True
    
    def is_overdue(self):
        """Check if step is overdue"""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline and self.status != StageStatus.COMPLETED
    
    def days_until_deadline(self):
        """Get days until deadline"""
        if not self.deadline:
            return None
        delta = self.deadline - datetime.utcnow()
        return delta.days
    
    def mark_completed(self):
        """Mark step as completed and update timestamps"""
        self.status = StageStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.completion_confirmation = True
        
        # Update stage progress
        self.stage.completed_steps += 1
        
        # Update journey progress
        journey = self.stage.journey
        journey.completed_steps += 1
        journey.calculate_progress()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'step_order': self.step_order,
            'step_type': self.step_type.value if self.step_type else None,
            'status': self.status.value if self.status else None,
            'is_mandatory': self.is_mandatory,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'urgency': self.urgency.value if self.urgency else None,
            'can_start': self.can_start(),
            'is_overdue': self.is_overdue(),
            'days_until_deadline': self.days_until_deadline(),
            'detailed_instructions': self.detailed_instructions,
            'checklist_items': self.checklist_items,
            'ai_assistance_available': self.ai_assistance_available,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }