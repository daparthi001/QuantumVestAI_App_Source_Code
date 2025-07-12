"""
Stock schemas
Created: 2025-05-19 03:29:10
Author: daparthi001
Updated: 2025-01-09 (AI Assistant) - Added Warren Buffett analysis schemas
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

# Warren Buffett Analysis Schemas
class BusinessQualityMetrics(BaseModel):
    consistent_earnings_growth: float
    high_roe: float
    low_debt_to_equity: float
    competitive_advantage: float
    management_effectiveness: float

class BuffettAnalysisResponse(BaseModel):
    intrinsic_value: float
    margin_of_safety: float
    quality_score: float
    investment_recommendation: str
    reasoning: List[str]
    quality_metrics: BusinessQualityMetrics

class FundamentalData(BaseModel):
    market_cap: float
    free_cash_flow: float
    revenue: float
    net_income: float
    total_debt: float
    total_equity: float
    return_on_equity: float
    eps: float
    book_value: float
    dividend_yield: float
    current_price: float
    historical_growth_rate: float
    operating_margin: float

class StockSearchResponse(BaseModel):
    symbol: str
    name: str
    price: Optional[float] = None
    change: Optional[float] = None

class StockDetailResponse(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

class StockPriceResponse(BaseModel):
    symbol: str
    current_price: float
    high_24h: float
    low_24h: float
    volume_24h: float
    last_updated: datetime
