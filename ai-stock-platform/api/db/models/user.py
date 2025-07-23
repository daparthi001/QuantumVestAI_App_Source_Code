"""
User Model Module
Created: 2025-05-21 17:07:45
Author: daparthi001
"""
from typing import Optional

from core.utils.password_utils import get_password_hash
from db.base import Base, TimestampMixin
from db.models.associations import user_watchlist
from sqlalchemy import Boolean, Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.ext.hybrid import hybrid_property


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
    # Historically this field has been named either ``hashed_password`` or
    # ``password_hash`` depending on the migration path used when the database
    # was created.  To transparently support both schemas we detect which column
    # is present at import time and map the ``hashed_password`` attribute to that
    # column.  ``password_hash`` is kept as a backward compatible synonym.

    _pwd_column_name = "hashed_password"
    _use_split_names = False
    try:  # Introspect the DB to determine which column actually exists
        from core.config import get_settings
        from sqlalchemy import create_engine, inspect

        settings = get_settings()
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        insp = inspect(engine)
        cols = [c["name"] for c in insp.get_columns("users")]
        engine.dispose()
        if "password_hash" in cols and "hashed_password" not in cols:
            _pwd_column_name = "password_hash"
        if "full_name" not in cols and "first_name" in cols and "last_name" in cols:
            _use_split_names = True
    except Exception:
        # If inspection fails (e.g., during tests with no DB) default to the
        # original ``hashed_password`` column name.
        pass

    hashed_password = Column(_pwd_column_name, String, nullable=False)
    password_hash = synonym("hashed_password")

    if _use_split_names:
        first_name = Column("first_name", String)
        last_name = Column("last_name", String)

        @hybrid_property
        def full_name(self) -> Optional[str]:
            parts = []
            if self.first_name:
                parts.append(self.first_name)
            if self.last_name:
                parts.append(self.last_name)
            return " ".join(parts) if parts else None

        @full_name.setter
        def full_name(self, value: Optional[str]) -> None:
            if value:
                names = value.split(" ", 1)
                self.first_name = names[0]
                self.last_name = names[1] if len(names) > 1 else None
            else:
                self.first_name = None
                self.last_name = None
    else:
        full_name = Column("full_name", String)
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

