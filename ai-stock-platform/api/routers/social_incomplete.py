"""Simplified social media router used for integration tests.

This module originally referenced a scheduler in ``app.main`` that is not part of
the open source codebase. The endpoints below now use the lightweight
``SocialMediaAPI`` implemented in :mod:`social_api_simple` so they work out of the
box without additional infrastructure.
"""

from fastapi import APIRouter, HTTPException, Query

from social_api_simple import SocialMediaAPI


router = APIRouter(prefix="/api/simple-social", tags=["Social Media"])

social_api = SocialMediaAPI()


@router.get("/twitter/sentiment/{ticker}")
async def get_stock_twitter_sentiment(
    ticker: str,
    days: int = Query(7, ge=1, le=30),
):
    """Return Twitter sentiment analysis for a stock ticker."""
    try:
        result = await social_api.get_twitter_sentiment(symbol=ticker, days=days)
        if result.get("status") == "error":
            raise HTTPException(status_code=503, detail=result.get("error"))
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Twitter sentiment: {str(e)}")


@router.get("/twitter/trending")
async def get_trending_tickers(limit: int = Query(10, ge=1, le=50)):
    """Return trending stock tickers on Twitter."""
    try:
        result = await social_api.get_trending_stocks(limit=limit)
        if result.get("status") == "error":
            raise HTTPException(status_code=503, detail=result.get("error"))
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trending tickers: {str(e)}")


@router.get("/twitter/health")
async def twitter_health() -> dict:
    """Simple health check for the Twitter integration."""
    return social_api.check_twitter_health()
