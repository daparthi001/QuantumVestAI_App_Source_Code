"""
WebSocket Connection Manager
Created: 2025-05-19 04:08:26
Author: daparthi001
"""
from fastapi import WebSocket
from typing import Dict, Set, Any
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.symbol_subscribers: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        logger.info(f"Client {client_id} connected. Active connections: {len(self.active_connections)}")
        
    async def disconnect(self, websocket: WebSocket, client_id: str):
        # Remove from active connections
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        
        # Remove from all symbol subscriptions
        for subscribers in self.symbol_subscribers.values():
            subscribers.discard(websocket)
        
        logger.info(f"Client {client_id} disconnected. Active connections: {len(self.active_connections)}")
        
    async def subscribe(self, websocket: WebSocket, symbol: str):
        if symbol not in self.symbol_subscribers:
            self.symbol_subscribers[symbol] = set()
        self.symbol_subscribers[symbol].add(websocket)
        logger.info(f"Subscription added for {symbol}. Total subscribers: {len(self.symbol_subscribers[symbol])}")
        
    async def unsubscribe(self, websocket: WebSocket, symbol: str):
        if symbol in self.symbol_subscribers:
            self.symbol_subscribers[symbol].discard(websocket)
            if not self.symbol_subscribers[symbol]:
                del self.symbol_subscribers[symbol]
            logger.info(f"Subscription removed for {symbol}")
            
    async def broadcast_stock_update(self, symbol: str, data: dict):
        if symbol in self.symbol_subscribers:
            message = {
                "type": "price_update",
                "data": {
                    "symbol": symbol,
                    "timestamp": datetime.utcnow().isoformat(),
                    **data
                }
            }

            for websocket in self.symbol_subscribers[symbol].copy():
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to client: {e}")
                    await self.handle_disconnection(websocket)

    async def broadcast_event(self, event_type: str, data: Any):
        if event_type in self.symbol_subscribers:
            message = {
                "type": event_type,
                "data": data,
            }

            for websocket in self.symbol_subscribers[event_type].copy():
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to client: {e}")
                    await self.handle_disconnection(websocket)
                    
    async def handle_disconnection(self, websocket: WebSocket):
        # Clean up disconnected websocket
        for client_id, connections in self.active_connections.copy().items():
            if websocket in connections:                await self.disconnect(websocket, client_id)
                break