"""
Case Tracking Routes
Handles case progress monitoring, milestone tracking, and statistics
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.case import Case
from models import db
from utils.case_tracking import CaseTracker, MilestoneType
from datetime import datetime, timedelta
import json

tracking_bp = Blueprint('tracking', __name__, url_prefix='/tracking')

@tracking_bp.route('/case/<int:case_id>')
@login_required
def case_progress(case_id):
    """Display case progress tracking page"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        flash('Case not found or access denied', 'error')
        return redirect(url_for('cases.list_cases'))
    
    tracker = CaseTracker()
    progress_data = tracker.get_case_progress(case_id)
    
    return render_template('tracking/case_progress.html', 
                         case=case, 
                         progress=progress_data)

@tracking_bp.route('/api/case/<int:case_id>/progress')
@login_required
def api_case_progress(case_id):
    """API endpoint for case progress data"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        return jsonify({'error': 'Case not found or access denied'}), 404
    
    tracker = CaseTracker()
    progress_data = tracker.get_case_progress(case_id)
    
    return jsonify(progress_data)

@tracking_bp.route('/api/case/<int:case_id>/milestones')
@login_required
def api_case_milestones(case_id):
    """API endpoint for case milestones"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        return jsonify({'error': 'Case not found or access denied'}), 404
    
    tracker = CaseTracker()
    milestones = tracker._get_case_milestones(case_id)
    
    return jsonify({
        'case_id': case_id,
        'milestones': milestones
    })

@tracking_bp.route('/api/case/<int:case_id>/next-actions')
@login_required
def api_next_actions(case_id):
    """API endpoint for next recommended actions"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        return jsonify({'error': 'Case not found or access denied'}), 404
    
    tracker = CaseTracker()
    progress_data = tracker.get_case_progress(case_id)
    
    return jsonify({
        'case_id': case_id,
        'next_actions': progress_data.get('next_actions', []),
        'current_stage': progress_data.get('current_stage', 'preparation'),
        'blocking_issues': progress_data.get('blocking_issues', [])
    })

@tracking_bp.route('/api/user/statistics')
@login_required
def api_user_statistics():
    """API endpoint for user's overall case statistics"""
    tracker = CaseTracker()
    stats = tracker.get_case_statistics(current_user.id)
    
    return jsonify(stats)

@tracking_bp.route('/overview')
@login_required
def progress_overview():
    """Display progress overview for all user cases"""
    user_cases = Case.query.filter_by(user_id=current_user.id).order_by(Case.updated_at.desc()).all()
    
    tracker = CaseTracker()
    
    # Get progress for each case
    cases_progress = []
    for case in user_cases:
        progress_data = tracker.get_case_progress(case.id)
        cases_progress.append({
            'case': case,
            'progress': progress_data
        })
    
    # Get overall statistics
    stats = tracker.get_case_statistics(current_user.id)
    
    return render_template('tracking/progress_overview.html', 
                         cases_progress=cases_progress,
                         stats=stats)

