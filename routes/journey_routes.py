from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from utils.db import db  # Correct import from utils/db.py
from models.case import Case
from models.legal_journey import JourneyStage, JourneyStep, StageStatus
from utils.legal_journey import LegalJourneyManager, get_journey_stage_color, get_step_type_icon
import json
from datetime import datetime

journey_bp = Blueprint('journey', __name__, url_prefix='/journey')

@journey_bp.route('/case/<int:case_id>')
@login_required
def view_case_journey(case_id):
    """View the legal journey for a specific case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    # Get or create journey
    journey_manager = LegalJourneyManager()
    
    # Check if journey exists
    existing_stages = JourneyStage.query.filter_by(case_id=case_id).first()
    
    if not existing_stages:
        # Create journey for case
        stages = journey_manager.create_journey_for_case(case)
        if not stages:
            flash('Could not create a journey for this case type. Please update your case information.', 'warning')
            return redirect(url_for('cases.view_case', case_id=case_id))
    
    # Get journey progress and data
    progress = journey_manager.get_journey_progress(case)
    next_steps = journey_manager.get_next_steps(case, limit=5)
    suggestions = journey_manager.suggest_next_actions(case)
    
    return render_template('journey/case_journey.html', 
                         case=case, 
                         progress=progress,
                         next_steps=next_steps,
                         suggestions=suggestions,
                         get_stage_color=get_journey_stage_color,
                         get_step_icon=get_step_type_icon)

@journey_bp.route('/stage/<int:stage_id>')
@login_required
def view_stage(stage_id):
    """View details of a specific journey stage"""
    stage = JourneyStage.query.get_or_404(stage_id)
    case = Case.query.filter_by(id=stage.case_id, user_id=current_user.id).first_or_404()
    
    # Get all steps for this stage
    steps = JourneyStep.query.filter_by(stage_id=stage_id).order_by(JourneyStep.order).all()
    
    return render_template('journey/stage_detail.html', 
                         case=case, 
                         stage=stage, 
                         steps=steps,
                         get_step_icon=get_step_type_icon)

@journey_bp.route('/step/<int:step_id>')
@login_required
def view_step(step_id):
    """View details of a specific journey step"""
    step = JourneyStep.query.get_or_404(step_id)
    stage = JourneyStage.query.get(step.stage_id)
    case = Case.query.filter_by(id=stage.case_id, user_id=current_user.id).first_or_404()
    
    # Get personalized guidance
    journey_manager = LegalJourneyManager()
    guidance = journey_manager.get_personalized_guidance(case, step)
    
    return render_template('journey/step_detail.html', 
                         case=case, 
                         stage=stage, 
                         step=step,
                         guidance=guidance,
                         get_step_icon=get_step_type_icon)

@journey_bp.route('/step/<int:step_id>/complete', methods=['POST'])
@login_required
def complete_step(step_id):
    """Mark a step as completed"""
    step = JourneyStep.query.get_or_404(step_id)
    stage = JourneyStage.query.get(step.stage_id)
    case = Case.query.filter_by(id=stage.case_id, user_id=current_user.id).first_or_404()
    
    try:
        user_notes = request.form.get('notes', '').strip()
        
        journey_manager = LegalJourneyManager()
        success = journey_manager.complete_step(step_id, user_notes)
        
        if success:
            flash(f'Step "{step.name}" marked as completed!', 'success')
        else:
            flash('Error completing step. Please try again.', 'error')
    
    except Exception as e:
        flash(f'Error completing step: {str(e)}', 'error')
    
    return redirect(url_for('journey.view_case_journey', case_id=case.id))

@journey_bp.route('/step/<int:step_id>/uncomplete', methods=['POST'])
@login_required
def uncomplete_step(step_id):
    """Mark a completed step as incomplete"""
    step = JourneyStep.query.get_or_404(step_id)
    stage = JourneyStage.query.get(step.stage_id)
    case = Case.query.filter_by(id=stage.case_id, user_id=current_user.id).first_or_404()
    
    try:
        step.is_completed = False
        step.completed_at = None
        step.user_notes = None
        
        # If this affects stage completion, revert stage status
        if stage.status == StageStatus.COMPLETED:
            stage.status = StageStatus.IN_PROGRESS
            stage.completed_at = None
        
        db.session.commit()
        flash(f'Step "{step.name}" marked as incomplete.', 'info')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating step: {str(e)}', 'error')
    
    return redirect(url_for('journey.view_case_journey', case_id=case.id))

@journey_bp.route('/case/<int:case_id>/create-journey', methods=['POST'])
@login_required
def create_journey(case_id):
    """Create a new journey for a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete existing journey if it exists
        existing_stages = JourneyStage.query.filter_by(case_id=case_id).all()
        for stage in existing_stages:
            JourneyStep.query.filter_by(stage_id=stage.id).delete()
            db.session.delete(stage)
        
        # Create new journey
        journey_manager = LegalJourneyManager()
        stages = journey_manager.create_journey_for_case(case)
        
        if stages:
            flash('Legal journey created successfully!', 'success')
        else:
            flash('Could not create journey for this case type.', 'error')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating journey: {str(e)}', 'error')
    
    return redirect(url_for('journey.view_case_journey', case_id=case_id))

