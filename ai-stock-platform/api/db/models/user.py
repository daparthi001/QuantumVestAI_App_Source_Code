"""
Complete User Model for QuantumVestAI (Simplified - No SQL Expression Conflicts)
Created: 2025-05-17 14:29:46 UTC
Updated: 2025-07-23 - Complete rewrite with full name support and fixed circular references
Author: daparthi001
"""
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, Table, event
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship, Session, synonym
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select, exists, case
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:  # pragma: no cover - optional dependency may be missing
    import hashlib

    def generate_password_hash(password: str) -> str:
        """Minimal fallback password hashing using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password_hash(pw_hash: str, password: str) -> bool:
        """Verify a password against the SHA256 fallback hash."""
        return pw_hash == hashlib.sha256(password.encode()).hexdigest()


from db.base import Base
from db.models.associations import user_watchlist

# Import related models so that SQLAlchemy is aware of them when this module
# is imported in isolation. Without these imports the mapper configuration can
# fail when resolving relationship targets like "Watchlist" or "WatchList".
from .watchlist import Watchlist  # noqa: F401
from .watchlist_stock import WatchlistStock  # noqa: F401
from .stock import WatchList, Alert  # noqa: F401


class User(Base):
    """
    Enhanced User model with full name support, role-based permissions,
    and comprehensive user management features.
    """
    __tablename__ = "users"
    # Allow redefining the table in test environments where models may
    # be imported multiple times.
    __table_args__ = {"extend_existing": True}

    # Primary identification
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
    _has_is_superuser = True
    _has_role = True
    try:  # Introspect the DB to determine which columns actually exist
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
        _has_is_superuser = "is_superuser" in cols
        _has_role = "role" in cols
    except Exception:
        # If inspection fails (e.g., during tests with no DB) default to the
        # original column names.
        _has_is_superuser = True
        _has_role = True
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

    def __init__(self, **kwargs):
        """Allow ``full_name`` for split-name schemas."""
        if "full_name" in kwargs and type(self)._use_split_names:
            value = kwargs.pop("full_name")
            if value:
                parts = value.split(" ", 1)
                kwargs.setdefault("first_name", parts[0])
                if len(parts) > 1:
                    kwargs.setdefault("last_name", parts[1])
        super().__init__(**kwargs)

    is_active = Column(Boolean, default=True)
    if _has_is_superuser:
        is_superuser = Column(Boolean, default=False)
    else:
        if _has_role:
            @hybrid_property
            def is_superuser(self) -> bool:
                """Compatibility shim when ``is_superuser`` column is absent."""
                return getattr(self, "role", "") == "admin"

            @is_superuser.setter
            def is_superuser(self, value: bool) -> None:
                if value:
                    self.role = "admin"
                elif getattr(self, "role", None) == "admin":
                    self.role = "free"
        else:
            # When both ``is_superuser`` and ``role`` columns are missing,
            # store the flag on the instance to avoid recursive lookups.
            @hybrid_property
            def is_superuser(self) -> bool:  # type: ignore[override]
                return getattr(self, "_is_superuser", False)

            @is_superuser.setter
            def is_superuser(self, value: bool) -> None:
                setattr(self, "_is_superuser", bool(value))

    if _has_role:
        role = Column(String, default="free", nullable=False)
    else:
        if _has_is_superuser:
            @hybrid_property
            def role(self) -> str:  # type: ignore[override]
                return "admin" if getattr(self, "is_superuser", False) else "free"

            @role.setter
            def role(self, value: str) -> None:
                if value == "admin":
                    self.is_superuser = True
                else:
                    self.is_superuser = False
        else:
            # Neither ``role`` nor ``is_superuser`` columns exist.  Use an
            # instance attribute to avoid recursion between the two hybrid
            # properties.
            @hybrid_property
            def role(self) -> str:  # type: ignore[override]
                return getattr(self, "_role", "free")

            @role.setter
            def role(self, value: str) -> None:
                setattr(self, "_role", value)


    # Relationships
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        foreign_keys="UserRole.user_id",
    )
    # Individual positions held by the user
    positions = relationship(
        "Position",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    # Transactions executed by the user
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    # Deprecated ``portfolios`` relationship removed as there is no Portfolio model
    user_settings = relationship("UserSetting", back_populates="user", cascade="all, delete-orphan", lazy="select")
    audit_logs = relationship("AuditLog", back_populates="user", lazy="select")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan", lazy="select")

    # Watchlist relationships
    watchlist = relationship(
        "Stock",
        secondary=user_watchlist,
        back_populates="watched_by",
        lazy="select",
    )
    watchlist_entries = relationship(
        "WatchList",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    watchlists = relationship(
        "Watchlist",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    alerts = relationship(
        "Alert",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )


    # ==========================================
    # COMPUTED PROPERTIES
    # ==========================================

    @hybrid_property
    def effective_display_name(self) -> str:
        """
        Get the best available display name with fallback hierarchy:
        display_name -> full_name -> first_name -> username
        """
        return (
            self.display_name or
            self.full_name or
            getattr(self, "first_name", None) or
            self.username
        )

    # ==========================================
    # ROLE AND PERMISSION MANAGEMENT (FIXED)
    # ==========================================

    @hybrid_property
    def roles(self) -> List[str]:
        """Get all role names for the user"""
        if hasattr(self, 'user_roles') and self.user_roles:
            return [ur.role.name for ur in self.user_roles if ur.role]
        return []

    @hybrid_property
    def primary_role(self) -> str:
        """Get the user's primary role (first assigned role or 'user' default)"""
        if hasattr(self, 'user_roles') and self.user_roles:
            if len(self.user_roles) > 0:
                primary_user_role = self.user_roles[0]
                if primary_user_role.role:
                    return primary_user_role.role.name
        return "user"

    @hybrid_property
    def is_admin(self) -> bool:
        """Check if user has admin role - FIXED to avoid circular reference"""
        # Direct database lookup instead of calling other properties
        if hasattr(self, 'user_roles') and self.user_roles:
            for user_role in self.user_roles:
                if hasattr(user_role, 'role') and user_role.role and user_role.role.name == "admin":
                    return True
        return False

    @hybrid_property
    def is_superuser(self) -> bool:
        """Alias for is_admin (backward compatibility) - FIXED"""
        return self.is_admin

    @hybrid_property
    def role(self) -> str:
        """
        Legacy role property for backward compatibility - FIXED.
        Returns 'admin' for admin users, 'free' for others.
        """
        # Direct database lookup instead of calling is_admin to avoid circular reference
        if hasattr(self, 'user_roles') and self.user_roles:
            for user_role in self.user_roles:
                if hasattr(user_role, 'role') and user_role.role:
                    if user_role.role.name == "admin":
                        return "admin"
            return "user"  # Has roles but not admin
        return "free"  # No roles assigned

    @hybrid_property
    def permissions(self) -> Dict[str, Any]:
        """Get aggregated permissions from all user roles"""
        all_permissions = {}
        if hasattr(self, 'user_roles') and self.user_roles:
            for user_role in self.user_roles:
                if user_role.role and user_role.role.permissions:
                    role_permissions = user_role.role.permissions
                    if isinstance(role_permissions, dict):
                        all_permissions.update(role_permissions)
        return all_permissions

    # ==========================================
    # AUTHENTICATION METHODS (No Werkzeug)
    # ==========================================

    def _hash_password(self, password: str) -> str:
        """
        Hash password using PBKDF2 with SHA-256.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        # Generate a random salt
        salt = secrets.token_hex(32)
        
        # Hash the password with the salt using PBKDF2
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        # Return salt + hash as hex string
        return f"{salt}${password_hash.hex()}"

    def _verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed: Stored password hash
            
        Returns:
            True if password matches
        """
        try:
            # Split salt and hash
            salt, stored_hash = hashed.split('$', 1)
            
            # Hash the provided password with the same salt
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            # Compare hashes
            return password_hash.hex() == stored_hash
        except (ValueError, AttributeError):
            # Handle malformed hash
            return False

    def set_password(self, password: str) -> None:
        """Set password hash"""
        self.password_hash = self._hash_password(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        return self._verify_password(password, self.password_hash)

    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()

    # ==========================================
    # PERMISSION CHECKING METHODS
    # ==========================================

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: Permission name to check
            
        Returns:
            bool: True if user has the permission
        """
        permissions = self.permissions
        
        # Check for 'all' permission (admin override)
        if permissions.get("all"):
            return True
            
        # Check for specific permission
        return permissions.get(permission, False)

    def has_role(self, role_name: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            role_name: Role name to check
            
        Returns:
            bool: True if user has the role
        """
        return role_name in self.roles

    def has_any_role(self, role_names: List[str]) -> bool:
        """
        Check if user has any of the specified roles.
        
        Args:
            role_names: List of role names to check
            
        Returns:
            bool: True if user has any of the roles
        """
        user_roles = set(self.roles)
        return bool(user_roles.intersection(set(role_names)))

    def has_all_roles(self, role_names: List[str]) -> bool:
        """
        Check if user has all of the specified roles.
        
        Args:
            role_names: List of role names to check
            
        Returns:
            bool: True if user has all of the roles
        """
        user_roles = set(self.roles)
        return set(role_names).issubset(user_roles)

    # ==========================================
    # ROLE MANAGEMENT METHODS
    # ==========================================

    def add_role(self, role, session: Optional[Session] = None) -> bool:
        """
        Add a role to the user.
        
        Args:
            role: Role object to add
            session: Optional database session
            
        Returns:
            bool: True if role was added, False if already exists
        """
        # Check if user already has this role
        existing = next((ur for ur in self.user_roles if ur.role_id == role.id), None)
        if existing:
            return False
            
        try:
            from db.models.user_role import UserRole
            user_role = UserRole(user_id=self.id, role_id=role.id)
            self.user_roles.append(user_role)
            
            if session:
                session.add(user_role)
        except ImportError:
            # Handle case where UserRole model isn't available yet
            pass
            
        return True

    def remove_role(self, role, session: Optional[Session] = None) -> bool:
        """
        Remove a role from the user.
        
        Args:
            role: Role object to remove
            session: Optional database session
            
        Returns:
            bool: True if role was removed, False if not found
        """
        user_role = next((ur for ur in self.user_roles if ur.role_id == role.id), None)
        if not user_role:
            return False
            
        self.user_roles.remove(user_role)
        
        if session:
            session.delete(user_role)
            
        return True

    def clear_roles(self, session: Optional[Session] = None) -> None:
        """
        Remove all roles from the user.
        
        Args:
            session: Optional database session
        """
        if session:
            for user_role in self.user_roles:
                session.delete(user_role)
                
        self.user_roles.clear()

    def set_roles(self, roles: List, session: Optional[Session] = None) -> None:
        """
        Set user roles (replaces existing roles).
        
        Args:
            roles: List of Role objects
            session: Optional database session
        """
        self.clear_roles(session)
        for role in roles:
            self.add_role(role, session)

    # ==========================================
    # USER SETTINGS MANAGEMENT
    # ==========================================

    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """
        Get a user-specific setting value.
        
        Args:
            category: Setting category
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        if hasattr(self, 'user_settings') and self.user_settings:
            setting = next(
                (us for us in self.user_settings 
                 if us.category == category and us.key == key), 
                None
            )
            if setting:
                return setting.value
        return default

    def set_setting(self, category: str, key: str, value: Any, session: Optional[Session] = None) -> None:
        """
        Set a user-specific setting value.
        
        Args:
            category: Setting category
            key: Setting key
            value: Setting value
            session: Optional database session
        """
        # Find existing setting
        existing = next(
            (us for us in self.user_settings 
             if us.category == category and us.key == key), 
            None
        )
        
        if existing:
            existing.value = str(value) if value is not None else None
            existing.updated_at = datetime.utcnow()
        else:
            try:
                from db.models.user_setting import UserSetting
                new_setting = UserSetting(
                    user_id=self.id,
                    category=category,
                    key=key,
                    value=str(value) if value is not None else None
                )
                self.user_settings.append(new_setting)
                
                if session:
                    session.add(new_setting)
            except ImportError:
                # Handle case where UserSetting model isn't available yet
                pass

    # ==========================================
    # VALIDATION METHODS
    # ==========================================

    def is_active_user(self) -> bool:
        """Check if user is active and verified"""
        return self.is_active and self.is_verified

    def can_login(self) -> bool:
        """Check if user can log in"""
        return self.is_active

    @hybrid_method
    def is_email_verified(self) -> bool:
        """Check if user's email is verified"""
        return self.is_verified

    # ==========================================
    # SERIALIZATION METHODS
    # ==========================================

    def to_dict(self, include_sensitive: bool = False, include_roles: bool = True) -> Dict[str, Any]:
        """
        Convert user to dictionary for API responses.
        
        Args:
            include_sensitive: Include sensitive data like permissions
            include_roles: Include role information
            
        Returns:
            Dict containing user data
        """
        user_dict = {
            "id": self.id,
            "uuid": str(self.uuid),
            "username": self.username,
            "email": self.email,
            "first_name": getattr(self, "first_name", None),
            "last_name": getattr(self, "last_name", None),
            "full_name": self.full_name,
            "display_name": self.display_name,
            "effective_display_name": self.effective_display_name,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_roles:
            user_dict.update({
                "is_admin": self.is_admin,
                "is_superuser": self.is_superuser,  # Backward compatibility
                "primary_role": self.primary_role,
                "role": self.role,  # Legacy field
                "roles": self.roles,
            })
            
        if include_sensitive:
            user_dict.update({
                "permissions": self.permissions,
            })
            
        return user_dict

    def to_public_dict(self) -> Dict[str, Any]:
        """
        Convert user to public dictionary (limited information).
        
        Returns:
            Dict containing public user data only
        """
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "username": self.username,
            "full_name": self.full_name,
            "display_name": self.display_name,
            "effective_display_name": self.effective_display_name,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    # ==========================================
    # STRING REPRESENTATIONS
    # ==========================================

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, username='{self.username}', "
            f"email='{self.email}', role='{self.primary_role}', "
            f"active={self.is_active})>"
        )

    def __str__(self) -> str:
        return f"{self.effective_display_name} ({self.email})"


    # ==========================================
    # ASYNC DATABASE OPERATIONS
    # ==========================================

    @classmethod
    async def get_by_username(
        cls, db: AsyncSession, username: str
    ) -> Optional["User"]:
        """Asynchronously fetch a user by username."""
        result = await db.execute(
            select(cls).where(cls.username == username.lower().strip())
        )
        return result.scalars().first()

    @classmethod
    async def get_by_email(
        cls, db: AsyncSession, email: str
    ) -> Optional["User"]:
        """Asynchronously fetch a user by email address."""
        result = await db.execute(
            select(cls).where(cls.email == email.lower().strip())
        )
        return result.scalars().first()

    @classmethod
    async def get_by_uuid(
        cls, db: AsyncSession, user_uuid: uuid.UUID
    ) -> Optional["User"]:
        """Asynchronously fetch a user by UUID."""
        result = await db.execute(select(cls).where(cls.uuid == user_uuid))
        return result.scalars().first()

    async def save(self, db: AsyncSession) -> None:
        """Persist the user and refresh the instance."""
        db.add(self)
        await db.commit()
        await db.refresh(self)


# ==========================================
# EVENT LISTENERS
# ==========================================

@event.listens_for(User, 'before_update')
def update_user_timestamp(mapper, connection, target):
    """Update the updated_at timestamp before updates"""
    target.updated_at = datetime.utcnow()


@event.listens_for(User, 'before_insert')
def validate_user_before_insert(mapper, connection, target):
    """Validate user data before insertion"""
    # Ensure username and email are lowercase
    if target.username:
        target.username = target.username.lower().strip()
    if target.email:
        target.email = target.email.lower().strip()
        
    # Ensure names are properly formatted
    if target.first_name:
        target.first_name = target.first_name.strip()
    if target.last_name:
        target.last_name = target.last_name.strip()
    if target.display_name:
        target.display_name = target.display_name.strip()


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email address"""
    return session.query(User).filter(User.email == email.lower().strip()).first()


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return session.query(User).filter(User.username == username.lower().strip()).first()


def get_user_by_uuid(session: Session, user_uuid: uuid.UUID) -> Optional[User]:
    """Get user by UUID"""
    return session.query(User).filter(User.uuid == user_uuid).first()


def create_user(
    session: Session,
    username: str,
    email: str,
    password: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    **kwargs
) -> User:
    """
    Create a new user with validation.
    
    Args:
        session: Database session
        username: Username
        email: Email address
        password: Plain text password
        first_name: Optional first name
        last_name: Optional last name
        **kwargs: Additional user fields
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If username or email already exists
    """
    # Check for existing users
    if get_user_by_email(session, email):
        raise ValueError("Email already registered")
    if get_user_by_username(session, username):
        raise ValueError("Username already taken")
    
    # Create user
    user = User(
        username=username.lower().strip(),
        email=email.lower().strip(),
        first_name=first_name.strip() if first_name else None,
        last_name=last_name.strip() if last_name else None,
        **kwargs
    )
    
    # Set password
    user.set_password(password)
    
    # Add to session
    session.add(user)
    session.flush()  # Get the ID

    return user


# ==========================================
# ASYNC UTILITY METHODS
# ==========================================

@classmethod
async def get_by_username(cls, session: AsyncSession, username: str) -> Optional["User"]:
    """Asynchronously fetch a user by username."""
    result = await session.execute(
        select(User).where(User.username == username.lower().strip())
    )
    return result.scalars().first()


@classmethod
async def get_by_email(cls, session: AsyncSession, email: str) -> Optional["User"]:
    """Asynchronously fetch a user by email."""
    result = await session.execute(
        select(User).where(User.email == email.lower().strip())
    )
    return result.scalars().first()


@classmethod
async def get_by_uuid(cls, session: AsyncSession, user_uuid: uuid.UUID) -> Optional["User"]:
    """Asynchronously fetch a user by UUID."""
    result = await session.execute(
        select(User).where(User.uuid == user_uuid)
    )
    return result.scalars().first()


async def save(self, session: AsyncSession) -> None:
    """Persist the user using an async database session."""
    session.add(self)
    await session.commit()
    await session.refresh(self)
