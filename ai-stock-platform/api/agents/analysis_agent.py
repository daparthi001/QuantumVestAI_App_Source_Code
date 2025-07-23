"""Agent that performs analysis on fetched data."""

import asyncio
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class DataAnalysisAgent:
    """Run a synchronous analysis function in the background."""

    name: str
    analysis_fn: Callable[[Any], Any]

    async def analyze(self, data: Any) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analysis_fn, data)
