from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WatchlistItemBase(BaseModel):
    """Base schema for watchlist items."""
    ticker: str
    notes: Optional[str] = None

class WatchlistItemCreate(WatchlistItemBase):
    """Schema for creating a watchlist item."""
    pass

class WatchlistItemUpdate(BaseModel):
    """Schema for updating a watchlist item."""
    notes: Optional[str] = None

class WatchlistItem(WatchlistItemBase):
    """Schema for watchlist item with stock info."""
    id: int
    user_id: int
    stock_id: int
    created_at: datetime
    stock_info: dict  # Contains ticker, name, price, etc.
    
    class Config:
        orm_mode = True