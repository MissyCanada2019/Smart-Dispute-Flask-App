from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from utils.db import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            # Validate input
            if not email or not password:
                flash('Email and password are required')
                return redirect(url_for('auth.login'))
                
            if '@' not in email or '.' not in email:
                flash('Please enter a valid email address')
                return redirect(url_for('auth.login'))
                
            if len(password) < 8:
                flash('Password must be at least 8 characters')
                return redirect(url_for('auth.login'))
            
            current_app.logger.debug(f"Attempting login for: {email}")
            
            user = db.session.query(User).filter_by(email=email).first()

            if not user:
                current_app.logger.warning(f"User not found: {email}")
                flash('Please check your login details and try again.')
                return redirect(url_for('auth.login'))
                
            if not user.check_password(password):
                current_app.logger.warning(f"Invalid password for: {email}")
                flash('Please check your login details and try again.')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            current_app.logger.info(f"User logged in: {email}")
            return redirect(url_for('dashboard.main'))
        except Exception as e:
            current_app.logger.exception(f"Login error for {email}: {str(e)}")  # Log full traceback
            flash(f'An error occurred during login: {str(e)}')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.register'))
        
        new_user = User(email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
