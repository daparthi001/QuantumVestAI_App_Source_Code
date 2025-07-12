"""
Portfolio Schemas
Created: 2025-05-20 04:48:48
Author: daparthi001
"""
from pydantic import BaseModel, Field, constr
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal

class PortfolioBase(BaseModel):
    """Base portfolio schema."""
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    currency: str = "USD"
    is_private: bool = True

class PortfolioCreate(PortfolioBase):
    """Create portfolio schema."""
    pass

class PortfolioUpdate(PortfolioBase):
    """Update portfolio schema."""
    pass

class TransactionBase(BaseModel):
    """Base transaction schema."""
    ticker: constr(min_length=1, max_length=10)
    transaction_type: str = Field(..., regex="^(buy|sell)$")
    shares: Decimal = Field(..., gt=0)
    price_per_share: Decimal = Field(..., gt=0)
    date: datetime
    fees: Optional[Decimal] = Field(0, ge=0)
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    """Create transaction schema."""
    pass

class TransactionResponse(TransactionBase):
    """Transaction response schema."""
    id: int
    portfolio_id: int
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Position(BaseModel):
    """Portfolio position schema."""
    ticker: str
    shares: Decimal
    average_cost: Decimal
    current_price: Decimal
    market_value: Decimal
    total_return: Decimal
    total_return_percent: float
    day_change: Decimal
    day_change_percent: float

class PortfolioResponse(PortfolioBase):
    """Portfolio response schema."""
    id: int
    user_id: int
    total_value: Decimal
    total_cost: Decimal
    total_return: Decimal
    total_return_percent: float
    positions_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PortfolioDetailResponse(PortfolioResponse):
    """Detailed portfolio response schema."""
    positions: List[Position]
    transactions: Optional[List[TransactionResponse]]
    cash_balance: Decimal
    dividend_income: Decimal

class PerformanceMetrics(BaseModel):
    """Performance metrics schema."""
    alpha: float
    beta: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    volatility: float
    r_squared: float
    tracking_error: float

class PortfolioAnalyticsResponse(BaseModel):
    """Portfolio analytics response schema."""
    portfolio_id: int
    period: str
    start_date: datetime
    end_date: datetime
    initial_value: Decimal
    final_value: Decimal
    total_return: float
    benchmark_return: float
    excess_return: float
    metrics: PerformanceMetrics
    daily_returns: List[Dict[str, Any]]
    benchmark_comparison: Dict[str, Any]

class AllocationItem(BaseModel):
    """Allocation item schema."""
    category: str
    percentage: float
    market_value: Decimal
    positions: List[Position]
    risk_contribution: float

class PortfolioAllocationResponse(BaseModel):
    """Portfolio allocation response schema."""
    portfolio_id: int
    group_by: str
    timestamp: datetime
    allocations: List[AllocationItem]
    concentration_risk: float
    rebalancing_needed: bool
    target_allocations: Optional[Dict[str, float]]

class DiversificationMetrics(BaseModel):
    """Diversification metrics schema."""
    herfindahl_index: float
    effective_n: float
    correlation_matrix: List[List[float]]
    risk_contribution: Dict[str, float]
    sector_exposure: Dict[str, float]
    geographic_exposure: Dict[str, float]
    size_exposure: Dict[str, float]

class PortfolioDiversificationResponse(BaseModel):
    """Portfolio diversification response schema."""
    portfolio_id: int
    timestamp: datetime
    metrics: DiversificationMetrics
    recommendations: List[Dict[str, Any]]
    risk_factors: Dict[str, float]
