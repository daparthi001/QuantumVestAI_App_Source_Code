from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from api.core.security import get_optional_current_user, get_current_user
from api.core.config import settings
from api.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from api.db.session import get_db
from api.db.models.user import User
from api.services.forecast_service import ForecastService
from api.services.stock_service import StockService

router = APIRouter(prefix="/forecast")

@router.get("/{ticker}")
async def get_stock_forecast(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    days: int = Query(7, ge=1, le=settings.MAX_FORECAST_DAYS, description="Forecast days"),
    model: str = Query("ensemble", regex="^(ensemble|lstm|prophet|xgboost|arima)$", description="Forecast model"),
    include_sentiment: bool = Query(False, description="Include sentiment analysis"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get forecast for a stock."""
    # Check if ticker exists
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Check if user has sufficient permissions for advanced models
    if current_user and current_user.role == "free" and model != "ensemble":
        raise PermissionDeniedError("Free users can only access ensemble model forecasts")
    
    # Check if user has sufficient permissions for sentiment analysis
    if include_sentiment and (not current_user or current_user.role == "free"):
        include_sentiment = False  # Silently ignore for free users
    
    # Get forecast
    forecast_service = ForecastService(db)
    forecast = await forecast_service.get_forecast(ticker, days, model, include_sentiment)
    
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not generate forecast for {ticker}"
        )
    
    return forecast

@router.get("/{ticker}/compare-models")
async def compare_forecast_models(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    days: int = Query(7, ge=1, le=settings.MAX_FORECAST_DAYS, description="Forecast days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare different forecast models for a stock."""
    # Check if user has sufficient permissions
    if current_user.role == "free":
        raise PermissionDeniedError("Model comparison requires a premium subscription")
    
    # Check if ticker exists
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Get model comparison
    forecast_service = ForecastService(db)
    comparison = await forecast_service.compare_models(ticker, days)
    
    return comparison

@router.get("/{ticker}/predictability")
async def get_stock_predictability(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get predictability analysis for a stock."""
    # Check if ticker exists
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Get predictability analysis
    forecast_service = ForecastService(db)
    predictability = await forecast_service.get_predictability(ticker)
    
    return predictability

@router.get("/{ticker}/backtest")
async def backtest_forecast(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    days: int = Query(7, ge=1, le=30, description="Forecast days"),
    start_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$", description="Backtest start date (YYYY-MM-DD)"),
    end_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$", description="Backtest end date (YYYY-MM-DD)"),
    model: str = Query("ensemble", regex="^(ensemble|lstm|prophet|xgboost|arima)$", description="Forecast model"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Backtest a forecast model on historical data."""
    # Check if user has sufficient permissions
    if current_user.role not in ["premium", "admin"]:
        raise PermissionDeniedError("Backtesting requires a premium subscription")
    
    # Check if ticker exists
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Run backtest
    forecast_service = ForecastService(db)
    backtest_results = await forecast_service.backtest(ticker, days, start_date, end_date, model)
    
    return backtest_results

@router.get("/recommendations")
async def get_forecast_recommendations(
    limit: int = Query(5, ge=1, le=20, description="Maximum number of recommendations"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stock recommendations based on forecasts."""
    forecast_service = ForecastService(db)
    recommendations = await forecast_service.get_recommendations(limit, current_user.id)
    
    return recommendations