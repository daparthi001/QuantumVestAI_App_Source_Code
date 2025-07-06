"""
Sentiment Analysis Routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter(prefix="/api/v1/sentiment", tags=["sentiment"])

@router.get("/{symbol}")
async def get_sentiment(symbol: str):
    """Get sentiment analysis for a stock symbol"""
    return {
        "status": "success",
        "data": {
            "symbol": symbol.upper(),
            "overall_sentiment": "positive",
            "sentiment_score": 0.78,
            "date": datetime.now().isoformat(),
            "sources": {
                "news": 0.82,
                "social_media": 0.76,
                "analyst_ratings": 0.74
            },
            "recent_changes": {
                "1_day": 0.03,
                "1_week": 0.07,
                "1_month": 0.12
            }
        }
    }