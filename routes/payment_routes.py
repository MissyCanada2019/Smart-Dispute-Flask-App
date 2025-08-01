"""
Payment Routes
E-transfer payment processing for Canadian legal services
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.payment_system import payment_manager
from models.case import Case
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
            
            # Verify case belongs to user if specified
            if case_id:
                case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
                if not case:
                    flash('Invalid case selected', 'error')
                    return render_template('payment/create.html')
            
            # Create payment request
            result = payment_manager.create_payment_request(
                user_id=current_user.id,
                service_type=service_type,
                case_id=case_id,
                custom_amount=custom_amount
            )
            
            if result['success']:
                flash('Payment request created successfully', 'success')
                return redirect(url_for('payment.payment_instructions', 
                                      payment_reference=result['payment_reference']))
            else:
                flash(f'Error creating payment: {result["error"]}', 'error')
                
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            flash('An error occurred while creating the payment request', 'error')
    
    # Get user's cases for the form
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    service_prices = payment_manager.SERVICE_PRICES
    
    return render_template('payment/create.html', 
                         cases=user_cases, 
                         service_prices=service_prices)

@payment_bp.route('/instructions/<payment_reference>')
@login_required
def payment_instructions(payment_reference):
    """Display payment instructions for e-transfer"""
    try:
        payment_status = payment_manager.get_payment_status(payment_reference)
        
        if not payment_status['success']:
            flash('Payment reference not found', 'error')
            return redirect(url_for('payment.payment_dashboard'))
        
        # Verify payment belongs to current user
        user_payments = payment_manager.get_user_payments(current_user.id)
        payment_data = None
        
        for payment in user_payments:
            if payment.get('id') == payment_reference:
                payment_data = payment
                break
        
        if not payment_data:
            flash('Payment not found or access denied', 'error')
            return redirect(url_for('payment.payment_dashboard'))
        
        return render_template('payment/instructions.html', 
                             payment=payment_data,
                             etransfer_email=payment_manager.ETRANSFER_EMAIL)
        
    except Exception as e:
        logger.error(f"Error loading payment instructions: {str(e)}")
        flash('Error loading payment instructions', 'error')
        return redirect(url_for('payment.payment_dashboard'))

@payment_bp.route('/status/<payment_reference>')
@login_required
def payment_status(payment_reference):
    """Check payment status"""
    try:
        result = payment_manager.get_payment_status(payment_reference)
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(result)
        
        if not result['success']:
            flash('Payment reference not found', 'error')
            return redirect(url_for('payment.payment_dashboard'))
        
        return render_template('payment/status.html', payment=result)
        
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error checking payment status'
        })

@payment_bp.route('/verify/<payment_reference>', methods=['POST'])
@login_required
def verify_payment(payment_reference):
    """Manual payment verification (admin only for now)"""
    try:
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        verification_data = {
            'verified_by': current_user.id,
            'verification_method': 'manual',
            'notes': request.json.get('notes', '')
        }
        
        result = payment_manager.verify_payment(payment_reference, verification_data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@payment_bp.route('/api/pricing')
def api_pricing():
    """API endpoint for service pricing"""
    return jsonify({
        'success': True,
        'pricing': payment_manager.SERVICE_PRICES,
        'currency': 'CAD',
        'etransfer_email': payment_manager.ETRANSFER_EMAIL
    })

@payment_bp.route('/webhook/etransfer', methods=['POST'])
def etransfer_webhook():
    """Webhook endpoint for e-transfer notifications (future integration)"""
    try:
        # This would be used for automatic payment verification
        # when integrated with banking APIs
        logger.info("E-transfer webhook received")
        
        # Verify webhook signature here
        # Parse payment notification
        # Update payment status automatically
        
        return jsonify({
            'success': True,
            'message': 'Webhook received'
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@payment_bp.errorhandler(404)
def not_found(error):
    return render_template('payment/404.html'), 404

@payment_bp.errorhandler(500)
def internal_error(error):
    return render_template('payment/500.html'), 500