"""
User management router.
Created: 2025-05-17 14:29:46 UTC
Author: daparthi001
"""
from typing import Any

from core.dependencies import get_current_user, get_db
from core.exceptions import NotFoundError
from fastapi import APIRouter, Depends, File, UploadFile
from schemas.user import UserProfile, UserUpdate
from services.storage import upload_file
from sqlalchemy.orm import Session

from models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user profile.
    """
    return current_user

@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_in: UserUpdate
) -> Any:
    """
    Update current user profile.
    """
    # Update user fields
    for field, value in user_in.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/me/avatar", response_model=UserProfile)
async def update_avatar(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...)
) -> Any:
    """
    Update user avatar.
    """
    # Upload file to storage
    avatar_url = await upload_file(
        file,
        folder="avatars",
        user_id=str(current_user.id)
    )
    
    # Update user
    current_user.avatar_url = avatar_url
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user profile by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found")
    return user
