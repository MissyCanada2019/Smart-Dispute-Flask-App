from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db
from models.case import Case
from utils.dashboard import DashboardManager, format_time_ago, get_urgency_class
import json
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def main_dashboard():
    """Main user dashboard"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if not dashboard_data['success']:
            flash(f'Error loading dashboard: {dashboard_data.get("error", "Unknown error")}', 'error')
            return redirect(url_for('index'))
        
        return render_template('dashboard/main.html', 
                             data=dashboard_data,
                             format_time_ago=format_time_ago,
                             get_urgency_class=get_urgency_class)
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@dashboard_bp.route('/analytics')
@login_required
def analytics_dashboard():
    """Analytics and insights dashboard"""
    try:
        dashboard_manager = DashboardManager()
        analytics_data = dashboard_manager.get_case_analytics(current_user.id)
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        return render_template('dashboard/analytics.html', 
                             analytics=analytics_data,
                             dashboard_data=dashboard_data)
    
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@dashboard_bp.route('/api/metrics')
@login_required
def get_dashboard_metrics():
    """API endpoint to get dashboard metrics"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            return jsonify({
                'success': True,
                'metrics': dashboard_data['metrics']
            })
        else:
            return jsonify({
                'success': False,
                'error': dashboard_data.get('error', 'Unknown error')
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/recent-activity')
@login_required
def get_recent_activity():
    """API endpoint to get recent activity"""
    try:
        limit = request.args.get('limit', 10, type=int)
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            activities = dashboard_data['recent_activity'][:limit]
            
            # Format activities for JSON response
            formatted_activities = []
            for activity in activities:
                formatted_activity = activity.copy()
                if 'timestamp' in formatted_activity and formatted_activity['timestamp']:
                    formatted_activity['timestamp'] = formatted_activity['timestamp'].isoformat()
                    formatted_activity['time_ago'] = format_time_ago(activity['timestamp'])
                formatted_activities.append(formatted_activity)
            
            return jsonify({
                'success': True,
                'activities': formatted_activities
            })
        else:
            return jsonify({
                'success': False,
                'error': dashboard_data.get('error', 'Unknown error')
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/deadlines')
@login_required
def get_upcoming_deadlines():
    """API endpoint to get upcoming deadlines"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            deadlines = dashboard_data['upcoming_deadlines']
            
            # Format deadlines for JSON response
            formatted_deadlines = []
            for deadline in deadlines:
                formatted_deadline = deadline.copy()
                if 'date' in formatted_deadline:
                    formatted_deadline['date'] = formatted_deadline['date'].isoformat()
                if 'time' in formatted_deadline and formatted_deadline['time']:
                    formatted_deadline['time'] = formatted_deadline['time'].isoformat()
                formatted_deadlines.append(formatted_deadline)
            
            return jsonify({
                'success': True,
                'deadlines': formatted_deadlines
            })
        else:
            return jsonify({
                'success': False,
                'error': dashboard_data.get('error', 'Unknown error')
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/actionable-items')
@login_required
def get_actionable_items():
    """API endpoint to get actionable items"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            return jsonify({
                'success': True,
                'actionable_items': dashboard_data['actionable_items']
            })
        else:
            return jsonify({
                'success': False,
                'error': dashboard_data.get('error', 'Unknown error')
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/analytics')
@login_required
def get_analytics_data():
    """API endpoint to get analytics data"""
    try:
        dashboard_manager = DashboardManager()
        analytics_data = dashboard_manager.get_case_analytics(current_user.id)
        
        return jsonify(analytics_data)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/quick-actions')
@login_required
def quick_actions():
    """Quick actions page for common tasks"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        # Get user's cases for quick actions
        user_cases = Case.query.filter_by(user_id=current_user.id).order_by(Case.updated_at.desc()).limit(10).all()
        
        return render_template('dashboard/quick_actions.html',
                             cases=user_cases,
                             actionable_items=dashboard_data.get('actionable_items', []) if dashboard_data['success'] else [])
    
    except Exception as e:
        flash(f'Error loading quick actions: {str(e)}', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@dashboard_bp.route('/notifications')
@login_required
def notifications():
    """Notifications management page"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        notifications = dashboard_data.get('notifications', []) if dashboard_data['success'] else []
        
        return render_template('dashboard/notifications.html',
                             notifications=notifications)
    
    except Exception as e:
        flash(f'Error loading notifications: {str(e)}', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@dashboard_bp.route('/help')
@login_required
def dashboard_help():
    """Dashboard help and guide"""
    return render_template('dashboard/help.html')

# Widget endpoints for AJAX loading
@dashboard_bp.route('/widgets/case-summary')
@login_required
def case_summary_widget():
    """Case summary widget"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            return render_template('dashboard/widgets/case_summary.html',
                                 cases=dashboard_data['cases'],
                                 metrics=dashboard_data['metrics'])
        else:
            return render_template('dashboard/widgets/error.html',
                                 error="Failed to load case summary")
    
    except Exception as e:
        return render_template('dashboard/widgets/error.html',
                             error=str(e))

@dashboard_bp.route('/widgets/recent-activity')
@login_required
def recent_activity_widget():
    """Recent activity widget"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            return render_template('dashboard/widgets/recent_activity.html',
                                 activities=dashboard_data['recent_activity'],
                                 format_time_ago=format_time_ago)
        else:
            return render_template('dashboard/widgets/error.html',
                                 error="Failed to load recent activity")
    
    except Exception as e:
        return render_template('dashboard/widgets/error.html',
                             error=str(e))

@dashboard_bp.route('/widgets/upcoming-deadlines')
@login_required
def upcoming_deadlines_widget():
    """Upcoming deadlines widget"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            return render_template('dashboard/widgets/upcoming_deadlines.html',
                                 deadlines=dashboard_data['upcoming_deadlines'],
                                 get_urgency_class=get_urgency_class)
        else:
            return render_template('dashboard/widgets/error.html',
                                 error="Failed to load deadlines")
    
    except Exception as e:
        return render_template('dashboard/widgets/error.html',
                             error=str(e))

@dashboard_bp.route('/widgets/actionable-items')
@login_required
def actionable_items_widget():
    """Actionable items widget"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            return render_template('dashboard/widgets/actionable_items.html',
                                 items=dashboard_data['actionable_items'])
        else:
            return render_template('dashboard/widgets/error.html',
                                 error="Failed to load actionable items")
    
    except Exception as e:
        return render_template('dashboard/widgets/error.html',
                             error=str(e))

# Auto-refresh endpoint for real-time updates
@dashboard_bp.route('/api/refresh')
@login_required
def refresh_dashboard():
    """Refresh dashboard data for real-time updates"""
    try:
        dashboard_manager = DashboardManager()
        dashboard_data = dashboard_manager.get_user_dashboard_data(current_user.id)
        
        if dashboard_data['success']:
            # Format data for JSON response
            response_data = {
                'success': True,
                'metrics': dashboard_data['metrics'],
                'recent_activity_count': len(dashboard_data['recent_activity']),
                'deadlines_count': len(dashboard_data['upcoming_deadlines']),
                'actionable_items_count': len(dashboard_data['actionable_items']),
                'notifications_count': len(dashboard_data['notifications']),
                'last_updated': dashboard_data['generated_at']
            }
            
            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'error': dashboard_data.get('error', 'Unknown error')
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500