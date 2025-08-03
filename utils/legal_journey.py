***
Legal Journey Guidance System
Provides step-by-step workflows and guidance for Canadian legal processes
"""

from typing import Dict, List, Any, Optional, Tuple
from models.case import Case, CaseType, CaseStatus
from models.legal_journey import JourneyStage, JourneyStep, StageStatus, StepType
from models import db
from utils.ai_services import AIServiceManager
import json
from datetime import datetime, timedelta

# Standard legal workflows for Canadian provinces
LEGAL_WORKFLOWS = {
    'family_court': {
        'ON': {
            'name': 'Ontario Family Court Process',
            'description': 'Step-by-step guide for family court proceedings in Ontario',
            'stages': [
                {
                    'name': 'Case Preparation',
                    'description': 'Gather documents and prepare your case',
                    'order': 1,
                    'estimated_duration_days': 14,
                    'steps': [
                        {
                            'name': 'Collect Personal Documents',
                            'description': 'Gather identification, marriage certificates, birth certificates',
                            'type': StepType.DOCUMENT_COLLECTION,
                            'order': 1,
                            'estimated_duration_days': 3,
                            'is_required': True,
                            'guidance': 'You will need: Valid photo ID, marriage certificate (if applicable), birth certificates for all children, proof of income, bank statements from last 3 months'
                        },
                        {
                            'name': 'Financial Documentation',
                            'description': 'Gather financial records and statements',
                            'type': StepType.DOCUMENT_COLLECTION,
                            'order': 2,
                            'estimated_duration_days': 5,
                            'is_required': True,
                            'guidance': 'Collect: Tax returns (last 2 years), pay stubs, bank statements, property valuations, investment statements, debt documentation'
                        },
                        {
                            'name': 'Document Evidence',
                            'description': 'Collect any supporting evidence for your case',
                            'type': StepType.EVIDENCE_GATHERING,
                            'order': 3,
                            'estimated_duration_days': 7,
                            'is_required': False,
                            'guidance': 'This may include: Photos, emails, text messages, witness statements, medical records, police reports (if applicable)'
                        }
                    ]
                },
                {
                    'name': 'Form Preparation and Filing',
                    'description': 'Complete and file required court forms',
                    'order': 2,
                    'estimated_duration_days': 10,
                    'steps': [
                        {
                            'name': 'Complete Application Form',
                            'description': 'Fill out Form 8 (Application - General) or appropriate form',
                            'type': StepType.FORM_COMPLETION,
                            'order': 1,
                            'estimated_duration_days': 3,
                            'is_required': True,
                            'guidance': 'Use our AI-powered form filling feature to help complete your application accurately'
                        },
                        {
                            'name': 'Prepare Supporting Affidavit',
                            'description': 'Create detailed affidavit supporting your application',
                            'type': StepType.FORM_COMPLETION,
                            'order': 2,
                            'estimated_duration_days': 5,
                            'is_required': True,
                            'guidance': 'Your affidavit should clearly state the facts and include all relevant details'
                        },
                        {
                            'name': 'File Documents with Court',
                            'description': 'Submit your application and supporting documents to the court',
                            'type': StepType.COURT_FILING,
                            'order': 3,
                            'estimated_duration_days': 2,
                            'is_required': True,
                            'guidance': 'File at the appropriate courthouse for your jurisdiction. Keep copies of all filed documents'
                        }
                    ]
                },
                {
                    'name': 'Service and Response',
                    'description': 'Serve documents on other parties and await response',
                    'order': 3,
                    'estimated_duration_days': 30,
                    'steps': [
                        {
                            'name': 'Serve Documents on Other Party',
                            'description': 'Legally serve your application on the respondent',
                            'type': StepType.LEGAL_SERVICE,
                            'order': 1,
                            'estimated_duration_days': 7,
                            'is_required': True,
                            'guidance': 'Documents must be served personally or by an approved alternative method'
                        },
                        {
                            'name': 'File Affidavit of Service',
                            'description': 'File proof that documents were properly served',
                            'type': StepType.COURT_FILING,
                            'order': 2,
                            'estimated_duration_days': 3,
                            'is_required': True,
                            'guidance': 'File this within the required timeframe after service'
                        },
                        {
                            'name': 'Await Response',
                            'description': 'Wait for the other party to file their response',
                            'type': StepType.WAITING_PERIOD,
                            'order': 3,
                            'estimated_duration_days': 20,
                            'is_required': False,
                            'guidance': 'The respondent typically has 30 days to respond after being served'
                        }
                    ]
                },
                {
                    'name': 'Case Conference',
                    'description': 'Attend mandatory case conference',
                    'order': 4,
                    'estimated_duration_days': 21,
                    'steps': [
                        {
                            'name': 'Schedule Case Conference',
                            'description': 'Book a case conference date with the court',
                            'type': StepType.COURT_SCHEDULING,
                            'order': 1,
                            'estimated_duration_days': 7,
                            'is_required': True,
                            'guidance': 'Case conference must be scheduled within required timeframes'
                        },
                        {
                            'name': 'Prepare Case Conference Brief',
                            'description': 'Complete Form 17C - Case Conference Brief',
                            'type': StepType.FORM_COMPLETION,
                            'order': 2,
                            'estimated_duration_days': 7,
                            'is_required': True,
                            'guidance': 'This form outlines the issues and your position'
                        },
                        {
                            'name': 'Attend Case Conference',
                            'description': 'Participate in case conference with judge',
                            'type': StepType.COURT_APPEARANCE,
                            'order': 3,
                            'estimated_duration_days': 1,
                            'is_required': True,
                            'guidance': 'Be prepared to discuss settlement and case management'
                        }
                    ]
                },
                {
                    'name': 'Resolution',
                    'description': 'Resolve the matter through settlement or trial',
                    'order': 5,
                    'estimated_duration_days': 60,
                    'steps': [
                        {
                            'name': 'Negotiate Settlement',
                            'description': 'Attempt to reach agreement with other party',
                            'type': StepType.NEGOTIATION,
                            'order': 1,
                            'estimated_duration_days': 30,
                            'is_required': False,
                            'guidance': 'Most cases settle without going to trial'
                        },
                        {
                            'name': 'Prepare for Trial (if needed)',
                            'description': 'Complete trial preparation if settlement unsuccessful',
                            'type': StepType.TRIAL_PREPARATION,
                            'order': 2,
                            'estimated_duration_days': 20,
                            'is_required': False,
                            'guidance': 'Gather witnesses, prepare evidence, complete required forms'
                        },
                        {
                            'name': 'Attend Trial or Finalize Settlement',
                            'description': 'Complete the legal process',
                            'type': StepType.COURT_APPEARANCE,
                            'order': 3,
                            'estimated_duration_days': 1,
                            'is_required': True,
                            'guidance': 'Follow all court orders and complete required documentation'
                        }
                    ]
                }
            ]
        },
        'BC': {
            'name': 'BC Supreme Court Family Law Process',
            'description': 'Family law proceedings in British Columbia Supreme Court',
            'stages': [
                {
                    'name': 'Initial Preparation',
                    'description': 'Prepare your case and gather documentation',
                    'order': 1,
                    'estimated_duration_days': 21,
                    'steps': [
                        {
                            'name': 'Determine Court Jurisdiction',
                            'description': 'Confirm whether Provincial Court or Supreme Court is appropriate',
                            'type': StepType.LEGAL_RESEARCH,
                            'order': 1,
                            'estimated_duration_days': 2,
                            'is_required': True,
                            'guidance': 'Provincial Court handles most family matters; Supreme Court handles divorce and property division'
                        },
                        {
                            'name': 'Collect Required Documents',
                            'description': 'Gather all necessary personal and financial documents',
                            'type': StepType.DOCUMENT_COLLECTION,
                            'order': 2,
                            'estimated_duration_days': 14,
                            'is_required': True,
                            'guidance': 'Required documents vary by case type but typically include ID, financial records, and relationship documents'
                        }
                    ]
                }
                # Additional BC-specific stages would go here
            ]
        }
    },
    'child_protection': {
        'ON': {
            'name': 'Ontario Child Protection Process',
            'description': 'Legal process for child protection matters in Ontario',
            'stages': [
                {
                    'name': 'Understanding the Process',
                    'description': 'Learn about child protection law and your rights',
                    'order': 1,
                    'estimated_duration_days': 7,
                    'steps': [
                        {
                            'name': 'Know Your Rights',
                            'description': 'Understand your rights as a parent in child protection proceedings',
                            'type': StepType.LEGAL_RESEARCH,
                            'order': 1,
                            'estimated_duration_days': 3,
                            'is_required': True,
                            'guidance': 'You have the right to legal representation, to be heard by the court, and to present evidence'
                        },
                        {
                            'name': 'Understand the Timeline',
                            'description': 'Learn about important deadlines and court timeline',
                            'type': StepType.LEGAL_RESEARCH,
                            'order': 2,
                            'estimated_duration_days': 2,
                            'is_required': True,
                            'guidance': 'Child protection cases have strict timelines that must be followed'
                        }
                    ]
                }
                # Additional child protection stages would go here
            ]
        }
    },
    'tribunal': {
        'ON': {
            'name': 'Ontario Tribunal Process',
            'description': 'General process for Ontario administrative tribunals',
            'stages': [
                {
                    'name': 'Application Preparation',
                    'description': 'Prepare and submit your tribunal application',
                    'order': 1,
                    'estimated_duration_days': 14,
                    'steps': [
                        {
                            'name': 'Identify Correct Tribunal',
                            'description': 'Confirm you are applying to the right tribunal',
                            'type': StepType.LEGAL_RESEARCH,
                            'order': 1,
                            'estimated_duration_days': 2,
                            'is_required': True,
                            'guidance': 'Different tribunals handle different types of disputes'
                        },
                        {
                            'name': 'Complete Application',
                            'description': 'Fill out the required application forms',
                            'type': StepType.FORM_COMPLETION,
                            'order': 2,
                            'estimated_duration_days': 7,
                            'is_required': True,
                            'guidance': 'Be thorough and include all relevant information'
                        }
                    ]
                }
                # Additional tribunal stages would go here
            ]
        }
    }
}

class LegalJourneyManager:
    """Manages legal journey workflows and guidance"""
    
    def __init__(self):
        self.ai_service = AIServiceManager()
    
    def create_journey_for_case(self, case: Case) -> Optional[List[JourneyStage]]:
        """Create a legal journey workflow for a case"""
        try:
            # Get workflow definition for case type and province
            workflow = self._get_workflow_for_case(case)
            if not workflow:
                return None
            
            journey_stages = []
            
            for stage_def in workflow['stages']:
                # Create journey stage
                stage = JourneyStage(
                    case_id=case.id,
                    name=stage_def['name'],
                    description=stage_def['description'],
                    order=stage_def['order'],
                    estimated_duration_days=stage_def['estimated_duration_days'],
                    status=StageStatus.NOT_STARTED
                )
                
                db.session.add(stage)
                db.session.flush()  # Get the stage ID
                
                # Create journey steps for this stage
                for step_def in stage_def['steps']:
                    step = JourneyStep(
                        stage_id=stage.id,
                        name=step_def['name'],
                        description=step_def['description'],
                        step_type=step_def['type'],
                        order=step_def['order'],
                        estimated_duration_days=step_def['estimated_duration_days'],
                        is_required=step_def['is_required'],
                        guidance=step_def['guidance'],
                        is_completed=False
                    )
                    db.session.add(step)
                
                journey_stages.append(stage)
            
            db.session.commit()
            
            # Start the first stage
            if journey_stages:
                journey_stages[0].status = StageStatus.IN_PROGRESS
                journey_stages[0].started_at = datetime.utcnow()
                db.session.commit()
            
            return journey_stages
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating journey for case: {str(e)}")
            return None
    
    def _get_workflow_for_case(self, case: Case) -> Optional[Dict[str, Any]]:
        """Get the appropriate workflow definition for a case"""
        if not case.case_type or not case.province:
            return None
        
        case_type = case.case_type.value
        province = case.province
        
        # Check for specific workflow
        if case_type in LEGAL_WORKFLOWS and province in LEGAL_WORKFLOWS[case_type]:
            return LEGAL_WORKFLOWS[case_type][province]
        
        # Fall back to Ontario workflow if available (as it's most comprehensive)
        if case_type in LEGAL_WORKFLOWS and 'ON' in LEGAL_WORKFLOWS[case_type]:
            workflow