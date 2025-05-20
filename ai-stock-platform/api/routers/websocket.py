"""
WebSocket Router Implementation
Created: 2025-05-19 03:43:23
Author: daparthi001
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set, Optional
import logging
import json
from datetime import datetime

from core.security import get_current_user
from api.db.models.user import User
from api.services.stock_service import StockService
from core.config import settings

logger = logging.getLogger("api")

router = APIRouter()

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
    
    async def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
    
    async def broadcast(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {str(e)}")

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: Optional[str] = None
):
    """WebSocket endpoint for real-time updates"""
    try:
        # Verify token if provided
        user = None
        if token:
            try:
                user = await get_current_user(token)
            except Exception as e:
                await websocket.close(code=4001, reason="Invalid token")
                return
        
        # Connect to WebSocket
        await manager.connect(websocket, client_id)
        logger.info(f"WebSocket connected: {client_id}")
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_json()
                
                # Add metadata
                data["timestamp"] = datetime.utcnow().isoformat()
                data["client_id"] = client_id
                if user:
                    data["user_id"] = user.id
                
                # Process message based on type
                message_type = data.get("type")
                if message_type == "subscribe":
                    # Handle subscription
                    await handle_subscription(websocket, data, user)
                elif message_type == "unsubscribe":
                    # Handle unsubscription
                    await handle_unsubscription(websocket, data, user)
                else:
                    # Handle unknown message type
                    await websocket.send_json({
                        "error": "Unknown message type",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        except WebSocketDisconnect:
            await manager.disconnect(websocket, client_id)
            logger.info(f"WebSocket disconnected: {client_id}")
        
        except Exception as e:
            logger.error(f"WebSocket error for {client_id}: {str(e)}")
            await websocket.close(code=4000, reason="Internal server error")
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        try:
            await websocket.close(code=4000, reason="Connection error")
        except:
            pass

async def handle_subscription(websocket: WebSocket, data: dict, user: Optional[User]):
    """Handle subscription requests"""
    try:
        # Validate subscription request
        if "topic" not in data:
            await websocket.send_json({
                "error": "Missing topic in subscription request",
                "timestamp": datetime.utcnow().isoformat()
            })
            return
        
        # Add subscription logic here
        # Example: Subscribe to stock updates
        topic = data["topic"]
        await websocket.send_json({
            "type": "subscribed",
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        await websocket.send_json({
            "error": "Subscription failed",
            "timestamp": datetime.utcnow().isoformat()
        })

async def handle_unsubscription(websocket: WebSocket, data: dict, user: Optional[User]):
    """Handle unsubscription requests"""
    try:
        # Validate unsubscription request
        if "topic" not in data:
            await websocket.send_json({
                "error": "Missing topic in unsubscription request",
                "timestamp": datetime.utcnow().isoformat()
            })
            return
        
        # Add unsubscription logic here
        topic = data["topic"]
        await websocket.send_json({
            "type": "unsubscribed",
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Unsubscription error: {str(e)}")
        await websocket.send_json({
            "error": "Unsubscription failed",
            "timestamp": datetime.utcnow().isoformat()
        })