"""
Complete User Model for QuantumVestAI
Created: 2025-05-17 14:29:46 UTC
Updated: 2025-07-23 - Complete rewrite with full name support and fixed circular references
Author: daparthi001
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, Table, event
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship, Session
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


class User(Base):
    """
    Enhanced User model with full name support, role-based permissions,
    and comprehensive user management features.
    """
    __tablename__ = "users"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    
    # Personal information with full name support
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Status and verification
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", lazy="select")
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan", lazy="select")
    user_settings = relationship("UserSetting", back_populates="user", cascade="all, delete-orphan", lazy="select")
    audit_logs = relationship("AuditLog", back_populates="user", lazy="select")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan", lazy="select")

    # ==========================================
    # COMPUTED PROPERTIES (Full Name Support)
    # ==========================================

    @hybrid_property
    def full_name(self) -> str:
        """
        Generate full name from first_name and last_name.
        Falls back to username if no name components available.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name.strip()} {self.last_name.strip()}".strip()
        elif self.first_name:
            return self.first_name.strip()
        elif self.last_name:
            return self.last_name.strip()
        else:
            return self.username

    @full_name.expression
    def full_name(cls):
        """SQL expression for full_name generation"""
        return case(
            [
                (
                    (cls.first_name.isnot(None)) & (cls.last_name.isnot(None)),
                    func.trim(func.concat(cls.first_name, ' ', cls.last_name))
                ),
                (cls.first_name.isnot(None), func.trim(cls.first_name)),
                (cls.last_name.isnot(None), func.trim(cls.last_name))
            ],
            else_=cls.username
        )

    @hybrid_property
    def effective_display_name(self) -> str:
        """
        Get the best available display name with fallback hierarchy:
        display_name -> full_name -> first_name -> username
        """
        return (
            self.display_name or 
            self.full_name or 
            self.first_name or 
            self.username
        )

    @effective_display_name.expression
    def effective_display_name(cls):
        """SQL expression for effective_display_name"""
        return func.coalesce(
            cls.display_name,
            cls.full_name,
            cls.first_name,
            cls.username
        )

    # ==========================================
    # ROLE AND PERMISSION MANAGEMENT
    # ==========================================

    @hybrid_property
    def roles(self) -> List[str]:
        """Get all role names for the user"""
        if self.user_roles:
            return [ur.role.name for ur in self.user_roles if ur.role]
        return []

    @hybrid_property
    def primary_role(self) -> str:
        """Get the user's primary role (first assigned role or 'user' default)"""
        if self.user_roles and len(self.user_roles) > 0:
            primary_user_role = self.user_roles[0]
            if primary_user_role.role:
                return primary_user_role.role.name
        return "user"

    @primary_role.expression
    def primary_role(cls):
        """SQL expression for primary_role"""
        from db.models.role import Role
        from db.models.user_role import UserRole
        
        # Subquery to get the first role for the user
        first_role = (
            select(Role.name)
            .select_from(UserRole.join(Role))
            .where(UserRole.user_id == cls.id)
            .order_by(UserRole.id)
            .limit(1)
        ).scalar_subquery()
        
        return func.coalesce(first_role, 'user')

    @hybrid_property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return "admin" in self.roles

    @is_admin.expression
    def is_admin(cls):
        """SQL expression for is_admin"""
        from db.models.role import Role
        from db.models.user_role import UserRole
        
        return exists().where(
            (UserRole.user_id == cls.id) &
            (UserRole.role_id == Role.id) &
            (Role.name == "admin")
        )

    @hybrid_property
    def is_superuser(self) -> bool:
        """Alias for is_admin (backward compatibility)"""
        return self.is_admin

    @is_superuser.expression
    def is_superuser(cls):
        """SQL expression for is_superuser"""
        return cls.is_admin

    @hybrid_property
    def role(self) -> str:
        """
        Legacy role property for backward compatibility.
        Returns 'admin' for admin users, 'free' for others.
        """
        return "admin" if self.is_admin else "free"

    @role.expression
    def role(cls):
        """SQL expression for legacy role property"""
        return case([(cls.is_admin, "admin")], else_="free")

    @hybrid_property
    def permissions(self) -> Dict[str, Any]:
        """Get aggregated permissions from all user roles"""
        all_permissions = {}
        if self.user_roles:
            for user_role in self.user_roles:
                if user_role.role and user_role.role.permissions:
                    role_permissions = user_role.role.permissions
                    if isinstance(role_permissions, dict):
                        all_permissions.update(role_permissions)
        return all_permissions

    # ==========================================
    # AUTHENTICATION METHODS
    # ==========================================

    def set_password(self, password: str) -> None:
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = func.now()

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
            
        from db.models.user_role import UserRole
        user_role = UserRole(user_id=self.id, role_id=role.id)
        self.user_roles.append(user_role)
        
        if session:
            session.add(user_role)
            
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
        if self.user_settings:
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
            existing.updated_at = func.now()
        else:
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
            "first_name": self.first_name,
            "last_name": self.last_name,
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