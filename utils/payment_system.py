faggikj"""
Payment System
E-transfer integration for Canadian legal services
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from models import db
from models.user import User
from models.case import Case
from utils.notification_system import notification_manager
from models.notification import NotificationType, NotificationPriority
import uuid
import json

logger = logging.getLogger(__name__)

class PaymentManager:
    """Manages e-transfer payments for legal services"""
    
    ETRANSFER_EMAIL = "admin@justice-bot.command"
    
    # Service pricing in CAD
    SERVICE_PRICES = {
        'case_analysis': 49.99,
        'form_assistance': 29.99,
        'document_review': 39.99,
        'full_service': 149.99,
        'consultation': 99.99,
        'premium_support': 199.99
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.PaymentManager')
    
    def create_payment_request(self, user_id: int, service_type: str, case_id: Optional[int] = None, 
                             custom_amount: Optional[float] = None) -> Dict[str, Any]:
        """Create a new payment request for e-transfer"""
        try:
            user = User.query.get_or_404(user_id)
            
            # Determine amount
            amount = custom_amount or self.SERVICE_PRICES.get(service_type, 49.99)
            
            # Generate unique payment reference
            payment_reference = f"JB-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create payment record
            payment_data = {
                'id': payment_reference,
                'user_id': user_id,
                'case_id': case_id,
                'service_type': service_type,
                'amount': amount,
                'currency': 'CAD',
                'status': 'pending',
                'etransfer_email': self.ETRANSFER_EMAIL,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=24),
                'payment_instructions': self._generate_payment_instructions(payment_reference, amount, service_type)
            }
            
            # Store payment data (in production, this would be in a payments table)
            self._store_payment_data(payment_reference, payment_data)
            
            # Send payment instructions to user
            self._send_payment_instructions(user, payment_data)
            
            # Log payment request
            self.logger.info(f"Payment request created: {payment_reference} for user {user_id}, amount ${amount}")
            
            return {
                'success': True,
                'payment_reference': payment_reference,
                'amount': amount,
                'currency': 'CAD',
                'etransfer_email': self.ETRANSFER_EMAIL,
                'expires_at': payment_data['expires_at'],
                'instructions': payment_data['payment_instructions']
            }
            
        except Exception as e:
            self.logger.error(f"Error creating payment request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_payment_instructions(self, payment_reference: str, amount: float, service_type: str) -> Dict[str, Any]:
        """Generate detailed payment instructions for e-transfer"""
        return {
            'recipient_email': self.ETRANSFER_EMAIL,
            'amount': amount,
            'currency': 'CAD',
            'reference': payment_reference,
            'message': f"Payment for {service_type.replace('_', ' ').title()} - Ref: {payment_reference}",
            'security_question': "What is your payment reference?",
            'security_answer': payment_reference,
            'steps': [
                "Log in to your online banking or mobile banking app",
                f"Select 'Send Money' or 'Interac e-Transfer'",
                f"Enter recipient email: {self.ETRANSFER_EMAIL}",
                f"Enter amount: ${amount:.2f} CAD",
                f"Security Question: 'What is your payment reference?'",
                f"Security Answer: '{payment_reference}'",
                f"Message/Memo: 'Payment for {service_type.replace('_', ' ').title()} - Ref: {payment_reference}'",
                "Send the e-transfer",
                "You will receive a confirmation email once payment is processed"
            ]
        }
    
    def _store_payment_data(self, payment_reference: str, payment_data: Dict[str, Any]):
        """Store payment data (temporary file-based storage for demo)"""
        try:
            import os
            import json
            
            # Create payments directory if it doesn't exist
            payments_dir = 'data/payments'
            os.makedirs(payments_dir, exist_ok=True)
            
            # Store payment data as JSON file
            payment_file = os.path.join(payments_dir, f"{payment_reference}.json")
            
            # Convert datetime objects to strings for JSON serialization
            serializable_data = payment_data.copy()
            for key, value in serializable_data.items():
                if isinstance(value, datetime):
                    serializable_data[key] = value.isoformat()
            
            with open(payment_file, 'w') as f:
                json.dump(serializable_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error storing payment data: {str(e)}")
    
    def _send_payment_instructions(self, user: User, payment_data: Dict[str, Any]):
        """Send payment instructions to user via notification"""
        try:
            instructions = payment_data['payment_instructions']
            
            message = f"""
Payment Request Created

Service: {payment_data['service_type'].replace('_', ' ').title()}
Amount: ${payment_data['amount']:.2f} CAD
Reference: {payment_data['id']}

