from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.db import db
from models.case import Case
from flask_login import login_required, current_user

case_bp = Blueprint('case', __name__)

@case_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_case():
    if request.method == 'POST':
        # Extract form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        case_type = request.form.get('case_type', '').strip()
        province = request.form.get('province', '').strip()
        
        # Create a new case instance
        new_case = Case(
            title=title,
            description=description,
            case_type=case_type,
            province=province,
            user_id=current_user.id
        )
        
        # Insert into database
        try:
            db.session.add(new_case)
            db.session.commit()
            flash('Case created successfully', 'success')
            return redirect(url_for('case.view_case', case_id=new_case.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating case: {str(e)}', 'danger')
    return render_template('cases/create.html')

@case_bp.route('/list')
@login_required
def list_cases():
    user_cases = db.session.query(Case).filter_by(user_id=current_user.id).all()
    return render_template('cases/list.html', cases=user_cases)

@case_bp.route('/view/<int:case_id>')
@login_required
def view_case(case_id):
    case = db.session.query(Case).filter_by(id=case_id, user_id=current_user.id).first_or_404()
    return render_template('cases/view.html', case=case)