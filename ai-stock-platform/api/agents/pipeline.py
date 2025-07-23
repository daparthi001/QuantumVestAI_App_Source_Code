"""Manager for coordinating data fetching and analysis agents."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, List

from .data_fetch_agent import DataFetchAgent
from .analysis_agent import DataAnalysisAgent


@dataclass
class DataPipelineManager:
    """Run multiple fetch and analysis agents as a pipeline."""

    fetch_agents: List[DataFetchAgent] = field(default_factory=list)
    analysis_agents: List[DataAnalysisAgent] = field(default_factory=list)

    def add_fetch_agent(self, agent: DataFetchAgent) -> None:
        self.fetch_agents.append(agent)

    def add_analysis_agent(self, agent: DataAnalysisAgent) -> None:
        self.analysis_agents.append(agent)

    async def run(self) -> List[Any]:
        """Fetch data and run analyses concurrently."""
        fetch_tasks = [agent.fetch() for agent in self.fetch_agents]
        fetched = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        results: List[Any] = []
        for data in fetched:
            if isinstance(data, Exception):
                continue
            analysis_tasks = [agent.analyze(data) for agent in self.analysis_agents]
            analysed = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            results.extend(r for r in analysed if not isinstance(r, Exception))
        return results
