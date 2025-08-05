"""
Payment Routes
E-transfer payment processing for Canadian legal services
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.payment_system import payment_manager
from models.case import Case
from utils.db import db  # Corrected import
import logging

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')
logger = logging.getLogger(__name__)

@payment_bp.route('/')
@login_required
def payment_dashboard():
    """Payment dashboard showing user's payment history"""
    try:
        user_payments = payment_manager.get_user_payments(current_user.id)
        return render_template('payment/dashboard.html', payments=user_payments)
    except Exception as e:
        logger.error(f"Error loading payment dashboard: {str(e)}")
        flash('Error loading payment information', 'error')
        return redirect(url_for('dashboard.main'))

@payment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_payment():
    """Create a new payment request"""
    if request.method == 'POST':
        try:
            service_type = request.form.get('service_type')
            case_id = request.form.get('case_id', type=int)
            custom_amount = request.form.get('custom_amount', type=float)
            
            if not service_type:
                flash('Service type is required', 'error')
                return render_template('payment/create.html')
            
            # Payment creation logic
            payment = payment_manager.create_payment(
                user_id=current_user.id,
                service_type=service_type,
                amount=custom_amount,
                case_id=case_id
            )
            db.session.add(payment)
            db.session.commit()
            
            return redirect(url_for('payment.payment_details', payment_id=payment.id))
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            flash('Error creating payment. Please try again.', 'error')
            return render_template('payment/create.html')
    
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template('payment/create.html', cases=user_cases)

@payment_bp.route('/details/<int:payment_id>')
@login_required
def payment_details(payment_id):
    """View payment details and initiate payment"""
    payment = payment_manager.get_payment(payment_id)
    if not payment or payment.user_id != current_user.id:
        flash('Payment not found', 'error')
        return redirect(url_for('payment.payment_dashboard'))
    
    return render_template('payment/details.html', payment=payment)