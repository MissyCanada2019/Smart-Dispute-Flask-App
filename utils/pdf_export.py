"""
PDF Export System for Court Forms
Generates professional PDF documents from completed court forms
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import black, white, gray
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
from models.court_form import FormSubmission, FormTemplate, FormField
from models.case import Case
from models.user import User

class CourtFormPDFGenerator:
    """Generates professional PDF documents for Canadian court forms"""
    
    def __init__(self):
        self.page_width = letter[0]
        self.page_height = letter[1]
        self.margin = 0.75 * inch
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for court forms"""
        # Court header style
        self.styles.add(ParagraphStyle(
            name='CourtHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=black
        ))
        
        # Form title style
        self.styles.add(ParagraphStyle(
            name='FormTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=black
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=black
        ))
        
        # Field label style
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=6,
            spaceAfter=2,
            textColor=black,
            fontName='Helvetica-Bold'
        ))
        
        # Field value style
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=black,
            leftIndent=20
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=gray
        ))
        
        # Legal disclaimer style
        self.styles.add(ParagraphStyle(
            name='LegalDisclaimer',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceBefore=20,
            spaceAfter=10,
            textColor=black,
            alignment=TA_JUSTIFY
        ))
    
    def generate_form_pdf(self, submission: FormSubmission) -> BytesIO:
        """Generate PDF for a form submission"""
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Build content
        story = []
        
        # Add header
        story.extend(self._build_header(submission))
        
        # Add form content
        story.extend(self._build_form_content(submission))
        
        # Add footer
        story.extend(self._build_footer(submission))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _build_header(self, submission: FormSubmission) -> List:
        """Build the PDF header section"""
        story = []
        
        # Get template and case info
        template = FormTemplate.query.get(submission.template_id)
        case = Case.query.get(submission.case_id) if submission.case_id else None
        
        # Court jurisdiction header
        if template and template.province:
            province_names = {
                'ON': 'ONTARIO',
                'BC': 'BRITISH COLUMBIA',
                'AB': 'ALBERTA',
                'QC': 'QUEBEC',
                'NS': 'NOVA SCOTIA',
                'NB': 'NEW BRUNSWICK',
                'MB': 'MANITOBA',
                'SK': 'SASKATCHEWAN',
                'PE': 'PRINCE EDWARD ISLAND',
                'NL': 'NEWFOUNDLAND AND LABRADOR',
                'NT': 'NORTHWEST TERRITORIES',
                'NU': 'NUNAVUT',
                'YT': 'YUKON'
            }
            
            province_name = province_names.get(template.province, template.province)
            
            if template.category == 'family_court':
                court_header = f"SUPERIOR COURT OF JUSTICE - FAMILY COURT<br/>FOR {province_name}"
            elif template.category == 'child_protection':
                court_header = f"ONTARIO COURT OF JUSTICE<br/>CHILD PROTECTION COURT<br/>FOR {province_name}"
            else:
                court_header = f"COURT OF {province_name}"
            
            story.append(Paragraph(court_header, self.styles['CourtHeader']))
            story.append(Spacer(1, 12))
        
        # Form title
        if template:
            story.append(Paragraph(template.name.upper(), self.styles['FormTitle']))
            if template.description:
                story.append(Paragraph(f"<i>{template.description}</i>", self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Case information table
        if case:
            case_data = [
                ['Court File No.:', case.case_number or '_' * 20],
                ['Case Type:', case.case_type.value.replace('_', ' ').title() if case.case_type else 'N/A'],
                ['Filed:', submission.submitted_at.strftime('%B %d, %Y') if submission.submitted_at else 'Draft']
            ]
            
            case_table = Table(case_data, colWidths=[2*inch, 4*inch])
            case_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(case_table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _build_form_content(self, submission: FormSubmission) -> List:
        """Build the main form content"""
        story = []
        
        # Get form data
        try:
            form_data = json.loads(submission.form_data) if submission.form_data else {}
        except json.JSONDecodeError:
            form_data = {}
        
        # Get template fields
        fields = FormField.query.filter_by(
            template_id=submission.template_id
        ).order_by(FormField.order).all()
        
        # Group fields by section (basic grouping)
        current_section = "Application Details"
        story.append(Paragraph(current_section, self.styles['SectionHeading']))
        
        for field in fields:
            # Skip conditional fields that don't apply
            if field.conditional_field:
                condition_value = form_data.get(field.conditional_field)
                if condition_value != field.conditional_value:
                    continue
            
            # Get field value
            field_value = form_data.get(field.name, '')
            
            # Handle different field types
            if field.field_type.value == 'textarea':
                # Multi-line text fields
                story.append(Paragraph(f"{field.label}:", self.styles['FieldLabel']))
                if field_value:
                    # Handle long text with proper formatting
                    formatted_value = field_value.replace('\n', '<br/>')
                    story.append(Paragraph(formatted_value, self.styles['FieldValue']))
                else:
                    story.append(Paragraph("_" * 50, self.styles['FieldValue']))
            elif field.field_type.value == 'select':
                # Select fields
                story.append(Paragraph(f"{field.label}:", self.styles['FieldLabel']))
                display_value = field_value if field_value else "_" * 20
                story.append(Paragraph(display_value, self.styles['FieldValue']))
            elif field.field_type.value == 'date':
                # Date fields
                story.append(Paragraph(f"{field.label}:", self.styles['FieldLabel']))
                if field_value:
                    try:
                        # Try to format date nicely
                        date_obj = datetime.strptime(field_value, '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%B %d, %Y')
                        story.append(Paragraph(formatted_date, self.styles['FieldValue']))
                    except:
                        story.append(Paragraph(field_value, self.styles['FieldValue']))
                else:
                    story.append(Paragraph("_" * 20, self.styles['FieldValue']))
            else:
                # Text and other fields
                story.append(Paragraph(f"{field.label}:", self.styles['FieldLabel']))
                display_value = field_value if field_value else "_" * 30
                story.append(Paragraph(display_value, self.styles['FieldValue']))
        
        # Add signature section
        story.append(Spacer(1, 30))
        story.append(Paragraph("SIGNATURE AND DECLARATION", self.styles['SectionHeading']))
        
        declaration_text = """
        I swear/affirm that the information set out in this application is true to the best of my knowledge, 
        information and belief. I understand that it is an offence under the Criminal Code to knowingly swear 
        or affirm a false affidavit.
        """
        story.append(Paragraph(declaration_text, self.styles['LegalDisclaimer']))
        
        # Signature table
        signature_data = [
            ['', ''],
            ['_' * 40, f"Date: {datetime.now().strftime('%B %d, %Y')}"],
            ['Signature of Applicant', '']
        ]
        
        signature_table = Table(signature_data, colWidths=[3*inch, 2*inch])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        story.append(signature_table)
        
        return story
    
    def _build_footer(self, submission: FormSubmission) -> List:
        """Build the PDF footer section"""
        story = []
        
        story.append(Spacer(1, 30))
        
        # Legal disclaimer
        disclaimer = """
        <b>IMPORTANT NOTICE:</b> This form was generated by Smart Dispute Canada, 
        an AI-powered legal assistance platform. This document is for informational purposes only 
        and does not constitute legal advice. Please review all information carefully before filing 
        with the court. Consult with a qualified legal professional if you need legal advice.
        """
        story.append(Paragraph(disclaimer, self.styles['LegalDisclaimer']))
        
        # Generation info
        footer_text = f"""
        Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | 
        Smart Dispute Canada | 
        Form ID: {submission.id}
        """
        story.append(Paragraph(footer_text, self.styles['Footer']))
        
        return story
    
    def generate_form_summary_pdf(self, submissions: List[FormSubmission]) -> BytesIO:
        """Generate a summary PDF of multiple form submissions"""
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        story = []
        
        # Header
        story.append(Paragraph("COURT FORMS SUMMARY", self.styles['CourtHeader']))
        story.append(Spacer(1, 20))
        
        # Summary table
        summary_data = [['Form Name', 'Status', 'Created', 'Case']]
        
        for submission in submissions:
            template = FormTemplate.query.get(submission.template_id)
            case = Case.query.get(submission.case_id) if submission.case_id else None
            
            summary_data.append([
                template.name if template else 'Unknown Form',
                submission.status.value.title(),
                submission.created_at.strftime('%Y-%m-%d'),
                case.title if case else 'No Case'
            ])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1*inch, 1*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Smart Dispute Canada"
        story.append(Paragraph(footer_text, self.styles['Footer']))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer

class PDFExportManager:
    """Manages PDF export operations for court forms"""
    
    def __init__(self):
        self.generator = CourtFormPDFGenerator()
    
    def export_form_submission(self, submission_id: int, user_id: int) -> Optional[BytesIO]:
        """Export a single form submission to PDF"""
        try:
            # Get submission with user verification
            submission = FormSubmission.query.filter_by(
                id=submission_id,
                user_id=user_id
            ).first()
            
            if not submission:
                return None
            
            # Generate PDF
            pdf_buffer = self.generator.generate_form_pdf(submission)
            return pdf_buffer
            
        except Exception as e:
            print(f"Error exporting form submission {submission_id}: {str(e)}")
            return None
    
    def export_case_forms(self, case_id: int, user_id: int) -> Optional[BytesIO]:
        """Export all completed forms for a case to a single PDF"""
        try:
            # Verify case ownership
            case = Case.query.filter_by(id=case_id, user_id=user_id).first()
            if not case:
                return None
            
            # Get all completed forms for the case
            submissions = FormSubmission.query.filter_by(
                case_id=case_id,
                user_id=user_id
            ).filter(FormSubmission.status.in_(['completed', 'submitted'])).all()
            
            if not submissions:
                return None
            
            # Generate combined PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch
            )
            
            story = []
            
            for i, submission in enumerate(submissions):
                if i > 0:
                    story.append(PageBreak())
                
                # Generate individual form content
                individual_pdf = self.generator.generate_form_pdf(submission)
                # Note: In a full implementation, you'd merge the PDFs properly
                # For now, we'll generate each form in sequence
                form_story = self.generator._build_header(submission)
                form_story.extend(self.generator._build_form_content(submission))
                form_story.extend(self.generator._build_footer(submission))
                story.extend(form_story)
            
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"Error exporting case forms for case {case_id}: {str(e)}")
            return None
    
    def export_user_forms_summary(self, user_id: int) -> Optional[BytesIO]:
        """Export a summary of all user's forms"""
        try:
            submissions = FormSubmission.query.filter_by(user_id=user_id).all()
            
            if not submissions:
                return None
            
            pdf_buffer = self.generator.generate_form_summary_pdf(submissions)
            return pdf_buffer
            
        except Exception as e:
            print(f"Error exporting user forms summary for user {user_id}: {str(e)}")
            return None
    
    def get_export_filename(self, submission_id: int, user_id: int) -> str:
        """Generate appropriate filename for exported PDF"""
        try:
            submission = FormSubmission.query.filter_by(
                id=submission_id,
                user_id=user_id
            ).first()
            
            if not submission:
                return f"form_export_{submission_id}.pdf"
            
            template = FormTemplate.query.get(submission.template_id)
            case = Case.query.get(submission.case_id) if submission.case_id else None
            
            # Create filename
            parts = []
            
            if template:
                # Clean template name for filename
                clean_name = ''.join(c for c in template.name if c.isalnum() or c in (' ', '-', '_')).strip()
                clean_name = clean_name.replace(' ', '_')
                parts.append(clean_name)
            
            if case and case.case_number:
                parts.append(case.case_number)
            
            parts.append(f"ID{submission.id}")
            
            filename = '_'.join(parts) + '.pdf'
            return filename
            
        except Exception as e:
            print(f"Error generating filename for submission {submission_id}: {str(e)}")
            return f"form_export_{submission_id}.pdf"

# Global export manager instance
pdf_export_manager = PDFExportManager()