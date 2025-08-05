"""
Payment System Integration
Handles e-transfer payments for Canadian legal services
"""

import logging
from datetime import datetime
from utils.db import db  # Corrected import
from models.payment import Payment, PaymentStatus

# Initialize logger
logger = logging.getLogger(__name__)

class PaymentManager:
    """Manages payment processing and tracking"""
    
    def create_payment(self, user_id, service_type, amount, case_id=None):
        """Create a new payment record"""
        payment = Payment(
            user_id=user_id,
            service_type=service_type,
            amount=amount,
            case_id=case_id,
            status=PaymentStatus.PENDING
        )
        db.session.add(payment)
        db.session.commit()
        return payment
    
    def process_payment(self, payment_id):
        """Process payment through e-transfer gateway"""
        payment = Payment.query.get(payment_id)
        if not payment:
            return None
        
        try:
            # Simplified payment processing logic
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()
            db.session.commit()
            return payment
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            db.session.rollback()
            return None
    
    def get_payment(self, payment_id):
        """Get payment by ID"""
        return Payment.query.get(payment_id)
    
    def get_user_payments(self, user_id):
        """Get all payments for a user"""
        return Payment.query.filter_by(user_id=user_id).all()

# Global payment manager instance
payment_manager = PaymentManager()