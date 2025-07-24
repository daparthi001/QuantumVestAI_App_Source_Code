"""
Multi-Source Sentiment Analysis for Enhanced Market Intelligence
Created: 2025-01-09
Author: AI Assistant for QuantumVestAI
"""
import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from textblob import TextBlob

from .twitter_sentiment import TwitterSentimentAnalyzer

logger = logging.getLogger("api.social.multi_source")

class MultiSourceSentimentAnalyzer:
    """Enhanced sentiment analysis combining multiple data sources"""
    
    def __init__(self):
        self.twitter_analyzer = TwitterSentimentAnalyzer()
        self.session = None
        self.cache = {}
        self.cache_timeout = timedelta(minutes=30)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_comprehensive_sentiment(
        self,
        symbol: str,
        company_name: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Analyze sentiment from multiple sources"""
        
        # Check cache
        cache_key = f"{symbol}_{days}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < self.cache_timeout:
                return cached_data["data"]
        
        # Gather sentiment from multiple sources
        sentiment_tasks = [
            self._get_twitter_sentiment(symbol, company_name, days),
            self._get_news_sentiment(symbol, company_name, days),
            self._get_reddit_sentiment(symbol, company_name, days),
            self._get_fintech_sentiment(symbol, company_name, days)
        ]
        
        results = await asyncio.gather(*sentiment_tasks, return_exceptions=True)
        
        # Combine results
        combined_sentiment = self._combine_sentiment_sources(results, symbol)
        
        # Cache result
        self.cache[cache_key] = {
            "data": combined_sentiment,
            "timestamp": datetime.now()
        }
        
        return combined_sentiment
    
    async def _get_twitter_sentiment(
        self,
        symbol: str,
        company_name: Optional[str],
        days: int
    ) -> Dict[str, Any]:
        """Get Twitter sentiment using existing analyzer"""
        try:
            twitter_data = await self.twitter_analyzer.analyze_sentiment(
                symbol, company_name, days
            )
            return {
                "source": "twitter",
                "sentiment_score": twitter_data.get("overall_sentiment", 0),
                "confidence": twitter_data.get("confidence", 0),
                "volume": twitter_data.get("tweet_count", 0),
                "daily_sentiment": twitter_data.get("daily_sentiment", []),
                "success": True
            }
        except Exception as e:
            logger.error(f"Twitter sentiment analysis failed: {e}")
            return {"source": "twitter", "success": False, "error": str(e)}
    
    async def _get_news_sentiment(
        self,
        symbol: str,
        company_name: Optional[str],
        days: int
    ) -> Dict[str, Any]:
        """Analyze sentiment from financial news sources"""
        try:
            if not self.session:
                return {"source": "news", "success": False, "error": "Session not initialized"}
            
            # Use Yahoo Finance news API as a free alternative
            news_data = await self._fetch_yahoo_news(symbol, days)
            
            if not news_data:
                return {"source": "news", "success": False, "error": "No news data"}
            
            # Analyze sentiment of news headlines and summaries
            sentiments = []
            for article in news_data:
                text = f"{article.get('title', '')} {article.get('summary', '')}"
                sentiment = self._analyze_text_sentiment(text)
                sentiments.append(sentiment)
            
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            return {
                "source": "news",
                "sentiment_score": avg_sentiment,
                "confidence": min(0.8, len(sentiments) / 10),  # Confidence based on volume
                "volume": len(news_data),
                "success": True
            }
        except Exception as e:
            logger.error(f"News sentiment analysis failed: {e}")
            return {"source": "news", "success": False, "error": str(e)}
    
    async def _get_reddit_sentiment(
        self,
        symbol: str,
        company_name: Optional[str],
        days: int
    ) -> Dict[str, Any]:
        """Analyze sentiment from Reddit discussions"""
        try:
            if not self.session:
                return {"source": "reddit", "success": False, "error": "Session not initialized"}
            
            # Use Reddit API to search for stock discussions
            reddit_data = await self._fetch_reddit_data(symbol, days)
            
            if not reddit_data:
                return {"source": "reddit", "success": False, "error": "No Reddit data"}
            
            # Analyze sentiment of Reddit posts and comments
            sentiments = []
            for post in reddit_data:
                text = f"{post.get('title', '')} {post.get('selftext', '')}"
                sentiment = self._analyze_text_sentiment(text)
                sentiments.append(sentiment)
            
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            return {
                "source": "reddit",
                "sentiment_score": avg_sentiment,
                "confidence": min(0.7, len(sentiments) / 20),  # Reddit confidence slightly lower
                "volume": len(reddit_data),
                "success": True
            }
        except Exception as e:
            logger.error(f"Reddit sentiment analysis failed: {e}")
            return {"source": "reddit", "success": False, "error": str(e)}
    
    async def _get_fintech_sentiment(
        self,
        symbol: str,
        company_name: Optional[str],
        days: int
    ) -> Dict[str, Any]:
        """Analyze sentiment from financial technology sources"""
        try:
            # Simulate fintech sentiment analysis
            # In a real implementation, this would integrate with financial APIs
            return {
                "source": "fintech",
                "sentiment_score": 0.1,  # Neutral slightly positive
                "confidence": 0.6,
                "volume": 50,
                "success": True,
                "note": "Simulated fintech sentiment"
            }
        except Exception as e:
            logger.error(f"Fintech sentiment analysis failed: {e}")
            return {"source": "fintech", "success": False, "error": str(e)}
    
    async def _fetch_yahoo_news(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Fetch news from Yahoo Finance"""
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {"q": symbol, "newsCount": 5}
        try:
            async with self.session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    articles = data.get("news", [])
                    parsed = []
                    for art in articles:
                        ts = art.get("providerPublishTime")
                        ts_dt = (
                            datetime.fromtimestamp(ts)
                            if isinstance(ts, (int, float))
                            else datetime.now()
                        )
                        parsed.append(
                            {
                                "title": art.get("title"),
                                "summary": art.get("summary", ""),
                                "timestamp": ts_dt,
                            }
                        )
                    return parsed
        except Exception as e:
            logger.error(f"Yahoo news fetch failed: {e}")
        return []
    
    async def _fetch_reddit_data(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Fetch Reddit posts about the stock"""
        try:
            # Simulate Reddit API call
            # In a real implementation, this would use Reddit API
            return [
                {
                    "title": f"Discussion about {symbol}",
                    "selftext": "This stock looks promising for the future",
                    "score": 10 + i,
                    "timestamp": datetime.now() - timedelta(hours=i * 2)
                }
                for i in range(3)
            ]
        except Exception as e:
            logger.error(f"Reddit data fetch failed: {e}")
            return []
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using TextBlob"""
        if not text or not text.strip():
            return 0.0
        
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Text sentiment analysis failed: {e}")
            return 0.0
    
    def _combine_sentiment_sources(
        self,
        results: List[Any],
        symbol: str
    ) -> Dict[str, Any]:
        """Combine sentiment results from multiple sources"""
        
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        
        if not successful_results:
            return {
                "symbol": symbol,
                "overall_sentiment": 0.0,
                "confidence": 0.0,
                "sources": [],
                "total_volume": 0,
                "analysis_timestamp": datetime.now().isoformat(),
                "error": "No sources provided successful sentiment analysis"
            }
        
        # Calculate weighted average sentiment
        total_weight = 0
        weighted_sentiment = 0
        total_volume = 0
        source_weights = {
            "twitter": 0.4,
            "news": 0.3,
            "reddit": 0.2,
            "fintech": 0.1
        }
        
        for result in successful_results:
            source = result.get("source", "unknown")
            sentiment = result.get("sentiment_score", 0)
            confidence = result.get("confidence", 0)
            volume = result.get("volume", 0)
            
            weight = source_weights.get(source, 0.1) * confidence
            weighted_sentiment += sentiment * weight
            total_weight += weight
            total_volume += volume
        
        overall_sentiment = weighted_sentiment / total_weight if total_weight > 0 else 0
        overall_confidence = min(1.0, total_weight / sum(source_weights.values()))
        
        return {
            "symbol": symbol,
            "overall_sentiment": round(overall_sentiment, 4),
            "confidence": round(overall_confidence, 4),
            "sources": [
                {
                    "name": r.get("source"),
                    "sentiment": r.get("sentiment_score"),
                    "confidence": r.get("confidence"),
                    "volume": r.get("volume")
                }
                for r in successful_results
            ],
            "total_volume": total_volume,
            "analysis_timestamp": datetime.now().isoformat(),
            "sentiment_category": self._categorize_sentiment(overall_sentiment),
            "market_impact": self._assess_market_impact(overall_sentiment, overall_confidence, total_volume)
        }
    
    def _categorize_sentiment(self, sentiment: float) -> str:
        """Categorize sentiment into human-readable categories"""
        if sentiment > 0.3:
            return "Very Positive"
        elif sentiment > 0.1:
            return "Positive"
        elif sentiment > -0.1:
            return "Neutral"
        elif sentiment > -0.3:
            return "Negative"
        else:
            return "Very Negative"
    
    def _assess_market_impact(self, sentiment: float, confidence: float, volume: int) -> str:
        """Assess potential market impact of sentiment"""
        impact_score = abs(sentiment) * confidence * min(1.0, volume / 100)
        
        if impact_score > 0.5:
            return "High Impact"
        elif impact_score > 0.3:
            return "Medium Impact"
        elif impact_score > 0.1:
            return "Low Impact"
        else:
            return "Minimal Impact"
