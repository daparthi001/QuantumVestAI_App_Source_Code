"""
Risk Analysis Schemas
Created: 2025-05-20 04:54:55
Author: daparthi001
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal

class RiskMetric(BaseModel):
    """Risk metric schema."""
    name: str
    value: float
    confidence_interval: Optional[List[float]]
    benchmark: Optional[float]
    z_score: Optional[float]

class PortfolioRiskResponse(BaseModel):
    """Portfolio risk response schema."""
    portfolio_id: int
    timestamp: datetime
    total_risk: float
    systematic_risk: float
    specific_risk: float
    metrics: List[RiskMetric]
    risk_decomposition: Dict[str, float]
    risk_contributions: Dict[str, float]
    var_analysis: Dict[str, Any]

class MarketIndicator(BaseModel):
    """Market indicator schema."""
    name: str
    value: float
    signal: str
    trend: str
    z_score: float
    historical_percentile: float

class MarketRiskResponse(BaseModel):
    """Market risk response schema."""
    timestamp: datetime
    risk_level: str
    indicators: List[MarketIndicator]
    market_stress: float
    regime_analysis: Dict[str, Any]
    leading_indicators: Dict[str, float]
    risk_appetite: Dict[str, Any]

class RiskFactor(BaseModel):
    """Risk factor schema."""
    name: str
    category: str
    exposure: float
    contribution: float
    sensitivity: float
    significance: float

class RiskFactorResponse(BaseModel):
    """Risk factor response schema."""
    factor_type: str
    factors: List[RiskFactor]
    total_explained: float
    residual: float
    factor_correlations: Dict[str, List[float]]

class StressScenario(BaseModel):
    """Stress scenario schema."""
    name: str
    impact: float
    affected_positions: List[Dict[str, Any]]
    risk_measures: Dict[str, float]
    recovery_period: Optional[int]

class StressTestResponse(BaseModel):
    """Stress test response schema."""
    portfolio_id: int
    timestamp: datetime
    scenarios: List[StressScenario]
    aggregated_impact: float
    risk_capacity: float
    recommendations: List[str]

class ScenarioResult(BaseModel):
    """Scenario result schema."""
    name: str
    probability: float
    portfolio_value: Decimal
    pnl: Decimal
    pnl_percent: float
    risk_metrics: Dict[str, float]

class ScenarioAnalysisResponse(BaseModel):
    """Scenario analysis response schema."""
    portfolio_id: int
    timestamp: datetime
    scenarios: List[ScenarioResult]
    expected_value: Decimal
    worst_case: Decimal
    best_case: Decimal
    confidence_interval: List[float]

class RiskAlert(BaseModel):
    """Risk alert schema."""
    id: int
    portfolio_id: int
    metric: str
    threshold: float
    current_value: float
    status: str
    triggered_at: Optional[datetime]

class RiskAlertResponse(RiskAlert):
    """Risk alert response schema."""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CorrelationData(BaseModel):
    """Correlation data schema."""
    matrix: List[List[float]]
    symbols: List[str]
    periods: Dict[str, List[float]]
    stability: Dict[str, float]

class CorrelationResponse(BaseModel):
    """Correlation response schema."""
    timestamp: datetime
    method: str
    lookback_days: int
    data: CorrelationData
    clusters: Optional[Dict[str, List[str]]]
    network_analysis: Optional[Dict[str, Any]]

class VaRResult(BaseModel):
    """VaR result schema."""
    value: float
    confidence_level: float
    time_horizon: int
    contribution: Dict[str, float]
    historical_breaches: List[Dict[str, Any]]

class VaRResponse(BaseModel):
    """VaR response schema."""
    portfolio_id: int
    timestamp: datetime
    method: str
    var_result: VaRResult
    cvar: float
    component_var: Dict[str, float]
    stress_var: Optional[float]
    backtesting: Dict[str, Any]