E-Transfer Instructions:
• Send to: {instructions['recipient_email']}
• Amount: ${instructions['amount']:.2f} CAD
• Security Question: {instructions['security_question']}
• Security Answer: {instructions['security_answer']}
• Message: {instructions['message']}

Please complete payment within 24 hours. You will receive confirmation once processed.
            """.strip()
            
            notification_manager.create_notification(
                user_id=user.id,
                notification_type=NotificationType.PAYMENT,
                title="Payment Instructions - E-Transfer",
                message=message,
                priority=NotificationPriority.HIGH
            )
            
        except Exception as e:
            self.logger.error(f"Error sending payment instructions: {str(e)}")
    
    def verify_payment(self, payment_reference: str, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify e-transfer payment (manual verification for now)"""
        try:
            # In production, this would integrate with banking APIs
            payment_data = self._get_payment_data(payment_reference)
            
            if not payment_data:
                return {
                    'success': False,
                    'error': 'Payment reference not found'
                }
            
            # Update payment status
            payment_data['status'] = 'verified'
            payment_data['verified_at'] = datetime.utcnow()
            payment_data['verification_data'] = verification_data
            
            self._store_payment_data(payment_reference, payment_data)
            
            # Notify user of payment confirmation
            user = User.query.get(payment_data['user_id'])
            if user:
                notification_manager.create_notification(
                    user_id=user.id,
                    notification_type=NotificationType.PAYMENT,
                    title="Payment Confirmed",
                    message=f"Your payment of ${payment_data['amount']:.2f} CAD has been confirmed. Reference: {payment_reference}",
                    priority=NotificationPriority.HIGH
                )
            
            # Activate service
            self._activate_service(payment_data)
            
            return {
                'success': True,
                'payment_reference': payment_reference,
                'status': 'verified'
            }
            
        except Exception as e:
            self.logger.error(f"Error verifying payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_payment_data(self, payment_reference: str) -> Optional[Dict[str, Any]]:
        """Retrieve payment data"""
        try:
            import os
            import json
            
            payment_file = f"data/payments/{payment_reference}.json"
            
            if not os.path.exists(payment_file):
                return None
            
            with open(payment_file, 'r') as f:
                data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            for key, value in data.items():
                if key.endswith('_at') and isinstance(value, str):
                    try:
                        data[key] = datetime.fromisoformat(value)
                    except:
                        pass
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error retrieving payment data: {str(e)}")
            return None
    
    def _activate_service(self, payment_data: Dict[str, Any]):
        """Activate the paid service for the user"""
        try:
            user_id = payment_data['user_id']
            service_type = payment_data['service_type']
            case_id = payment_data.get('case_id')
            
            # Update user or case with service activation
            if case_id:
                case = Case.query.get(case_id)
                if case:
                    # Add service to case metadata
                    if not case.metadata:
                        case.metadata = {}
                    
                    if 'paid_services' not in case.metadata:
                        case.metadata['paid_services'] = []
                    
                    case.metadata['paid_services'].append({
                        'service_type': service_type,
                        'payment_reference': payment_data['id'],
                        'activated_at': datetime.utcnow().isoformat()
                    })
                    
                    db.session.commit()
            
            # Log service activation
            self.logger.info(f"Service activated: {service_type} for user {user_id}, payment {payment_data['id']}")
            
        except Exception as e:
            self.logger.error(f"Error activating service: {str(e)}")
    
    def get_user_payments(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all payments for a user"""
        try:
            import os
            import json
            
            payments_dir = 'data/payments'
            if not os.path.exists(payments_dir):
                return []
            
            user_payments = []
            
            for filename in os.listdir(payments_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(payments_dir, filename), 'r') as f:
                            payment_data = json.load(f)
                        
                        if payment_data.get('user_id') == user_id:
                            user_payments.append(payment_data)
                    except:
                        continue
            
            # Sort by creation date (newest first)
            user_payments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return user_payments
            
        except Exception as e:
            self.logger.error(f"Error getting user payments: {str(e)}")
            return []
    
    def get_payment_status(self, payment_reference: str) -> Dict[str, Any]:
        """Get current status of a payment"""
        try:
            payment_data = self._get_payment_data(payment_reference)
            
            if not payment_data:
                return {
                    'success': False,
                    'error': 'Payment not found'
                }
            
            return {
                'success': True,
                'payment_reference': payment_reference,
                'status': payment_data.get('status', 'unknown'),
                'amount': payment_data.get('amount'),
                'service_type': payment_data.get('service_type'),
                'created_at': payment_data.get('created_at'),
                'expires_at': payment_data.get('expires_at')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting payment status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global payment manager instance
payment_manager = PaymentManager()