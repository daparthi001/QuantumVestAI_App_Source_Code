"""
Alerting Router
Created: 2025-05-20 04:59:13
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError, PermissionDeniedError
from db.session import get_db
from db.models.user import User
from services.alerting_service import AlertingService
from schemas.alerting import (
    AlertCreate,
    AlertResponse,
    AlertRuleResponse,
    AlertHistoryResponse,
    AlertTriggerResponse,
    AlertChannelResponse,
    AlertStatusResponse,
    AlertAggregationResponse
)

router = APIRouter(
    prefix="/alerts",
    tags=["alerting"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create alert",
    description="Create a new alert"
)
async def create_alert(
    alert: AlertCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AlertResponse:
    """Create new alert."""
    service = AlertingService(db)
    
    # Check alert limits based on user role
    if current_user.role == "free":
        active_alerts = await service.get_active_alerts_count(current_user.id)
        if active_alerts >= 5:
            raise PermissionDeniedError("Free users are limited to 5 active alerts")
    
    result = await service.create_alert(
        alert=alert,
        user_id=current_user.id
    )
    
    background_tasks.add_task(
        service.initialize_alert_monitoring,
        alert_id=result.id
    )
    
    return result

@router.get(
    "/rules",
    response_model=List[AlertRuleResponse],
    summary="List alert rules",
    description="Get available alert rules"
)
async def list_alert_rules(
    category: Optional[str] = Query(
        None,
        regex="^(price|volume|technical|fundamental|news)$"
    ),
    asset_type: Optional[str] = Query(
        None,
        regex="^(stock|crypto|forex|commodity)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[AlertRuleResponse]:
    """List alert rules."""
    service = AlertingService(db)
    return await service.list_alert_rules(
        category=category,
        asset_type=asset_type,
        user_role=current_user.role
    )

@router.get(
    "/history",
    response_model=List[AlertHistoryResponse],
    summary="Get alert history",
    description="Get historical alert triggers"
)
async def get_alert_history(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    alert_ids: Optional[List[int]] = Query(None),
    status: Optional[str] = Query(
        None,
        regex="^(triggered|acknowledged|resolved)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[AlertHistoryResponse]:
    """Get alert history."""
    service = AlertingService(db)
    return await service.get_alert_history(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        alert_ids=alert_ids,
        status=status
    )

@router.post(
    "/{alert_id}/trigger",
    response_model=AlertTriggerResponse,
    summary="Trigger alert",
    description="Manually trigger an alert"
)
async def trigger_alert(
    alert_id: int,
    trigger_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AlertTriggerResponse:
    """Trigger alert manually."""
    if current_user.role != "admin":
        raise PermissionDeniedError("Manual triggers restricted to admin users")
    
    service = AlertingService(db)
    return await service.trigger_alert(
        alert_id=alert_id,
        trigger_data=trigger_data,
        user_id=current_user.id
    )

@router.get(
    "/channels",
    response_model=List[AlertChannelResponse],
    summary="List channels",
    description="Get available alert channels"
)
async def list_alert_channels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[AlertChannelResponse]:
    """List alert channels."""
    service = AlertingService(db)
    channels = await service.list_channels(user_id=current_user.id)
    
    # Filter channels based on user role
    if current_user.role == "free":
        channels = [ch for ch in channels if ch.channel_type in ["email", "web"]]
    
    return channels

@router.get(
    "/{alert_id}/status",
    response_model=AlertStatusResponse,
    summary="Get status",
    description="Get alert status and metrics"
)
async def get_alert_status(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AlertStatusResponse:
    """Get alert status."""
    service = AlertingService(db)
    status = await service.get_alert_status(
        alert_id=alert_id,
        user_id=current_user.id
    )
    
    if not status:
        raise ResourceNotFoundError(f"Alert {alert_id} not found")
    
    return status

@router.get(
    "/aggregation",
    response_model=AlertAggregationResponse,
    summary="Get aggregation",
    description="Get alert aggregation analytics"
)
async def get_alert_aggregation(
    group_by: str = Query(
        "category",
        regex="^(category|status|severity|channel)$"
    ),
    time_range: str = Query(
        "1d",
        regex="^(1h|1d|1w|1m)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AlertAggregationResponse:
    """Get alert aggregation."""
    service = AlertingService(db)
    return await service.get_aggregation(
        user_id=current_user.id,
        group_by=group_by,
        time_range=time_range
    )
