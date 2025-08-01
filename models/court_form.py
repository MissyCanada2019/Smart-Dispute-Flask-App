from models import db
from datetime import datetime
from enum import Enum

class FormStatus(Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUBMITTED = "submitted"
    FILED = "filed"

class FieldType(Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    PHONE = "phone"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE = "file"
    SIGNATURE = "signature"
    ADDRESS = "address"
    LEGAL_NAME = "legal_name"

class FormTemplate(db.Model):
    __tablename__ = 'form_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    form_code = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "ON-14A", "BC-F1"
    description = db.Column(db.Text)
    
    # Jurisdiction details
    province = db.Column(db.String(50), nullable=False)  # Province/Territory
    court_type = db.Column(db.String(100))  # Superior Court, Provincial Court, etc.
    case_types = db.Column(db.JSON)  # Array of applicable case types
    
    # Form metadata
    version = db.Column(db.String(20), default="1.0")
    effective_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    
    # Form structure
    form_sections = db.Column(db.JSON)  # Sections and their order
    instructions = db.Column(db.Text)  # General instructions
    filing_instructions = db.Column(db.Text)  # How to file this form
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fields = db.relationship('FormField', backref='template', lazy=True, cascade='all, delete-orphan')
    submissions = db.relationship('FormSubmission', backref='template', lazy=True)
    
    def __repr__(self):
        return f'<FormTemplate {self.form_code}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'form_code': self.form_code,
            'description': self.description,
            'province': self.province,
            'court_type': self.court_type,
            'case_types': self.case_types,
            'version': self.version,
            'is_active': self.is_active,
            'instructions': self.instructions,
            'filing_instructions': self.filing_instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FormField(db.Model):
    __tablename__ = 'form_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('form_templates.id'), nullable=False)
    
    # Field identification
    field_name = db.Column(db.String(100), nullable=False)  # Programmatic name
    label = db.Column(db.String(200), nullable=False)  # Human-readable label
    field_type = db.Column(db.Enum(FieldType), nullable=False)
    
    # Field properties
    section = db.Column(db.String(100))  # Which section this field belongs to
    order_index = db.Column(db.Integer, default=0)  # Order within section
    is_required = db.Column(db.Boolean, default=False)
    placeholder = db.Column(db.String(200))
    help_text = db.Column(db.Text)
    
    # Validation rules
    min_length = db.Column(db.Integer)
    max_length = db.Column(db.Integer)
    pattern = db.Column(db.String(200))  # Regex pattern for validation
    validation_message = db.Column(db.String(200))
    
    # Options for select/radio/checkbox fields
    options = db.Column(db.JSON)  # Array of {value, label} objects
    
    # Auto-fill configuration
    auto_fill_source = db.Column(db.String(100))  # Source for AI auto-fill
    auto_fill_mapping = db.Column(db.JSON)  # How to map data to this field
    
    # Conditional display
    depends_on = db.Column(db.String(100))  # Field name this depends on
    show_when = db.Column(db.JSON)  # Conditions for showing this field
    
    def __repr__(self):
        return f'<FormField {self.field_name}: {self.label}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_name': self.field_name,
            'label': self.label,
            'field_type': self.field_type.value if self.field_type else None,
            'section': self.section,
            'order_index': self.order_index,
            'is_required': self.is_required,
            'placeholder': self.placeholder,
            'help_text': self.help_text,
            'options': self.options,
            'auto_fill_source': self.auto_fill_source
        }

class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('form_templates.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Submission details
    status = db.Column(db.Enum(FormStatus), default=FormStatus.DRAFT)
    submission_data = db.Column(db.JSON)  # All form field values
    
    # AI assistance tracking
    ai_prefilled_fields = db.Column(db.JSON)  # Which fields were auto-filled
    ai_confidence_scores = db.Column(db.JSON)  # Confidence for each auto-filled field
    user_modifications = db.Column(db.JSON)  # Track what user changed
    
    # Processing and filing
    generated_pdf_path = db.Column(db.String(500))
    filing_reference = db.Column(db.String(100))  # Court filing reference number
    filed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    submitted_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<FormSubmission {self.id}: {self.template.form_code}>'
    
    def get_field_value(self, field_name):
        """Get value for a specific field"""
        if self.submission_data and field_name in self.submission_data:
            return self.submission_data[field_name]
        return None
    
    def set_field_value(self, field_name, value):
        """Set value for a specific field"""
        if not self.submission_data:
            self.submission_data = {}
        self.submission_data[field_name] = value
        
    def get_completion_percentage(self):
        """Calculate form completion percentage"""
        if not self.template or not self.template.fields:
            return 0
        
        required_fields = [f for f in self.template.fields if f.is_required]
        if not required_fields:
            return 100
        
        completed_fields = 0
        for field in required_fields:
            value = self.get_field_value(field.field_name)
            if value and str(value).strip():
                completed_fields += 1
        
        return int((completed_fields / len(required_fields)) * 100)
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'case_id': self.case_id,
            'status': self.status.value if self.status else None,
            'completion_percentage': self.get_completion_percentage(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'filing_reference': self.filing_reference
        }