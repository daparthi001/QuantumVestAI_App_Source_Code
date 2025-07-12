"""
Compliance Router
Created: 2025-05-20 05:00:34
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError, PermissionDeniedError, ComplianceViolationError
from db.session import get_db
from db.models.user import User
from services.compliance_service import ComplianceService
from schemas.compliance import (
    ComplianceRuleResponse,
    ComplianceCheckResponse,
    ComplianceReportResponse,
    ComplianceViolationResponse,
    ComplianceConfigResponse,
    ComplianceAuditResponse,
    RegulatoryFilingResponse,
    ComplianceStatusResponse
)

router = APIRouter(
    prefix="/compliance",
    tags=["compliance"],
    dependencies=[Depends(get_current_user)]
)

@router.get(
    "/rules",
    response_model=List[ComplianceRuleResponse],
    summary="List rules",
    description="Get compliance rules"
)
async def list_compliance_rules(
    category: Optional[str] = Query(
        None,
        regex="^(trading|portfolio|risk|regulatory)$"
    ),
    status: Optional[str] = Query(
        None,
        regex="^(active|inactive|pending)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ComplianceRuleResponse]:
    """List compliance rules."""
    if current_user.role not in ["admin", "compliance"]:
        raise PermissionDeniedError(
            "Compliance rules access restricted to admin and compliance users"
        )
    
    service = ComplianceService(db)
    return await service.list_rules(
        category=category,
        status=status
    )

@router.post(
    "/check",
    response_model=ComplianceCheckResponse,
    summary="Check compliance",
    description="Check compliance for an action"
)
async def check_compliance(
    action_type: str = Query(
        ...,
        regex="^(trade|portfolio_change|risk_limit|user_action)$"
    ),
    action_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ComplianceCheckResponse:
    """Check compliance for action."""
    service = ComplianceService(db)
    result = await service.check_compliance(
        action_type=action_type,
        action_data=action_data,
        user_id=current_user.id
    )
    
    if not result.compliant:
        raise ComplianceViolationError(
            "Action violates compliance rules",
            details=result.violations
        )
    
    return result

@router.get(
    "/reports",
    response_model=List[ComplianceReportResponse],
    summary="List reports",
    description="Get compliance reports"
)
async def list_compliance_reports(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    report_type: Optional[str] = Query(
        None,
        regex="^(daily|weekly|monthly|quarterly|annual)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ComplianceReportResponse]:
    """List compliance reports."""
    if current_user.role not in ["admin", "compliance"]:
        raise PermissionDeniedError(
            "Compliance reports access restricted to admin and compliance users"
        )
    
    service = ComplianceService(db)
    return await service.list_reports(
        start_date=start_date,
        end_date=end_date,
        report_type=report_type
    )

@router.get(
    "/violations",
    response_model=List[ComplianceViolationResponse],
    summary="List violations",
    description="Get compliance violations"
)
async def list_violations(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    severity: Optional[str] = Query(
        None,
        regex="^(low|medium|high|critical)$"
    ),
    status: Optional[str] = Query(
        None,
        regex="^(open|resolved|investigating)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ComplianceViolationResponse]:
    """List compliance violations."""
    service = ComplianceService(db)
    return await service.list_violations(
        start_date=start_date,
        end_date=end_date,
        severity=severity,
        status=status,
        user_id=current_user.id
    )

@router.get(
    "/config",
    response_model=ComplianceConfigResponse,
    summary="Get configuration",
    description="Get compliance configuration"
)
async def get_compliance_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ComplianceConfigResponse:
    """Get compliance configuration."""
    if current_user.role not in ["admin", "compliance"]:
        raise PermissionDeniedError(
            "Configuration access restricted to admin and compliance users"
        )
    
    service = ComplianceService(db)
    return await service.get_config()

@router.post(
    "/audit",
    response_model=ComplianceAuditResponse,
    summary="Run audit",
    description="Run compliance audit"
)
async def run_compliance_audit(
    audit_type: str = Query(
        ...,
        regex="^(full|portfolio|trading|risk)$"
    ),
    parameters: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ComplianceAuditResponse:
    """Run compliance audit."""
    if current_user.role not in ["admin", "compliance"]:
        raise PermissionDeniedError(
            "Audit execution restricted to admin and compliance users"
        )
    
    service = ComplianceService(db)
    audit = await service.create_audit(
        audit_type=audit_type,
        parameters=parameters,
        user_id=current_user.id
    )
    
    background_tasks.add_task(
        service.run_audit,
        audit_id=audit.id
    )
    
    return audit

@router.post(
    "/regulatory-filing",
    response_model=RegulatoryFilingResponse,
    summary="Submit filing",
    description="Submit regulatory filing"
)
async def submit_regulatory_filing(
    filing_type: str = Query(
        ...,
        regex="^(form_pf|form_adr|form_13f|form_13h)$"
    ),
    filing_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RegulatoryFilingResponse:
    """Submit regulatory filing."""
    if current_user.role not in ["admin", "compliance"]:
        raise PermissionDeniedError(
            "Filing submission restricted to admin and compliance users"
        )
    
    service = ComplianceService(db)
    return await service.submit_filing(
        filing_type=filing_type,
        filing_data=filing_data,
        user_id=current_user.id
    )

@router.get(
    "/status",
    response_model=ComplianceStatusResponse,
    summary="Get status",
    description="Get compliance status overview"
)
async def get_compliance_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ComplianceStatusResponse:
    """Get compliance status."""
    service = ComplianceService(db)
    return await service.get_status(user_id=current_user.id)
