from utils.db import db
from datetime import datetime
from enum import Enum as PyEnum

class FormStatus(PyEnum):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    REJECTED = 'rejected'

class CourtForm(db.Model):  # Renamed from FormTemplate
    __tablename__ = 'court_forms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    province = db.Column(db.String(100), nullable=False)
    form_type = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    fields = db.relationship('FormField', backref='template', lazy=True)

    def __repr__(self):
        return f'<CourtForm {self.id}: {self.name}>'  # Updated class name

class FormField(db.Model):
    __tablename__ = 'form_fields'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('court_forms.id'), nullable=False)  # Updated foreign key
    field_name = db.Column(db.String(255), nullable=False)
    field_type = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    required = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    options = db.Column(db.JSON)

    def __repr__(self):
        return f'<FormField {self.id}: {self.field_name}>'

class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('court_forms.id'), nullable=False)  # Updated foreign key
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    submission_data = db.Column(db.JSON, nullable=False)
    status = db.Column(db.Enum(FormStatus), default=FormStatus.SUBMITTED)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<FormSubmission {self.id}>'