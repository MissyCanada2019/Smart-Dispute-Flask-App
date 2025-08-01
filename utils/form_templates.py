"""
Court Form Template Management System
Handles Canadian provincial court form templates and field definitions
"""

from typing import Dict, List, Any, Optional
from models.court_form import FormTemplate, FormField, FieldType
from models import db
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
        'type': FieldType.TEXT,
        'required': True,
        'placeholder': 'Enter your full legal name',
        'validation_rules': {'min_length': 2, 'max_length': 100}
    },
    'applicant_address': {
        'label': 'Address',
        'type': FieldType.TEXTAREA,
        'required': True,
        'placeholder': 'Enter your complete address',
        'validation_rules': {'min_length': 10, 'max_length': 200}
    },
    'applicant_phone': {
        'label': 'Phone Number',
        'type': FieldType.TEXT,
        'required': True,
        'placeholder': '(xxx) xxx-xxxx',
        'validation_rules': {'pattern': r'^\(\d{3}\)\s\d{3}-\d{4}$'}
    },
    'applicant_email': {
        'label': 'Email Address',
        'type': FieldType.EMAIL,
        'required': False,
        'placeholder': 'your.email@example.com'
    },
    'case_number': {
        'label': 'Court File Number',
        'type': FieldType.TEXT,
        'required': False,
        'placeholder': 'Enter court file number if available'
    },
    'court_location': {
        'label': 'Court Location',
        'type': FieldType.TEXT,
        'required': True,
        'placeholder': 'City where court is located'
    },
    'matter_description': {
        'label': 'Description of Matter',
        'type': FieldType.TEXTAREA,
        'required': True,
        'placeholder': 'Briefly describe the legal matter',
        'validation_rules': {'min_length': 20, 'max_length': 1000}
    },
    'date_of_incident': {
        'label': 'Date of Incident/Event',
        'type': FieldType.DATE,
        'required': False
    },
    'relief_sought': {
        'label': 'Relief Sought',
        'type': FieldType.TEXTAREA,
        'required': True,
        'placeholder': 'Describe what you are asking the court to do',
        'validation_rules': {'min_length': 10, 'max_length': 500}
    }
}

