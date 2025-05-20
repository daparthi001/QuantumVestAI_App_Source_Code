"""
Risk Analysis Router
Created: 2025-05-20 04:54:55
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError, PermissionDeniedError
from db.session import get_db
from api.db.models.user import User
from api.services.risk_service import RiskService
from api.schemas.risk import (
    PortfolioRiskResponse,
    MarketRiskResponse,
    RiskFactorResponse,
    StressTestResponse,
    ScenarioAnalysisResponse,
    RiskAlertResponse,
    CorrelationResponse,
    VaRResponse
)

router = APIRouter(
    prefix="/risk",
    tags=["risk"],
    dependencies=[Depends(get_current_user)]
)

@router.get(
    "/portfolio/{portfolio_id}",
    response_model=PortfolioRiskResponse,
    summary="Portfolio risk",
    description="Get portfolio risk analysis"
)
async def get_portfolio_risk(
    portfolio_id: int,
    risk_measures: List[str] = Query(
        ["var", "cvar", "beta", "volatility"],
        description="Risk measures to calculate"
    ),
    confidence_level: float = Query(
        0.95,
        ge=0.8,
        le=0.99,
        description="Confidence level for VaR"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioRiskResponse:
    """Get portfolio risk analysis."""
    if current_user.role == "free":
        raise PermissionDeniedError("Risk analysis requires premium subscription")
    
    service = RiskService(db)
    risk = await service.get_portfolio_risk(
        portfolio_id=portfolio_id,
        risk_measures=risk_measures,
        confidence_level=confidence_level,
        user_id=current_user.id
    )
    
    if not risk:
        raise ResourceNotFoundError(f"Portfolio {portfolio_id} not found")
    
    return risk

@router.get(
    "/market",
    response_model=MarketRiskResponse,
    summary="Market risk",
    description="Get market risk indicators"
)
async def get_market_risk(
    indices: List[str] = Query(
        ["SPX", "VIX", "TNX"],
        description="Market indices to analyze"
    ),
    lookback_days: int = Query(
        30,
        ge=1,
        le=365,
        description="Analysis lookback period"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MarketRiskResponse:
    """Get market risk indicators."""
    service = RiskService(db)
    return await service.get_market_risk(
        indices=indices,
        lookback_days=lookback_days
    )

@router.get(
    "/factors",
    response_model=List[RiskFactorResponse],
    summary="Risk factors",
    description="Get risk factor analysis"
)
async def get_risk_factors(
    portfolio_id: Optional[int] = None,
    factor_types: List[str] = Query(
        ["macro", "style", "sector"],
        description="Risk factor types"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[RiskFactorResponse]:
    """Get risk factor analysis."""
    service = RiskService(db)
    return await service.get_risk_factors(
        portfolio_id=portfolio_id,
        factor_types=factor_types,
        user_id=current_user.id
    )

@router.post(
    "/stress-test",
    response_model=StressTestResponse,
    summary="Stress test",
    description="Run portfolio stress test"
)
async def run_stress_test(
    portfolio_id: int,
    scenarios: Dict[str, Any],
    shock_level: float = Query(
        1.0,
        ge=0.1,
        le=3.0,
        description="Shock intensity multiplier"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> StressTestResponse:
    """Run stress test."""
    if current_user.role != "premium":
        raise PermissionDeniedError(
            "Stress testing requires premium subscription"
        )
    
    service = RiskService(db)
    return await service.run_stress_test(
        portfolio_id=portfolio_id,
        scenarios=scenarios,
        shock_level=shock_level,
        user_id=current_user.id
    )

@router.post(
    "/scenario-analysis",
    response_model=ScenarioAnalysisResponse,
    summary="Scenario analysis",
    description="Run scenario analysis"
)
async def run_scenario_analysis(
    portfolio_id: int,
    scenarios: List[Dict[str, Any]],
    probability_weighted: bool = Query(
        True,
        description="Use probability-weighted results"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ScenarioAnalysisResponse:
    """Run scenario analysis."""
    service = RiskService(db)
    return await service.run_scenario_analysis(
        portfolio_id=portfolio_id,
        scenarios=scenarios,
        probability_weighted=probability_weighted,
        user_id=current_user.id
    )

@router.post(
    "/alerts",
    response_model=RiskAlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create risk alert",
    description="Create new risk monitoring alert"
)
async def create_risk_alert(
    portfolio_id: int,
    metric: str = Query(..., regex="^(var|drawdown|volatility|correlation)$"),
    threshold: float = Query(..., description="Alert threshold"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RiskAlertResponse:
    """Create risk alert."""
    service = RiskService(db)
    return await service.create_alert(
        portfolio_id=portfolio_id,
        metric=metric,
        threshold=threshold,
        user_id=current_user.id
    )

@router.get(
    "/correlation",
    response_model=CorrelationResponse,
    summary="Get correlations",
    description="Get asset correlations"
)
async def get_correlations(
    symbols: List[str],
    lookback_days: int = Query(
        90,
        ge=30,
        le=365,
        description="Correlation lookback period"
    ),
    method: str = Query(
        "pearson",
        regex="^(pearson|spearman|kendall)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CorrelationResponse:
    """Get asset correlations."""
    service = RiskService(db)
    return await service.get_correlations(
        symbols=symbols,
        lookback_days=lookback_days,
        method=method
    )

@router.get(
    "/var/{portfolio_id}",
    response_model=VaRResponse,
    summary="Calculate VaR",
    description="Calculate Value at Risk"
)
async def calculate_var(
    portfolio_id: int,
    method: str = Query(
        "historical",
        regex="^(historical|parametric|monte_carlo)$"
    ),
    confidence_level: float = Query(
        0.95,
        ge=0.9,
        le=0.99
    ),
    time_horizon: int = Query(
        1,
        ge=1,
        le=30,
        description="Time horizon in days"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> VaRResponse:
    """Calculate Value at Risk."""
    if current_user.role == "free":
        raise PermissionDeniedError("VaR calculation requires premium subscription")
    
    service = RiskService(db)
    return await service.calculate_var(
        portfolio_id=portfolio_id,
        method=method,
        confidence_level=confidence_level,
        time_horizon=time_horizon,
        user_id=current_user.id
    )