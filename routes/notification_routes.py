"""
Notification Routes
Handles user notifications, reminders, and alerts
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.notification import Notification, NotificationType, NotificationPriority
from models.case import Case
from models import db
from utils.notification_system import NotificationManager, DeadlineType, notification_manager
from datetime import datetime, timedelta
import json

notification_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notification_bp.route('/')
@login_required
def list_notifications():
    """Display user's notifications"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get notification summary
    summary = notification_manager.get_notification_summary(current_user.id)
    
    return render_template('notifications/list.html', 
                         notifications=notifications,
                         summary=summary)

@notification_bp.route('/api/list')
@login_required
def api_list_notifications():
    """API endpoint for notifications"""
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)
    
    notifications = notification_manager.get_user_notifications(
        current_user.id, unread_only=unread_only, limit=limit
    )
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'type': notification.notification_type.value,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority.value,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'case_id': notification.case_id,
            'case_title': notification.case.title if notification.case else None,
            'action_url': notification.action_url,
            'icon': get_notification_icon(notification.notification_type),
            'color': get_notification_color(notification.priority)
        })
    
    return jsonify({
        'notifications': notification_data,
        'total_count': len(notification_data)
    })

@notification_bp.route('/api/summary')
@login_required
def api_notification_summary():
    """API endpoint for notification summary"""
    summary = notification_manager.get_notification_summary(current_user.id)
    return jsonify(summary)

