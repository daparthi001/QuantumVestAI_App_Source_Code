import os
import sys
from fastapi.testclient import TestClient

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.main import app
from core.security import create_access_token


def test_token_verify_endpoint_success():
    client = TestClient(app)
    token = create_access_token({"sub": "tester"})
    resp = client.post("/api/v1/auth/verify", json={"token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["valid"] is True
    assert data["data"]["user"]["username"] == "tester"
