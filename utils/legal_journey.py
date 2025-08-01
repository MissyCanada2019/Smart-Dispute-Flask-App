"""
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
            workflow = LEGAL_WORKFLOWS[case_type]['ON'].copy()
            # Modify for generic use
            workflow['name'] = f"Canadian {case_type.replace('_', ' ').title()} Process"
            workflow['description'] = f"General {case_type.replace('_', ' ')} process (adapted from Ontario)"
            return workflow
        
        return None
    
    def get_current_stage(self, case: Case) -> Optional[JourneyStage]:
        """Get the current active stage for a case"""
        return JourneyStage.query.filter_by(
            case_id=case.id,
            status=StageStatus.IN_PROGRESS
        ).first()
    
    def get_next_steps(self, case: Case, limit: int = 3) -> List[JourneyStep]:
        """Get the next steps for a case"""
        current_stage = self.get_current_stage(case)
        if not current_stage:
            return []
        
        # Get incomplete steps from current stage
        next_steps = JourneyStep.query.filter_by(
            stage_id=current_stage.id,
            is_completed=False
        ).order_by(JourneyStep.order).limit(limit).all()
        
        return next_steps
    
    def complete_step(self, step_id: int, user_notes: str = None) -> bool:
        """Mark a step as completed"""
        try:
            step = JourneyStep.query.get(step_id)
            if not step:
                return False
            
            step.is_completed = True
            step.completed_at = datetime.utcnow()
            step.user_notes = user_notes
            
            # Check if stage is now complete
            stage = JourneyStage.query.get(step.stage_id)
            if stage:
                remaining_steps = JourneyStep.query.filter_by(
                    stage_id=stage.id,
                    is_completed=False,
                    is_required=True
                ).count()
                
                if remaining_steps == 0:
                    # Complete the stage
                    stage.status = StageStatus.COMPLETED
                    stage.completed_at = datetime.utcnow()
                    
                    # Start next stage
                    next_stage = JourneyStage.query.filter_by(
                        case_id=stage.case_id
                    ).filter(
                        JourneyStage.order > stage.order
                    ).order_by(JourneyStage.order).first()
                    
                    if next_stage:
                        next_stage.status = StageStatus.IN_PROGRESS
                        next_stage.started_at = datetime.utcnow()
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error completing step: {str(e)}")
            return False
    
    def get_journey_progress(self, case: Case) -> Dict[str, Any]:
        """Get overall journey progress for a case"""
        stages = JourneyStage.query.filter_by(case_id=case.id).order_by(JourneyStage.order).all()
        
        if not stages:
            return {
                'total_stages': 0,
                'completed_stages': 0,
                'current_stage': None,
                'progress_percentage': 0,
                'estimated_completion_date': None
            }
        
        completed_stages = len([s for s in stages if s.status == StageStatus.COMPLETED])
        current_stage = next((s for s in stages if s.status == StageStatus.IN_PROGRESS), None)
        
        # Calculate progress percentage
        progress_percentage = (completed_stages / len(stages)) * 100
        if current_stage:
            # Add partial progress for current stage
            total_steps = JourneyStep.query.filter_by(stage_id=current_stage.id).count()
            completed_steps = JourneyStep.query.filter_by(stage_id=current_stage.id, is_completed=True).count()
            if total_steps > 0:
                stage_progress = (completed_steps / total_steps) / len(stages) * 100
                progress_percentage += stage_progress
        
        # Estimate completion date
        estimated_completion_date = None
        if current_stage:
            remaining_days = sum(
                s.estimated_duration_days for s in stages 
                if s.status == StageStatus.NOT_STARTED
            )
            if current_stage.started_at:
                days_elapsed = (datetime.utcnow() - current_stage.started_at).days
                remaining_current_stage = max(0, current_stage.estimated_duration_days - days_elapsed)
                remaining_days += remaining_current_stage
            
            estimated_completion_date = datetime.utcnow() + timedelta(days=remaining_days)
        
        return {
            'total_stages': len(stages),
            'completed_stages': completed_stages,
            'current_stage': current_stage,
            'progress_percentage': min(100, int(progress_percentage)),
            'estimated_completion_date': estimated_completion_date,
            'stages': stages
        }
    
    def get_personalized_guidance(self, case: Case, step: JourneyStep) -> Dict[str, Any]:
        """Get AI-powered personalized guidance for a step"""
        try:
            # Prepare context for AI
            context = f"""
            Provide personalized legal guidance for a self-represented litigant in Canada.
            
            CASE INFORMATION:
            - Case Type: {case.case_type.value if case.case_type else 'Unknown'}
            - Province: {case.province}
            - Case Description: {case.description}
            
            CURRENT STEP:
            - Step Name: {step.name}
            - Description: {step.description}
            - Type: {step.step_type.value}
            - Standard Guidance: {step.guidance}
            
            Please provide:
            1. Specific, actionable advice for this step
            2. Common mistakes to avoid
            3. Resources or contacts that might help
            4. Estimated time and effort required
            5. Any province-specific considerations
            
            Keep the advice practical and accessible for someone without legal training.
            """
            
            ai_response = self.ai_service.analyze_text_with_claude(
                context,
                max_tokens=1000,
                temperature=0.3
            )
            
            if ai_response and 'analysis' in ai_response:
                return {
                    'success': True,
                    'personalized_guidance': ai_response['analysis'],
                    'standard_guidance': step.guidance
                }
        
        except Exception as e:
            print(f"Error getting personalized guidance: {str(e)}")
        
        return {
            'success': False,
            'personalized_guidance': None,
            'standard_guidance': step.guidance
        }
    
    def suggest_next_actions(self, case: Case) -> List[Dict[str, Any]]:
        """Suggest next actions based on case status and journey progress"""
        suggestions = []
        
        try:
            # Get current journey status
            progress = self.get_journey_progress(case)
            next_steps = self.get_next_steps(case, limit=5)
            
            # Add step-based suggestions
            for step in next_steps:
                suggestions.append({
                    'type': 'journey_step',
                    'title': step.name,
                    'description': step.description,
                    'priority': 'high' if step.is_required else 'medium',
                    'estimated_duration': f"{step.estimated_duration_days} days",
                    'action_url': f"/journey/step/{step.id}",
                    'step_id': step.id
                })
            
            # Add general suggestions based on case status
            if case.status == CaseStatus.INITIAL:
                suggestions.append({
                    'type': 'case_action',
                    'title': 'Upload Evidence',
                    'description': 'Upload relevant documents and evidence to strengthen your case',
                    'priority': 'high',
                    'action_url': f"/cases/{case.id}/evidence/upload"
                })
            
            # Add form-related suggestions
            if progress['progress_percentage'] > 30:  # Case is progressing
                suggestions.append({
                    'type': 'form_action',
                    'title': 'Prepare Court Forms',
                    'description': 'Use AI-powered form filling to prepare required court documents',
                    'priority': 'medium',
                    'action_url': f"/forms/case/{case.id}"
                })
        
        except Exception as e:
            print(f"Error generating suggestions: {str(e)}")
        
        return suggestions[:10]  # Return top 10 suggestions

def get_journey_stage_color(status: StageStatus) -> str:
    """Get bootstrap color class for stage status"""
    color_map = {
        StageStatus.NOT_STARTED: 'secondary',
        StageStatus.IN_PROGRESS: 'primary',
        StageStatus.COMPLETED: 'success',
        StageStatus.ON_HOLD: 'warning'
    }
    return color_map.get(status, 'secondary')

def get_step_type_icon(step_type: StepType) -> str:
    """Get Font Awesome icon for step type"""
    icon_map = {
        StepType.DOCUMENT_COLLECTION: 'fas fa-file-alt',
        StepType.FORM_COMPLETION: 'fas fa-edit',
        StepType.EVIDENCE_GATHERING: 'fas fa-search',
        StepType.COURT_FILING: 'fas fa-paper-plane',
        StepType.LEGAL_SERVICE: 'fas fa-envelope',
        StepType.COURT_APPEARANCE: 'fas fa-gavel',
        StepType.WAITING_PERIOD: 'fas fa-clock',
        StepType.NEGOTIATION: 'fas fa-handshake',
        StepType.TRIAL_PREPARATION: 'fas fa-tasks',
        StepType.LEGAL_RESEARCH: 'fas fa-book',
        StepType.COURT_SCHEDULING: 'fas fa-calendar'
    }
    return icon_map.get(step_type, 'fas fa-circle')