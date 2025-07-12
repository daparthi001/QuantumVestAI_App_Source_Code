"""
Whitepaper Analysis Schemas
Created: 2025-05-20 04:49:49
Author: daparthi001
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class WhitepaperBase(BaseModel):
    """Base whitepaper schema."""
    ticker: str
    document_type: str
    document_date: datetime
    title: Optional[str]
    file_size: int
    file_type: str
    page_count: int
    language: str = "en"

class WhitepaperResponse(WhitepaperBase):
    """Whitepaper response schema."""
    id: int
    user_id: int
    status: str
    processing_status: str
    created_at: datetime
    updated_at: datetime
    file_url: str
    thumbnail_url: Optional[str]

    class Config:
        from_attributes = True

class FinancialMetric(BaseModel):
    """Financial metric schema."""
    name: str
    value: float
    unit: str
    year: int
    quarter: Optional[int]
    trend: str
    confidence: float

class RiskFactor(BaseModel):
    """Risk factor schema."""
    category: str
    description: str
    severity: str
    likelihood: str
    impact: str
    mitigation: Optional[str]

class StrategicGoal(BaseModel):
    """Strategic goal schema."""
    objective: str
    timeframe: str
    metrics: List[str]
    progress: Optional[float]
    dependencies: List[str]

class WhitepaperAnalysisResponse(BaseModel):
    """Whitepaper analysis response schema."""
    whitepaper_id: int
    analysis_type: str
    timestamp: datetime
    financial_metrics: List[FinancialMetric]
    risk_factors: List[RiskFactor]
    strategic_goals: List[StrategicGoal]
    key_insights: List[str]
    market_impact: Dict[str, Any]
    sentiment_analysis: Dict[str, float]
    confidence_score: float

class ComparisonItem(BaseModel):
    """Comparison item schema."""
    aspect: str
    first_value: Any
    second_value: Any
    difference: Optional[float]
    significance: str
    notes: Optional[str]

class WhitepaperComparisonResponse(BaseModel):
    """Whitepaper comparison response schema."""
    first_whitepaper_id: int
    second_whitepaper_id: int
    timestamp: datetime
    comparison_aspects: List[str]
    comparisons: List[ComparisonItem]
    summary: str
    key_differences: List[str]
    recommendations: List[str]

class Metric(BaseModel):
    """Metric schema."""
    name: str
    value: Any
    category: str
    context: Optional[str]
    page_reference: int
    confidence: float

class WhitepaperMetricsResponse(BaseModel):
    """Whitepaper metrics response schema."""
    whitepaper_id: int
    timestamp: datetime
    metric_types: List[str]
    metrics: List[Metric]
    trends: Dict[str, List[float]]
    benchmarks: Dict[str, Any]
    data_quality: float

class SummarySection(BaseModel):
    """Summary section schema."""
    title: str
    content: str
    key_points: List[str]
    word_count: int
    page_references: List[int]

class WhitepaperSummaryResponse(BaseModel):
    """Whitepaper summary response schema."""
    whitepaper_id: int
    timestamp: datetime
    summary_type: str
    sections: List[SummarySection]
    total_word_count: int
    key_takeaways: List[str]
    methodology: str
    confidence_score: float
