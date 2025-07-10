"""
Trending Stocks Service

This service handles fetching and caching trending stock data,
providing real-time updates only.

Created: 2025-01-09
Author: AI Assistant
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from core.config import settings

# Try to import aiohttp, fallback to None if not available
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    aiohttp = None
    AIOHTTP_AVAILABLE = False

logger = logging.getLogger(__name__)

class TrendingStocksService:
    """Service for managing trending stocks data with real-time updates and caching."""
    
    def __init__(self):
        # Use configured API key or fallback to the default demo key
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY", settings.ALPHA_VANTAGE_API_KEY)
        if not self.api_key:
            raise RuntimeError(
                "ALPHA_VANTAGE_API_KEY must be set for real-time data access"
            )
        self.base_url = "https://www.alphavantage.co/query"
        self.cache_ttl = int(os.getenv("CACHE_TTL_TRENDING_STOCKS", "300"))  # 5 minutes
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        
        # Log dependency status
        if not AIOHTTP_AVAILABLE:
            raise RuntimeError("aiohttp is required for real-time data access")
        
        # Default trending symbols to fetch
        self.trending_symbols = [
            "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", 
            "TSLA", "META", "NFLX", "CRM", "ADBE"
        ]
    
    async def get_trending_stocks(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Get trending stocks with pagination.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
            
        Returns:
            Dict containing stocks data and pagination info
        """
        try:
            # Check cache first
            if self._is_cache_valid():
                logger.info("Returning trending stocks from cache")
                return self._get_paginated_data(self._cache["stocks"], page, limit)
            
            # Fetch fresh data
            logger.info("Fetching fresh trending stocks data")
            stocks_data = await self._fetch_trending_stocks()
            
            # Update cache
            self._update_cache(stocks_data)
            
            return self._get_paginated_data(stocks_data, page, limit)
            
        except Exception as e:
            logger.error(f"Error fetching trending stocks: {e}")
            raise
    
    async def _fetch_trending_stocks(self) -> List[Dict[str, Any]]:
        """Fetch trending stocks data from external API."""
        if not AIOHTTP_AVAILABLE:
            raise RuntimeError("aiohttp is required for real-time data access")
        
        stocks_data = []
        
        async with aiohttp.ClientSession() as session:
            # Fetch data for each trending symbol
            tasks = [
                self._fetch_stock_quote(session, symbol) 
                for symbol in self.trending_symbols
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, result in zip(self.trending_symbols, results):
                if isinstance(result, Exception):
                    logger.warning(f"Failed to fetch data for {symbol}: {result}")
                    continue
                    
                if result:
                    stocks_data.append(result)
        
        # Sort by change percentage (descending) for trending effect
        stocks_data.sort(key=lambda x: x.get("change_percent", 0), reverse=True)
        
        return stocks_data
    
    async def _fetch_stock_quote(self, session, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch a single stock quote from Alpha Vantage."""
        if not AIOHTTP_AVAILABLE:
            # This should not be called if aiohttp is not available, but provide a safeguard
            logger.warning(f"Cannot fetch stock quote for {symbol} - aiohttp not available")
            return None
            
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            async with session.get(self.base_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_alpha_vantage_response(symbol, data)
                else:
                    logger.warning(f"API request failed for {symbol}: status {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching data for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _parse_alpha_vantage_response(self, symbol: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Alpha Vantage API response into our format."""
        try:
            quote = data.get("Global Quote", {})
            if not quote:
                return None
            
            # Alpha Vantage field mappings
            price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            change_percent = float(quote.get("10. change percent", "0%").rstrip('%'))
            volume = int(quote.get("06. volume", 0))
            
            # Get company name mapping (simplified)
            company_names = {
                "AAPL": "Apple Inc.",
                "MSFT": "Microsoft Corporation", 
                "AMZN": "Amazon.com Inc.",
                "GOOGL": "Alphabet Inc.",
                "NVDA": "NVIDIA Corporation",
                "TSLA": "Tesla Inc.",
                "META": "Meta Platforms Inc.",
                "NFLX": "Netflix Inc.",
                "CRM": "Salesforce Inc.",
                "ADBE": "Adobe Inc."
            }
            
            return {
                "symbol": symbol,
                "name": company_names.get(symbol, f"{symbol} Corp."),
                "price": round(price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "last_updated": datetime.now().isoformat()
            }
            
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing data for {symbol}: {e}")
            return None
    
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is valid based on TTL."""
        if not self._cache_timestamp or not self._cache:
            return False
        
        age = datetime.now() - self._cache_timestamp
        return age.total_seconds() < self.cache_ttl
    
    def _update_cache(self, stocks_data: List[Dict[str, Any]]) -> None:
        """Update cache with fresh data."""
        self._cache = {
            "stocks": stocks_data,
            "timestamp": datetime.now().isoformat()
        }
        self._cache_timestamp = datetime.now()
        logger.info(f"Cache updated with {len(stocks_data)} stocks")
    
    def _get_paginated_data(self, stocks_data: List[Dict[str, Any]], page: int, limit: int) -> Dict[str, Any]:
        """Apply pagination to stocks data."""
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_stocks = stocks_data[start_idx:end_idx]
        
        return {
            "stocks": paginated_stocks,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(stocks_data),
                "has_next": end_idx < len(stocks_data),
                "has_prev": page > 1
            },
            "metadata": {
                "last_updated": self._cache.get("timestamp") if self._cache else datetime.now().isoformat(),
                "cache_ttl_seconds": self.cache_ttl,
                "data_source": "real"
            }
        }
    
    
    def invalidate_cache(self) -> None:
        """Manually invalidate the cache to force fresh data fetch."""
        self._cache = {}
        self._cache_timestamp = None
        logger.info("Trending stocks cache invalidated")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get current cache status for monitoring."""
        if not self._cache_timestamp:
            return {"status": "empty", "age_seconds": None}
        
        age = datetime.now() - self._cache_timestamp
        age_seconds = int(age.total_seconds())
        
        return {
            "status": "valid" if age_seconds < self.cache_ttl else "expired",
            "age_seconds": age_seconds,
            "ttl_seconds": self.cache_ttl,
            "items_count": len(self._cache.get("stocks", [])),
            "last_updated": self._cache_timestamp.isoformat()        }

