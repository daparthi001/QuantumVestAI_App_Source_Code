"""Yahoo Finance RapidAPI Service.

Provides access to Yahoo Finance data via RapidAPI using environment variables.
"""
import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class YahooRapidAPIService:
    """Fetch data from Yahoo Finance through RapidAPI."""

    @classmethod
    def get_timeseries(cls, symbol: str, region: str = "US") -> Optional[Dict[str, Any]]:
        """Return timeseries data for a symbol.

        If the RAPIDAPI_KEY environment variable is not set the method
        returns ``None`` without making a network request.
        """
        host = os.getenv("RAPIDAPI_HOST", "apidojo-yahoo-finance-v1.p.rapidapi.com")
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            logger.warning("RAPIDAPI_KEY not configured")
            return None

        url = f"https://{host}/stock/v2/get-timeseries"
        headers = {"x-rapidapi-host": host, "x-rapidapi-key": api_key}
        params = {"symbol": symbol, "region": region}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Failed to fetch timeseries: %s", exc)
            return None

