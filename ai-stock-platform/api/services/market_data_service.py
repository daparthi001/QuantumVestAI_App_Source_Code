"""Market data service that returns live quotes for free users."""

from __future__ import annotations

import asyncio
from typing import Dict, Optional

from services.yahoo_rapidapi_service import YahooRapidAPIService


class MarketDataService:
    """Provide access to live market quotes.

    The previous implementation returned hard coded values which meant free tier
    users never received real data.  This version fetches prices from Yahoo
    Finance via ``YahooRapidAPIService``.  If the RapidAPI key is not configured
    or the request fails the method returns ``None`` instead of raising an
    exception so that callers can handle the failure gracefully.
    """

    async def get_quote(self, symbol: str) -> Optional[Dict[str, float]]:
        """Return a live market quote for ``symbol``.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            Dictionary containing price information or ``None`` if unavailable.
        """

        try:
            # ``YahooRapidAPIService`` is synchronous; run it in a thread so the
            # async interface remains non-blocking.
            data = await asyncio.to_thread(
                YahooRapidAPIService.get_live_price, symbol
            )
        except Exception:
            return None

        if not data:
            return None

        price = data.get("price")
        return {
            "symbol": symbol.upper(),
            # Yahoo endpoint provides a single price; use it for bid/ask/last to
            # maintain backwards compatibility with previous callers.
            "bid": price,
            "ask": price,
            "last": price,
            "change": data.get("change"),
            "percent_change": data.get("percent_change"),
        }
