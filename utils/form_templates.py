"""
Court Form Template Management System
Handles Canadian provincial court form templates and field definitions
"""

from typing import Dict, List, Any, Optional
from models.court_form import FormTemplate, FormField  # Removed FieldType
from utils.db import Session  # Import Session from utils.db
import json

# Canadian provinces and territories
CANADIAN_PROVINCES = {
    'AB': 'Alberta',
    'BC': 'British Columbia', 
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'NS': 'Nova Scotia',
    'ON': 'Ontario',
    'PE': 'Prince Edward Island',
    'QC': 'Quebec',
    'SK': 'Saskatchewan',
    'NT': 'Northwest Territories',
    'NU': 'Nunavut',
    'YT': 'Yukon'
}

# Standard form field definitions that are common across provinces
STANDARD_FIELDS = {
    'applicant_name': {
        'label': 'Full Name of Applicant',
        'type': 'text',  # Changed from FieldType.TEXT to string
        'required': True,
        'placeholder': 'Enter your full legal name',
        'validation_rules': {'min_length': 2, 'max_length': 100}
    },
    'applicant_address': {
        'label': 'Address',
        'type': 'textarea',  # Changed from FieldType.TEXTAREA
        'required': True,
        'placeholder': 'Enter your complete address',
        'validation_rules': {'min_length': 10, 'max_length': 200}
    },
    'applicant_phone': {
        'label': 'Phone Number',
        'type': 'text',  # Changed from FieldType.TEXT
        'required': True,
        'placeholder': '(xxx) xxx-xxxx',
        'validation_rules': {'pattern': r'^\(\d{3}\)\s\d{3}-\d{4}$'}
    },
    'applicant_email': {
        'label': 'Email Address',
        'type': 'email',  # Changed from FieldType.EMAIL
        'required': False,
        'placeholder': 'your.email@example.com'
    },
    'case_number': {
        'label': 'Court File Number',
        'type': 'text',  # Changed from FieldType.TEXT
        'required': True,
        'placeholder': 'Enter court file number',
        'validation_rules': {'pattern': r'^[A-Za-z0-9-]+$'}
    }
    # ... other fields would be updated similarly ...
}

# FormTemplateManager class would be implemented using string-based field types
class FormTemplateManager:
    @staticmethod
    def create_template(province_code: str, form_data: Dict[str, Any]) -> FormTemplate:
        """Create a new form template for a province"""
        # Implementation using string-based field types
        pass
    
    @staticmethod
    def get_templates_for_province(province_code: str) -> List[FormTemplate]:
        """Get all active templates for a province"""
        # Implementation using string-based field types
        pass
    
    # Other methods would be implemented similarly

def get_form_suggestions_for_case(case: 'Case') -> List[FormTemplate]:
    """Get suggested form templates for a given case"""
    # This is a simplified example; implement your own logic
    session = Session()
    try:
        # Query templates matching the case's province
        stmt = session.query(FormTemplate).filter_by(province=case.province)
        templates = stmt.all()
        return templates
    finally:
        session.close()