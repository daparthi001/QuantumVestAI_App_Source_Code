"""
Watchlist Schemas
Created: 2025-05-20 04:44:57
Author: daparthi001
"""
from pydantic import BaseModel, constr
from typing import List, Optional
from datetime import datetime

class WatchlistBase(BaseModel):
    """Base watchlist schema."""
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None

class WatchlistCreate(WatchlistBase):
    """Create watchlist schema."""
    pass

class WatchlistUpdate(WatchlistBase):
    """Update watchlist schema."""
    pass

class WatchlistStockAdd(BaseModel):
    """Add stock to watchlist schema."""
    ticker: constr(min_length=1, max_length=10)

class WatchlistStock(BaseModel):
    """Watchlist stock schema."""
    ticker: str
    company_name: str
    current_price: float
    price_change: float
    price_change_percent: float
    added_at: datetime

    class Config:
        from_attributes = True

class WatchlistResponse(WatchlistBase):
    """Watchlist response schema."""
    id: int
    user_id: int
    stock_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WatchlistDetailResponse(WatchlistResponse):
    """Detailed watchlist response schema."""
    stocks: List[WatchlistStock]

class WatchlistPerformance(BaseModel):
    """Watchlist performance metrics schema."""
    total_value: float
    total_gain: float
    total_gain_percent: float
    best_performer: WatchlistStock
    worst_performer: WatchlistStock
    period_start: datetime
    period_end: datetime

class WatchlistPerformanceResponse(BaseModel):
    """Watchlist performance response schema."""
    watchlist_id: int
    name: str
    performance: WatchlistPerformance

