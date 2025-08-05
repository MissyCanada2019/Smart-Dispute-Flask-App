from utils.db import db
from datetime import datetime
from enum import Enum as PyEnum

class PaymentStatus(PyEnum):
    """Payment status enumeration"""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    CANCELLED = 'cancelled'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='CAD')
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    transaction_id = db.Column(db.String(100))
    processed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id}: {self.amount} {self.currency} - {self.status.value}>'