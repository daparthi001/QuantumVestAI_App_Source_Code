"""
Background service to periodically fetch and cache Twitter sentiment data
"""
import logging
import time
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.services.twitter_service import TwitterService
from app.db.crud import get_popular_stock_tickers
from app.db import deps

# Set up logging
logger = logging.getLogger(__name__)

class TwitterSentimentScheduler:
    """Service to fetch Twitter sentiment data in the background"""
    
    def __init__(self, cache_ttl_minutes: int = 60):
        self.twitter_service = TwitterService()
        self.sentiment_cache: Dict[str, Dict[str, Any]] = {}
        self.trending_cache: Optional[Dict[str, Any]] = None
        self.trending_timestamp: Optional[datetime] = None
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.work_queue = queue.Queue()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        self.running = True
    
    def _worker(self):
        """Background worker thread to process ticker sentiment requests"""
        logger.info("Starting Twitter sentiment background worker")
        while self.running:
            try:
                # Get work from queue with 1 min timeout
                ticker = self.work_queue.get(timeout=60)
                if ticker:
                    try:
                        # Fetch sentiment data
                        sentiment = self.twitter_service.get_sentiment_summary(ticker)
                        self.sentiment_cache[ticker] = {
                            'data': sentiment,
                            'timestamp': datetime.utcnow()
                        }
                        logger.info(f"Updated Twitter sentiment cache for {ticker}")
                    except Exception as e:
                        logger.error(f"Error updating sentiment for {ticker}: {e}")
                    finally:
                        self.work_queue.task_done()
                
                # If queue is empty, refresh trending data
                if self.work_queue.empty() and (
                    not self.trending_timestamp or 
                    datetime.utcnow() - self.trending_timestamp > self.cache_ttl
                ):
                    try:
                        trending = self.twitter_service.get_trending_tickers()
                        self.trending_cache = {
                            'data': trending,
                            'timestamp': datetime.utcnow()
                        }
                        self.trending_timestamp = datetime.utcnow()
                        logger.info("Updated Twitter trending stocks cache")
                    except Exception as e:
                        logger.error(f"Error updating trending stocks: {e}")
                
                # Add popular stocks to queue if not already cached
                try:
                    # Get database session
                    db = next(deps.get_db())
                    # Get popular stocks
                    popular_tickers = get_popular_stock_tickers(db, limit=20)
                    # Add to queue if not recently cached
                    now = datetime.utcnow()
                    for ticker in popular_tickers:
                        if ticker not in self.sentiment_cache or \
                           now - self.sentiment_cache[ticker]['timestamp'] > self.cache_ttl:
                            self.queue_ticker_update(ticker)
                except Exception as e:
                    logger.error(f"Error scheduling popular stock updates: {e}")
                    
            except queue.Empty:
                # No work, just continue looping
                continue
            except Exception as e:
                logger.error(f"Error in Twitter sentiment worker: {e}")
                time.sleep(10)  # Wait a bit to avoid crash loops
    
    def queue_ticker_update(self, ticker: str):
        """Add ticker to the sentiment update queue"""
        try:
            # Don't add duplicates
            if ticker not in [item for item in list(self.work_queue.queue)]:
                self.work_queue.put(ticker)
        except Exception as e:
            logger.error(f"Error queueing ticker update for {ticker}: {e}")
    
    def get_sentiment(self, ticker: str) -> Dict[str, Any]:
        """
        Get cached sentiment data for a ticker, queue update if needed
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Cached sentiment data or empty response
        """
        now = datetime.utcnow()
        
        # Check if we have cached data and it's not expired
        if ticker in self.sentiment_cache and \
           now - self.sentiment_cache[ticker]['timestamp'] < self.cache_ttl:
            return self.sentiment_cache[ticker]['data']
        
        # Queue ticker for update (non-blocking)
        self.queue_ticker_update(ticker)
        
        # Return cached data even if expired, or empty response
        if ticker in self.sentiment_cache:
            return self.sentiment_cache[ticker]['data']
        else:
            # Return default response
            return {
                'ticker': ticker,
                'tweet_count': 0,
                'avg_sentiment': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'timestamp': now.isoformat()
            }
    
    def get_trending(self) -> Dict[str, Any]:
        """
        Get cached trending stocks data
        
        Returns:
            Cached trending data or empty list
        """
        now = datetime.utcnow()
        
        # Return trending if we have it and it's not expired
        if self.trending_cache and \
           now - self.trending_cache['timestamp'] < self.cache_ttl:
            return {'trending_tickers': self.trending_cache['data'], 'count': len(self.trending_cache['data'])}
        
        # Return empty or old data
        if self.trending_cache:
            return {'trending_tickers': self.trending_cache['data'], 'count': len(self.trending_cache['data'])}
        else:
            return {'trending_tickers': [], 'count': 0}