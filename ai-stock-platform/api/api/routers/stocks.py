"""
Stock market data and analysis router.
Created: 2025-05-17 14:29:46 UTC
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import date, datetime, timedelta

from api.core.dependencies import get_db, get_current_user
from api.schemas.stock import (
    StockCreate,
    StockUpdate,
    StockResponse,
    StockPrice,
    StockAnalysis
)
from api.models.stock import Stock
from api.services.market_data import fetch_stock_data
from api.core.exceptions import NotFoundError

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/", response_model=List[StockResponse])
async def list_stocks(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    sector: Optional[str] = None,
    search: Optional[str] = None
) -> Any:
    """
    List stocks with optional filtering.
    """
    query = db.query(Stock)
    
    if sector:
        query = query.filter(Stock.sector == sector)
    
    if search:
        query = query.filter(
            Stock.symbol.ilike(f"%{search}%") |
            Stock.name.ilike(f"%{search}%")
        )
    
    stocks = query.offset(skip).limit(limit).all()
    return stocks

@router.get("/{symbol}", response_model=StockResponse)
async def get_stock(
    *,
    db: Session = Depends(get_db),
    symbol: str,
    include_prices: bool = False
) -> Any:
    """
    Get stock details by symbol.
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    if not stock:
        raise NotFoundError(f"Stock {symbol} not found")
    
    return stock

@router.get("/{symbol}/prices", response_model=List[StockPrice])
async def get_stock_prices(
    *,
    db: Session = Depends(get_db),
    symbol: str,
    start_date: date = Query(default=(datetime.now() - timedelta(days=30)).date()),
    end_date: date = Query(default=datetime.now().date())
) -> Any:
    """
    Get historical prices for a stock.
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    if not stock:
        raise NotFoundError(f"Stock {symbol} not found")
    
    prices = db.query(StockPrice).filter(
        StockPrice.stock_id == stock.id,
        StockPrice.date >= start_date,
        StockPrice.date <= end_date
    ).order_by(StockPrice.date.asc()).all()
    
    return prices

@router.get("/{symbol}/analysis", response_model=StockAnalysis)
async def get_stock_analysis(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    symbol: str
) -> Any:
    """
    Get technical analysis for a stock.
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    if not stock:
        raise NotFoundError(f"Stock {symbol} not found")
    
    # Queue background task to update analysis
    background_tasks.add_task(
        update_stock_analysis,
        stock.id
    )
    
    return stock.latest_analysis