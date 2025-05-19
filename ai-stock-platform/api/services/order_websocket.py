"""
Order WebSocket Service
Created: 2025-05-19 04:49:34
Author: daparthi001
"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
from api.models.orders import Order, OrderStatus
from api.utils.websocket_manager import WebSocketManager

class OrderWebSocketService:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.ws_manager = WebSocketManager()

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Connect a user to the WebSocket
        """
        await self.ws_manager.connect(websocket)
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Disconnect a user from the WebSocket
        """
        await self.ws_manager.disconnect(websocket)
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_order_update(self, user_id: str, order: Order):
        """
        Broadcast order updates to connected clients
        """
        if user_id in self.active_connections:
            message = {
                'type': 'order_update',
                'data': {
                    'order_id': order.id,
                    'symbol': order.symbol,
                    'status': order.status,
                    'executed_quantity': order.executed_quantity,
                    'executed_price': order.executed_price,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            await self._send_to_user(user_id, message)

    async def broadcast_execution_report(self, user_id: str, execution: Dict):
        """
        Broadcast execution reports to connected clients
        """
        if user_id in self.active_connections:
            message = {
                'type': 'execution_report',
                'data': {
                    'order_id': execution['order_id'],
                    'symbol': execution['symbol'],
                    'executed_quantity': execution['quantity'],
                    'executed_price': execution['price'],
                    'timestamp': execution['timestamp']
                }
            }
            
            await self._send_to_user(user_id, message)

    async def broadcast_order_book_update(self, symbol: str, order_book: Dict):
        """
        Broadcast order book updates to all connected clients
        """
        message = {
            'type': 'order_book_update',
            'symbol': symbol,
            'data': order_book,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.ws_manager.broadcast(message)

    async def _send_to_user(self, user_id: str, message: Dict):
        """
        Send message to all connections of a specific user
        """
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Error sending message to websocket: {e}")
                    await self.disconnect(websocket, user_id)

    async def start_heartbeat(self):
        """
        Start heartbeat to keep connections alive
        """
        while True:
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            heartbeat = {
                'type': 'heartbeat',
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.ws_manager.broadcast(heartbeat)