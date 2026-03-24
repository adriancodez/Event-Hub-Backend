from extensions import db
from uuid import uuid4
from datetime import datetime, timezone
from enum import Enum

class EventStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text())
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    ticket_price = db.Column(db.Float, default=0.0)
    vip_price = db.Column(db.Float, nullable=True)
    vvip_price = db.Column(db.Float, nullable=True)
    max_attendees = db.Column(db.Integer, nullable=True)
    banner_url = db.Column(db.String(500), nullable=True)
    renewal_period = db.Column(db.String(20), default='monthly')
    status = db.Column(db.Enum(EventStatus), default=EventStatus.PENDING, nullable=False)
    
    leader_id = db.Column(db.String(), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    leader = db.relationship('User', backref='events', foreign_keys=[leader_id])
    tickets = db.relationship('Ticket', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'location': self.location,
            'ticket_price': self.ticket_price,
            'vip_price': self.vip_price,
            'vvip_price': self.vvip_price,
            'max_attendees': self.max_attendees,
            'banner_url': self.banner_url,
            'renewal_period': self.renewal_period,
            'status': self.status.value,
            'leader_id': self.leader_id,
            'leader_name': self.leader.username if self.leader else None,
            'club_name': self.leader.club_name if self.leader and self.leader.role.name == 'LEADER' else None,
            'tickets_sold': self.tickets.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
