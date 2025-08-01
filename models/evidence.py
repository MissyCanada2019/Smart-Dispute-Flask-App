from models import db
from datetime import datetime
from enum import Enum
import os

class EvidenceType(Enum):
    DOCUMENT = "document"
    IMAGE = "image" 
    AUDIO = "audio"
    VIDEO = "video"
    EMAIL = "email"
    TEXT = "text"
    OTHER = "other"

class EvidenceStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ANALYZED = "analyzed"
    ERROR = "error"

class EvidenceRelevance(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

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
    evidence_type = db.Column(db.Enum(EvidenceType), nullable=False)
    status = db.Column(db.Enum(EvidenceStatus), default=EvidenceStatus.UPLOADED)
    relevance = db.Column(db.Enum(EvidenceRelevance), default=EvidenceRelevance.UNKNOWN)
    
    # Relationships
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
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
    
    @property
    def file_extension(self):
        """Get file extension from original filename"""
        return os.path.splitext(self.original_filename)[1].lower()
    
    @property
    def is_image(self):
        """Check if evidence is an image file"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        return self.file_extension in image_extensions
    
    @property
    def is_pdf(self):
        """Check if evidence is a PDF file"""
        return self.file_extension == '.pdf'
    
    @property
    def is_document(self):
        """Check if evidence is a document file"""
        doc_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
        return self.file_extension in doc_extensions
    
    def get_processing_status_message(self):
        """Get human-readable processing status"""
        status_messages = {
            EvidenceStatus.UPLOADED: "File uploaded successfully",
            EvidenceStatus.PROCESSING: "Processing file content...",
            EvidenceStatus.PROCESSED: "File content extracted",
            EvidenceStatus.ANALYZED: "AI analysis completed",
            EvidenceStatus.ERROR: "Error processing file"
        }
        return status_messages.get(self.status, "Unknown status")
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_hash': self.file_hash,
            'title': self.title,
            'description': self.description,
            'evidence_type': self.evidence_type.value if self.evidence_type else None,
            'status': self.status.value if self.status else None,
            'relevance': self.relevance.value if self.relevance else None,
            'ai_relevance_score': self.ai_relevance_score,
            'ai_summary': self.ai_summary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            'is_confidential': self.is_confidential,
            'storage_encrypted': self.storage_encrypted,
            'access_count': self.access_count,
            'is_image': self.is_image,
            'is_pdf': self.is_pdf,
            'is_document': self.is_document,
            'processing_status_message': self.get_processing_status_message()
        }
    
    def update_access_stats(self):
        """Update access statistics when file is accessed"""
        self.last_accessed_at = datetime.utcnow()
        self.access_count = (self.access_count or 0) + 1
        db.session.commit()
    
    def get_security_level(self):
        """Get security level description"""
        if self.storage_encrypted and self.is_confidential:
            return "High Security (Encrypted & Confidential)"
        elif self.storage_encrypted:
            return "Medium Security (Encrypted)"
        elif self.is_confidential:
            return "Medium Security (Confidential)"
        else:
            return "Standard Security"