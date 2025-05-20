"""
Whitepaper Analysis Router
Created: 2025-05-20 04:49:49
Author: daparthi001
"""
from fastapi import APIRouter, Depends, File, UploadFile, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.core.security import get_current_user
from api.core.exceptions import (
    ResourceNotFoundError, 
    ValidationError,
    PermissionDeniedError
)
from api.db.session import get_db
from api.db.models.user import User
from api.services.whitepaper_service import WhitepaperService
from api.schemas.whitepaper import (
    WhitepaperResponse,
    WhitepaperAnalysisResponse,
    WhitepaperComparisonResponse,
    WhitepaperMetricsResponse,
    WhitepaperSummaryResponse
)

router = APIRouter(
    prefix="/whitepapers",
    tags=["whitepapers"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/upload",
    response_model=WhitepaperResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload whitepaper",
    description="Upload a new whitepaper for analysis"
)
async def upload_whitepaper(
    file: UploadFile = File(...),
    ticker: str = Query(..., min_length=1, max_length=10),
    document_type: str = Query(
        "annual_report",
        regex="^(annual_report|quarterly_report|presentation|research)$"
    ),
    document_date: str = Query(
        ...,
        regex=r"^\d{4}-\d{2}-\d{2}$",
        description="Document date (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WhitepaperResponse:
    """Upload whitepaper for analysis."""
    if current_user.role == "free":
        raise PermissionDeniedError(
            "Whitepaper analysis requires premium subscription"
        )
    
    # Validate file type
    allowed_types = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise ValidationError("Invalid file type. Only PDF and Word documents are allowed.")
    
    service = WhitepaperService(db)
    whitepaper = await service.upload_whitepaper(
        file=file,
        ticker=ticker,
        document_type=document_type,
        document_date=document_date,
        user_id=current_user.id
    )
    
    return whitepaper

@router.get(
    "/{whitepaper_id}/analysis",
    response_model=WhitepaperAnalysisResponse,
    summary="Get analysis",
    description="Get comprehensive analysis of a whitepaper"
)
async def get_whitepaper_analysis(
    whitepaper_id: int,
    analysis_type: str = Query(
        "full",
        regex="^(full|financial|strategic|risk|sentiment)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WhitepaperAnalysisResponse:
    """Get whitepaper analysis."""
    service = WhitepaperService(db)
    analysis = await service.get_analysis(
        whitepaper_id=whitepaper_id,
        analysis_type=analysis_type,
        user_id=current_user.id
    )
    
    if not analysis:
        raise ResourceNotFoundError(f"Whitepaper {whitepaper_id} not found")
    
    return analysis

@router.get(
    "/{whitepaper_id}/compare/{compare_id}",
    response_model=WhitepaperComparisonResponse,
    summary="Compare whitepapers",
    description="Compare two whitepapers"
)
async def compare_whitepapers(
    whitepaper_id: int,
    compare_id: int,
    comparison_aspects: List[str] = Query(
        ["financial_metrics", "strategic_goals", "risk_factors"],
        description="Aspects to compare"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WhitepaperComparisonResponse:
    """Compare whitepapers."""
    service = WhitepaperService(db)
    comparison = await service.compare_whitepapers(
        whitepaper_id=whitepaper_id,
        compare_id=compare_id,
        aspects=comparison_aspects,
        user_id=current_user.id
    )
    
    return comparison

@router.get(
    "/{whitepaper_id}/metrics",
    response_model=WhitepaperMetricsResponse,
    summary="Get metrics",
    description="Get extracted metrics from whitepaper"
)
async def get_whitepaper_metrics(
    whitepaper_id: int,
    metric_types: List[str] = Query(
        ["financial", "operational", "market"],
        description="Types of metrics to extract"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WhitepaperMetricsResponse:
    """Get whitepaper metrics."""
    service = WhitepaperService(db)
    metrics = await service.get_metrics(
        whitepaper_id=whitepaper_id,
        metric_types=metric_types,
        user_id=current_user.id
    )
    
    if not metrics:
        raise ResourceNotFoundError(f"Whitepaper {whitepaper_id} not found")
    
    return metrics

@router.get(
    "/{whitepaper_id}/summary",
    response_model=WhitepaperSummaryResponse,
    summary="Get summary",
    description="Get AI-generated summary of whitepaper"
)
async def get_whitepaper_summary(
    whitepaper_id: int,
    summary_type: str = Query(
        "executive",
        regex="^(executive|detailed|bullet_points)$"
    ),
    max_length: int = Query(
        1000,
        ge=100,
        le=5000,
        description="Maximum summary length"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WhitepaperSummaryResponse:
    """Get whitepaper summary."""
    service = WhitepaperService(db)
    summary = await service.get_summary(
        whitepaper_id=whitepaper_id,
        summary_type=summary_type,
        max_length=max_length,
        user_id=current_user.id
    )
    
    if not summary:
        raise ResourceNotFoundError(f"Whitepaper {whitepaper_id} not found")
    
    return summary