from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.db import get_session  # Import get_session instead of Session
from models.case import cases, Case  # Import the Table and helper class
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
        session = get_session()
        try:
            insert_stmt = cases.insert().values(
                title=new_case.title,
                description=new_case.description,
                case_type=new_case.case_type,
                province=new_case.province,
                user_id=new_case.user_id
            )
            result = session.execute(insert_stmt)
            new_case.id = result.inserted_primary_key[0]
            session.commit()
            flash('Case created successfully', 'success')
            return redirect(url_for('case.view_case', case_id=new_case.id))
        except Exception as e:
            session.rollback()
            flash(f'Error creating case: {str(e)}', 'danger')
        finally:
            session.close()
    return render_template('cases/create.html')

@case_bp.route('/list')
@login_required
def list_cases():
    session = get_session()
    try:
        # Query cases for the current user
        query = cases.select().where(cases.c.user_id == current_user.id)
        result = session.execute(query)
        user_cases = [Case(**row) for row in result]
        return render_template('cases/list.html', cases=user_cases)
    finally:
        session.close()

@case_bp.route('/view/<int:case_id>')
@login_required
def view_case(case_id):
    session = get_session()
    try:
        # Query case by ID
        query = cases.select().where(cases.c.id == case_id)
        result = session.execute(query)
        case_data = result.fetchone()
        
        if not case_data:
            flash('Case not found', 'danger')
            return redirect(url_for('case.list_cases'))
        
        case = Case(**case_data)
        return render_template('cases/view.html', case=case)
    finally:
        session.close()