@notification_bp.route('/api/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def api_mark_read(notification_id):
    """Mark a notification as read"""
    success = notification_manager.mark_notification_read(notification_id, current_user.id)
    
    if success:
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    else:
        return jsonify({'success': False, 'error': 'Failed to mark notification as read'}), 400

@notification_bp.route('/api/mark-all-read', methods=['POST'])
@login_required
def api_mark_all_read():
    """Mark all notifications as read"""
    success = notification_manager.mark_all_read(current_user.id)
    
    if success:
        return jsonify({'success': True, 'message': 'All notifications marked as read'})
    else:
        return jsonify({'success': False, 'error': 'Failed to mark notifications as read'}), 400

@notification_bp.route('/api/delete/<int:notification_id>', methods=['DELETE'])
@login_required
def api_delete_notification(notification_id):
    """Delete a notification"""
    success = notification_manager.delete_notification(notification_id, current_user.id)
    
    if success:
        return jsonify({'success': True, 'message': 'Notification deleted'})
    else:
        return jsonify({'success': False, 'error': 'Failed to delete notification'}), 400

@notification_bp.route('/reminders')
@login_required
def list_reminders():
    """Display user's reminders and deadlines"""
    upcoming_deadlines = notification_manager.get_upcoming_deadlines(current_user.id, days_ahead=60)
    
    # Group deadlines by urgency
    overdue = [d for d in upcoming_deadlines if d['is_overdue']]
    urgent = [d for d in upcoming_deadlines if not d['is_overdue'] and d['days_until'] <= 3]
    upcoming = [d for d in upcoming_deadlines if not d['is_overdue'] and d['days_until'] > 3]
    
    return render_template('notifications/reminders.html',
                         overdue_deadlines=overdue,
                         urgent_deadlines=urgent,
                         upcoming_deadlines=upcoming)

@notification_bp.route('/create-reminder', methods=['GET', 'POST'])
@login_required
def create_reminder():
    """Create a custom reminder"""
    if request.method == 'POST':
        try:
            case_id = request.form.get('case_id', type=int)
            title = request.form.get('title', '').strip()
            message = request.form.get('message', '').strip()
            remind_date = request.form.get('remind_date')
            remind_time = request.form.get('remind_time', '09:00')
            deadline_type = request.form.get('deadline_type', 'custom')
            
            if not all([case_id, title, message, remind_date]):
                flash('All fields are required', 'error')
                return redirect(url_for('notifications.create_reminder'))
            
            # Verify user owns the case
            case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
            if not case:
                flash('Case not found or access denied', 'error')
                return redirect(url_for('notifications.create_reminder'))
            
            # Parse datetime
            remind_datetime_str = f"{remind_date} {remind_time}"
            remind_at = datetime.strptime(remind_datetime_str, '%Y-%m-%d %H:%M')
            
            # Create reminder
            success = notification_manager.create_custom_reminder(
                user_id=current_user.id,
                case_id=case_id,
                title=title,
                message=message,
                remind_at=remind_at,
                deadline_type=DeadlineType(deadline_type)
            )
            
            if success:
                flash('Reminder created successfully', 'success')
                return redirect(url_for('notifications.list_reminders'))
            else:
                flash('Failed to create reminder', 'error')
                
        except ValueError as e:
            flash('Invalid date or time format', 'error')
        except Exception as e:
            flash(f'Error creating reminder: {str(e)}', 'error')
    
    # Get user's cases for the form
    user_cases = Case.query.filter_by(user_id=current_user.id).order_by(Case.title).all()
    
    return render_template('notifications/create_reminder.html', cases=user_cases)

@notification_bp.route('/settings')
@login_required
def notification_settings():
    """Notification preferences and settings"""
    # For now, return a basic settings page
    # In the future, this could include email preferences, notification frequency, etc.
    return render_template('notifications/settings.html')

@notification_bp.route('/api/recent', methods=['GET'])
@login_required
def api_recent_notifications():
    """Get recent notifications for header/navbar display"""
    limit = request.args.get('limit', 5, type=int)
    
    recent = notification_manager.get_user_notifications(
        current_user.id, unread_only=True, limit=limit
    )
    
    notifications_data = []
    for notification in recent:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message[:100] + ('...' if len(notification.message) > 100 else ''),
            'priority': notification.priority.value,
            'created_at': notification.created_at.isoformat(),
            'time_ago': get_time_ago(notification.created_at),
            'action_url': notification.action_url,
            'icon': get_notification_icon(notification.notification_type),
            'color': get_notification_color(notification.priority)
        })
    
    unread_count = notification_manager.get_notification_summary(current_user.id)['unread_count']
    
    return jsonify({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@notification_bp.route('/widget')
@login_required
def notification_widget():
    """Render notification widget for embedding"""
    recent = notification_manager.get_user_notifications(
        current_user.id, unread_only=True, limit=3
    )
    
    summary = notification_manager.get_notification_summary(current_user.id)
    
    return render_template('notifications/widget.html', 
                         notifications=recent,
                         summary=summary)

@notification_bp.route('/test-notification', methods=['POST'])
@login_required
def test_notification():
    """Create a test notification (for development/testing)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    notification = notification_manager.create_notification(
        user_id=current_user.id,
        notification_type=NotificationType.SYSTEM,
        title="Test Notification",
        message="This is a test notification to verify the system is working correctly.",
        priority=NotificationPriority.LOW
    )
    
    if notification:
        return jsonify({'success': True, 'message': 'Test notification created'})
    else:
        return jsonify({'success': False, 'error': 'Failed to create test notification'}), 500

# Utility functions
def get_notification_icon(notification_type: NotificationType) -> str:
    """Get appropriate icon for notification type"""
    icons = {
        NotificationType.CASE_UPDATE: 'fas fa-folder',
        NotificationType.EVIDENCE_UPDATE: 'fas fa-file-upload',
        NotificationType.FORM_UPDATE: 'fas fa-file-alt',
        NotificationType.JOURNEY_UPDATE: 'fas fa-route',
        NotificationType.DEADLINE: 'fas fa-clock',
        NotificationType.REMINDER: 'fas fa-bell',
        NotificationType.PROGRESS_UPDATE: 'fas fa-chart-line',
        NotificationType.SYSTEM: 'fas fa-cog'
    }
    return icons.get(notification_type, 'fas fa-info-circle')

def get_notification_color(priority: NotificationPriority) -> str:
    """Get appropriate color for notification priority"""
    colors = {
        NotificationPriority.URGENT: 'danger',
        NotificationPriority.HIGH: 'warning',
        NotificationPriority.MEDIUM: 'info',
        NotificationPriority.LOW: 'secondary'
    }
    return colors.get(priority, 'secondary')

def get_time_ago(timestamp: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    delta = now - timestamp
    
    if delta.days > 0:
        return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

# Background task to check and create deadline reminders
def check_deadline_reminders():
    """Background task to check for deadline reminders"""
    try:
        created_count = notification_manager.check_and_create_deadline_reminders()
        print(f"Created {created_count} deadline reminder notifications")
        return created_count
    except Exception as e:
        print(f"Error in deadline reminder check: {str(e)}")
        return 0

# Background task to send daily digests
def send_daily_digests():
    """Background task to send daily digest notifications"""
    try:
        from models.user import User
        users = User.query.filter_by(is_active=True).all()
        
        sent_count = 0
        for user in users:
            success = notification_manager.send_daily_digest(user.id)
            if success:
                sent_count += 1
        
        print(f"Sent daily digests to {sent_count} users")
        return sent_count
        
    except Exception as e:
        print(f"Error sending daily digests: {str(e)}")
        return 0

# Background task to cleanup old notifications
def cleanup_old_notifications():
    """Background task to cleanup old notifications"""
    try:
        cleaned_count = notification_manager.cleanup_old_notifications(days_old=30)
        print(f"Cleaned up {cleaned_count} old notifications")
        return cleaned_count
    except Exception as e:
        print(f"Error cleaning up notifications: {str(e)}")
        return 0

# Error handlers
@notification_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Notification not found'}), 404

@notification_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access denied'}), 403