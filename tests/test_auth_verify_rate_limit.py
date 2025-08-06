import os
import sys
from fastapi.testclient import TestClient

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.main import app
from core.security import create_access_token


def test_verify_endpoint_not_rate_limited():
    client = TestClient(app)
    token = create_access_token({"sub": "tester"})
    for _ in range(15):
        resp = client.post("/api/v1/auth/verify", json={"token": token})
        assert resp.status_code == 200
        assert resp.json()["data"]["valid"] is True
