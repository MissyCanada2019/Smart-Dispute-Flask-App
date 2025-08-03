from sqlalchemy import Table, Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, MetaData
from datetime import datetime

metadata = MetaData()

form_templates = Table('form_templates', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(200), nullable=False),
    Column('form_code', String(50), unique=True, nullable=False),
    Column('description', Text),
    Column('province', String(50), nullable=False),
    Column('court_type', String(100)),
    Column('case_types', JSON),
    Column('version', String(20), default="1.0"),
    Column('effective_date', DateTime),
    Column('is_active', Boolean, default=True),
    Column('form_sections', JSON),
    Column('instructions', Text),
    Column('filing_instructions', Text),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

form_fields = Table('form_fields', metadata,
    Column('id', Integer, primary_key=True),
    Column('template_id', Integer, ForeignKey('form_templates.id'), nullable=False),
    Column('field_name', String(100), nullable=False),
    Column('label', String(200), nullable=False),
    Column('field_type', String(50), nullable=False),
    Column('section', String(100)),
    Column('order_index', Integer, default=0),
    Column('is_required', Boolean, default=False),
    Column('placeholder', String(200)),
    Column('help_text', Text),
    Column('min_length', Integer),
    Column('max_length', Integer),
    Column('pattern', String(200)),
    Column('validation_message', String(200)),
    Column('options', JSON)
)

form_submissions = Table('form_submissions', metadata,
    Column('id', Integer, primary_key=True),
    Column('template_id', Integer, ForeignKey('form_templates.id'), nullable=False),
    Column('case_id', Integer, ForeignKey('cases.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('status', String(50), default='draft'),
    Column('submitted_data', JSON, nullable=False),
    Column('submitted_at', DateTime),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

# Helper classes for form operations
class FormTemplate:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.form_code = kwargs.get('form_code')
        self.description = kwargs.get('description')
        self.province = kwargs.get('province')
        self.court_type = kwargs.get('court_type')
        self.case_types = kwargs.get('case_types')
        self.version = kwargs.get('version')
        self.is_active = kwargs.get('is_active', True)
        self.form_sections = kwargs.get('form_sections')
        self.instructions = kwargs.get('instructions')
        self.filing_instructions = kwargs.get('filing_instructions')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
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

class FormField:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.template_id = kwargs.get('template_id')
        self.field_name = kwargs.get('field_name')
        self.label = kwargs.get('label')
        self.field_type = kwargs.get('field_type')
        self.section = kwargs.get('section')
        self.order_index = kwargs.get('order_index', 0)
        self.is_required = kwargs.get('is_required', False)
        self.placeholder = kwargs.get('placeholder')
        self.help_text = kwargs.get('help_text')
        self.min_length = kwargs.get('min_length')
        self.max_length = kwargs.get('max_length')
        self.pattern = kwargs.get('pattern')
        self.validation_message = kwargs.get('validation_message')
        self.options = kwargs.get('options')
    
    def __repr__(self):
        return f'<FormField {self.field_name} in Template {self.template_id}>'

class FormSubmission:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.template_id = kwargs.get('template_id')
        self.case_id = kwargs.get('case_id')
        self.user_id = kwargs.get('user_id')
        self.status = kwargs.get('status', 'draft')
        self.submitted_data = kwargs.get('submitted_data')
        self.submitted_at = kwargs.get('submitted_at')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    def __repr__(self):
        return f'<FormSubmission {self.id} for Template {self.template_id}>'