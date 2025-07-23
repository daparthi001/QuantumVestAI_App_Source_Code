"""Asynchronous agent for fetching JSON data from external sources."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

import aiohttp


@dataclass
class DataFetchAgent:
    """Fetch data from a configured URL."""

    name: str
    source_url: str

    async def fetch(self, params: Optional[Dict[str, Any]] = None) -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.source_url, params=params, timeout=10) as resp:
                resp.raise_for_status()
                return await resp.json()
