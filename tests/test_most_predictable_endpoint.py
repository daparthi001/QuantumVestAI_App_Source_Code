import os
import sys
from fastapi.testclient import TestClient

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.main import app


def test_most_predictable_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/stocks/most-predictable")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "success"
    assert isinstance(payload.get("data"), list)
    assert payload["data"]
