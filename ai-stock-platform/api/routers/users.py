"""
User management router.
Created: 2025-05-17 14:29:46 UTC
Updated: 2025-07-23 - Fixed for new User model and schema
Author: daparthi001
"""
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from core.dependencies import get_current_user, get_db
from core.exceptions import NotFoundError, ValidationError, PermissionError
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from schemas.user import UserProfile, UserUpdate, UserCreate, UserListResponse
from services.storage import upload_file
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from db.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user profile with full details.
    """
    return current_user.to_dict(include_sensitive=False)


@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_in: UserUpdate
) -> Any:
    """
    Update current user profile with enhanced validation.
    """
    # Validate email uniqueness if being updated
    if user_in.email and user_in.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == user_in.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise ValidationError("Email already registered")
    
    # Validate username uniqueness if being updated
    if user_in.username and user_in.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == user_in.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise ValidationError("Username already taken")
    
    # Update user fields
    update_data = user_in.dict(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    # Update timestamp
    current_user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
    
    return current_user.to_dict(include_sensitive=False)


@router.post("/me/avatar", response_model=UserProfile)
async def update_avatar(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...)
) -> Any:
    """
    Update user avatar with file validation.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise ValidationError("Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.")
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size and file.size > max_size:
        raise ValidationError("File too large. Maximum size is 5MB.")
    
    try:
        # Upload file to storage
        avatar_url = await upload_file(
            file,
            folder="avatars",
            user_id=str(current_user.uuid)  # Use UUID instead of ID
        )
        
        # Update user
        current_user.avatar_url = avatar_url
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}"
        )
    
    return current_user.to_dict(include_sensitive=False)


@router.delete("/me/avatar", response_model=UserProfile)
async def delete_avatar(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Remove user avatar.
    """
    current_user.avatar_url = None
    current_user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove avatar"
        )
    
    return current_user.to_dict(include_sensitive=False)


@router.get("/{user_identifier}", response_model=UserProfile)
async def get_user_profile(
    user_identifier: str,  # Can be ID, UUID, or username
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get user profile by ID, UUID, or username.
    Supports multiple identifier types for flexibility.
    """
    user = None
    
    # Try to find user by different identifier types
    if user_identifier.isdigit():
        # Try by ID
        user = db.query(User).options(
            joinedload(User.user_roles).joinedload('role')
        ).filter(User.id == int(user_identifier)).first()
    
    if not user:
        try:
            # Try by UUID
            uuid_obj = UUID(user_identifier)
            user = db.query(User).options(
                joinedload(User.user_roles).joinedload('role')
            ).filter(User.uuid == uuid_obj).first()
        except ValueError:
            # Try by username
            user = db.query(User).options(
                joinedload(User.user_roles).joinedload('role')
            ).filter(User.username == user_identifier).first()
    
    if not user:
        raise NotFoundError("User not found")
    
    # Check if user has permission to view this profile
    if user.id != current_user.id and not current_user.has_permission("read_users"):
        raise PermissionError("Insufficient permissions to view user profile")
    
    return user.to_dict(include_sensitive=False)


@router.get("/", response_model=UserListResponse)
async def list_users(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    role: Optional[str] = None
) -> Any:
    """
    List users with filtering and pagination.
    Requires admin permissions.
    """
    # Check permissions
    if not current_user.has_permission("read_users"):
        raise PermissionError("Insufficient permissions to list users")
    
    # Build query
    query = db.query(User).options(
        joinedload(User.user_roles).joinedload('role')
    )
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if role:
        from db.models.role import Role
        from db.models.user_role import UserRole
        query = query.join(UserRole).join(Role).filter(Role.name == role)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    # Convert to dict format
    user_list = [user.to_dict(include_sensitive=False) for user in users]
    
    return {
        "users": user_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/", response_model=UserProfile)
async def create_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_in: UserCreate
) -> Any:
    """
    Create a new user.
    Requires admin permissions.
    """
    # Check permissions
    if not current_user.has_permission("create_users"):
        raise PermissionError("Insufficient permissions to create users")
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_in.email).first():
        raise ValidationError("Email already registered")
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_in.username).first():
        raise ValidationError("Username already taken")
    
    # Create user
    user_data = user_in.dict(exclude={"password"})
    user = User(**user_data)
    
    # Set password
    if user_in.password:
        user.set_password(user_in.password)
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Assign default role if specified
        if hasattr(user_in, 'default_role') and user_in.default_role:
            from db.models.role import Role
            role = db.query(Role).filter(Role.name == user_in.default_role).first()
            if role:
                user.add_role(role)
                db.commit()
                db.refresh(user)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return user.to_dict(include_sensitive=False)


@router.put("/{user_id}", response_model=UserProfile)
async def update_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: int,
    user_in: UserUpdate
) -> Any:
    """
    Update a user by ID.
    Requires admin permissions or self-update.
    """
    # Get target user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found")
    
    # Check permissions
    if user.id != current_user.id and not current_user.has_permission("update_users"):
        raise PermissionError("Insufficient permissions to update this user")
    
    # Validate email uniqueness if being updated
    if user_in.email and user_in.email != user.email:
        existing_user = db.query(User).filter(
            User.email == user_in.email,
            User.id != user.id
        ).first()
        if existing_user:
            raise ValidationError("Email already registered")
    
    # Validate username uniqueness if being updated
    if user_in.username and user_in.username != user.username:
        existing_user = db.query(User).filter(
            User.username == user_in.username,
            User.id != user.id
        ).first()
        if existing_user:
            raise ValidationError("Username already taken")
    
    # Update user fields
    update_data = user_in.dict(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    return user.to_dict(include_sensitive=False)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: int
) -> Any:
    """
    Delete a user by ID (soft delete).
    Requires admin permissions.
    """
    # Check permissions
    if not current_user.has_permission("delete_users"):
        raise PermissionError("Insufficient permissions to delete users")
    
    # Get target user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found")
    
    # Prevent self-deletion
    if user.id == current_user.id:
        raise ValidationError("Cannot delete your own account")
    
    # Soft delete (deactivate instead of hard delete)
    user.is_active = False
    user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.post("/{user_id}/activate", response_model=UserProfile)
async def activate_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: int
) -> Any:
    """
    Activate a deactivated user.
    Requires admin permissions.
    """
    # Check permissions
    if not current_user.has_permission("update_users"):
        raise PermissionError("Insufficient permissions to activate users")
    
    # Get target user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found")
    
    user.is_active = True
    user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )
    
    return user.to_dict(include_sensitive=False)


@router.get("/search/suggestions")
async def get_user_suggestions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: str,
    limit: int = 10
) -> Any:
    """
    Get user suggestions for autocomplete.
    Returns basic user info for search suggestions.
    """
    if len(q) < 2:
        return {"suggestions": []}
    
    search_term = f"%{q}%"
    users = db.query(User).filter(
        User.is_active == True,
        (User.username.ilike(search_term)) |
        (User.first_name.ilike(search_term)) |
        (User.last_name.ilike(search_term)) |
        (User.email.ilike(search_term))
    ).limit(limit).all()
    
    suggestions = [
        {
            "id": user.id,
            "uuid": str(user.uuid),
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "avatar_url": getattr(user, 'avatar_url', None)
        }
        for user in users
    ]
    
    return {"suggestions": suggestions}