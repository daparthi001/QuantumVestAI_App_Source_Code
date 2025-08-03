import pandas as pd


class SentimentService:
    """Determine simple trend sentiment from price history."""

    def analyze(self, history: pd.DataFrame) -> str:
        if history.empty:
            return "Neutral"
        start = history["y"].iloc[0]
        end = history["y"].iloc[-1]
        change = (end - start) / start if start else 0
        if change > 0.01:
            return "Bullish"
        if change < -0.01:
            return "Bearish"
        return "Neutral"
