"""
User Model
Created: 2025-05-19 05:45:27
Author: daparthi001
"""
from sqlalchemy import Boolean, Column, String, Integer
from sqlalchemy.orm import Mapped, relationship
from db.base_class import Base, TimestampMixin

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