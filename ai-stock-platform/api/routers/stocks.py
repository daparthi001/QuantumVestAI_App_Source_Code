"""
Stock Routes Implementation
Created: 2025-05-19 03:46:56
Author: daparthi001
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.core.deps import (
    get_db,
    get_current_user,
    verify_premium_access,
    get_stock_service
)
from api.services.stock_service import StockService
from api.schemas.stock import (
    StockCreate,
    StockUpdate,
    StockResponse,
    StockPriceResponse,
    TechnicalIndicatorsResponse
)
from api.core.logging import logger

router = APIRouter()

@router.get("/stocks/{symbol}", response_model=StockResponse)
async def get_stock_info(
    symbol: str = Path(..., description="Stock symbol"),
    stock_service: StockService = Depends(get_stock_service),
    current_user = Depends(get_current_user)
):
    """Get stock information"""
    try:
        stock_info = await stock_service.get_stock_info(symbol)
        if not stock_info:
            raise HTTPException(
                status_code=404,
                detail=f"Stock with symbol {symbol} not found"
            )
        return stock_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stock info for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/stocks/{symbol}/prices", response_model=List[StockPriceResponse])
async def get_stock_prices(
    symbol: str = Path(..., description="Stock symbol"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    interval: str = Query("1d", regex="^(1d|5d|1wk|1mo|3mo)$"),
    stock_service: StockService = Depends(get_stock_service),
    current_user = Depends(get_current_user)
):
    """Get historical stock prices"""
    try:
        prices = await stock_service.get_historical_prices(
            symbol,
            start_date,
            end_date,
            interval
        )
        return prices
    except Exception as e:
        logger.error(f"Error getting prices for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch stock prices"
        )

@router.get("/stocks/{symbol}/indicators", response_model=TechnicalIndicatorsResponse)
async def get_technical_indicators(
    symbol: str = Path(..., description="Stock symbol"),
    indicators: List[str] = Query(
        ["sma", "rsi", "macd", "bollinger"],
        description="List of indicators to calculate"
    ),
    current_user = Depends(verify_premium_access),
    stock_service: StockService = Depends(get_stock_service)
):
    """Get technical indicators for a stock"""
    try:
        result = await stock_service.calculate_technical_indicators(
            symbol,
            indicators
        )
        return result
    except Exception as e:
        logger.error(f"Error calculating indicators for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate indicators"
        )

@router.post("/stocks/watchlist", response_model=Dict[str, Any])
async def add_to_watchlist(
    symbol: str = Query(..., description="Stock symbol"),
    current_user = Depends(get_current_user),
    stock_service: StockService = Depends(get_stock_service),
    db: Session = Depends(get_db)
):
    """Add stock to user's watchlist"""
    try:
        # Verify stock exists
        stock_info = await stock_service.get_stock_info(symbol)
        if not stock_info:
            raise HTTPException(
                status_code=404,
                detail=f"Stock with symbol {symbol} not found"
            )
        
        # Add to watchlist
        result = await stock_service.add_to_watchlist(
            db,
            current_user.id,
            symbol
        )
        return {
            "status": "success",
            "message": f"Added {symbol} to watchlist",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding {symbol} to watchlist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to add stock to watchlist"
        )