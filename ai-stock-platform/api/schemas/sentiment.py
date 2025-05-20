"""
Sentiment Analysis Schemas
Created: 2025-05-20 04:46:38
Author: daparthi001
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class SentimentScore(BaseModel):
    """Sentiment score schema."""
    score: float = Field(..., ge=-1.0, le=1.0)
    magnitude: float = Field(..., ge=0.0)
    confidence: float = Field(..., ge=0.0, le=1.0)

class SourceSentiment(BaseModel):
    """Source sentiment schema."""
    source: str
    sentiment: SentimentScore
    volume: int
    trending_topics: List[str]

class SentimentResponse(BaseModel):
    """Sentiment response schema."""
    ticker: str
    timestamp: datetime
    overall_sentiment: SentimentScore
    sources: List[SourceSentiment]
    price_correlation: float
    volume_impact: float

class SentimentTrend(BaseModel):
    """Sentiment trend schema."""
    date: datetime
    sentiment: float
    volume: int
    price: float
    news_count: int
    social_mentions: int

class SentimentTrendsResponse(BaseModel):
    """Sentiment trends response schema."""
    ticker: str
    period_start: datetime
    period_end: datetime
    trends: List[SentimentTrend]
    correlation_metrics: Dict[str, float]

class SentimentSource(BaseModel):
    """Sentiment source schema."""
    source_name: str
    url: str
    title: Optional[str]
    content: str
    published_at: datetime
    sentiment: SentimentScore
    reach: int
    engagement: int

class SentimentSourcesResponse(BaseModel):
    """Sentiment sources response schema."""
    source_type: str
    sources: List[SentimentSource]
    aggregated_sentiment: SentimentScore

class SentimentAlert(BaseModel):
    """Sentiment alert schema."""
    id: int
    user_id: int
    ticker: str
    threshold: float
    source: str
    is_active: bool
    created_at: datetime
    last_triggered: Optional[datetime]

    class Config:
        from_attributes = True

class SentimentAlertResponse(SentimentAlert):
    """Sentiment alert response schema."""
    pass

class NewsArticle(BaseModel):
    """News article schema."""
    title: str
    url: str
    source: str
    published_at: datetime
    sentiment: SentimentScore
    summary: str
    keywords: List[str]
    impact_score: float

class NewsSentimentResponse(BaseModel):
    """News sentiment response schema."""
    ticker: str
    articles: List[NewsArticle]
    aggregated_sentiment: SentimentScore
    significant_topics: List[Dict[str, Any]]