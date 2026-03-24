from extensions import db
from uuid import uuid4
from datetime import datetime, timezone
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    event_id = db.Column(db.String(), db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.String(), db.ForeignKey('users.id'), nullable=False)
    
    ticket_price = db.Column(db.Float, nullable=False)
    commission = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    mpesa_receipt = db.Column(db.String(100), nullable=True)
    payment_phone = db.Column(db.String(20), nullable=True)
    
    purchased_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='tickets', foreign_keys=[user_id])
    
    @staticmethod
    def calculate_commission(price):
        return round(price * 0.05, 2)
    
    @staticmethod
    def calculate_total(price):
        commission = Ticket.calculate_commission(price)
        return round(price + commission, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'ticket_price': self.ticket_price,
            'commission': self.commission,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status.value,
            'mpesa_receipt': self.mpesa_receipt,
            'purchased_at': self.purchased_at.isoformat() if self.purchased_at else None
        }
    
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e