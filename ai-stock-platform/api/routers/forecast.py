"""
Forecast Router
Created: 2025-05-20 04:42:45
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from api.core.security import get_optional_current_user, get_current_user
from api.core.config import settings
from api.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from api.db.session import get_db
from api.db.models.user import User
from api.services.forecast_service import ForecastService
from api.services.stock_service import StockService
from api.schemas.forecast import (
    ForecastResponse,
    ModelComparisonResponse,
    PredictabilityResponse,
    BacktestResponse,
    RecommendationResponse
)

router = APIRouter(
    prefix="/forecast",
    tags=["forecast"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/{ticker}",
    response_model=ForecastResponse,
    summary="Get stock forecast",
    description="Get forecast for a stock using specified model"
)
async def get_stock_forecast(
    ticker: str = Path(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol"
    ),
    days: int = Query(
        7,
        ge=1,
        le=settings.MAX_FORECAST_DAYS,
        description="Forecast days"
    ),
    model: str = Query(
        "ensemble",
        regex="^(ensemble|lstm|prophet|xgboost|arima)$",
        description="Forecast model"
    ),
    include_sentiment: bool = Query(
        False,
        description="Include sentiment analysis"
    ),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> ForecastResponse:
    """
    Get forecast for a stock.
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days to forecast
        model: Forecast model to use
        include_sentiment: Whether to include sentiment analysis
        db: Database session
        current_user: Optional current user
    
    Returns:
        ForecastResponse: Forecast data
    
    Raises:
        ResourceNotFoundError: If stock not found
        PermissionDeniedError: If user doesn't have required permissions
    """
    # Verify ticker exists
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Check permissions for advanced models
    if current_user and current_user.role == "free" and model != "ensemble":
        raise PermissionDeniedError(
            "Free users can only access ensemble model forecasts"
        )
    
    # Check permissions for sentiment analysis
    if include_sentiment and (not current_user or current_user.role == "free"):
        include_sentiment = False
    
    # Get forecast
    forecast_service = ForecastService(db)
    forecast = await forecast_service.get_forecast(
        ticker=ticker,
        days=days,
        model=model,
        include_sentiment=include_sentiment
    )
    
    if not forecast:
        raise ResourceNotFoundError(
            f"Could not generate forecast for {ticker}"
        )
    
    return forecast

@router.get(
    "/{ticker}/compare-models",
    response_model=ModelComparisonResponse,
    summary="Compare forecast models",
    description="Compare different forecast models for a stock"
)
async def compare_forecast_models(
    ticker: str = Path(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol"
    ),
    days: int = Query(
        7,
        ge=1,
        le=settings.MAX_FORECAST_DAYS,
        description="Forecast days"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ModelComparisonResponse:
    """Compare different forecast models for a stock."""
    # Check premium access
    if current_user.role == "free":
        raise PermissionDeniedError(
            "Model comparison requires a premium subscription"
        )
    
    # Verify ticker exists
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Get model comparison
    forecast_service = ForecastService(db)
    comparison = await forecast_service.compare_models(ticker, days)
    
    return comparison

@router.get(
    "/{ticker}/predictability",
    response_model=PredictabilityResponse,
    summary="Get stock predictability",
    description="Get predictability analysis for a stock"
)
async def get_stock_predictability(
    ticker: str = Path(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PredictabilityResponse:
    """Get predictability analysis for a stock."""
    # Verify ticker exists
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Get predictability analysis
    forecast_service = ForecastService(db)
    predictability = await forecast_service.get_predictability(ticker)
    
    return predictability

@router.get(
    "/{ticker}/backtest",
    response_model=BacktestResponse,
    summary="Backtest forecast model",
    description="Backtest a forecast model on historical data"
)
async def backtest_forecast(
    ticker: str = Path(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol"
    ),
    days: int = Query(
        7,
        ge=1,
        le=30,
        description="Forecast days"
    ),
    start_date: str = Query(
        ...,
        regex=r"^\d{4}-\d{2}-\d{2}$",
        description="Backtest start date (YYYY-MM-DD)"
    ),
    end_date: str = Query(
        ...,
        regex=r"^\d{4}-\d{2}-\d{2}$",
        description="Backtest end date (YYYY-MM-DD)"
    ),
    model: str = Query(
        "ensemble",
        regex="^(ensemble|lstm|prophet|xgboost|arima)$",
        description="Forecast model"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> BacktestResponse:
    """Backtest a forecast model on historical data."""
    # Check premium access
    if current_user.role not in ["premium", "admin"]:
        raise PermissionDeniedError(
            "Backtesting requires a premium subscription"
        )
    
    # Verify ticker exists
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Run backtest
    forecast_service = ForecastService(db)
    backtest_results = await forecast_service.backtest(
        ticker=ticker,
        days=days,
        start_date=start_date,
        end_date=end_date,
        model=model
    )
    
    return backtest_results

@router.get(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Get forecast recommendations",
    description="Get stock recommendations based on forecasts"
)
async def get_forecast_recommendations(
    limit: int = Query(
        5,
        ge=1,
        le=20,
        description="Maximum number of recommendations"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RecommendationResponse:
    """Get stock recommendations based on forecasts."""
    forecast_service = ForecastService(db)
    recommendations = await forecast_service.get_recommendations(
        limit=limit,
        user_id=current_user.id
    )
    
    return recommendations