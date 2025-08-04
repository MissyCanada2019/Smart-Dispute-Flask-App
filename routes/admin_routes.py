from flask import Blueprint, render_template, redirect, url_for, flash
from utils.db import db
from models.user import User
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Access denied: Admins only', 'danger')
        return redirect(url_for('dashboard.main'))
    
    users = db.session.query(User).all()
    return render_template('admin/dashboard.html', users=users)

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied: Admins only', 'danger')
        return redirect(url_for('dashboard.main'))
    
    users = db.session.query(User).all()
    return render_template('admin/manage_users.html', users=users)
