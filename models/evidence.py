from sqlalchemy import Table, Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float, Boolean, MetaData
from datetime import datetime

evidence_metadata = MetaData()

evidence = Table('evidence', metadata,
    Column('id', Integer, primary_key=True),
    Column('filename', String(255), nullable=False),
    Column('original_filename', String(255), nullable=False),
    Column('file_path', String(500), nullable=False),
    Column('file_size', Integer),
    Column('mime_type', String(100)),
    Column('file_hash', String(64)),  # SHA-256 hash for integrity checking
    
    # Evidence metadata
    Column('title', String(200)),
    Column('description', Text),
    Column('evidence_type', String(50), nullable=False),  # Using string instead of Enum
    Column('status', String(50), default='uploaded'),  # Using string instead of Enum
    Column('relevance', String(50), default='unknown'),  # Using string instead of Enum
    
    # Relationships
    Column('case_id', Integer, ForeignKey('cases.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    
    # Processing results
    Column('extracted_text', Text),  # OCR or document text extraction
    Column('ai_summary', Text),  # AI-generated summary
    Column('ai_relevance_score', Float, default=0.0),  # 0-1 relevance score
    Column('ai_analysis', JSON),  # Detailed AI analysis results
    
    # Key information extraction
    Column('identified_dates', JSON),  # Array of dates found in evidence
    Column('identified_names', JSON),  # Array of names/parties mentioned
    Column('identified_locations', JSON),  # Array of locations mentioned
    Column('legal_keywords', JSON),  # Legal terms and concepts identified
    
    # Timestamps
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    Column('uploaded_at', DateTime, default=datetime.utcnow),  # When file was uploaded
    Column('processed_at', DateTime),
    Column('analyzed_at', DateTime),
    
    # Security and access
    Column('is_confidential', Boolean, default=False),
    Column('storage_encrypted', Boolean, default=False),  # Whether file is encrypted on disk
    Column('access_restrictions', JSON),  # Who can access this evidence
    Column('last_accessed_at', DateTime),  # Last time file was accessed
    Column('access_count', Integer, default=0)  # Number of times file was accessed
)

# Helper class for evidence operations
class Evidence:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.filename = kwargs.get('filename')
        self.original_filename = kwargs.get('original_filename')
        self.file_path = kwargs.get('file_path')
        self.file_size = kwargs.get('file_size')
        self.mime_type = kwargs.get('mime_type')
        self.file_hash = kwargs.get('file_hash')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.evidence_type = kwargs.get('evidence_type')
        self.status = kwargs.get('status', 'uploaded')
        self.relevance = kwargs.get('relevance', 'unknown')
        self.case_id = kwargs.get('case_id')
        self.user_id = kwargs.get('user_id')
        self.extracted_text = kwargs.get('extracted_text')
        self.ai_summary = kwargs.get('ai_summary')
        self.ai_relevance_score = kwargs.get('ai_relevance_score', 0.0)
        self.ai_analysis = kwargs.get('ai_analysis')
        self.identified_dates = kwargs.get('identified_dates')
        self.identified_names = kwargs.get('identified_names')
        self.identified_locations = kwargs.get('identified_locations')
        self.legal_keywords = kwargs.get('legal_keywords')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.uploaded_at = kwargs.get('uploaded_at')
        self.processed_at = kwargs.get('processed_at')
        self.analyzed_at = kwargs.get('analyzed_at')
        self.is_confidential = kwargs.get('is_confidential', False)
        self.storage_encrypted = kwargs.get('storage_encrypted', False)
        self.access_restrictions = kwargs.get('access_restrictions')
        self.last_accessed_at = kwargs.get('last_accessed_at')
        self.access_count = kwargs.get('access_count', 0)
    
    def __repr__(self):
        return f'<Evidence {self.id}: {self.original_filename}>'