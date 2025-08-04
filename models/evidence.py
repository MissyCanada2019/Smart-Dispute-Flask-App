from utils.db import db
from datetime import datetime

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
    status = db.Column(db.String(50), default='uploaded')
    relevance = db.Column(db.String(50), default='unknown')

    # Relationships
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Processing results
    extracted_text = db.Column(db.Text)  # OCR or document text extraction
    ai_summary = db.Column(db.Text)  # AI-generated summary
    ai_relevance_score = db.Column(db.Float, default=0.0)  # 0-1 relevance score
    ai_analysis = db.Column(db.JSON)  # Detailed AI analysis results

    # Key information extraction
    identified_dates = db.Column(db.JSON)  # Array of dates found in evidence
    identified_names = db.Column(db.JSON)  # Array of names/parties mentioned
    identified_locations = db.Column(db.JSON)  # Array of locations mentioned
    legal_keywords = db.Column(db.JSON)  # Legal terms and concepts identified

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # When file was uploaded
    processed_at = db.Column(db.DateTime)
    analyzed_at = db.Column(db.DateTime)

    # Security and access
    is_confidential = db.Column(db.Boolean, default=False)
    storage_encrypted = db.Column(db.Boolean, default=False)  # Whether file is encrypted on disk
    access_restrictions = db.Column(db.JSON)  # Who can access this evidence
    last_accessed_at = db.Column(db.DateTime)  # Last time file was accessed
    access_count = db.Column(db.Integer, default=0)  # Number of times file was accessed

    def __repr__(self):
        return f'<Evidence {self.id}: {self.original_filename}>'