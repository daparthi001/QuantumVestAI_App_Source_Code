"""Tests for market-data WebSocket origin handling."""
import os
import sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

pytest.importorskip("httpx")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.websocket import router as websocket_router


def test_market_data_websocket_allows_disallowed_origin(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    app = FastAPI()
    app.include_router(websocket_router)
    client = TestClient(app)
    headers = {"origin": "https://evil.com"}
    with client.websocket_connect("/ws/market-data", headers=headers) as ws:
        ws.send_json({"type": "subscribe", "data": {"symbol": "AAPL"}})
        resp = ws.receive_json()
        assert resp["type"] == "subscribed"
        assert resp["topic"] == "AAPL"
