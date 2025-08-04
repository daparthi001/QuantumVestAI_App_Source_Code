"""Yahoo Finance price service using RapidAPI with caching."""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class YahooRapidAPIService:
    """Fetch live price data from Yahoo Finance via RapidAPI."""

    _cache: dict[str, tuple[float, Dict[str, float]]] = {}
    _cache_ttl = 60.0  # seconds - increased to respect API rate limits
    _last_request_time = 0.0  # track last request time
    _request_delay = 0.5  # minimum seconds between requests

    @classmethod
    def get_live_price(cls, symbol: str, region: str = "US") -> Optional[Dict[str, float]]:
        """Return price, change, and percent change for ``symbol``.

        The result is cached for ``_cache_ttl`` seconds to avoid hitting rate
        limits during high-frequency requests.  If the ``RAPIDAPI_KEY``
        environment variable is missing the function returns ``None`` without
        making a network request.
        """
        host = os.getenv("RAPIDAPI_HOST", "apidojo-yahoo-finance-v1.p.rapidapi.com")
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            logger.error("RAPIDAPI_KEY not configured - cannot fetch data")
            raise ValueError("RAPIDAPI_KEY environment variable must be set")

        key = symbol.upper()
        now = time.time()
        cached = cls._cache.get(key)
        if cached and now - cached[0] < cls._cache_ttl:
            return cached[1]
            
        # Respect rate limits
        time_since_last = now - cls._last_request_time
        if time_since_last < cls._request_delay:
            time.sleep(cls._request_delay - time_since_last)
        
        cls._last_request_time = time.time()

        url = f"https://{host}/market/v2/get-quotes"
        headers = {"x-rapidapi-host": host, "x-rapidapi-key": api_key}
        params = {"symbols": symbol, "region": region}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            normalized = cls._normalize_quote(resp.json())
            if normalized is not None:
                cls._cache[key] = (now, normalized)
            return normalized
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Failed to fetch live price: %s", exc)
            return None

    @staticmethod
    def _normalize_quote(data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Extract price fields from the raw API response."""
        try:
            quote = data["quoteResponse"]["result"][0]
            return {
                "price": float(quote["regularMarketPrice"]),
                "change": float(quote["regularMarketChange"]),
                "percent_change": float(quote["regularMarketChangePercent"]),
            }
        except Exception:  # pragma: no cover - unexpected format
            return None


__all__ = ["YahooRapidAPIService"]
