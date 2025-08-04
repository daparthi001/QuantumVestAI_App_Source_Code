"""
WebSocket Router Implementation
Created: 2025-05-19 03:43:23
Author: daparthi001
"""
import logging
from datetime import datetime
from typing import Optional

from core.security import get_current_user
from core.middleware.cors import is_origin_allowed
from db.models.user import User
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

# Import the local websocket manager using a relative import to avoid package
# resolution issues when the application is executed as a module
# Import the local websocket manager using an absolute path so the module works
# both when the package is executed and when files are run directly.
from websocket.manager import ConnectionManager

logger = logging.getLogger("api")

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket, client_id: str, token: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time updates."""
    try:
        origin = websocket.headers.get("origin")
        if not is_origin_allowed(origin):
            if client_id == "market-data":
                if origin is None:
                    logger.info(
                        "Allowing market-data WebSocket connection without Origin header"
                    )
                else:
                    logger.info(
                        "Allowing market-data WebSocket connection with disallowed Origin: %s",
                        origin,
                    )
            else:
                logger.warning(
                    f"Rejected WebSocket connection from origin: {origin}"
                )
                await websocket.close(code=1008)
                return

        # Gather token from query params, cookies, or headers
        cookie_token = websocket.cookies.get("access_token")
        auth_header = websocket.headers.get("authorization")

        if not token:
            token = cookie_token
        if not token and auth_header:
            if auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
        if token and token.startswith("Bearer "):
            token = token.split(" ", 1)[1]

        # Require and verify token, except for public market data stream
        user = None
        if not token:
            if client_id == "market-data":
                logger.info("Allowing anonymous WebSocket connection for market-data")
            else:
                await websocket.close(code=4001, reason="Token required")
                return
        if token:
            try:
                user = await get_current_user(token=token)
            except Exception:
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
                    await websocket.send_json(
                        {
                            "error": "Unknown message type",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

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
        payload = data.get("data", data)
        topic = payload.get("type") or payload.get("symbol") or payload.get("topic")
        if not topic:
            await websocket.send_json(
                {
                    "error": "Missing topic in subscription request",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return

        await manager.subscribe(websocket, topic)
        await websocket.send_json(
            {
                "type": "subscribed",
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        await websocket.send_json(
            {"error": "Subscription failed", "timestamp": datetime.utcnow().isoformat()}
        )


async def handle_unsubscription(websocket: WebSocket, data: dict, user: Optional[User]):
    """Handle unsubscription requests"""
    try:
        payload = data.get("data", data)
        topic = payload.get("type") or payload.get("symbol") or payload.get("topic")
        if not topic:
            await websocket.send_json(
                {
                    "error": "Missing topic in unsubscription request",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return

        await manager.unsubscribe(websocket, topic)
        await websocket.send_json(
            {
                "type": "unsubscribed",
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Unsubscription error: {str(e)}")
        await websocket.send_json(
            {
                "error": "Unsubscription failed",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
