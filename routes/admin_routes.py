"""
Admin Routes
Administrative tools for managing form templates, legal workflows, and system configuration
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db
from models.user import User
from models.case import Case
from models.court_form import FormTemplate, FormField, FormSubmission
from models.evidence import Evidence
from utils.form_templates import FormTemplateManager
from utils.notification_system import notification_manager
from models.notification import NotificationType, NotificationPriority
import json
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    # Get system statistics
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_cases': Case.query.count(),
        'total_forms': FormSubmission.query.count(),
        'completed_forms': FormSubmission.query.filter_by(status='completed').count(),
        'total_evidence': Evidence.query.count(),
        'form_templates': FormTemplate.query.filter_by(is_active=True).count()
    }
    
    # Get recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_cases = Case.query.order_by(Case.created_at.desc()).limit(5).all()
    recent_forms = FormSubmission.query.order_by(FormSubmission.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_users=recent_users,
                         recent_cases=recent_cases,
                         recent_forms=recent_forms)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """User management interface"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.email.contains(search))
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/manage_users.html', users=users, search=search)

@admin_bp.route('/forms')
@login_required
@admin_required
def manage_forms():
    """Form template management interface"""
    templates = FormTemplate.query.order_by(FormTemplate.province, FormTemplate.name).all()
    
    # Group by province
    templates_by_province = {}
    for template in templates:
        if template.province not in templates_by_province:
            templates_by_province[template.province] = []
        templates_by_province[template.province].append(template)
    
    return render_template('admin/manage_forms.html', 
                         templates_by_province=templates_by_province)

@admin_bp.route('/forms/template/<int:template_id>')
@login_required
@admin_required
def edit_template(template_id):
    """Edit form template"""
    template = FormTemplate.query.get_or_404(template_id)
    fields = FormField.query.filter_by(template_id=template_id).order_by(FormField.order).all()
    
    return render_template('admin/edit_template.html', template=template, fields=fields)

@admin_bp.route('/forms/template/<int:template_id>/update', methods=['POST'])
@login_required
@admin_required
def update_template(template_id):
    """Update form template"""
    template = FormTemplate.query.get_or_404(template_id)
    
    try:
        template.name = request.form.get('name', '').strip()
        template.description = request.form.get('description', '').strip()
        template.category = request.form.get('category', '').strip()
        template.case_type = request.form.get('case_type', '').strip()
        template.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Template updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating template: {str(e)}', 'error')
    
    return redirect(url_for('admin.edit_template', template_id=template_id))

@admin_bp.route('/forms/template/<int:template_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_template(template_id):
    """Toggle template active status"""
    template = FormTemplate.query.get_or_404(template_id)
    
    try:
        template.is_active = not template.is_active
        db.session.commit()
        
        status = 'activated' if template.is_active else 'deactivated'
        flash(f'Template {status} successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating template: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_forms'))

@admin_bp.route('/forms/initialize-templates', methods=['POST'])
@login_required
@admin_required
def initialize_templates():
    """Initialize default form templates"""
    try:
        created_count = FormTemplateManager.initialize_default_templates()
        flash(f'Successfully initialized {created_count} form templates', 'success')
        
    except Exception as e:
        flash(f'Error initializing templates: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_forms'))

@admin_bp.route('/system')
@login_required
@admin_required
def system_settings():
    """System settings and configuration"""
    return render_template('admin/system_settings.html')

@admin_bp.route('/notifications')
@login_required
@admin_required
def manage_notifications():
    """Notification management interface"""
    # Get notification statistics
    from models.notification import Notification
    
    stats = {
        'total_notifications': Notification.query.count(),
        'unread_notifications': Notification.query.filter_by(is_read=False).count(),
        'urgent_notifications': Notification.query.filter_by(priority='urgent').count(),
        'notifications_today': Notification.query.filter(
            Notification.created_at >= datetime.utcnow().date()
        ).count()
    }
    
    # Get recent notifications
    recent_notifications = Notification.query.order_by(
        Notification.created_at.desc()
    ).limit(20).all()
    
    return render_template('admin/manage_notifications.html', 
                         stats=stats,
                         recent_notifications=recent_notifications)

@admin_bp.route('/notifications/broadcast', methods=['GET', 'POST'])
@login_required
@admin_required
def broadcast_notification():
    """Send broadcast notification to all users"""
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            message = request.form.get('message', '').strip()
            priority = request.form.get('priority', 'medium')
            user_filter = request.form.get('user_filter', 'all')
            
            if not title or not message:
                flash('Title and message are required', 'error')
                return render_template('admin/broadcast_notification.html')
            
            # Get target users
            if user_filter == 'active':
                users = User.query.filter_by(is_active=True).all()
            elif user_filter == 'admins':
                users = User.query.filter_by(is_admin=True).all()
            else:
                users = User.query.all()
            
            # Send notifications
            sent_count = 0
            for user in users:
                success = notification_manager.create_notification(
                    user_id=user.id,
                    notification_type=NotificationType.SYSTEM,
                    title=title,
                    message=message,
                    priority=NotificationPriority(priority)
                )
                if success:
                    sent_count += 1
            
            flash(f'Broadcast sent to {sent_count} users successfully', 'success')
            return redirect(url_for('admin.manage_notifications'))
            
        except Exception as e:
            flash(f'Error sending broadcast: {str(e)}', 'error')
    
    return render_template('admin/broadcast_notification.html')

@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_system_stats():
    """API endpoint for system statistics"""
    stats = {
        'users': {
            'total': User.query.count(),
            'active': User.query.filter_by(is_active=True).count(),
            'admins': User.query.filter_by(is_admin=True).count(),
            'new_this_week': User.query.filter(
                User.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        },
        'cases': {
            'total': Case.query.count(),
            'active': Case.query.filter_by(status='active').count(),
            'completed': Case.query.filter_by(status='completed').count(),
            'new_this_week': Case.query.filter(
                Case.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        },
        'forms': {
            'total': FormSubmission.query.count(),
            'completed': FormSubmission.query.filter_by(status='completed').count(),
            'draft': FormSubmission.query.filter_by(status='draft').count(),
            'new_this_week': FormSubmission.query.filter(
                FormSubmission.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        },
        'evidence': {
            'total': Evidence.query.count(),
            'analyzed': Evidence.query.filter_by(status='analyzed').count(),
            'high_relevance': Evidence.query.filter(Evidence.ai_relevance_score >= 0.8).count(),
            'new_this_week': Evidence.query.filter(
                Evidence.uploaded_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
    }
    
    return jsonify(stats)

@admin_bp.route('/logs')
@login_required
@admin_required
def view_logs():
    """View system logs"""
    return render_template('admin/logs.html')

@admin_bp.route('/payments')
@login_required
@admin_required
def manage_payments():
    """Payment management interface"""
    return render_template('admin/manage_payments.html')

# Error handlers
@admin_bp.errorhandler(403)
def forbidden(error):
    flash('Access denied - Admin privileges required', 'error')
    return redirect(url_for('index'))

@admin_bp.errorhandler(404)
def not_found(error):
    return render_template('admin/404.html'), 404
