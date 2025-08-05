"""
Trending Stocks Service

This service handles fetching and caching trending stock data,
providing real-time updates only.

Created: 2025-01-09
Author: AI Assistant
"""
import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import requests

# Optional Redis cache support
try:  # pragma: no cover - cache is optional in tests
    from api.core.cache import cache as redis_cache  # type: ignore
except Exception:  # pragma: no cover - Redis or package not available
    try:
        from core.cache import cache as redis_cache  # type: ignore
    except Exception:  # pragma: no cover - final fallback
        redis_cache = None

# Explicitly import the settings instance to avoid ambiguity with the
# `core.config` package which also contains a `settings` submodule.
# Import settings directly from the API package to avoid the compatibility
# module in ``core`` which exposes a submodule with the same name.  Importing
# via ``core.config.settings`` can result in the module object being returned
# instead of the ``settings`` instance, leading to missing attribute errors.
# Import the settings object from the API's ``core`` package explicitly.
# This avoids accidentally importing the similarly named package located in
# the repository root which lacks several attributes such as
# ``ALPHA_VANTAGE_API_KEY``.
# Attempt to import the settings object.  Some test environments load this
# module directly via ``importlib`` without configuring ``PYTHONPATH``.  In
# those cases importing ``api.core.config`` or the compatibility
# ``core.config`` package fails which previously raised an ``ImportError`` and
# prevented the service from being used.  To keep the service functional across
# all environments, fall back to reading the required configuration directly
# from environment variables when the settings modules cannot be imported.
try:  # pragma: no cover - exercised indirectly in tests
    from api.core.config import settings
