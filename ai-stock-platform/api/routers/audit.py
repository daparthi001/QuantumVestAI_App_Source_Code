"""
Audit Router
Created: 2025-05-20 05:02:05
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.exceptions import PermissionDeniedError, ResourceNotFoundError
from core.security import get_current_user
from db.models.user import User
from db.session import get_db
from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query, status
from schemas.audit import (AuditEventResponse, AuditExportResponse,
                           AuditFilterResponse, AuditLogResponse,
                           AuditSearchResponse, AuditStatisticsResponse,
                           AuditTrailResponse, UserActivityResponse)
from services.audit_service import AuditService
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(get_current_user)]
)

@router.get(
    "/logs",
    response_model=List[AuditLogResponse],
    summary="Get audit logs",
    description="Get system audit logs"
)
async def get_audit_logs(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    event_type: Optional[str] = Query(
        None,
        regex="^(user|system|security|data|compliance)$"
    ),
    severity: Optional[str] = Query(
        None,
        regex="^(info|warning|error|critical)$"
    ),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[AuditLogResponse]:
    """Get audit logs."""
    if current_user.role not in ["admin", "auditor"]:
        raise PermissionDeniedError(
            "Audit logs access restricted to admin and auditor users"
        )
    
    service = AuditService(db)
    return await service.get_logs(
        start_date=start_date,
        end_date=end_date,
        event_type=event_type,
        severity=severity,
        limit=limit
    )

@router.get(
    "/trail/{resource_id}",
    response_model=AuditTrailResponse,
    summary="Get audit trail",
    description="Get resource audit trail"
)
async def get_audit_trail(
    resource_id: str,
    resource_type: str = Query(
        ...,
        regex="^(user|portfolio|trade|alert|report)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AuditTrailResponse:
    """Get resource audit trail."""
    service = AuditService(db)
    trail = await service.get_trail(
        resource_id=resource_id,
        resource_type=resource_type,
        user_id=current_user.id
    )
    
    if not trail:
        raise ResourceNotFoundError(
            f"Audit trail not found for {resource_type} {resource_id}"
        )
    
    return trail

@router.get(
    "/events/{event_id}",
    response_model=AuditEventResponse,
    summary="Get event details",
    description="Get audit event details"
)
async def get_audit_event(
    event_id: str,
    include_context: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AuditEventResponse:
    """Get audit event details."""
    if current_user.role not in ["admin", "auditor"]:
        raise PermissionDeniedError(
            "Event details access restricted to admin and auditor users"
        )
    
    service = AuditService(db)
    event = await service.get_event(
        event_id=event_id,
        include_context=include_context
    )
    
    if not event:
        raise ResourceNotFoundError(f"Audit event {event_id} not found")
    
    return event

@router.get(
    "/filters",
    response_model=AuditFilterResponse,
    summary="Get audit filters",
    description="Get available audit filters"
)
async def get_audit_filters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AuditFilterResponse:
    """Get available audit filters."""
    service = AuditService(db)
    return await service.get_filters()

@router.post(
    "/export",
    response_model=AuditExportResponse,
    summary="Export audit data",
    description="Export audit data to file"
)
async def export_audit_data(
    start_date: datetime,
    end_date: datetime,
    filters: Dict[str, Any],
    format: str = Query(
        "csv",
        regex="^(csv|json|pdf)$"
    ),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AuditExportResponse:
    """Export audit data."""
    if current_user.role not in ["admin", "auditor"]:
        raise PermissionDeniedError(
            "Data export restricted to admin and auditor users"
        )
    
    service = AuditService(db)
    export = await service.create_export(
        start_date=start_date,
        end_date=end_date,
        filters=filters,
        format=format,
        user_id=current_user.id
    )
    
    background_tasks.add_task(
        service.process_export,
        export_id=export.id
    )
    
    return export

@router.get(
    "/statistics",
    response_model=AuditStatisticsResponse,
    summary="Get statistics",
    description="Get audit statistics"
)
async def get_audit_statistics(
    time_range: str = Query(
        "1d",
        regex="^(1h|1d|1w|1m|1y)$"
    ),
    group_by: Optional[str] = Query(
        None,
        regex="^(event_type|severity|user|resource)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AuditStatisticsResponse:
    """Get audit statistics."""
    service = AuditService(db)
    return await service.get_statistics(
        time_range=time_range,
        group_by=group_by
    )

@router.post(
    "/search",
    response_model=AuditSearchResponse,
    summary="Search audit logs",
    description="Search audit logs with query"
)
async def search_audit_logs(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AuditSearchResponse:
    """Search audit logs."""
    service = AuditService(db)
    return await service.search_logs(
        query=query,
        filters=filters,
        page=page,
        page_size=page_size
    )

@router.get(
    "/activity/{user_id}",
    response_model=UserActivityResponse,
    summary="Get user activity",
    description="Get user activity audit"
)
async def get_user_activity(
    user_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    activity_type: Optional[str] = Query(
        None,
        regex="^(login|action|system|data)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserActivityResponse:
    """Get user activity audit."""
    if current_user.role not in ["admin", "auditor"] and current_user.id != user_id:
        raise PermissionDeniedError(
            "Activity access restricted to admin, auditor, or own user"
        )
    
    service = AuditService(db)
    return await service.get_user_activity(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        activity_type=activity_type
    )
