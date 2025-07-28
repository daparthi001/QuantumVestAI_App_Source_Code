"""
Analytics Schemas
Created: 2025-05-20 05:03:42
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PortfolioMetrics(BaseModel):
    """Portfolio metrics schema."""
    returns: Dict[str, float]
    risk_metrics: Dict[str, float]
    allocation: Dict[str, float]
    performance_attribution: Dict[str, float]
    factor_exposure: Dict[str, float]

class PortfolioAnalyticsResponse(BaseModel):
    """Portfolio analytics response schema."""
    portfolio_id: int
    timestamp: datetime
    time_range: str
    metrics: PortfolioMetrics
    benchmarks: Dict[str, Dict[str, float]]
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]

class MarketIndicator(BaseModel):
    """Market indicator schema."""
    symbol: str
    indicator: str
    value: float
    signal: str
    strength: float
    trend: str

class MarketAnalyticsResponse(BaseModel):
    """Market analytics response schema."""
    timestamp: datetime
    symbols: List[str]
    indicators: List[MarketIndicator]
    correlations: Dict[str, List[float]]
    trends: Dict[str, Dict[str, Any]]
    market_regime: Dict[str, Any]

class TradeMetrics(BaseModel):
    """Trade metrics schema."""
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration: float

class TradingAnalyticsResponse(BaseModel):
    """Trading analytics response schema."""
    period_start: datetime
    period_end: datetime
    metrics: TradeMetrics
    trades_analysis: Dict[str, Any]
    strategy_performance: Optional[Dict[str, Any]]
    optimization_suggestions: List[Dict[str, Any]]

class RiskExposure(BaseModel):
    """Risk exposure schema."""
    type: str
    value: float
    contribution: float
    limit: Optional[float]
    status: str

class RiskAnalyticsResponse(BaseModel):
    """Risk analytics response schema."""
    timestamp: datetime
    portfolio_id: Optional[int]
    risk_metrics: Dict[str, float]
    exposures: List[RiskExposure]
    stress_test_results: Optional[Dict[str, Any]]
    risk_decomposition: Dict[str, List[float]]

class AttributionFactor(BaseModel):
    """Attribution factor schema."""
    factor: str
    contribution: float
    exposure: float
    significance: float

class PerformanceAnalyticsResponse(BaseModel):
    """Performance analytics response schema."""
    portfolio_id: int
    timestamp: datetime
    total_return: float
    active_return: Optional[float]
    attribution: List[AttributionFactor]
    factor_analysis: Dict[str, Any]
    peer_comparison: Optional[Dict[str, Any]]

class Prediction(BaseModel):
    """Prediction schema."""
    symbol: str
    target: float
    confidence_interval: List[float]
    probability: float
    factors: Dict[str, float]

class PredictiveAnalyticsResponse(BaseModel):
    """Predictive analytics response schema."""
    timestamp: datetime
    horizon: str
    confidence_level: float
    predictions: List[Prediction]
    model_metrics: Dict[str, float]
    feature_importance: Dict[str, float]

    # Disable protected namespace warnings for fields beginning with "model_"
    model_config = {"protected_namespaces": ()}

class SentimentScore(BaseModel):
    """Sentiment score schema."""
    source: str
    score: float
    volume: int
    trend: str
    key_topics: List[str]

class SentimentAnalyticsResponse(BaseModel):
    """Sentiment analytics response schema."""
    timestamp: datetime
    symbols: List[str]
    sentiment_scores: List[SentimentScore]
    aggregate_sentiment: Dict[str, float]
    word_cloud: Dict[str, int]
    impact_analysis: Dict[str, Any]

class CustomAnalyticsResult(BaseModel):
    """Custom analytics result schema."""
    analysis_type: str
    results: Dict[str, Any]
    visualization_data: Dict[str, Any]
    statistical_tests: Dict[str, Any]

class CustomAnalyticsResponse(BaseModel):
    """Custom analytics response schema."""
    query_id: str
    timestamp: datetime
    query_type: str
    parameters: Dict[str, Any]
    results: CustomAnalyticsResult
    execution_time: float
    cache_hit: bool
