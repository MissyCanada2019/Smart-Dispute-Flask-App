from flask import Blueprint, render_template, redirect, url_for, flash
from models import db
from models.user import User
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Access denied: Admins only', 'danger')
        return redirect(url_for('dashboard.main'))
    return render_template('admin/dashboard.html')

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied: Admins only', 'danger')
        return redirect(url_for('dashboard.main'))
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)
