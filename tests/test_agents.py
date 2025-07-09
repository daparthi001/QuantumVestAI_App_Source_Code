import os
import sys
import asyncio
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.ml.agent_system import AIAgent, AgentManager


def test_agent_manager_async_predictions():
    dates = pd.date_range(end="2024-01-10", periods=10)
    df = pd.DataFrame({"adjusted_close": range(10)}, index=dates)

    def model_one(ticker, hist, days_ahead):
        future = pd.date_range(start=hist.index[-1], periods=days_ahead + 1)[1:]
        return pd.DataFrame({"date": future, "predicted_close": [1] * days_ahead}).set_index("date")

    def model_two(ticker, hist, days_ahead):
        future = pd.date_range(start=hist.index[-1], periods=days_ahead + 1)[1:]
        return pd.DataFrame({"date": future, "predicted_close": [2] * days_ahead}).set_index("date")

    manager = AgentManager()
    manager.register(AIAgent("one", model_one))
    manager.register(AIAgent("two", model_two))

    results = asyncio.run(manager.run_predictions("TEST", df, days_ahead=2))
    assert len(results) == 2
    assert list(results[0]["predicted_close"]) == [1, 1]
    assert list(results[1]["predicted_close"]) == [2, 2]
