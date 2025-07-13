"""
Market Data Schemas
Created: 2025-05-20 04:47:45
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    """OHLCV data schema."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float]

class HistoricalDataResponse(BaseModel):
    """Historical data response schema."""
    ticker: str
    interval: str
    currency: str
    data: List[OHLCV]
    start_date: datetime
    end_date: datetime
    data_points: int

class IndicatorValue(BaseModel):
    """Technical indicator value schema."""
    timestamp: datetime
    value: float
    signal: Optional[float]
    histogram: Optional[float]

class TechnicalIndicatorResponse(BaseModel):
    """Technical indicator response schema."""
    indicator: str
    ticker: str
    period: str
    values: List[IndicatorValue]
    parameters: Dict[str, Any]

class MarketIndex(BaseModel):
    """Market index schema."""
    symbol: str
    name: str
    last_price: float
    change: float
    change_percent: float
    high_52w: float
    low_52w: float
    components_count: int
    updated_at: datetime

class MarketIndexResponse(BaseModel):
    """Market index response schema."""
    index: MarketIndex
    top_gainers: List[Dict[str, Any]]
    top_losers: List[Dict[str, Any]]
    volume: int
    timestamp: datetime

class SectorData(BaseModel):
    """Sector data schema."""
    name: str
    performance: float
    volume: int
    market_cap: float
    companies_count: int
    top_performers: List[Dict[str, Any]]

class SectorPerformanceResponse(BaseModel):
    """Sector performance response schema."""
    period: str
    timestamp: datetime
    sectors: List[SectorData]
    market_correlation: Dict[str, float]

class EarningsData(BaseModel):
    """Earnings data schema."""
    date: datetime
    ticker: str
    company_name: str
    eps_estimate: Optional[float]
    eps_actual: Optional[float]
    revenue_estimate: Optional[float]
    revenue_actual: Optional[float]
    period_end: str
    before_after: str
    conference_call_time: Optional[datetime]

class EarningsCalendarResponse(BaseModel):
    """Earnings calendar response schema."""
    earnings_date: datetime
    companies: List[EarningsData]
    total_reports: int
    market_impact: float

class ScreenerCriteria(BaseModel):
    """Screener criteria schema."""
    field: str
    operator: str
    value: Any

class ScreenerResult(BaseModel):
    """Screener result schema."""
    ticker: str
    company_name: str
    sector: str
    industry: str
    market_cap: float
    price: float
    change_percent: float
    volume: int
    criteria_matched: List[str]

class ScreenerResponse(BaseModel):
    """Screener response schema."""
    criteria: List[ScreenerCriteria]
    results: List[ScreenerResult]
    total_matches: int
    execution_time: float
    timestamp: datetime
