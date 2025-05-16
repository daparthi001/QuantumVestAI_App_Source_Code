from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional

from api.core.security import get_current_user, get_optional_current_user
from api.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from api.db.session import get_db
from api.db.models.user import User
from api.services.data_service import DataService

router = APIRouter(prefix="/sentiment")

@router.get("/{ticker}")
async def get_stock_sentiment(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get sentiment analysis for a stock."""
    # If user is not authenticated or free user, check rate limits
    if not current_user or current_user.role == "free":
        # In a real implementation, apply stricter rate limits
        pass
    
    data_service = DataService(db)
    sentiment = await data_service.get_sentiment_analysis(ticker)
    
    if not sentiment.get("success", False):
        raise ResourceNotFoundError(sentiment.get("error", "Failed to retrieve sentiment data"))
    
    # Free users get limited data
    if not current_user or current_user.role == "free":
        # Remove detailed news content
        if "sentiment" in sentiment and "news" in sentiment["sentiment"]:
            # Limit to just 3 articles and remove descriptions
            limited_news = []
            for article in sentiment["sentiment"]["news"][:3]:
                limited_news.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "published_at": article.get("published_at", ""),
                    "sentiment": article.get("sentiment", "")
                })
            sentiment["sentiment"]["news"] = limited_news
    
    return sentiment

@router.get("/compare")
async def compare_sentiment(
    tickers: str = Query(..., description="Comma-separated list of ticker symbols"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare sentiment analysis for multiple stocks."""
    # Check user permissions
    if current_user.role == "free":
        raise PermissionDeniedError("Sentiment comparison requires a paid subscription")
    
    data_service = DataService(db)
    ticker_list = [t.strip() for t in tickers.split(',') if t.strip()]
    
    if not ticker_list:
        return {"error": "No valid tickers provided", "success": False}
    
    # Limit to 5 tickers
    ticker_list = ticker_list[:5]
    
    results = {}
    for ticker in ticker_list:
        sentiment = await data_service.get_sentiment_analysis(ticker)
        if sentiment.get("success"):
            results[ticker] = sentiment.get("sentiment", {}).get("summary", {})
        else:
            results[ticker] = {"error": sentiment.get("error", "Unknown error")}
    
    return {
        "results": results,
        "success": True,
        "tickers": ticker_list
    }

@router.get("/trending/topics")
async def get_trending_sentiment_topics(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trending topics based on financial news sentiment."""
    # Check user permissions
    if current_user.role == "free":
        raise PermissionDeniedError("Trending topics analysis requires a paid subscription")
    
    data_service = DataService(db)
    trending_topics = await data_service.get_trending_sentiment_topics(days)
    
    return trending_topics

@router.get("/market/mood")
async def get_market_sentiment_mood(
    db: Session = Depends(get_db)
):
    """Get overall market sentiment mood."""
    data_service = DataService(db)
    market_mood = await data_service.get_market_sentiment_mood()
    
    return market_mood