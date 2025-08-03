from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.db import get_session  # Import get_session instead of Session
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Get a new session instance
        session = get_session()
        try:
            user = session.query(User).filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                flash('Please check your login details and try again.')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            return redirect(url_for('dashboard.main'))
        finally:
            # Always close the session
            session.close()
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        # Get a new session instance
        session = get_session()
        try:
            # Check if user already exists
            user = session.query(User).filter_by(email=email).first()
            if user:
                flash('Email address already exists')
                return redirect(url_for('auth.register'))
            
            # Create new user
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
            
            # Add and commit
            session.add(new_user)
            session.commit()
            
            flash('Account created successfully!')
            return redirect(url_for('auth.login'))
        finally:
            session.close()
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
