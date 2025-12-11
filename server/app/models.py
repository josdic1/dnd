from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model):
    __tablename__ = 'users'

    # Use UUIDs, not Integers. Integers are guessable (User 5 is followed by User 6).
    # UUIDs are secure and scale across microservices better.
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # The Identity Anchor
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=True) # Optional? Phone is key.
    
    # The Trust Graph (The most important line)
    referred_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # The Gate
    # States: 'PENDING_BG_CHECK', 'ACTIVE', 'SUSPENDED', 'WAITLIST'
    status = db.Column(db.String(20), default='PENDING_BG_CHECK', nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    # NO PASSWORDS. 
    # Auth is handled via OTP or tokens in a separate table/service.
    
    def __init__(self, name, phone, email=None, referred_by_id=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.referred_by_id = referred_by_id
    
    def __repr__(self):
        return f'<User: {self.name} | Status: {self.status} | Referred By: {self.referred_by_id}>'