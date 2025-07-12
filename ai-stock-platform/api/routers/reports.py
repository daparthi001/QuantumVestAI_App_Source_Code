"""
Reports Router
Created: 2025-05-20 04:57:51
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
from services.report_service import ReportService
from schemas.reports import (
    ReportCreate,
    ReportResponse,
    ReportTemplateResponse,
    ReportScheduleResponse,
    ReportGenerationResponse,
    CustomReportResponse,
    ReportDeliveryResponse
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create report",
    description="Create a new report"
)
async def create_report(
    report: ReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """Create new report."""
    if current_user.role == "free" and report.report_type != "basic":
        raise PermissionDeniedError(
            "Advanced reports require premium subscription"
        )
    
    service = ReportService(db)
    result = await service.create_report(
        report=report,
        user_id=current_user.id
    )
    
    background_tasks.add_task(
        service.generate_report,
        report_id=result.id
    )
    
    return result

@router.get(
    "/templates",
    response_model=List[ReportTemplateResponse],
    summary="List templates",
    description="Get available report templates"
)
async def list_templates(
    category: Optional[str] = Query(
        None,
        regex="^(portfolio|risk|performance|tax)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ReportTemplateResponse]:
    """List report templates."""
    service = ReportService(db)
    return await service.list_templates(
        category=category,
        user_role=current_user.role
    )

@router.post(
    "/schedule",
    response_model=ReportScheduleResponse,
    summary="Schedule report",
    description="Schedule periodic report generation"
)
async def schedule_report(
    template_id: int,
    schedule: Dict[str, Any],
    delivery_options: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportScheduleResponse:
    """Schedule periodic report."""
    if current_user.role == "free":
        raise PermissionDeniedError(
            "Report scheduling requires premium subscription"
        )
    
    service = ReportService(db)
    return await service.schedule_report(
        template_id=template_id,
        schedule=schedule,
        delivery_options=delivery_options,
        user_id=current_user.id
    )

@router.get(
    "/{report_id}/status",
    response_model=ReportGenerationResponse,
    summary="Get status",
    description="Get report generation status"
)
async def get_report_status(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportGenerationResponse:
    """Get report generation status."""
    service = ReportService(db)
    status = await service.get_status(
        report_id=report_id,
        user_id=current_user.id
    )
    
    if not status:
        raise ResourceNotFoundError(f"Report {report_id} not found")
    
    return status

@router.post(
    "/custom",
    response_model=CustomReportResponse,
    summary="Create custom report",
    description="Create custom report with specific metrics"
)
async def create_custom_report(
    metrics: List[str],
    parameters: Dict[str, Any],
    format: str = Query(
        "pdf",
        regex="^(pdf|excel|html)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CustomReportResponse:
    """Create custom report."""
    if current_user.role != "premium":
        raise PermissionDeniedError(
            "Custom reports require premium subscription"
        )
    
    service = ReportService(db)
    return await service.create_custom_report(
        metrics=metrics,
        parameters=parameters,
        format=format,
        user_id=current_user.id
    )

@router.post(
    "/{report_id}/deliver",
    response_model=ReportDeliveryResponse,
    summary="Deliver report",
    description="Deliver report via specified channel"
)
async def deliver_report(
    report_id: int,
    delivery_method: str = Query(
        ...,
        regex="^(email|api|sftp|webhook)$"
    ),
    delivery_config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportDeliveryResponse:
    """Deliver report."""
    service = ReportService(db)
    return await service.deliver_report(
        report_id=report_id,
        delivery_method=delivery_method,
        delivery_config=delivery_config,
        user_id=current_user.id
    )
