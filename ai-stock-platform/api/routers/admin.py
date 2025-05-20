"""
Admin Router
Created: 2025-05-20 04:45:46
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from core.security import get_current_admin_user
from core.exceptions import ResourceNotFoundError, ValidationError
from db.session import get_db
from db.models.user import User
from services.admin_service import AdminService
from schemas.admin import (
    SystemStatusResponse,
    UserManagementResponse,
    APIKeyResponse,
    UsageStatsResponse,
    ModelPerformanceResponse,
    AuditLogResponse
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)]
)

@router.get(
    "/system/status",
    response_model=SystemStatusResponse,
    summary="System status",
    description="Get system status and health metrics"
)
async def get_system_status(
    db: Session = Depends(get_db)
) -> SystemStatusResponse:
    """Get system status."""
    service = AdminService(db)
    return await service.get_system_status()

@router.get(
    "/users",
    response_model=List[UserManagementResponse],
    summary="List users",
    description="Get list of all users with management options"
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    role: Optional[str] = Query(None, regex="^(free|premium|admin)$"),
    search: Optional[str] = Query(None, min_length=3),
    db: Session = Depends(get_db)
) -> List[UserManagementResponse]:
    """List all users."""
    service = AdminService(db)
    return await service.list_users(page, limit, role, search)

@router.post(
    "/users/{user_id}/suspend",
    response_model=UserManagementResponse,
    summary="Suspend user",
    description="Suspend a user account"
)
async def suspend_user(
    user_id: int,
    reason: str = Query(..., min_length=10),
    db: Session = Depends(get_db)
) -> UserManagementResponse:
    """Suspend user account."""
    service = AdminService(db)
    user = await service.suspend_user(user_id, reason)
    
    if not user:
        raise ResourceNotFoundError(f"User {user_id} not found")
    
    return user

@router.post(
    "/api-keys",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
    description="Create a new API key for a user"
)
async def create_api_key(
    user_id: int,
    expires_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
) -> APIKeyResponse:
    """Create new API key."""
    service = AdminService(db)
    return await service.create_api_key(user_id, expires_days)

@router.get(
    "/usage/stats",
    response_model=UsageStatsResponse,
    summary="Usage statistics",
    description="Get platform usage statistics"
)
async def get_usage_stats(
    start_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$"),
    db: Session = Depends(get_db)
) -> UsageStatsResponse:
    """Get usage statistics."""
    service = AdminService(db)
    return await service.get_usage_stats(start_date, end_date)

@router.get(
    "/models/performance",
    response_model=List[ModelPerformanceResponse],
    summary="Model performance",
    description="Get ML model performance metrics"
)
async def get_model_performance(
    period: str = Query(
        "1d",
        regex="^(1d|1w|1m|3m|6m|1y|all)$",
        description="Performance period"
    ),
    db: Session = Depends(get_db)
) -> List[ModelPerformanceResponse]:
    """Get model performance metrics."""
    service = AdminService(db)
    return await service.get_model_performance(period)

@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    summary="Audit logs",
    description="Get system audit logs"
)
async def get_audit_logs(
    start_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$"),
    log_type: Optional[str] = Query(
        None,
        regex="^(auth|data|model|system)$",
        description="Log type filter"
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[AuditLogResponse]:
    """Get audit logs."""
    service = AdminService(db)
    return await service.get_audit_logs(
        start_date,
        end_date,
        log_type,
        page,
        limit
    )