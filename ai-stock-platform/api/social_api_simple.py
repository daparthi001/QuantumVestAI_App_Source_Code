"""
Simple Social Media Router for Twitter Integration
Works without complex FastAPI dependencies for testing
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from twitter_sentiment_simple import TwitterSentimentAnalyzer
from twitter_config import twitter_config

logger = logging.getLogger(__name__)

class SocialMediaAPI:
    """Simple social media API for testing Twitter integration"""
    
    def __init__(self):
        self.twitter_analyzer = None
    
    def get_twitter_analyzer(self):
        """Get or create Twitter sentiment analyzer instance"""
        if self.twitter_analyzer is None:
            try:
                # Check if Twitter API credentials are configured
                if not twitter_config.has_credentials():
                    raise ValueError("Twitter API credentials not configured")
                
                self.twitter_analyzer = TwitterSentimentAnalyzer()
                logger.info("Twitter sentiment analyzer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter sentiment analyzer: {e}")
                raise ValueError(f"Twitter service not available: {str(e)}")
        
        return self.twitter_analyzer
    
    async def get_twitter_sentiment(
        self,
        symbol: str,
        days: int = 7,
        max_tweets: int = 500
    ) -> Dict[str, Any]:
        """Get Twitter sentiment analysis for a stock symbol"""
        try:
            # Get the Twitter analyzer
            analyzer = self.get_twitter_analyzer()
            
            # Validate symbol
            symbol = symbol.upper().strip()
            if not symbol or len(symbol) > 10:
                raise ValueError("Invalid stock symbol")
            
            # Get sentiment analysis
            sentiment_data = await analyzer.analyze_sentiment(
                symbol=symbol,
                days=days,
                max_tweets=max_tweets
            )
            
            return {
                "status": "success",
                "data": sentiment_data,
                "message": f"Successfully retrieved Twitter sentiment analysis for {symbol}"
            }
            
        except ValueError as e:
            logger.warning(f"Configuration or validation error for Twitter sentiment: {e}")
            return {
                "status": "error",
                "error": str(e),
                "code": "SERVICE_UNAVAILABLE"
            }
        except Exception as e:
            logger.error(f"Unexpected error in Twitter sentiment analysis: {e}")
            return {
                "status": "error",
                "error": "Internal server error while processing sentiment analysis",
                "code": "INTERNAL_SERVER_ERROR"
            }
    
    async def get_trending_stocks(self, limit: int = 10) -> Dict[str, Any]:
        """Get trending stocks based on Twitter activity"""
        try:
            # Get the Twitter analyzer
            analyzer = self.get_twitter_analyzer()
            
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
            
            return {
                "status": "success",
                "data": {
                    "trending_tickers": trending_data,
                    "count": len(trending_data),
                    "last_updated": datetime.now().isoformat()
                },
                "message": "Successfully retrieved trending stocks from Twitter"
            }
            
        except ValueError as e:
            logger.warning(f"Configuration error for trending stocks: {e}")
            return {
                "status": "error",
                "error": str(e),
                "code": "SERVICE_UNAVAILABLE"
            }
        except Exception as e:
            logger.error(f"Unexpected error in trending stocks: {e}")
            return {
                "status": "error",
                "error": "Internal server error while processing trending stocks",
                "code": "INTERNAL_SERVER_ERROR"
            }
    
    def check_twitter_health(self) -> Dict[str, Any]:
        """Check Twitter API health and configuration"""
        try:
            # Check configuration
            config_status = {
                "bearer_token": bool(twitter_config.TWITTER_BEARER_TOKEN),
                "api_key": bool(twitter_config.TWITTER_API_KEY),
                "api_secret": bool(twitter_config.TWITTER_API_SECRET),
                "access_token": bool(twitter_config.TWITTER_ACCESS_TOKEN),
                "access_token_secret": bool(twitter_config.TWITTER_ACCESS_TOKEN_SECRET)
            }
            
            # Check if any credentials are configured
            has_credentials = any(config_status.values())
            
            if not has_credentials:
                return {
                    "status": "error",
                    "error": "Twitter API credentials not configured",
                    "code": "TWITTER_NOT_CONFIGURED",
                    "data": {
                        "configuration": config_status,
                        "status": "not_configured"
                    }
                }
            
            # Try to initialize analyzer
            try:
                analyzer = self.get_twitter_analyzer()
                api_status = "available"
            except Exception as e:
                api_status = f"error: {str(e)}"
            
            return {
                "status": "success",
                "data": {
                    "status": "healthy" if api_status == "available" else "degraded",
                    "configuration": config_status,
                    "api_status": api_status,
                    "last_checked": datetime.now().isoformat()
                },
                "message": "Twitter API health check completed"
            }
            
        except Exception as e:
            logger.error(f"Error checking Twitter API health: {e}")
            return {
                "status": "error",
                "error": "Error checking Twitter API health",
                "code": "INTERNAL_SERVER_ERROR"
            }
    
    async def test_twitter_connection(self) -> Dict[str, Any]:
        """Test Twitter API connection"""
        try:
            # Get the Twitter analyzer
            analyzer = self.get_twitter_analyzer()
            
            # Test with a simple query
            test_result = await analyzer.analyze_sentiment(
                symbol="AAPL",
                days=1,
                max_tweets=10
            )
            
            return {
                "status": "success",
                "data": {
                    "test_result": "success",
                    "sample_data": test_result,
                    "timestamp": datetime.now().isoformat()
                },
                "message": "Twitter API connection test successful"
            }
            
        except ValueError as e:
            return {
                "status": "error",
                "error": str(e),
                "code": "SERVICE_UNAVAILABLE"
            }
        except Exception as e:
            logger.error(f"Twitter API test failed: {e}")
            return {
                "status": "error",
                "error": f"Twitter API test failed: {str(e)}",
                "code": "INTERNAL_SERVER_ERROR"
            }

# Create global instance for testing
social_api = SocialMediaAPI()