@tracking_bp.route('/milestone/add', methods=['POST'])
@login_required
def add_milestone():
    """Add a custom milestone to a case"""
    try:
        data = request.get_json()
        case_id = data.get('case_id')
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        milestone_date = data.get('date')
        
        if not case_id or not title:
            return jsonify({'success': False, 'error': 'Case ID and title are required'}), 400
        
        # Verify user owns the case
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            return jsonify({'success': False, 'error': 'Case not found or access denied'}), 404
        
        tracker = CaseTracker()
        
        # Parse date if provided
        custom_data = {}
        if milestone_date:
            try:
                parsed_date = datetime.fromisoformat(milestone_date.replace('Z', '+00:00'))
                custom_data['date'] = parsed_date.isoformat()
            except:
                pass
        
        success = tracker.record_milestone(
            case_id=case_id,
            milestone_type=MilestoneType.CUSTOM,
            title=title,
            description=description,
            custom_data=custom_data
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Milestone added successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to add milestone'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tracking_bp.route('/api/case/<int:case_id>/timeline')
@login_required
def api_case_timeline(case_id):
    """API endpoint for detailed case timeline"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        return jsonify({'error': 'Case not found or access denied'}), 404
    
    # Build comprehensive timeline from various sources
    timeline_events = []
    
    # Case events
    timeline_events.append({
        'type': 'case_created',
        'title': 'Case Created',
        'description': f'Case "{case.title}" was created',
        'date': case.created_at.isoformat() if case.created_at else None,
        'icon': 'fas fa-plus-circle',
        'color': 'success'
    })
    
    # Evidence events
    from models.evidence import Evidence
    evidence_list = Evidence.query.filter_by(case_id=case_id).order_by(Evidence.uploaded_at).all()
    for evidence in evidence_list:
        timeline_events.append({
            'type': 'evidence_uploaded',
            'title': 'Evidence Uploaded',
            'description': f'Uploaded "{evidence.title}"',
            'date': evidence.uploaded_at.isoformat() if evidence.uploaded_at else None,
            'icon': 'fas fa-file-upload',
            'color': 'info',
            'details': {
                'evidence_id': evidence.id,
                'filename': evidence.original_filename,
                'relevance_score': evidence.ai_relevance_score
            }
        })
        
        if evidence.analyzed_at:
            timeline_events.append({
                'type': 'evidence_analyzed',
                'title': 'Evidence Analyzed',
                'description': f'AI analysis completed for "{evidence.title}"',
                'date': evidence.analyzed_at.isoformat(),
                'icon': 'fas fa-brain',
                'color': 'purple',
                'details': {
                    'evidence_id': evidence.id,
                    'relevance_score': evidence.ai_relevance_score
                }
            })
    
    # Form events
    from models.court_form import CourtForm
    court_forms = CourtForm.query.filter_by(case_id=case_id).order_by(CourtForm.created_at).all()
    for form in court_forms:
        timeline_events.append({
            'type': 'form_created',
            'title': 'Form Created',
            'description': f'Created {form.form_name}',
            'date': form.created_at.isoformat() if form.created_at else None,
            'icon': 'fas fa-file-alt',
            'color': 'primary',
            'details': {
                'form_id': form.id,
                'form_name': form.form_name
            }
        })
        
        if form.updated_at and form.updated_at != form.created_at:
            timeline_events.append({
                'type': 'form_updated',
                'title': 'Form Updated',
                'description': f'Updated {form.form_name}',
                'date': form.updated_at.isoformat(),
                'icon': 'fas fa-edit',
                'color': 'warning',
                'details': {
                    'form_id': form.id,
                    'form_name': form.form_name,
                    'status': form.status.value if form.status else 'draft'
                }
            })
    
    # Legal journey events
    from models.legal_journey import LegalJourney
    legal_journey = LegalJourney.query.filter_by(case_id=case_id).first()
    if legal_journey:
        timeline_events.append({
            'type': 'journey_started',
            'title': 'Legal Journey Started',
            'description': f'Started guided legal process',
            'date': legal_journey.created_at.isoformat() if legal_journey.created_at else None,
            'icon': 'fas fa-route',
            'color': 'secondary'
        })
        
        if legal_journey.current_stage_index > 0:
            timeline_events.append({
                'type': 'stage_progress',
                'title': 'Stage Progress',
                'description': f'Advanced to stage {legal_journey.current_stage_index + 1}',
                'date': legal_journey.updated_at.isoformat() if legal_journey.updated_at else None,
                'icon': 'fas fa-step-forward',
                'color': 'success'
            })
    
    # Sort timeline by date
    timeline_events.sort(key=lambda x: x['date'] or '9999-12-31', reverse=True)
    
    return jsonify({
        'case_id': case_id,
        'timeline': timeline_events,
        'total_events': len(timeline_events)
    })

@tracking_bp.route('/api/progress-summary')
@login_required
def api_progress_summary():
    """API endpoint for progress summary across all cases"""
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    tracker = CaseTracker()
    
    summary = {
        'total_cases': len(user_cases),
        'cases_by_progress': {
            'not_started': 0,
            'in_progress': 0,
            'near_completion': 0,
            'completed': 0
        },
        'urgent_actions': [],
        'recent_activity': [],
        'progress_distribution': []
    }
    
    all_actions = []
    
    for case in user_cases:
        progress_data = tracker.get_case_progress(case.id)
        overall_progress = progress_data.get('overall_progress', 0)
        
        # Categorize by progress
        if overall_progress == 0:
            summary['cases_by_progress']['not_started'] += 1
        elif overall_progress < 75:
            summary['cases_by_progress']['in_progress'] += 1
        elif overall_progress < 100:
            summary['cases_by_progress']['near_completion'] += 1
        else:
            summary['cases_by_progress']['completed'] += 1
        
        # Collect urgent actions
        next_actions = progress_data.get('next_actions', [])
        for action in next_actions:
            if action.get('priority') in ['high', 'urgent']:
                action['case_title'] = case.title
                action['case_id'] = case.id
                all_actions.append(action)
        
        # Add to progress distribution
        summary['progress_distribution'].append({
            'case_id': case.id,
            'case_title': case.title,
            'progress': overall_progress,
            'current_stage': progress_data.get('current_stage', 'preparation')
        })
    
    # Sort urgent actions by priority
    priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
    all_actions.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    summary['urgent_actions'] = all_actions[:5]  # Top 5 urgent actions
    
    return jsonify(summary)

@tracking_bp.route('/widget/progress/<int:case_id>')
@login_required
def progress_widget(case_id):
    """Render progress widget for embedding in other pages"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        return "Case not found", 404
    
    tracker = CaseTracker()
    progress_data = tracker.get_case_progress(case_id)
    
    return render_template('tracking/progress_widget.html',
                         case=case,
                         progress=progress_data)

@tracking_bp.route('/export/<int:case_id>')
@login_required
def export_progress_report(case_id):
    """Export case progress report"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        flash('Case not found or access denied', 'error')
        return redirect(url_for('cases.list_cases'))
    
    tracker = CaseTracker()
    progress_data = tracker.get_case_progress(case_id)
    
    # For now, render a printable report
    # In the future, this could generate PDF or other formats
    return render_template('tracking/progress_report.html',
                         case=case,
                         progress=progress_data,
                         generated_at=datetime.utcnow())

# Error handlers
@tracking_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@tracking_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access denied'}), 403