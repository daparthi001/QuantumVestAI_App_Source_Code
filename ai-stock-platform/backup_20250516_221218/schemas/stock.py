from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class StockBase(BaseModel):
    """Base stock schema with common fields."""
    ticker: str
    name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None

class StockCreate(StockBase):
    """Schema for creating a new stock."""
    pass

class StockPrice(BaseModel):
    """Schema for stock price data point."""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adjusted_close: Optional[float] = None
    volume: int

    class Config:
        orm_mode = True

class StockInfo(StockBase):
    """Schema for detailed stock information."""
    id: Optional[int] = None
    last_price: Optional[float] = None
    last_updated: Optional[datetime] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    day_volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    
    # Predictability metrics
    predictability_score: Optional[float] = None
    volatility_score: Optional[float] = None
    trend_score: Optional[float] = None
    volume_score: Optional[float] = None
    
    # User-specific data (populated by API)
    is_in_watchlist: Optional[bool] = None
    
    class Config:
        orm_mode = True
        
    @validator('price_change_percent')
    def round_percent(cls, v):
        """Round percentage to 2 decimal places if not None."""
        if v is not None:
            return round(v, 2)
        return v

class StockSearch(BaseModel):
    """Schema for stock search results."""
    ticker: str
    name: str
    exchange: str = Field(default="")
    
    class Config:
        orm_mode = True

class StockTrending(BaseModel):
    """Schema for trending stocks."""
    ticker: str
    name: str
    price: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    signal: Optional[str] = None  # buy, sell, hold
    
    class Config:
        orm_mode = True

class StockForecast(BaseModel):
    """Schema for stock forecast data."""
    ticker: str
    current_price: float
    end_price: float
    peak_price: float
    minimum_price: float
    price_range: float
    confidence_level: int = Field(..., ge=0, le=100)
    volatility: str  # Low, Medium, High
    volatility_description: str
    trend: str  # Upward, Downward, Sideways
    trend_strength: str
    signal: str  # Buy, Sell, Hold
    signal_strength: str
    accuracy: float = Field(..., ge=0, le=100)
    forecast_points: List[Dict[str, Any]]
    summary: str
    
    class Config:
        orm_mode = True

class PredictabilityAnalysis(BaseModel):
    """Schema for stock predictability analysis."""
    score: int = Field(..., ge=0, le=100)
    category: str  # Very High, High, Medium, Low, Very Low
    factors: Dict[str, Dict[str, Any]]
    
    class Config:
        orm_mode = True

class ModelComparison(BaseModel):
    """Schema for model comparison results."""
    ensemble: Dict[str, float]
    lstm: Dict[str, float]
    prophet: Dict[str, float]
    xgboost: Dict[str, float]
    arima: Dict[str, float]
    
    class Config:
        orm_mode = True