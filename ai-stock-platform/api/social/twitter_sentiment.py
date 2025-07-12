"""
Twitter Sentiment Analysis for Stocks
Created: 2025-06-19 03:09:13
Author: daparthi001
Enhanced: 2025-01-09 (AI Assistant)
"""
import logging
import pandas as pd
import tweepy
from textblob import TextBlob
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
import asyncio
from core.config.settings import settings
from core.exceptions import ExternalAPIError, RateLimitError, ConfigurationError
from models.sentiment import SentimentRecord

logger = logging.getLogger("api.social")

class TwitterSentimentAnalyzer:
    """Twitter sentiment analysis for stocks"""
    
    def __init__(self):
        """Initialize Twitter sentiment analyzer with proper error handling"""
        try:
            # Check if credentials are available
            if not any([
                settings.TWITTER_BEARER_TOKEN,
                settings.TWITTER_API_KEY,
                settings.TWITTER_API_SECRET,
                settings.TWITTER_ACCESS_TOKEN,
                settings.TWITTER_ACCESS_TOKEN_SECRET
            ]):
                raise ConfigurationError("Twitter API credentials not configured")
            
            # Twitter API credentials
            self.client = tweepy.Client(
                bearer_token=settings.TWITTER_BEARER_TOKEN,
                consumer_key=settings.TWITTER_API_KEY,
                consumer_secret=settings.TWITTER_API_SECRET,
                access_token=settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True  # Automatically wait when rate limited
            )
            
            # Cache for recent sentiment analysis
            self.sentiment_cache = {}
            
            logger.info("Twitter sentiment analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            raise ConfigurationError(f"Twitter API initialization failed: {str(e)}")
        
    async def analyze_sentiment(
        self, 
        symbol: str,
        company_name: Optional[str] = None,
        days: int = 7,
        max_tweets: int = 500
    ) -> Dict[str, Any]:
        """Analyze Twitter sentiment for a stock symbol"""
        
        # Check cache first
        cache_key = f"{symbol}_{days}"
        if cache_key in self.sentiment_cache and \
           datetime.now() - self.sentiment_cache[cache_key]["timestamp"] < timedelta(hours=1):
            return self.sentiment_cache[cache_key]["data"]
        
        # Build search query
        search_terms = []
        
        # Add cashtag
        search_terms.append(f"${symbol}")
        
        # Add company name if provided
        if company_name:
            # Extract main company name (without Inc., Corp., etc.)
            clean_name = re.sub(r'\s+(Inc\.?|Corp\.?|Corporation|Company|Ltd\.?)$', '', company_name)
            search_terms.append(clean_name)
        
        # Combine search terms
        query = " OR ".join(search_terms)
        
        # Add stock market related words to filter out irrelevant tweets
        query += " (stock OR market OR invest OR trading OR shares OR price)"
        
        # Add filters to improve quality
        query += " -is:retweet lang:en"
        
        # Calculate start time
        start_time = datetime.now() - timedelta(days=days)
        
        try:
            # Get tweets (in a separate thread to avoid blocking)
            tweets = await asyncio.to_thread(
                self._fetch_tweets,
                query=query,
                start_time=start_time,
                max_results=max_tweets
            )
            
            # Analyze sentiment
            sentiment_scores = []
            tweet_data = []
            
            for tweet in tweets:
                try:
                    blob = TextBlob(self._clean_tweet(tweet.text))
                    sentiment_score = blob.sentiment.polarity
                    
                    sentiment_scores.append(sentiment_score)
                    tweet_data.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "sentiment": sentiment_score,
                        "engagement": (tweet.public_metrics.get("retweet_count", 0) + 
                                      tweet.public_metrics.get("reply_count", 0) + 
                                      tweet.public_metrics.get("like_count", 0))
                    })
                except Exception as e:
                    logger.warning(f"Error processing tweet {tweet.id}: {e}")
                    continue
            
            # Calculate overall sentiment
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                
                # Determine sentiment label
                if avg_sentiment > 0.1:
                    sentiment_label = "positive"
                elif avg_sentiment < -0.1:
                    sentiment_label = "negative"
                else:
                    sentiment_label = "neutral"
                
                # Sort tweets by engagement and sentiment (for top mentions)
                sorted_tweets = sorted(
                    tweet_data, 
                    key=lambda x: (abs(x["sentiment"]) * 0.7 + x["engagement"] * 0.3),
                    reverse=True
                )
                
                # Get top mentions
                top_mentions = []
                for tweet in sorted_tweets[:10]:
                    top_mentions.append({
                        "text": tweet["text"],
                        "sentiment": tweet["sentiment"],
                        "source": "twitter",
                        "url": f"https://twitter.com/twitter/status/{tweet['id']}",
                        "engagement": tweet["engagement"]
                    })
                
                # Calculate daily sentiment
                daily_sentiment = self._calculate_daily_sentiment(tweet_data)
                
                # Prepare result
                result = {
                    "symbol": symbol,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "sentiment_score": avg_sentiment,
                    "sentiment_label": sentiment_label,
                    "volume": len(tweets),
                    "trending_score": len(tweets) * (abs(avg_sentiment) + 0.5),
                    "sources": {
                        "twitter": len(tweets),
                        "reddit": 0,
                        "news": 0,
                        "other": 0
                    },
                    "top_mentions": top_mentions,
                    "daily_sentiment": daily_sentiment
                }
                
                # Cache the result
                self.sentiment_cache[cache_key] = {
                    "timestamp": datetime.now(),
                    "data": result
                }
                
                # Store in database asynchronously
                asyncio.create_task(self._store_sentiment_record(symbol, result))
                
                return result
            else:
                return {
                    "symbol": symbol,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "sentiment_score": 0,
                    "sentiment_label": "neutral",
                    "volume": 0,
                    "trending_score": 0,
                    "sources": {
                        "twitter": 0,
                        "reddit": 0,
                        "news": 0,
                        "other": 0
                    },
                    "top_mentions": [],
                    "daily_sentiment": []
                }
                
        except (RateLimitError, ConfigurationError, ExternalAPIError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Error analyzing Twitter sentiment for {symbol}: {str(e)}")
            raise ExternalAPIError(f"Sentiment analysis failed: {str(e)}")
    
    def _fetch_tweets(
        self, 
        query: str, 
        start_time: datetime,
        max_results: int = 100
    ) -> List[Any]:
        """Fetch tweets using the Twitter API with proper error handling"""
        tweets = []
        
        try:
            # Search parameters
            tweet_fields = ["created_at", "public_metrics", "context_annotations"]
            
            # Paginate through results
            pagination_token = None
            remaining_results = max_results
            
            while remaining_results > 0:
                # Determine batch size (max 100 per request)
                batch_size = min(remaining_results, 100)
                
                try:
                    # Make API request
                    response = self.client.search_recent_tweets(
                        query=query,
                        tweet_fields=tweet_fields,
                        start_time=start_time,
                        max_results=batch_size,
                        next_token=pagination_token
                    )
                    
                    # Check if we got any tweets
                    if not response or not response.data:
                        logger.info(f"No tweets found for query: {query}")
                        break
                        
                    # Add tweets to our list
                    tweets.extend(response.data)
                    remaining_results -= len(response.data)
                    
                    # Check if we have more results
                    if response.meta and response.meta.get("next_token") and remaining_results > 0:
                        pagination_token = response.meta["next_token"]
                    else:
                        break
                        
                except tweepy.TooManyRequests:
                    logger.warning("Twitter API rate limit exceeded")
                    raise RateLimitError("Twitter API rate limit exceeded")
                except tweepy.Unauthorized:
                    logger.error("Twitter API unauthorized - check credentials")
                    raise ConfigurationError("Twitter API credentials are invalid")
                except tweepy.Forbidden:
                    logger.error("Twitter API forbidden - check permissions")
                    raise ConfigurationError("Twitter API access forbidden")
                except tweepy.NotFound:
                    logger.warning(f"No tweets found for query: {query}")
                    break
                except tweepy.TwitterServerError as e:
                    logger.error(f"Twitter API server error: {e}")
                    raise ExternalAPIError(f"Twitter API server error: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error in Twitter API call: {e}")
                    raise ExternalAPIError(f"Twitter API error: {str(e)}")
            
            logger.info(f"Successfully fetched {len(tweets)} tweets for query: {query}")
            return tweets
            
        except (RateLimitError, ConfigurationError, ExternalAPIError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            raise ExternalAPIError(f"Failed to fetch tweets: {str(e)}")
    
    def _clean_tweet(self, text: str) -> str:
        """Clean tweet text for sentiment analysis"""
        # Remove links
        text = re.sub(r'https?:\/\/\S+', '', text)
        
        # Remove user mentions
        text = re.sub(r'@[A-Za-z0-9_]+', '', text)
        
        # Remove cashtags and hashtags
        text = re.sub(r'[$#][A-Za-z0-9_]+', '', text)
        
        # Remove non-alphanumeric characters
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_daily_sentiment(self, tweet_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate daily sentiment from tweet data"""
        # Group tweets by day
        daily_tweets = {}
        
        for tweet in tweet_data:
            day = tweet["created_at"].strftime("%Y-%m-%d")
            
            if day not in daily_tweets:
                daily_tweets[day] = {
                    "date": day,
                    "tweets": [],
                    "sentiment_scores": []
                }
            
            daily_tweets[day]["tweets"].append(tweet)
            daily_tweets[day]["sentiment_scores"].append(tweet["sentiment"])
        
        # Calculate average sentiment for each day
        daily_sentiment = []
        
        for day, data in daily_tweets.items():
            avg_sentiment = sum(data["sentiment_scores"]) / len(data["sentiment_scores"])
            
            daily_sentiment.append({
                "date": day,
                "sentiment_score": avg_sentiment,
                "volume": len(data["tweets"])
            })
        
        # Sort by date
        daily_sentiment.sort(key=lambda x: x["date"])
        
        return daily_sentiment
    
    async def _store_sentiment_record(self, symbol: str, sentiment_data: Dict[str, Any]) -> None:
        """Store sentiment record in database"""
        try:
            # Create sentiment record
            record = SentimentRecord(
                symbol=symbol,
                date=datetime.now(),
                sentiment_score=sentiment_data["sentiment_score"],
                sentiment_label=sentiment_data["sentiment_label"],
                volume=sentiment_data["volume"],
                trending_score=sentiment_data["trending_score"],
                data=sentiment_data
            )
            
            # Save to database
            await record.save()
        except Exception as e:
            logger.error(f"Error storing sentiment record: {str(e)}")
