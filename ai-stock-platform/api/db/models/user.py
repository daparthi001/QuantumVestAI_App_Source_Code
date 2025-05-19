from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Change this line to import Base from the correct location
from api.db.base import Base

# Association table for user watchlists
user_watchlist = Table(
    'user_watchlist',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('stock_id', Integer, ForeignKey('stocks.id', ondelete='CASCADE')),
    Column('notes', String),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    """User model for authentication and profile data."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    
    # Profile fields
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String, default="free")  # free, basic, premium, admin
    
    # Subscription info
    subscription_plan = Column(String, nullable=True)
    subscription_status = Column(String, nullable=True)  # active, cancelled, expired
    subscription_expiry = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Verification and security
    verification_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # API access
    api_key = Column(String, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    watchlist = relationship("Stock", secondary=user_watchlist, back_populates="watched_by")
    alerts = relationship("Alert", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"