from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, Body
from sqlalchemy.orm import Session
from typing import List

from api.core.security_utils import get_current_user
from api.core.exceptions import ResourceNotFoundError
from api.db.session import get_db
from api.db.models.user import User
from api.db.models.stock import Stock
from api.schemas.watchlist import WatchlistItem, WatchlistItemCreate, WatchlistItemUpdate
from api.services.stock_service import StockService

router = APIRouter(prefix="/watchlist")

@router.get("/", response_model=List[WatchlistItem])
async def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's watchlist."""
    stock_service = StockService(db)
    watchlist_items = stock_service.get_watchlist(current_user.id)
    
    return watchlist_items

@router.post("/", response_model=WatchlistItem, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    item: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add stock to watchlist."""
    # Check if stock exists
    stock = db.query(Stock).filter(Stock.ticker == item.ticker).first()
    
    if not stock:
        # Try to fetch stock info and create it
        stock_service = StockService(db)
        stock_info = stock_service.get_stock_info(item.ticker)
        
        if not stock_info:
            raise ResourceNotFoundError(f"Stock with ticker {item.ticker} not found")
        
        # Create stock in database
        stock = Stock(
            ticker=item.ticker,
            name=stock_info.name,
            exchange=stock_info.exchange,
            sector=stock_info.sector,
            industry=stock_info.industry,
            country=stock_info.country,
            last_price=stock_info.last_price,
            last_updated=stock_info.last_updated
        )
        db.add(stock)
        db.commit()
        db.refresh(stock)
    
    # Check if stock is already in watchlist
    if stock in current_user.watchlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock {item.ticker} is already in watchlist"
        )
    
    # Add to watchlist
    current_user.watchlist.append(stock)
    db.commit()
    
    # Set notes if provided
    if item.notes:
        # Update association table
        from sqlalchemy import text
        db.execute(
            text("""
                UPDATE user_watchlist 
                SET notes = :notes 
                WHERE user_id = :user_id AND stock_id = :stock_id
            """),
            {"notes": item.notes, "user_id": current_user.id, "stock_id": stock.id}
        )
        db.commit()
    
    # Return watchlist item
    stock_service = StockService(db)
    watchlist_item = stock_service.get_watchlist_item(current_user.id, item.ticker)
    
    return watchlist_item

@router.delete("/{ticker}")
async def remove_from_watchlist(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove stock from watchlist."""
    # Get stock
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    
    if not stock:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Check if stock is in watchlist
    if stock not in current_user.watchlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock {ticker} is not in watchlist"
        )
    
    # Remove from watchlist
    current_user.watchlist.remove(stock)
    db.commit()
    
    return {"success": True}

@router.put("/{ticker}", response_model=WatchlistItem)
async def update_watchlist_item(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    item: WatchlistItemUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update watchlist item."""
    # Get stock
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    
    if not stock:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    
    # Check if stock is in watchlist
    if stock not in current_user.watchlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock {ticker} is not in watchlist"
        )
    
    # Update notes
    from sqlalchemy import text
    db.execute(
        text("""
            UPDATE user_watchlist 
            SET notes = :notes 
            WHERE user_id = :user_id AND stock_id = :stock_id
        """),
        {"notes": item.notes, "user_id": current_user.id, "stock_id": stock.id}
    )
    db.commit()
    
    # Return updated watchlist item
    stock_service = StockService(db)
    watchlist_item = stock_service.get_watchlist_item(current_user.id, ticker)
    
    return watchlist_item

@router.get("/performance")
async def get_watchlist_performance(
    period: str = Query("1mo", regex=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Time period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance of stocks in watchlist."""
    stock_service = StockService(db)
    performance = stock_service.get_watchlist_performance(current_user.id, period)
    
    return performance