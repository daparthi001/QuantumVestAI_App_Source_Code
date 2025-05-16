from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional

from api.core.security import get_optional_current_user, get_current_user
from api.core.exceptions import ResourceNotFoundError
from api.db.session import get_db
from api.db.models.user import User
from api.db.models.stock import Stock, StockPrice
from api.schemas.stock import StockInfo, StockPrice as StockPriceSchema, StockSearch, StockTrending
from api.services.stock_service import StockService

router = APIRouter(prefix="/stocks")

@router.get("/search", response_model=List[StockSearch])
async def search_stocks(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Search for stocks by ticker or name."""
    stock_service = StockService(db)
    results = stock_service.search_stocks(q, limit)
    return results

@router.get("/{ticker}", response_model=StockInfo)
async def get_stock_info(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get detailed information about a stock."""
    stock_service = StockService(db)
    stock_info = stock_service.get_stock_info(ticker)
    
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Add watchlist status if user is authenticated
    if current_user:
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        stock_info.is_in_watchlist = stock in current_user.watchlist if stock else False
    
    return stock_info

@router.get("/{ticker}/history", response_model=List[StockPriceSchema])
async def get_stock_history(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    period: str = Query("1mo", regex=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Time period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical price data for a stock."""
    stock_service = StockService(db)
    history = stock_service.get_stock_history(ticker, period)
    
    if not history:
        raise ResourceNotFoundError(f"Historical data for {ticker} not found")
    
    return history

@router.get("/trending", response_model=List[StockTrending])
async def get_trending_stocks(
    limit: int = Query(10, ge=1, le=20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get currently trending stocks."""
    stock_service = StockService(db)
    trending = stock_service.get_trending_stocks(limit)
    return trending

@router.get("/most-predictable", response_model=List[StockInfo])
async def get_most_predictable_stocks(
    limit: int = Query(10, ge=1, le=20, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stocks with highest predictability scores."""
    stock_service = StockService(db)
    stocks = stock_service.get_most_predictable_stocks(limit)
    return stocks

@router.get("/sector/{sector}", response_model=List[StockInfo])
async def get_stocks_by_sector(
    sector: str = Path(..., description="Sector name"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get stocks by sector."""
    stock_service = StockService(db)
    stocks = stock_service.get_stocks_by_sector(sector, limit)
    return stocks

@router.get("/industry/{industry}", response_model=List[StockInfo])
async def get_stocks_by_industry(
    industry: str = Path(..., description="Industry name"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get stocks by industry."""
    stock_service = StockService(db)
    stocks = stock_service.get_stocks_by_industry(industry, limit)
    return stocks

@router.get("/markets/summary")
async def get_market_summary(
    db: Session = Depends(get_db)
):
    """Get overall market summary."""
    stock_service = StockService(db)
    summary = stock_service.get_market_summary()
    return summary