except Exception:  # pragma: no cover - handle missing package gracefully
    try:
        from core.config import settings  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - final fallback
        from types import SimpleNamespace

        settings = SimpleNamespace(
            ALPHA_VANTAGE_API_KEY=os.getenv("ALPHA_VANTAGE_API_KEY"),
            ENABLE_REAL_DATA=True,  # Always use real data
        )

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
        # Determine whether to fetch real data or use mocked values
        self.use_mock = False  # Always use real data
        
        # SSL verification settings - can be disabled with DISABLE_SSL_VERIFY=true env var
        # For development environments with SSL certificate issues
        self.ssl_verify = os.getenv("DISABLE_SSL_VERIFY", "false").lower() != "true"
        if not self.ssl_verify:
            logger.warning("SSL certificate verification is disabled - this is not recommended for production!")

        # Use configured API key, falling back to the settings value if provided
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY") or getattr(
            settings, "ALPHA_VANTAGE_API_KEY", None
        )
        if not self.api_key and not self.use_mock:
            raise RuntimeError(
                "ALPHA_VANTAGE_API_KEY must be set for real-time data access"
            )
        self.base_url = "https://www.alphavantage.co/query"
        self.cache_ttl = int(os.getenv("CACHE_TTL_TRENDING_STOCKS", "300"))  # 5 minutes
        # Delay between API requests to respect Alpha Vantage rate limits.
        # Free API keys are limited to 5 requests per minute so the default
        # interval of ``12`` seconds keeps us under the threshold.  The delay
        # can be configured via ``ALPHA_VANTAGE_REQUEST_INTERVAL``.
        self.request_interval = float(os.getenv("ALPHA_VANTAGE_REQUEST_INTERVAL", "12"))
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        self.warning_cooldown = int(os.getenv("TRENDING_WARNING_COOLDOWN", "60"))
        self._last_failure_warning: Optional[datetime] = None

        # Log dependency status. Only require aiohttp when real data is enabled
        if not self.use_mock and not AIOHTTP_AVAILABLE:
            raise RuntimeError("aiohttp is required for real-time data access")

        # Placeholder list used until live data is fetched. When ``ENABLE_REAL_DATA``
        # is true we start with an empty list so that ``_fetch_yahoo_trending_symbols``
        # is called on the first request to populate this list.
        # Initialize with empty list to force real-time data fetching
        self.trending_symbols: List[str] = []

    def fetch_trending_symbols(self):
        """Fetch trending symbols using Alpha Vantage."""
        try:
            logger.info("Fetching trending symbols from Alpha Vantage...")
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": "AAPL",  # Example symbol, replace with dynamic logic if needed
                "interval": "1min",
                "apikey": self.api_key,
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract relevant data (example logic, adjust based on Alpha Vantage response structure)
            trending_symbols = []
            for symbol, details in data.get("Meta Data", {}).items():
                trending_symbols.append({
                    "symbol": symbol,
                    "name": details.get("2. Symbol"),
                    "price": details.get("4. Last Refreshed"),
                })

            logger.info(f"Fetched {len(trending_symbols)} trending symbols from Alpha Vantage.")
            return trending_symbols

        except Exception as e:
            logger.error(f"Failed to fetch trending symbols from Alpha Vantage: {e}")
            return []

    async def get_trending_stocks(
        self, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get trending stocks with pagination.

        Args:
            page: Page number for pagination
            limit: Number of items per page

        Returns:
            Dict containing stocks data and pagination info
        """
        try:
            cache_key = "trending_stocks"
            # Prefer Redis cache if available
            if redis_cache:
                cached = redis_cache.get(cache_key)
                if cached:
                    logger.info("Returning trending stocks from Redis cache")
                    cached_data = json.loads(cached)
                    return self._get_paginated_data(
                        cached_data.get("stocks", []), page, limit
                    )

            # Fallback to in-memory cache
            if self._is_cache_valid():
                logger.info("Returning trending stocks from cache")
                return self._get_paginated_data(self._cache["stocks"], page, limit)

            # Fetch fresh data
            logger.info("Fetching fresh trending stocks data")
            if not self.trending_symbols:
                self.trending_symbols = await self._fetch_yahoo_trending_symbols()
                if not self.trending_symbols:
                    logger.warning("Failed to fetch trending symbols from Yahoo Finance, using fallback symbols")
                    # Fallback to common stock symbols
                    self.trending_symbols = [
                        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
                        "META", "NVDA", "AMD", "NFLX", "JPM",
                        "DIS", "PYPL", "INTC", "CSCO", "KO"
                    ]

            stocks_data = await self._fetch_trending_stocks()

            # Update caches
            if redis_cache:
                try:
                    redis_cache.set(
                        cache_key,
                        json.dumps({"stocks": stocks_data}),
                        ttl_seconds=self.cache_ttl,
                    )
                except Exception as exc:  # pragma: no cover - logging only
                    logger.warning(f"Failed to set Redis cache: {exc}")
            else:
                self._update_cache(stocks_data)

            return self._get_paginated_data(stocks_data, page, limit)

        except Exception as e:
            logger.error(f"Error fetching trending stocks: {e}")
            raise

    async def _fetch_trending_stocks(self) -> List[Dict[str, Any]]:
        """Fetch trending stocks data from external API."""
        if not AIOHTTP_AVAILABLE:
            raise RuntimeError("aiohttp is required for real-time data access")
            
        # Check if SSL verification should be disabled
        ssl_verify = os.getenv("DISABLE_SSL_VERIFY", "false").lower() != "true"
        ssl_context = None
        if not ssl_verify:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            logger.warning("SSL certificate verification disabled - not recommended for production")
            
        stocks_data = []
        connector = aiohttp.TCPConnector(ssl=ssl_context) if not ssl_verify else None
        async with aiohttp.ClientSession(connector=connector) as session:
            # Fetch each symbol sequentially to respect API rate limits.
            for idx, symbol in enumerate(self.trending_symbols):
                result = await self._fetch_stock_quote(session, symbol)
                if result:
                    stocks_data.append(result)
                else:
                    logger.warning(f"Failed to fetch data for {symbol}")
                # Avoid hitting the free tier limit of 5 requests per minute
                # by sleeping between calls. Skip the delay after the last request.
                if (
                    idx < len(self.trending_symbols) - 1
                    and self.request_interval > 0
                ):
                    await asyncio.sleep(self.request_interval)
        
        if not stocks_data:
            logger.error("Failed to fetch any real stock data")
            raise RuntimeError("Unable to retrieve any stock data from live data source")

        return stocks_data

    async def _fetch_stock_quote(
        self, session, symbol: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single stock quote from Alpha Vantage."""
        if not AIOHTTP_AVAILABLE:
            # This should not be called if aiohttp is not available, but provide a safeguard
            logger.warning(
                f"Cannot fetch stock quote for {symbol} - aiohttp not available"
            )
            return None

        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.api_key}
        
        # Check if SSL verification should be disabled
        ssl_verify = os.getenv("DISABLE_SSL_VERIFY", "false").lower() != "true"
        ssl_context = None
        if not ssl_verify:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        try:
            async with session.get(
                self.base_url, params=params, timeout=10, ssl=ssl_context
            ) as response:

                if response.status == 200:
                    try:
                        text = await response.text()
                        data = json.loads(text)
                    except Exception as exc:
                        logger.error(
                            f"Error decoding response for {symbol}: {exc}; body: {text[:100]}"
                        )
                        return None
                    return self._parse_alpha_vantage_response(symbol, data)
                else:
                    logger.warning(
                        f"API request failed for {symbol}: status {response.status}"

                    )
                    return None

        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching data for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def _parse_alpha_vantage_response(
        self, symbol: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Parse Alpha Vantage API response into our format."""
        try:
            if "Note" in data:
                logger.warning(f"Alpha Vantage note for {symbol}: {data['Note']}")
                return None
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                return None

            quote = data.get("Global Quote", {})
            if not quote:
                logger.warning(f"No quote data returned for {symbol}: {data}")
                return None

            # Alpha Vantage field mappings
            price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            change_percent = float(quote.get("10. change percent", "0%").rstrip("%"))
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
                "ADBE": "Adobe Inc.",
            }

            return {
                "symbol": symbol,
                "name": company_names.get(symbol, f"{symbol} Corp."),
                "price": round(price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "last_updated": datetime.now().isoformat(),
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
        self._cache = {"stocks": stocks_data, "timestamp": datetime.now().isoformat()}
        self._cache_timestamp = datetime.now()
        logger.info(f"Cache updated with {len(stocks_data)} stocks")

    def _get_paginated_data(
        self, stocks_data: List[Dict[str, Any]], page: int, limit: int
    ) -> Dict[str, Any]:
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
                "has_prev": page > 1,
            },
            "metadata": {
                "last_updated": self._cache.get("timestamp")
                if self._cache
                else datetime.now().isoformat(),
                "cache_ttl_seconds": self.cache_ttl,
                "data_source": "real",
            },
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
            "last_updated": self._cache_timestamp.isoformat(),
        }

