"""
Social Media Integration Router
Created: 2025-01-09
Author: AI Assistant
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import get_db_session
from core.responses import create_success_response, create_error_response
from core.exceptions import ExternalAPIError, RateLimitError, ConfigurationError
from core.config.settings import settings
from social.twitter_sentiment import TwitterSentimentAnalyzer

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social", tags=["Social Media"])

# Initialize Twitter sentiment analyzer (will be done lazily)
twitter_analyzer = None

def get_twitter_analyzer():
    """Get or create Twitter sentiment analyzer instance"""
    global twitter_analyzer
    if twitter_analyzer is None:
        try:
            # Check if Twitter API credentials are configured
            if not any([
                settings.TWITTER_BEARER_TOKEN,
                settings.TWITTER_API_KEY,
                settings.TWITTER_API_SECRET,
                settings.TWITTER_ACCESS_TOKEN,
                settings.TWITTER_ACCESS_TOKEN_SECRET
            ]):
                raise ConfigurationError("Twitter API credentials not configured")
            
            twitter_analyzer = TwitterSentimentAnalyzer()
            logger.info("Twitter sentiment analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter sentiment analyzer: {e}")
            raise ConfigurationError(f"Twitter service not available: {str(e)}")
    
    return twitter_analyzer

@router.get(
    "/twitter/sentiment/{symbol}",
    status_code=status.HTTP_200_OK,
    summary="Get Twitter Sentiment Analysis",
    description="Get sentiment analysis for a specific stock symbol based on Twitter data"
)
async def get_twitter_sentiment(
    symbol: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    max_tweets: int = Query(500, ge=100, le=1000, description="Maximum number of tweets to analyze")
):
    """Get Twitter sentiment analysis for a stock symbol"""
    try:
        # Get the Twitter analyzer
        analyzer = get_twitter_analyzer()
        
        # Validate symbol
        symbol = symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid stock symbol"
            )
        
        # Get sentiment analysis
        sentiment_data = await analyzer.analyze_sentiment(
            symbol=symbol,
            days=days,
            max_tweets=max_tweets
        )
        
        return create_success_response(
            data=sentiment_data,
            message=f"Successfully retrieved Twitter sentiment analysis for {symbol}"
        )
        
    except ConfigurationError as e:
        logger.warning(f"Configuration error for Twitter sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for Twitter API: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Twitter API rate limit exceeded. Please try again later."
        )
    except ExternalAPIError as e:
        logger.error(f"External API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Twitter API service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in Twitter sentiment analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing sentiment analysis"
        )

@router.get(
    "/twitter/trending",
    status_code=status.HTTP_200_OK,
    summary="Get Trending Stocks on Twitter",
    description="Get list of trending stocks based on Twitter activity"
)
async def get_trending_stocks(
    limit: int = Query(10, ge=1, le=50, description="Number of trending stocks to return")
):
    """Get trending stocks based on Twitter activity"""
    try:
        # Get the Twitter analyzer
        analyzer = get_twitter_analyzer()
        
        # For now, return demo data with proper structure
        # In a real implementation, this would analyze multiple stocks
        demo_trending = [
            {
                "ticker": "AAPL",
                "tweet_count": 1250,
                "engagement": 15000,
                "sentiment": 0.15,
                "volume_change": 0.08
            },
            {
                "ticker": "TSLA",
                "tweet_count": 980,
                "engagement": 12000,
                "sentiment": 0.22,
                "volume_change": 0.12
            },
            {
                "ticker": "MSFT",
                "tweet_count": 750,
                "engagement": 9500,
                "sentiment": 0.05,
                "volume_change": 0.03
            },
            {
                "ticker": "GOOGL",
                "tweet_count": 620,
                "engagement": 7800,
                "sentiment": -0.02,
                "volume_change": -0.01
            },
            {
                "ticker": "AMZN",
                "tweet_count": 580,
                "engagement": 6900,
                "sentiment": 0.08,
                "volume_change": 0.05
            }
        ]
        
        # Apply limit
        trending_data = demo_trending[:limit]
        
        return create_success_response(
            data={
                "trending_tickers": trending_data,
                "count": len(trending_data),
                "last_updated": datetime.now().isoformat()
            },
            message="Successfully retrieved trending stocks from Twitter"
        )
        
    except ConfigurationError as e:
        logger.warning(f"Configuration error for trending stocks: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in trending stocks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing trending stocks"
        )

@router.get(
    "/twitter/health",
    status_code=status.HTTP_200_OK,
    summary="Check Twitter API Health",
    description="Check the health and configuration of Twitter API integration"
)
async def check_twitter_health():
    """Check Twitter API health and configuration"""
    try:
        # Check configuration
        config_status = {
            "bearer_token": bool(settings.TWITTER_BEARER_TOKEN),
            "api_key": bool(settings.TWITTER_API_KEY),
            "api_secret": bool(settings.TWITTER_API_SECRET),
            "access_token": bool(settings.TWITTER_ACCESS_TOKEN),
            "access_token_secret": bool(settings.TWITTER_ACCESS_TOKEN_SECRET)
        }
        
        # Check if any credentials are configured
        has_credentials = any(config_status.values())
        
        if not has_credentials:
            return create_error_response(
                message="Twitter API credentials not configured",
                error_code="TWITTER_NOT_CONFIGURED",
                details={
                    "configuration": config_status,
                    "status": "not_configured"
                }
            )
        
        # Try to initialize analyzer
        try:
            analyzer = get_twitter_analyzer()
            api_status = "available"
        except Exception as e:
            api_status = f"error: {str(e)}"
        
        return create_success_response(
            data={
                "status": "healthy" if api_status == "available" else "degraded",
                "configuration": config_status,
                "api_status": api_status,
                "last_checked": datetime.now().isoformat()
            },
            message="Twitter API health check completed"
        )
        
    except Exception as e:
        logger.error(f"Error checking Twitter API health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking Twitter API health"
        )

@router.post(
    "/twitter/test",
    status_code=status.HTTP_200_OK,
    summary="Test Twitter API Connection",
    description="Test the Twitter API connection with a simple query"
)
async def test_twitter_connection():
    """Test Twitter API connection"""
    try:
        # Get the Twitter analyzer
        analyzer = get_twitter_analyzer()
        
        # Test with a simple query
        test_result = await analyzer.analyze_sentiment(
            symbol="AAPL",
            days=1,
            max_tweets=10
        )
        
        return create_success_response(
            data={
                "test_result": "success",
                "sample_data": test_result,
                "timestamp": datetime.now().isoformat()
            },
            message="Twitter API connection test successful"
        )
        
    except ConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Twitter API test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Twitter API test failed: {str(e)}"
        )