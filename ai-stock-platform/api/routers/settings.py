"""
Settings Router
Created: 2025-08-10
Author: OpenAI Assistant
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from db.session import get_db
from db.models.user import User
from db.models.user_setting import UserSetting

router = APIRouter()

# Default settings inserted for new users
DEFAULT_SETTINGS: List[Dict[str, str]] = [
    {"category": "general", "key": "theme", "value": "light"},
    {"category": "notifications", "key": "email", "value": "true"},
]

@router.get("/settings")
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Return settings for the authenticated user.

    If the user has no settings stored, insert default settings and
    return them instead of raising an error.
    """
    try:
        user_settings = (
            db.query(UserSetting)
            .filter(UserSetting.user_id == current_user.id)
            .all()
        )

        if not user_settings:
            defaults = [
                UserSetting(user_id=current_user.id, **s) for s in DEFAULT_SETTINGS
            ]
            db.add_all(defaults)
            db.commit()
            for setting in defaults:
                db.refresh(setting)
            user_settings = defaults

        return {"settings": [s.to_dict() for s in user_settings]}
    except Exception as exc:  # pragma: no cover - unexpected DB errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load settings: {exc}",
        )