# Province-specific form templates
PROVINCIAL_FORMS = {
    'ON': {
        'family_court_application': {
            'name': 'Application (General) - Form 8',
            'description': 'General application form for Ontario Family Court',
            'category': 'family_court',
            'fields': [
                'applicant_name', 'applicant_address', 'applicant_phone', 'applicant_email',
                'case_number', 'court_location', 'matter_description', 'relief_sought',
                {
                    'name': 'children_involved',
                    'label': 'Are there children involved?',
                    'type': FieldType.SELECT,
                    'required': True,
                    'options': ['Yes', 'No']
                },
                {
                    'name': 'children_details',
                    'label': 'Children Details (if applicable)',
                    'type': FieldType.TEXTAREA,
                    'required': False,
                    'placeholder': 'Names, ages, and current living arrangements of children',
                    'conditional_field': 'children_involved',
                    'conditional_value': 'Yes'
                }
            ]
        },
        'child_protection_application': {
            'name': 'Application - Child Protection',
            'description': 'Application form for child protection matters in Ontario',
            'category': 'child_protection',
            'fields': [
                'applicant_name', 'applicant_address', 'applicant_phone', 'applicant_email',
                'case_number', 'court_location', 'matter_description', 'date_of_incident',
                {
                    'name': 'child_name',
                    'label': 'Name of Child',
                    'type': FieldType.TEXT,
                    'required': True,
                    'placeholder': 'Full legal name of child'
                },
                {
                    'name': 'child_dob',
                    'label': 'Child Date of Birth',
                    'type': FieldType.DATE,
                    'required': True
                },
                {
                    'name': 'current_guardian',
                    'label': 'Current Guardian/Caregiver',
                    'type': FieldType.TEXT,
                    'required': True,
                    'placeholder': 'Name of person currently caring for child'
                },
                {
                    'name': 'protection_concerns',
                    'label': 'Protection Concerns',
                    'type': FieldType.TEXTAREA,
                    'required': True,
                    'placeholder': 'Describe specific concerns about child safety or welfare',
                    'validation_rules': {'min_length': 50, 'max_length': 2000}
                }
            ]
        }
    },
    'BC': {
        'family_law_application': {
            'name': 'Application About a Family Law Matter - Form F3',
            'description': 'General family law application for BC Supreme Court',
            'category': 'family_court',
            'fields': [
                'applicant_name', 'applicant_address', 'applicant_phone', 'applicant_email',
                'case_number', 'court_location', 'matter_description', 'relief_sought',
                {
                    'name': 'urgent_application',
                    'label': 'Is this an urgent application?',
                    'type': FieldType.SELECT,
                    'required': True,
                    'options': ['Yes', 'No']
                },
                {
                    'name': 'urgency_reason',
                    'label': 'Reason for Urgency',
                    'type': FieldType.TEXTAREA,
                    'required': False,
                    'placeholder': 'Explain why this matter is urgent',
                    'conditional_field': 'urgent_application',
                    'conditional_value': 'Yes'
                }
            ]
        }
    },
    'AB': {
        'family_court_application': {
            'name': 'Application - Form FL-3',
            'description': 'Application form for Alberta Family Court',
            'category': 'family_court',
            'fields': [
                'applicant_name', 'applicant_address', 'applicant_phone', 'applicant_email',
                'case_number', 'court_location', 'matter_description', 'relief_sought',
                {
                    'name': 'legal_representation',
                    'label': 'Do you have legal representation?',
                    'type': FieldType.SELECT,
                    'required': True,
                    'options': ['Yes', 'No', 'Self-represented']
                },
                {
                    'name': 'lawyer_details',
                    'label': 'Lawyer Details',
                    'type': FieldType.TEXTAREA,
                    'required': False,
                    'placeholder': 'Name, firm, and contact information of your lawyer',
                    'conditional_field': 'legal_representation',
                    'conditional_value': 'Yes'
                }
            ]
        }
    }
}

