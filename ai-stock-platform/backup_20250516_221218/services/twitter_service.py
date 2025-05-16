"""
Twitter service for retrieving and analyzing tweets related to stocks.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import tweepy
from textblob import TextBlob
import pandas as pd

from app.core.config import settings

logger = logging.getLogger(__name__)

class TwitterService:
    """Service for interacting with Twitter API and analyzing tweets."""
    
    def __init__(self):
        """Initialize Twitter API client."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Twitter API client with credentials from environment."""
        try:
            # Get credentials from environment variables or settings
            consumer_key = os.getenv("TWITTER_CONSUMER_KEY") or settings.twitter_consumer_key
            consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET") or settings.twitter_consumer_secret
            access_token = os.getenv("TWITTER_ACCESS_TOKEN") or settings.twitter_access_token
            access_secret = os.getenv("TWITTER_ACCESS_SECRET") or settings.twitter_access_secret
            
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )
            logger.info("Twitter API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API client: {e}")
            self.client = None
    
    def get_tweets_for_ticker(self, ticker: str, days_back: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent tweets related to a stock ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            days_back: Number of days to look back
            limit: Maximum number of tweets to retrieve
            
        Returns:
            List of tweet objects with additional sentiment analysis
        """
        if not self.client:
            logger.warning("Twitter API client not initialized")
            return []
        
        search_query = f"${ticker} lang:en -is:retweet"
        start_time = datetime.utcnow() - timedelta(days=days_back)
        
        try:
            # Search for tweets
            response = self.client.search_recent_tweets(
                query=search_query,
                start_time=start_time,
                max_results=min(limit, 100),  # API limit is 100 per request
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )
            
            if not response or not response.data:
                logger.info(f"No tweets found for ticker {ticker}")
                return []
            
            # Process and enrich tweets with sentiment analysis
            enriched_tweets = []
            for tweet in response.data:
                # Analyze sentiment
                analysis = TextBlob(tweet.text)
                sentiment_score = analysis.sentiment.polarity
                sentiment_category = 'positive' if sentiment_score > 0.1 else ('negative' if sentiment_score < -0.1 else 'neutral')
                
                # Create enriched tweet object
                enriched_tweet = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'author_id': tweet.author_id,
                    'retweet_count': tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'like_count': tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0,
                    'sentiment_score': sentiment_score,
                    'sentiment': sentiment_category
                }
                enriched_tweets.append(enriched_tweet)
            
            logger.info(f"Retrieved and analyzed {len(enriched_tweets)} tweets for {ticker}")
            return enriched_tweets
            
        except Exception as e:
            logger.error(f"Error retrieving tweets for {ticker}: {e}")
            return []
    
    def get_sentiment_summary(self, ticker: str, days_back: int = 7) -> Dict[str, Any]:
        """
        Get sentiment summary for a stock based on recent tweets.
        
        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back
            
        Returns:
            Dictionary with sentiment summary metrics
        """
        tweets = self.get_tweets_for_ticker(ticker, days_back=days_back, limit=500)
        
        if not tweets:
            return {
                'ticker': ticker,
                'tweet_count': 0,
                'avg_sentiment': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Calculate metrics
        sentiment_scores = [tweet['sentiment_score'] for tweet in tweets]
        sentiment_categories = [tweet['sentiment'] for tweet in tweets]
        
        # Calculate distribution
        total = len(sentiment_categories)
        distribution = {
            'positive': sentiment_categories.count('positive') / total,
            'neutral': sentiment_categories.count('neutral') / total,
            'negative': sentiment_categories.count('negative') / total
        }
        
        return {
            'ticker': ticker,
            'tweet_count': len(tweets),
            'avg_sentiment': sum(sentiment_scores) / len(sentiment_scores),
            'sentiment_distribution': distribution,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_trending_tickers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending stock tickers on Twitter.
        
        Args:
            limit: Maximum number of trending tickers to return
            
        Returns:
            List of trending tickers with tweet counts and sentiment
        """
        if not self.client:
            logger.warning("Twitter API client not initialized")
            return []
        
        # Common stock tickers to check for trending
        common_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 
                          'NVDA', 'JPM', 'V', 'JNJ', 'WMT', 'BAC', 'PG',
                          'DIS', 'NFLX', 'INTC', 'CSCO', 'VZ', 'KO', 'PEP']
        
        trending = []
        
        for ticker in common_tickers:
            try:
                # Search for recent tweets about this ticker
                search_query = f"${ticker} lang:en -is:retweet"
                response = self.client.search_recent_tweets(
                    query=search_query,
                    max_results=10,
                    tweet_fields=['public_metrics']
                )
                
                if response and response.data:
                    # Calculate engagement metrics
                    tweet_count = len(response.data)
                    engagement = sum(t.public_metrics['like_count'] + t.public_metrics['retweet_count'] 
                                    for t in response.data if hasattr(t, 'public_metrics'))
                    
                    # Calculate sentiment
                    sentiment_scores = [TextBlob(t.text).sentiment.polarity for t in response.data]
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                    
                    trending.append({
                        'ticker': ticker,
                        'tweet_count': tweet_count,
                        'engagement': engagement,
                        'sentiment': avg_sentiment
                    })
            except Exception as e:
                logger.error(f"Error checking trend for {ticker}: {e}")
        
        # Sort by engagement
        trending.sort(key=lambda x: x['engagement'], reverse=True)
        return trending[:limit]