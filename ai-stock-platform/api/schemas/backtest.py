"""
Backtest Schemas
Created: 2025-05-20 04:53:22
Author: daparthi001
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BacktestParameters(BaseModel):
    """Backtest parameters schema."""
    initial_capital: Decimal
    position_size: Optional[Decimal]
    max_positions: Optional[int]
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    commission: Optional[Decimal]
    slippage: Optional[Decimal]

class StrategyParameters(BaseModel):
    """Strategy parameters schema."""
    name: str
    parameters: Dict[str, Any]
    constraints: Optional[Dict[str, Any]]

class BacktestCreate(BaseModel):
    """Create backtest schema."""
    name: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    symbols: List[str]
    strategy: StrategyParameters
    parameters: BacktestParameters
    data_frequency: str = "1d"

class Trade(BaseModel):
    """Trade schema."""
    symbol: str
    side: str
    entry_time: datetime
    entry_price: Decimal
    exit_time: Optional[datetime]
    exit_price: Optional[Decimal]
    quantity: Decimal
    pnl: Optional[Decimal]
    pnl_percent: Optional[float]
    fees: Decimal

class BacktestResponse(BaseModel):
    """Backtest response schema."""
    id: int
    user_id: int
    name: str
    status: str
    progress: float
    created_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime]

    class Config:
        from_attributes = True

class PortfolioSnapshot(BaseModel):
    """Portfolio snapshot schema."""
    timestamp: datetime
    equity: Decimal
    cash: Decimal
    positions: Dict[str, Dict[str, Any]]
    margin_used: Optional[Decimal]

class BacktestResultResponse(BaseModel):
    """Backtest result response schema."""
    backtest_id: int
    status: str
    execution_time: float
    trades: List[Trade]
    portfolio_history: List[PortfolioSnapshot]
    statistics: Dict[str, Any]
    logs: List[Dict[str, Any]]

class PerformanceMetrics(BaseModel):
    """Performance metrics schema."""
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    recovery_factor: float

class BacktestPerformanceResponse(BaseModel):
    """Backtest performance response schema."""
    backtest_id: int
    timestamp: datetime
    metrics: PerformanceMetrics
    monthly_returns: Dict[str, float]
    equity_curve: List[Dict[str, Any]]
    drawdown_periods: List[Dict[str, Any]]

class Strategy(BaseModel):
    """Strategy schema."""
    id: int
    name: str
    category: str
    description: str
    parameters: Dict[str, Any]
    constraints: Optional[Dict[str, Any]]
    performance_stats: Optional[Dict[str, float]]

class StrategyResponse(Strategy):
    """Strategy response schema."""
    created_at: datetime
    updated_at: datetime
    usage_count: int

    class Config:
        from_attributes = True

class OptimizationConfig(BaseModel):
    """Optimization configuration schema."""
    parameter_ranges: Dict[str, List[Any]]
    optimization_metric: str
    max_iterations: int
    parallel_jobs: int

class OptimizationResult(BaseModel):
    """Optimization result schema."""
    parameters: Dict[str, Any]
    metric_value: float
    rank: int

class OptimizationResponse(BaseModel):
    """Optimization response schema."""
    id: int
    backtest_id: int
    status: str
    progress: float
    start_time: datetime
    end_time: Optional[datetime]
    best_results: List[OptimizationResult]
    optimization_path: List[Dict[str, Any]]

class RiskMetric(BaseModel):
    """Risk metric schema."""
    name: str
    value: float
    description: str
    benchmark: Optional[float]

class RiskMetricsResponse(BaseModel):
    """Risk metrics response schema."""
    backtest_id: int
    timestamp: datetime
    metrics: List[RiskMetric]
    var_analysis: Dict[str, Any]
    stress_tests: List[Dict[str, Any]]
    correlation_matrix: Optional[List[List[float]]]

class BacktestComparison(BaseModel):
    """Backtest comparison schema."""
    backtest_id: int
    name: str
    metrics: Dict[str, float]
    ranking: Dict[str, int]

class BacktestComparisonResponse(BaseModel):
    """Backtest comparison response schema."""
    timestamp: datetime
    backtests: List[BacktestComparison]
    comparison_matrix: Dict[str, List[float]]
    statistical_analysis: Dict[str, Any]
