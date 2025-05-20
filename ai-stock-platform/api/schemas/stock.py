"""
Stock schemas
Created: 2025-05-19 03:29:10
Author: daparthi001
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class StockBase(BaseModel):
    symbol: str
    name: Optional[str] = None

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: int
    current_price: Optional[float]
    high_24h: Optional[float]
    low_24h: Optional[float]
    volume_24h: Optional[float]
    last_updated: Optional[datetime]

    class Config:
        orm_mode = True

class WatchlistItem(BaseModel):
    symbol: str

class StockResponse(BaseModel):
    status: str
    data: Stock

class WatchlistResponse(BaseModel):
    status: str
    data: List[Stock]