class FormTemplateManager:
    """Manages court form templates and field definitions"""
    
    @staticmethod
    def get_available_provinces() -> Dict[str, str]:
        """Get list of available provinces"""
        return CANADIAN_PROVINCES
    
    @staticmethod
    def get_forms_for_province(province_code: str) -> Dict[str, Any]:
        """Get available forms for a specific province"""
        return PROVINCIAL_FORMS.get(province_code, {})
    
    @staticmethod
    def get_standard_field_definition(field_name: str) -> Optional[Dict[str, Any]]:
        """Get definition for a standard field"""
        return STANDARD_FIELDS.get(field_name)
    
    @staticmethod
    def create_form_template(province_code: str, form_key: str, case_type: str = None) -> Optional[FormTemplate]:
        """Create a form template from predefined definitions"""
        if province_code not in PROVINCIAL_FORMS:
            return None
            
        form_def = PROVINCIAL_FORMS[province_code].get(form_key)
        if not form_def:
            return None
        
        try:
            # Check if template already exists
            existing = FormTemplate.query.filter_by(
                name=form_def['name'],
                province=province_code
            ).first()
            
            if existing:
                return existing
            
            # Create new template
            template = FormTemplate(
                name=form_def['name'],
                description=form_def['description'],
                province=province_code,
                category=form_def['category'],
                case_type=case_type,
                is_active=True
            )
            
            db.session.add(template)
            db.session.flush()  # Get the ID
            
            # Create form fields
            order = 1
            for field_def in form_def['fields']:
                if isinstance(field_def, str):
                    # Standard field reference
                    std_field = STANDARD_FIELDS.get(field_def)
                    if std_field:
                        field = FormField(
                            template_id=template.id,
                            name=field_def,
                            label=std_field['label'],
                            field_type=std_field['type'],
                            required=std_field['required'],
                            placeholder=std_field.get('placeholder', ''),
                            validation_rules=json.dumps(std_field.get('validation_rules', {})),
                            options=json.dumps(std_field.get('options', [])),
                            order=order
                        )
                        db.session.add(field)
                        order += 1
                elif isinstance(field_def, dict):
                    # Custom field definition
                    field = FormField(
                        template_id=template.id,
                        name=field_def['name'],
                        label=field_def['label'],
                        field_type=field_def['type'],
                        required=field_def.get('required', False),
                        placeholder=field_def.get('placeholder', ''),
                        validation_rules=json.dumps(field_def.get('validation_rules', {})),
                        options=json.dumps(field_def.get('options', [])),
                        conditional_field=field_def.get('conditional_field'),
                        conditional_value=field_def.get('conditional_value'),
                        order=order
                    )
                    db.session.add(field)
                    order += 1
            
            db.session.commit()
            return template
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating form template: {str(e)}")
            return None
    
    @staticmethod
    def get_template_by_id(template_id: int) -> Optional[FormTemplate]:
        """Get a form template by ID"""
        return FormTemplate.query.get(template_id)
    
    @staticmethod
    def get_templates_for_case_type(case_type: str, province: str = None) -> List[FormTemplate]:
        """Get form templates for a specific case type"""
        query = FormTemplate.query.filter_by(case_type=case_type, is_active=True)
        if province:
            query = query.filter_by(province=province)
        return query.all()
    
    @staticmethod
    def validate_form_data(template_id: int, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form data against template requirements"""
        template = FormTemplate.query.get(template_id)
        if not template:
            return {'valid': False, 'errors': ['Template not found']}
        
        errors = []
        warnings = []
        
        # Get all fields for template
        fields = FormField.query.filter_by(template_id=template_id).all()
        
        for field in fields:
            field_value = form_data.get(field.name)
            
            # Check conditional fields
            if field.conditional_field:
                condition_value = form_data.get(field.conditional_field)
                if condition_value != field.conditional_value:
                    continue  # Skip validation for conditional field that doesn't apply
            
            # Required field validation
            if field.required and (not field_value or str(field_value).strip() == ''):
                errors.append(f'{field.label} is required')
                continue
            
            # Type-specific validation
            if field_value and field.validation_rules:
                try:
                    rules = json.loads(field.validation_rules)
                    
                    # String length validation
                    if 'min_length' in rules and len(str(field_value)) < rules['min_length']:
                        errors.append(f'{field.label} must be at least {rules["min_length"]} characters')
                    
                    if 'max_length' in rules and len(str(field_value)) > rules['max_length']:
                        errors.append(f'{field.label} must be no more than {rules["max_length"]} characters')
                    
                    # Pattern validation
                    if 'pattern' in rules:
                        import re
                        if not re.match(rules['pattern'], str(field_value)):
                            errors.append(f'{field.label} format is invalid')
                            
                except json.JSONDecodeError:
                    pass  # Skip validation if rules are malformed
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def initialize_default_templates():
        """Initialize default form templates for all provinces"""
        created_count = 0
        
        for province_code, forms in PROVINCIAL_FORMS.items():
            for form_key, form_def in forms.items():
                # Map form category to case type
                case_type_mapping = {
                    'family_court': 'family_court',
                    'child_protection': 'child_protection',
                    'tribunal': 'tribunal'
                }
                
                case_type = case_type_mapping.get(form_def['category'], 'other')
                
                template = FormTemplateManager.create_form_template(
                    province_code, 
                    form_key, 
                    case_type
                )
                
                if template:
                    created_count += 1
                    print(f"Created template: {template.name} for {CANADIAN_PROVINCES[province_code]}")
        
        return created_count

def get_form_suggestions_for_case(case) -> List[FormTemplate]:
    """Get suggested forms based on case details"""
    suggestions = []
    
    # Get forms for the case's province and type
    if case.province and case.case_type:
        province_code = case.province
        case_type = case.case_type.value
        
        templates = FormTemplateManager.get_templates_for_case_type(case_type, province_code)
        suggestions.extend(templates)
    
    # If no province-specific forms, get general templates for case type
    if not suggestions and case.case_type:
        templates = FormTemplateManager.get_templates_for_case_type(case.case_type.value)
        suggestions.extend(templates)
    
    return suggestions