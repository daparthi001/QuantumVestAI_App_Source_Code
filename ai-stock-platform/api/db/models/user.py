"""
User Model Module
Created: 2025-05-21 17:07:45
Author: daparthi001
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.models.associations import user_watchlist

from db.base import Base, TimestampMixin
from core.utils.password_utils import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional


class User(Base, TimestampMixin):
    """User model for authentication and profile"""

    __tablename__ = "users"
    # In test environments this module may be imported more than once under
    # different module names.  ``extend_existing`` avoids duplicate table
    # errors when SQLAlchemy registers the model multiple times.
    __table_args__ = {"extend_existing": True}

    # Authentication fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default="free", nullable=False)

    # Relationships
    positions = relationship(
        "Position", back_populates="user", cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    # Detailed watchlist entries with notes/targets
    watchlist_entries = relationship(
        "WatchList",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    # Older code expects this attribute name
    watchlists = watchlist_entries

    # Simple many-to-many relationship for stocks a user is watching
    watchlist = relationship(
        "Stock",
        secondary=user_watchlist,
        back_populates="watched_by",
    )

    alerts = relationship(
        "Alert",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        """Set encrypted password."""
        self.hashed_password = get_password_hash(password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    @classmethod
    async def get_by_username(
        cls, db: AsyncSession, username: str
    ) -> Optional["User"]:
        """Fetch a user by username."""
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(
        cls, db: AsyncSession, email: str
    ) -> Optional["User"]:
        """Fetch a user by email."""
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()

    async def save(self, db: AsyncSession) -> None:
        """Persist the user to the database."""
        db.add(self)
        await db.commit()
        await db.refresh(self)

