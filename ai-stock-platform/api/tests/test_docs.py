import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

import pytest
pytest.importorskip("httpx")

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_readme():
    resp = client.get("/docs/readme")
    assert resp.status_code == 200
    assert "QuantumVestAI" in resp.text


def test_get_uses():
    resp = client.get("/docs/uses")
    assert resp.status_code == 200
    assert "Usage" in resp.text or "usage" in resp.text.lower()
