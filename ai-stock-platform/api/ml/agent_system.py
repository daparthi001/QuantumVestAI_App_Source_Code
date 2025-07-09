from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

import pandas as pd
import asyncio

@dataclass
class AIAgent:
    """Simple prediction agent wrapping a model function."""

    name: str
    model_fn: Callable[[str, pd.DataFrame, int], pd.DataFrame]

    async def predict(
        self, ticker: str, historical_data: pd.DataFrame, days_ahead: int = 5
    ) -> pd.DataFrame:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.model_fn, ticker, historical_data, days_ahead
        )


class AgentManager:
    """Manage multiple :class:`AIAgent` instances and run them concurrently."""

    def __init__(self) -> None:
        self.agents: List[AIAgent] = []

    def register(self, agent: AIAgent) -> None:
        self.agents.append(agent)

    async def run_predictions(
        self, ticker: str, historical_data: pd.DataFrame, days_ahead: int = 5
    ) -> List[pd.DataFrame]:
        tasks = [
            asyncio.create_task(agent.predict(ticker, historical_data, days_ahead))
            for agent in self.agents
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
