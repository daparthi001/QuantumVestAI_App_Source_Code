"""
User Model
Created: 2025-05-20 20:31:25
Author: daparthi001
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.base import Base
from db.models.associations import user_watchlist, user_portfolio

class User(Base, TimestampMixin):
    """User model for authentication and authorization"""
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = Column(String, nullable=False)
    full_name: Mapped[str] = Column(String, nullable=True)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    is_superuser: Mapped[bool] = Column(Boolean, default=False)

    # Relationships
    stocks = relationship("Stock", back_populates="user")
    watchlists = relationship("Watchlist", back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username})"