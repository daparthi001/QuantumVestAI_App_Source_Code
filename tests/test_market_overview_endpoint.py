import os
import sys
from fastapi.testclient import TestClient

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.main import app


def test_market_overview_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/analytics/market-overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "indices" in data["data"]


def test_top_movers_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/analytics/top-movers")
    assert resp.status_code == 200
    payload = resp.json()
    assert "data" in payload
    assert "gainers" in payload["data"]
    assert "losers" in payload["data"]
