"""
Market Data Router
Created: 2025-05-20 04:47:45
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError, PermissionDeniedError
from db.session import get_db
from db.models.user import User
from services.data_service import MarketDataService
from schemas.market_data import (
    HistoricalDataResponse,
    TechnicalIndicatorResponse,
    MarketIndexResponse,
    SectorPerformanceResponse,
    EarningsCalendarResponse,
    ScreenerResponse
)

router = APIRouter(
    prefix="/data",
    tags=["market-data"],
    dependencies=[Depends(get_current_user)]
)

@router.get(
    "/historical/{ticker}",
    response_model=HistoricalDataResponse,
    summary="Get historical data",
    description="Get historical price and volume data"
)
async def get_historical_data(
    ticker: str = Path(..., min_length=1, max_length=10),
    interval: str = Query(
        "1d",
        regex="^(1m|5m|15m|30m|1h|1d|1wk|1mo)$"
    ),
    start_date: str = Query(
        ...,
        regex=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date (YYYY-MM-DD)"
    ),
    end_date: str = Query(
        ...,
        regex=r"^\d{4}-\d{2}-\d{2}$",
        description="End date (YYYY-MM-DD)"
    ),
    adjusted: bool = Query(True, description="Use adjusted prices"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HistoricalDataResponse:
    """Get historical market data."""
    if interval in ["1m", "5m"] and current_user.role == "free":
        raise PermissionDeniedError(
            "Minute-level data requires premium subscription"
        )
    
    service = MarketDataService(db)
    data = await service.get_historical_data(
        ticker=ticker,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        adjusted=adjusted
    )
    
    if not data:
        raise ResourceNotFoundError(f"Historical data not found for {ticker}")
    
    return data

@router.get(
    "/technical/{ticker}",
    response_model=List[TechnicalIndicatorResponse],
    summary="Get technical indicators",
    description="Calculate technical indicators for a stock"
)
async def get_technical_indicators(
    ticker: str = Path(..., min_length=1, max_length=10),
    indicators: List[str] = Query(
        ["SMA", "EMA", "RSI", "MACD"],
        description="Technical indicators to calculate"
    ),
    period: str = Query(
        "1mo",
        regex="^(1d|1wk|1mo|3mo|6mo|1y)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TechnicalIndicatorResponse]:
    """Get technical indicators."""
    if current_user.role == "free" and len(indicators) > 3:
        raise PermissionDeniedError(
            "Free users are limited to 3 indicators"
        )
    
    service = MarketDataService(db)
    data = await service.get_technical_indicators(
        ticker=ticker,
        indicators=indicators,
        period=period
    )
    
    return data

@router.get(
    "/market/indices",
    response_model=List[MarketIndexResponse],
    summary="Get market indices",
    description="Get major market indices data"
)
async def get_market_indices(
    indices: List[str] = Query(
        ["SPX", "NDX", "DJI"],
        description="Market indices to fetch"
    ),
    db: Session = Depends(get_db)
) -> List[MarketIndexResponse]:
    """Get market indices data."""
    service = MarketDataService(db)
    data = await service.get_market_indices(indices)
    return data

@router.get(
    "/market/sectors",
    response_model=SectorPerformanceResponse,
    summary="Get sector performance",
    description="Get market sector performance"
)
async def get_sector_performance(
    period: str = Query(
        "1d",
        regex="^(1d|1w|1m|3m|6m|1y|ytd)$"
    ),
    db: Session = Depends(get_db)
) -> SectorPerformanceResponse:
    """Get sector performance."""
    service = MarketDataService(db)
    data = await service.get_sector_performance(period)
    return data

@router.get(
    "/calendar/earnings",
    response_model=List[EarningsCalendarResponse],
    summary="Get earnings calendar",
    description="Get upcoming earnings announcements"
)
async def get_earnings_calendar(
    start_date: str = Query(
        ...,
        regex=r"^\d{4}-\d{2}-\d{2}$"
    ),
    end_date: str = Query(
        ...,
        regex=r"^\d{4}-\d{2}-\d{2}$"
    ),
    symbols: Optional[List[str]] = Query(
        None,
        description="Filter by symbols"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[EarningsCalendarResponse]:
    """Get earnings calendar."""
    service = MarketDataService(db)
    data = await service.get_earnings_calendar(
        start_date=start_date,
        end_date=end_date,
        symbols=symbols
    )
    return data

@router.post(
    "/screener",
    response_model=ScreenerResponse,
    summary="Stock screener",
    description="Screen stocks based on criteria"
)
async def screen_stocks(
    criteria: Dict[str, Any],
    limit: int = Query(50, ge=1, le=1000),
    sort_by: str = Query("market_cap", description="Sort field"),
    ascending: bool = Query(False, description="Sort order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ScreenerResponse:
    """Screen stocks based on criteria."""
    if current_user.role == "free" and len(criteria) > 3:
        raise PermissionDeniedError(
            "Free users are limited to 3 screening criteria"
        )
    
    service = MarketDataService(db)
    results = await service.screen_stocks(
        criteria=criteria,
        limit=limit,
        sort_by=sort_by,
        ascending=ascending
    )
    
    return results
