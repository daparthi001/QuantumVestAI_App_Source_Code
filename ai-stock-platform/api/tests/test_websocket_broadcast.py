"""Tests for WebSocket broadcasting via ConnectionManager."""
import asyncio
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))
import pytest
pytest.importorskip("httpx")

from fastapi.testclient import TestClient
from api.main import app, ws_manager


def test_websocket_broadcasts_updates():
    client = TestClient(app)
    with client.websocket_connect("/ws/test-client") as ws:
        ws.send_json({"type": "subscribe", "data": {"symbol": "AAPL"}})
        resp = ws.receive_json()
        assert resp["type"] == "subscribed"
        assert resp["topic"] == "AAPL"

        asyncio.get_event_loop().run_until_complete(
            ws_manager.broadcast_stock_update("AAPL", {"price": 123.45})
        )
        update = ws.receive_json()
        assert update["type"] == "price_update"
        assert update["data"]["symbol"] == "AAPL"
        assert update["data"]["price"] == 123.45

        asyncio.get_event_loop().run_until_complete(
            ws_manager.broadcast_event("top_movers", [{"symbol": "AAPL"}])
        )
        event = ws.receive_json()
        assert event["type"] == "top_movers"
        assert event["data"][0]["symbol"] == "AAPL"
