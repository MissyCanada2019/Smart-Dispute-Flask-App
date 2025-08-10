from utils.db import db
from datetime import datetime
from enum import Enum as PyEnum

class EvidenceStatus(PyEnum):
    PENDING = 'pending'
    REVIEWED = 'reviewed'
    REJECTED = 'rejected'
    ARCHIVED = 'archived'

class Evidence(db.Model):
    __tablename__ = 'evidence'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    file_hash = db.Column(db.String(64))  # SHA-256 hash for integrity checking

    # Evidence metadata
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    evidence_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(EvidenceStatus), default=EvidenceStatus.PENDING)
    relevance = db.Column(db.String(50), default='unknown')

    # Relationships
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # AI Analysis fields (optional, for future use)
    ai_relevance_score = db.Column(db.Float, nullable=True)
    analyzed_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # When file was uploaded

    def __repr__(self):
        return f'<Evidence {self.id}: {self.original_filename}>'