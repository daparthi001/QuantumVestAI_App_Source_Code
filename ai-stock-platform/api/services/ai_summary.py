"""Generate plain English explanations of market movements.

The real application uses a GPT model to craft natural language summaries.
To keep the test suite lightweight this module simply formats a short message
based on the provided sentiment and forecast data.  The interface mirrors what
would be expected from an actual GPT powered service so higher level modules
can rely on it without modification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class SummaryInput:
    symbol: str
    sentiment: Dict[str, Any]
    forecast: Dict[str, Any]


class AISummaryService:
    """Create human friendly summaries for stock movements."""

    def generate(self, data: SummaryInput) -> str:
        """Return a brief summary for the supplied ``data``."""

        sentiment = data.sentiment.get("label", "unknown")
        price = data.forecast.get("yhat") or data.forecast.get("prediction")
        if price is None:
            price_part = "an unknown price"
        else:
            price_part = f"around {price:.2f}"
        return (
            f"{data.symbol} shows {sentiment} sentiment with a price forecast "
            f"of {price_part}."
        )
