import os
import sys
from fastapi.testclient import TestClient

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.main import app


def test_pre_market_prediction_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/predictions/pre-market/TEST")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "success"
    assert "predicted_open" in payload["data"]
