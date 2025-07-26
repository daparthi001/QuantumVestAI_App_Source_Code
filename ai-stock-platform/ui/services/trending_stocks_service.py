"""Async wrapper around the API trending stocks endpoint."""

import asyncio
import logging
from typing import Any, Dict, Optional

from .api_client import APIClient

logger = logging.getLogger(__name__)

class TrendingStocksService:
    """Fetch trending stocks by calling the backend API."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.client = APIClient(token=token)

    async def get_trending_stocks(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Return trending stocks data from the API."""

        def _fetch() -> Dict[str, Any]:
            return self.client.get("/stocks/trending", params={"page": page, "limit": limit})

        try:
            return await asyncio.to_thread(_fetch)
        except Exception as exc:  # pragma: no cover - network errors
            logger.warning("Failed to fetch trending stocks: %s", exc)
            return {"stocks": [], "pagination": None}

__all__ = ["TrendingStocksService"]