@journey_bp.route('/api/case/<int:case_id>/progress')
@login_required
def get_journey_progress(case_id):
    """API endpoint to get journey progress"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        journey_manager = LegalJourneyManager()
        progress = journey_manager.get_journey_progress(case)
        
        # Convert datetime objects to ISO strings for JSON serialization
        if progress['estimated_completion_date']:
            progress['estimated_completion_date'] = progress['estimated_completion_date'].isoformat()
        
        # Remove non-serializable objects
        if 'stages' in progress:
            del progress['stages']
        if 'current_stage' in progress and progress['current_stage']:
            progress['current_stage_name'] = progress['current_stage'].name
            del progress['current_stage']
        
        return jsonify(progress)
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@journey_bp.route('/api/case/<int:case_id>/next-steps')
@login_required
def get_next_steps(case_id):
    """API endpoint to get next steps"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        journey_manager = LegalJourneyManager()
        next_steps = journey_manager.get_next_steps(case, limit=10)
        
        steps_data = []
        for step in next_steps:
            steps_data.append({
                'id': step.id,
                'name': step.name,
                'description': step.description,
                'type': step.step_type.value,
                'is_required': step.is_required,
                'is_completed': step.is_completed,
                'estimated_duration_days': step.estimated_duration_days,
                'guidance': step.guidance,
                'icon': get_step_type_icon(step.step_type)
            })
        
        return jsonify({
            'next_steps': steps_data
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@journey_bp.route('/api/case/<int:case_id>/suggestions')
@login_required
def get_action_suggestions(case_id):
    """API endpoint to get action suggestions"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        journey_manager = LegalJourneyManager()
        suggestions = journey_manager.suggest_next_actions(case)
        
        return jsonify({
            'suggestions': suggestions
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@journey_bp.route('/api/step/<int:step_id>/guidance')
@login_required
def get_step_guidance(step_id):
    """API endpoint to get personalized guidance for a step"""
    step = JourneyStep.query.get_or_404(step_id)
    stage = JourneyStage.query.get(step.stage_id)
    case = Case.query.filter_by(id=stage.case_id, user_id=current_user.id).first_or_404()
    
    try:
        journey_manager = LegalJourneyManager()
        guidance = journey_manager.get_personalized_guidance(case, step)
        
        return jsonify(guidance)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'standard_guidance': step.guidance
        }), 500

@journey_bp.route('/dashboard')
@login_required
def journey_dashboard():
    """Dashboard showing all user's legal journeys"""
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    
    journey_data = []
    journey_manager = LegalJourneyManager()
    
    for case in user_cases:
        # Check if case has a journey
        has_journey = JourneyStage.query.filter_by(case_id=case.id).first() is not None
        
        if has_journey:
            progress = journey_manager.get_journey_progress(case)
        else:
            progress = {
                'total_stages': 0,
                'completed_stages': 0,
                'progress_percentage': 0,
                'current_stage': None
            }
        
        journey_data.append({
            'case': case,
            'progress': progress,
            'has_journey': has_journey
        })
    
    return render_template('journey/dashboard.html', journey_data=journey_data)

@journey_bp.route('/help')
@login_required
def journey_help():
    """Help page explaining the legal journey system"""
    return render_template('journey/help.html')

# Integration with case routes
@journey_bp.route('/case/<int:case_id>/quick-actions')
@login_required
def quick_actions(case_id):
    """Get quick actions for a case journey"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    journey_manager = LegalJourneyManager()
    suggestions = journey_manager.suggest_next_actions(case)
    next_steps = journey_manager.get_next_steps(case, limit=3)
    
    return render_template('journey/quick_actions.html', 
                         case=case, 
                         suggestions=suggestions,
                         next_steps=next_steps,
                         get_step_icon=get_step_type_icon)