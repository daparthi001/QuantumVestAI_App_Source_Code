from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List

from api.core.security_utils import get_current_user, get_current_admin_user
from api.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from api.db.session import get_db
from api.db.models.user import User
from api.schemas.user import UserPrivate, UserPublic, UserUpdate

router = APIRouter(prefix="/users")

@router.get("/me", response_model=UserPrivate)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user

@router.put("/me", response_model=UserPrivate)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise ResourceNotFoundError("User not found")
    
    # Update user fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.email is not None:
        # Check if email is already used
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email
    
    if user_data.avatar_url is not None:
        user.avatar_url = user_data.avatar_url
    
    if user_data.bio is not None:
        user.bio = user_data.bio
    
    if user_data.phone is not None:
        user.phone = user_data.phone
    
    if user_data.timezone is not None:
        user.timezone = user_data.timezone
    
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")
    
    return user

@router.get("/", response_model=List[UserPublic])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List users (admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/{user_id}/role", response_model=UserPublic)
async def update_user_role(
    user_id: int,
    role: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user role (admin only)."""
    # Check role is valid
    valid_roles = ["free", "basic", "premium", "admin"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")
    
    # Prevent changing own role
    if user.id == current_user.id:
        raise PermissionDeniedError("Cannot change own role")
    
    # Update role
    user.role = role
    db.commit()
    db.refresh(user)
    
    return user

@router.put("/{user_id}/status", response_model=UserPublic)
async def update_user_status(
    user_id: int,
    is_active: bool = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user active status (admin only)."""
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")
    
    # Prevent deactivating own account
    if user.id == current_user.id:
        raise PermissionDeniedError("Cannot change own active status")
    
    # Update status
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/username/{username}", response_model=UserPublic)
async def get_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by username."""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise ResourceNotFoundError(f"User with username {username} not found")
    
    return user

@router.post("/regenerate-api-key", response_model=dict)
async def regenerate_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Regenerate API key for current user."""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise ResourceNotFoundError("User not found")
    
    # Generate new API key
    import uuid
    user.api_key = str(uuid.uuid4())
    db.commit()
    
    return {"api_key": user.api_key}