"""
Stocks Router
Created: 2025-05-20 04:43:53
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError
from db.session import get_db
from db.models.user import User
from services.stock_service import StockService
from schemas.stock import (
    StockResponse,
    StockDetailResponse,
    StockPriceResponse,
    StockSearchResponse
)

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/search",
    response_model=List[StockSearchResponse],
    summary="Search stocks",
    description="Search stocks by symbol or name"
)
async def search_stocks(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Results limit"),
    db: Session = Depends(get_db)
) -> List[StockSearchResponse]:
    """Search for stocks."""
    stock_service = StockService(db)
    results = await stock_service.search_stocks(query, limit)
    return results

@router.get(
    "/{ticker}",
    response_model=StockDetailResponse,
    summary="Get stock details",
    description="Get detailed information for a stock"
)
async def get_stock_details(
    ticker: str = Path(..., min_length=1, max_length=10),
    db: Session = Depends(get_db)
) -> StockDetailResponse:
    """Get stock details."""
    stock_service = StockService(db)
    stock = await stock_service.get_stock_details(ticker)
    
    if not stock:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    return stock

@router.get(
    "/{ticker}/price",
    response_model=StockPriceResponse,
    summary="Get stock price",
    description="Get current and historical prices for a stock"
)
async def get_stock_price(
    ticker: str = Path(..., min_length=1, max_length=10),
    interval: str = Query("1d", regex="^(1d|1h|15m|5m|1m)$"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
) -> StockPriceResponse:
    """Get stock price."""
    stock_service = StockService(db)
    price_data = await stock_service.get_stock_price(
        ticker=ticker,
        interval=interval,
        user=current_user
    )
    
    if not price_data:
        raise ResourceNotFoundError(f"Price data not found for {ticker}")
    
    return price_data