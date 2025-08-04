from utils.db import db
from datetime import datetime

class FormTemplate(db.Model):
    __tablename__ = 'form_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    form_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    province = db.Column(db.String(50), nullable=False)
    court_type = db.Column(db.String(100))
    case_types = db.Column(db.JSON)
    version = db.Column(db.String(20), default="1.0")
    effective_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    form_sections = db.Column(db.JSON)
    instructions = db.Column(db.Text)
    filing_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fields = db.relationship('FormField', backref='template', lazy=True)

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
    field_name = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(200), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(100))
    order_index = db.Column(db.Integer, default=0)
    is_required = db.Column(db.Boolean, default=False)
    placeholder = db.Column(db.String(200))
    help_text = db.Column(db.Text)
    min_length = db.Column(db.Integer)
    max_length = db.Column(db.Integer)
    pattern = db.Column(db.String(200))
    validation_message = db.Column(db.String(200))
    options = db.Column(db.JSON)

    def __repr__(self):
        return f'<FormField {self.field_name} in Template {self.template_id}>'

class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('form_templates.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='draft')
    submitted_data = db.Column(db.JSON, nullable=False)
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<FormSubmission {self.id} for Template {self.template_id}>'