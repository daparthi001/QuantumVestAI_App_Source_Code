import os
import sys
from fastapi.testclient import TestClient

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.main import app


def test_settings_endpoint():
    client = TestClient(app)
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

