"""
Sentiment Analysis Router
Created: 2025-05-20 04:46:38
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError, PermissionDeniedError
from api.db.session import get_db
from api.db.models.user import User
from api.services.sentiment_service import SentimentService
from api.schemas.sentiment import (
    SentimentResponse,
    SentimentTrendsResponse,
    SentimentSourcesResponse,
    SentimentAlertResponse,
    NewsSentimentResponse
)

router = APIRouter(
    prefix="/sentiment",
    tags=["sentiment"],
    dependencies=[Depends(get_current_user)]
)

@router.get(
    "/{ticker}",
    response_model=SentimentResponse,
    summary="Get sentiment",
    description="Get sentiment analysis for a stock"
)
async def get_stock_sentiment(
    ticker: str = Path(..., min_length=1, max_length=10),
    sources: List[str] = Query(
        ["news", "twitter", "reddit"],
        description="Sentiment sources to analyze"
    ),
    period: str = Query(
        "1d",
        regex="^(1d|1w|1m|3m|6m|1y|all)$",
        description="Analysis period"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SentimentResponse:
    """Get sentiment analysis for a stock."""
    if current_user.role == "free":
        raise PermissionDeniedError("Sentiment analysis requires premium subscription")
    
    service = SentimentService(db)
    sentiment = await service.get_sentiment(ticker, sources, period)
    
    if not sentiment:
        raise ResourceNotFoundError(f"Sentiment data not found for {ticker}")
    
    return sentiment

@router.get(
    "/{ticker}/trends",
    response_model=SentimentTrendsResponse,
    summary="Get sentiment trends",
    description="Get historical sentiment trends"
)
async def get_sentiment_trends(
    ticker: str = Path(..., min_length=1, max_length=10),
    days: int = Query(30, ge=1, le=365),
    source: str = Query(
        "all",
        regex="^(all|news|twitter|reddit)$",
        description="Sentiment source"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SentimentTrendsResponse:
    """Get sentiment trends."""
    if current_user.role == "free":
        raise PermissionDeniedError("Sentiment trends require premium subscription")
    
    service = SentimentService(db)
    trends = await service.get_trends(ticker, days, source)
    
    if not trends:
        raise ResourceNotFoundError(f"Sentiment trends not found for {ticker}")
    
    return trends

@router.get(
    "/{ticker}/sources",
    response_model=List[SentimentSourcesResponse],
    summary="Get sentiment sources",
    description="Get sentiment analysis by source"
)
async def get_sentiment_sources(
    ticker: str = Path(..., min_length=1, max_length=10),
    date: str = Query(
        None,
        regex=r"^\d{4}-\d{2}-\d{2}$",
        description="Analysis date (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[SentimentSourcesResponse]:
    """Get sentiment sources."""
    if current_user.role == "free":
        raise PermissionDeniedError("Source analysis requires premium subscription")
    
    service = SentimentService(db)
    sources = await service.get_sources(ticker, date)
    
    if not sources:
        raise ResourceNotFoundError(f"Sentiment sources not found for {ticker}")
    
    return sources

@router.post(
    "/alerts",
    response_model=SentimentAlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create sentiment alert",
    description="Create a new sentiment alert"
)
async def create_sentiment_alert(
    ticker: str = Query(..., min_length=1, max_length=10),
    threshold: float = Query(..., ge=-1.0, le=1.0),
    source: str = Query(
        "all",
        regex="^(all|news|twitter|reddit)$",
        description="Alert source"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SentimentAlertResponse:
    """Create sentiment alert."""
    if current_user.role == "free":
        raise PermissionDeniedError("Sentiment alerts require premium subscription")
    
    service = SentimentService(db)
    alert = await service.create_alert(
        user_id=current_user.id,
        ticker=ticker,
        threshold=threshold,
        source=source
    )
    
    return alert

@router.get(
    "/news/{ticker}",
    response_model=List[NewsSentimentResponse],
    summary="Get news sentiment",
    description="Get sentiment analysis of news articles"
)
async def get_news_sentiment(
    ticker: str = Path(..., min_length=1, max_length=10),
    days: int = Query(7, ge=1, le=30),
    min_score: float = Query(
        0.0,
        ge=-1.0,
        le=1.0,
        description="Minimum sentiment score"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[NewsSentimentResponse]:
    """Get news sentiment analysis."""
    if current_user.role == "free":
        raise PermissionDeniedError("News sentiment requires premium subscription")
    
    service = SentimentService(db)
    news = await service.get_news_sentiment(
        ticker=ticker,
        days=days,
        min_score=min_score
    )
    
    if not news:
        raise ResourceNotFoundError(f"News sentiment not found for {ticker}")
    
    return news