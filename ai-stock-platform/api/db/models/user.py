"""
User Model Module
Created: 2025-05-19 03:27:22
Updated: 2025-05-21 16:32:45
Author: daparthi001
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from db.base import Base, TimestampMixin
from core.security import get_password_hash

class User(Base, TimestampMixin):
    """User model for authentication and profile"""
    __tablename__ = "users"

    # Authentication fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationships
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("WatchList", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Set encrypted password"""
        self.hashed_password = get_password_hash(password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"