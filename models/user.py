from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from uuid import uuid4
from datetime import datetime, timedelta, timezone

class UserRole(Enum):
    ADMIN = "admin"
    LEADER = "leader"
    USER = "user"

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    
    # Leader-specific fields
    club_name = db.Column(db.String(100), nullable=True)
    subscription_active = db.Column(db.Boolean, default=False)
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    club_access_code = db.Column(db.String(10), unique=True, nullable=True)
    
    # Relationships  
    leader_id = db.Column(db.String(), db.ForeignKey('users.id'), nullable=True)
    club_members = db.relationship('User', backref='leader', remote_side=[id], foreign_keys='User.leader_id', lazy='select')

    def __repr__(self):
        return f"<User {self.username} - {self.role.value}>"
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_subscription_active(self):
        if self.role != UserRole.LEADER:
            return False
        if not self.subscription_active or not self.subscription_expires_at:
            return False
        expires_at = self.subscription_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > datetime.now(timezone.utc)
    
    def activate_subscription(self, duration_days=30):
        self.subscription_active = True
        self.subscription_expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
        if not self.club_access_code:
            self.club_access_code = self.generate_club_code()
    
    @staticmethod
    def generate_club_code():
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if self.role == UserRole.LEADER:
            data.update({
                'club_name': self.club_name,
                'subscription_active': self.is_subscription_active(),
                'club_access_code': self.club_access_code
            })
        
        return data
    
    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_leader_by_club_code(cls, club_code):
        return cls.query.filter_by(club_access_code=club_code, role=UserRole.LEADER).first()
