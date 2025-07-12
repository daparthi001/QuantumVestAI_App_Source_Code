"""
Notification Router
Created: 2025-05-20 04:50:55
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status, WebSocket
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError
from db.session import get_db
from db.models.user import User
from services.notification_service import NotificationService
from schemas.notification import (
    NotificationResponse,
    NotificationSettingsUpdate,
    NotificationSettingsResponse,
    AlertConfigCreate,
    AlertConfigResponse,
    NotificationStatsResponse
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(get_current_user)]
)

@router.get(
    "/",
    response_model=List[NotificationResponse],
    summary="Get notifications",
    description="Get user notifications"
)
async def get_notifications(
    status: Optional[str] = Query(
        None,
        regex="^(unread|read|all)$"
    ),
    category: Optional[str] = Query(
        None,
        regex="^(price|news|earnings|portfolio|system)$"
    ),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[NotificationResponse]:
    """Get user notifications."""
    service = NotificationService(db)
    return await service.get_notifications(
        user_id=current_user.id,
        status=status,
        category=category,
        limit=limit
    )

@router.post(
    "/mark-read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark as read",
    description="Mark notifications as read"
)
async def mark_notifications_read(
    notification_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notifications as read."""
    service = NotificationService(db)
    await service.mark_as_read(
        notification_ids=notification_ids,
        user_id=current_user.id
    )

@router.put(
    "/settings",
    response_model=NotificationSettingsResponse,
    summary="Update settings",
    description="Update notification settings"
)
async def update_notification_settings(
    settings: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> NotificationSettingsResponse:
    """Update notification settings."""
    service = NotificationService(db)
    return await service.update_settings(
        settings=settings,
        user_id=current_user.id
    )

@router.post(
    "/alerts",
    response_model=AlertConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create alert",
    description="Create new notification alert"
)
async def create_alert(
    alert: AlertConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AlertConfigResponse:
    """Create notification alert."""
    service = NotificationService(db)
    return await service.create_alert(
        alert=alert,
        user_id=current_user.id
    )

@router.get(
    "/alerts",
    response_model=List[AlertConfigResponse],
    summary="Get alerts",
    description="Get notification alerts"
)
async def get_alerts(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[AlertConfigResponse]:
    """Get notification alerts."""
    service = NotificationService(db)
    return await service.get_alerts(
        user_id=current_user.id,
        active_only=active_only
    )

@router.delete(
    "/alerts/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete alert",
    description="Delete notification alert"
)
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete notification alert."""
    service = NotificationService(db)
    success = await service.delete_alert(
        alert_id=alert_id,
        user_id=current_user.id
    )
    
    if not success:
        raise ResourceNotFoundError(f"Alert {alert_id} not found")

@router.get(
    "/stats",
    response_model=NotificationStatsResponse,
    summary="Get statistics",
    description="Get notification statistics"
)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> NotificationStatsResponse:
    """Get notification statistics."""
    service = NotificationService(db)
    return await service.get_stats(current_user.id)

@router.websocket("/ws")
async def notification_websocket(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """Real-time notification websocket."""
    service = NotificationService(db)
    await service.handle_websocket(websocket, token)
