from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from models.user import User
from models import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    if not current_user.is_admin:
        return "Unauthorized", 403
    return render_template('admin.html')

@admin_bp.route('/users')
@login_required
def list_users():
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    users = User.query.all()
    return jsonify([{"email": u.email, "is_admin": u.is_admin} for u in users])
