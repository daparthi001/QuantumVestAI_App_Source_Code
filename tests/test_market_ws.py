import os
import sys
import types
import asyncio

from fastapi.testclient import TestClient

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.main import app, ws_manager  # type: ignore
from api.websocket.market_ws import MarketWebSocket  # type: ignore


def test_market_ws_broadcasts_full_payload():
    client = TestClient(app)

    # Fake data provider
    fake_client = types.SimpleNamespace(
        fetch=lambda symbol: {
            "price": 123.0,
            "forecast": 125.0,
            "sentiment": "bullish",
        }
    )

    service = MarketWebSocket(ws_manager, client=fake_client)

    with client.websocket_connect("/ws/market-data") as ws:
        ws.send_json({"type": "subscribe", "data": {"symbol": "AAPL"}})
        resp = ws.receive_json()
        assert resp["type"] == "subscribed"

        asyncio.get_event_loop().run_until_complete(
            service.stream("AAPL", interval_range=(0, 0), iterations=1)
        )

        update = ws.receive_json()
        assert update["type"] == "price_update"
        payload = update["data"]
        assert payload["symbol"] == "AAPL"
        assert payload["price"] == 123.0
        assert payload["forecast"] == 125.0
        assert payload["sentiment"] == "bullish"
