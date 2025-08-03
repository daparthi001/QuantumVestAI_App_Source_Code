import os
import sys

import pandas as pd
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ai_analysis.prophet_service import ProphetService, ForecastPoint
from ai_analysis.sentiment_service import SentimentService
from api.main import app


def test_sentiment_service_classifies_trend():
    svc = SentimentService()
    up = pd.DataFrame({"ds": pd.date_range("2024-01-01", periods=3), "y": [1, 2, 3]})
    down = pd.DataFrame({"ds": pd.date_range("2024-01-01", periods=3), "y": [3, 2, 1]})
    flat = pd.DataFrame({"ds": pd.date_range("2024-01-01", periods=3), "y": [1, 1.005, 1.002]})
    assert svc.analyze(up) == "Bullish"
    assert svc.analyze(down) == "Bearish"
    assert svc.analyze(flat) == "Neutral"


def test_prophet_service_forecast(monkeypatch):
    service = ProphetService()

    sample = {
        "Time Series (Daily)": {
            "2024-01-03": {"4. close": "3"},
            "2024-01-02": {"4. close": "2"},
            "2024-01-01": {"4. close": "1"},
        }
    }

    class DummyResp:
        def raise_for_status(self):
            pass

        def json(self):
            return sample

    def fake_get(url, params=None, timeout=10):
        return DummyResp()

    import ai_analysis.prophet_service as ps

    monkeypatch.setattr(ps.requests, "get", fake_get)

    history = service.fetch_historical_data("TEST")
    assert len(history) == 3

    forecast = service.forecast(history, days=7)
    assert len(forecast) == 7
    assert all(fp.yhat == 3 for fp in forecast)


def test_ai_analyze_endpoint(monkeypatch):
    df = pd.DataFrame({"ds": pd.date_range("2024-01-01", periods=2), "y": [1, 2]})

    def fake_fetch(self, symbol):
        return df

    def fake_forecast(self, history, days=7):
        return [ForecastPoint(pd.Timestamp("2024-01-03"), 2.0)]

    monkeypatch.setattr(
        "ai_analysis.prophet_service.ProphetService.fetch_historical_data",
        fake_fetch,
    )
    monkeypatch.setattr(
        "ai_analysis.prophet_service.ProphetService.forecast",
        fake_forecast,
    )

    client = TestClient(app)
    resp = client.get("/api/ai/analyze", params={"symbol": "XYZ"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["data"]["sentiment"] == "Bullish"
    assert payload["data"]["forecast"][0]["yhat"] == 2.0
