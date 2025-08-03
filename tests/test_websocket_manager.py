import pytest

from api.websocket.manager import ConnectionManager


class DummyWebSocket:
    def __init__(self):
        self.accepted = False
        self.messages = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, message):
        self.messages.append(message)


@pytest.mark.asyncio
async def test_connection_manager_flow():
    manager = ConnectionManager()
    ws = DummyWebSocket()

    await manager.connect(ws, "client1")
    assert ws.accepted
    assert "client1" in manager.active_connections

    await manager.subscribe(ws, "AAPL")
    assert ws in manager.symbol_subscribers["AAPL"]

    await manager.broadcast_stock_update("AAPL", {"price": 10})
    assert ws.messages[0]["data"]["price"] == 10

    await manager.unsubscribe(ws, "AAPL")
    assert "AAPL" not in manager.symbol_subscribers

    await manager.disconnect(ws, "client1")
    assert manager.active_connections == {}
