"""
Analytics Router
Created: 2025-05-20 05:03:42
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from api.core.security import get_current_user
from api.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from api.db.session import get_db
from api.db.models.user import User
from api.services.analytics_service import AnalyticsService
from api.schemas.analytics import (
    PortfolioAnalyticsResponse,
    MarketAnalyticsResponse,
    TradingAnalyticsResponse,
    RiskAnalyticsResponse,
    PerformanceAnalyticsResponse,
    PredictiveAnalyticsResponse,
    SentimentAnalyticsResponse,
    CustomAnalyticsResponse
)

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)]
)

@router.get(
    "/portfolio/{portfolio_id}",
    response_model=PortfolioAnalyticsResponse,
    summary="Portfolio analytics",
    description="Get portfolio analytics and insights"
)
async def get_portfolio_analytics(
    portfolio_id: int,
    metrics: List[str] = Query(
        ["returns", "risk", "allocation", "performance"],
        description="Analytics metrics to calculate"
    ),
    time_range: str = Query(
        "1m",
        regex="^(1d|1w|1m|3m|6m|1y|ytd|all)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioAnalyticsResponse:
    """Get portfolio analytics."""
    service = AnalyticsService(db)
    analytics = await service.get_portfolio_analytics(
        portfolio_id=portfolio_id,
        metrics=metrics,
        time_range=time_range,
        user_id=current_user.id
    )
    
    if not analytics:
        raise ResourceNotFoundError(f"Portfolio {portfolio_id} not found")
    
    return analytics

@router.get(
    "/market",
    response_model=MarketAnalyticsResponse,
    summary="Market analytics",
    description="Get market analytics and trends"
)
async def get_market_analytics(
    symbols: List[str] = Query(
        ...,
        min_items=1,
        max_items=20,
        description="Market symbols to analyze"
    ),
    indicators: List[str] = Query(
        ["price", "volume", "volatility", "momentum"],
        description="Technical indicators to include"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MarketAnalyticsResponse:
    """Get market analytics."""
    service = AnalyticsService(db)
    return await service.get_market_analytics(
        symbols=symbols,
        indicators=indicators
    )

@router.get(
    "/trading",
    response_model=TradingAnalyticsResponse,
    summary="Trading analytics",
    description="Get trading performance analytics"
)
async def get_trading_analytics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    strategy: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TradingAnalyticsResponse:
    """Get trading analytics."""
    service = AnalyticsService(db)
    return await service.get_trading_analytics(
        start_date=start_date,
        end_date=end_date,
        strategy=strategy,
        user_id=current_user.id
    )

@router.get(
    "/risk",
    response_model=RiskAnalyticsResponse,
    summary="Risk analytics",
    description="Get risk analytics and exposure"
)
async def get_risk_analytics(
    portfolio_id: Optional[int] = None,
    risk_metrics: List[str] = Query(
        ["var", "volatility", "beta", "correlation"],
        description="Risk metrics to analyze"
    ),
    scenario: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RiskAnalyticsResponse:
    """Get risk analytics."""
    service = AnalyticsService(db)
    return await service.get_risk_analytics(
        portfolio_id=portfolio_id,
        risk_metrics=risk_metrics,
        scenario=scenario,
        user_id=current_user.id
    )

@router.get(
    "/performance",
    response_model=PerformanceAnalyticsResponse,
    summary="Performance analytics",
    description="Get performance attribution analytics"
)
async def get_performance_analytics(
    portfolio_id: int,
    benchmark: Optional[str] = None,
    factors: List[str] = Query(
        ["market", "size", "value", "momentum"],
        description="Performance factors"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PerformanceAnalyticsResponse:
    """Get performance analytics."""
    service = AnalyticsService(db)
    return await service.get_performance_analytics(
        portfolio_id=portfolio_id,
        benchmark=benchmark,
        factors=factors,
        user_id=current_user.id
    )

@router.get(
    "/predictive",
    response_model=PredictiveAnalyticsResponse,
    summary="Predictive analytics",
    description="Get predictive market analytics"
)
async def get_predictive_analytics(
    symbols: List[str],
    horizon: str = Query(
        "1d",
        regex="^(1d|1w|1m|3m|6m|1y)$"
    ),
    confidence_level: float = Query(0.95, ge=0.5, le=0.99),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PredictiveAnalyticsResponse:
    """Get predictive analytics."""
    if current_user.role == "free":
        raise PermissionDeniedError(
            "Predictive analytics requires premium subscription"
        )
    
    service = AnalyticsService(db)
    return await service.get_predictive_analytics(
        symbols=symbols,
        horizon=horizon,
        confidence_level=confidence_level
    )

@router.get(
    "/sentiment",
    response_model=SentimentAnalyticsResponse,
    summary="Sentiment analytics",
    description="Get market sentiment analytics"
)
async def get_sentiment_analytics(
    symbols: List[str],
    sources: List[str] = Query(
        ["news", "social", "filings"],
        description="Sentiment data sources"
    ),
    lookback_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SentimentAnalyticsResponse:
    """Get sentiment analytics."""
    service = AnalyticsService(db)
    return await service.get_sentiment_analytics(
        symbols=symbols,
        sources=sources,
        lookback_days=lookback_days
    )

@router.post(
    "/custom",
    response_model=CustomAnalyticsResponse,
    summary="Custom analytics",
    description="Run custom analytics query"
)
async def run_custom_analytics(
    query_type: str = Query(
        ...,
        regex="^(correlation|regression|clustering|factor)$"
    ),
    parameters: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CustomAnalyticsResponse:
    """Run custom analytics."""
    if current_user.role != "premium":
        raise PermissionDeniedError(
            "Custom analytics requires premium subscription"
        )
    
    service = AnalyticsService(db)
    return await service.run_custom_analytics(
        query_type=query_type,
        parameters=parameters,
        user_id=current_user.id
    )