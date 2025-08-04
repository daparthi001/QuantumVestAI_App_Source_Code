"""
WebSocket Router Implementation
Created: 2025-05-19 03:43:23
Author: daparthi001
"""
import logging
from datetime import datetime
from typing import Optional

from core.security import get_current_user, validate_token
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


@router.websocket("/ws/market-data")
async def market_data_ws(websocket: WebSocket, token: Optional[str] = Query(None)):
    # For market-data endpoint, we'll allow connections even without a token
    # This ensures backward compatibility with clients that don't send tokens
    
    # First, try to get token from query params if not provided directly
    if not token:
        query_params = dict(websocket.query_params)
        token = query_params.get("token")
    
    # Try to clean the token if present
    if token:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
            
        # Try validation but don't reject connection on failure
        try:
            validate_token(token)
            logger.info(f"Valid token provided for market-data WebSocket")
        except Exception as e:
            logger.warning(f"Invalid token for market-data WebSocket: {str(e)}")
            # We continue anyway for market-data
    else:
        logger.info("No token provided for market-data WebSocket")
        
    await websocket_endpoint(websocket, "market-data", token)


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket, client_id: str, token: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time updates."""
    try:
        # Log connection attempt with client ID
        logger.info(f"WebSocket connection attempt for client_id: {client_id}")
        
        # Check origin for CORS security
        origin = websocket.headers.get("origin")
        if not is_origin_allowed(origin):
            # Special handling for market-data endpoint
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
        qvai_token = websocket.cookies.get("qvai_token")  # Also check for qvai_token
        auth_header = websocket.headers.get("authorization")

        if not token:
            token = qvai_token or cookie_token  # Try qvai_token first, then access_token
        if not token and auth_header:
            if auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
        if token and token.startswith("Bearer "):
            token = token.split(" ", 1)[1]
            logger.info(f"Cleaned Bearer prefix from token for {client_id}")

        # Debug logging for token presence
        if token:
            logger.info(f"Token provided for WebSocket connection: {client_id[:10]}...")
        else:
            logger.warning(f"No token provided for WebSocket connection: {client_id}")
            
        # Require and verify token, except for public market data stream
        user = None
        # --- Begin: Extract token from cookie if not present in query param ---
        if not token:
            cookie_header = websocket.headers.get("cookie")
            if cookie_header:
                import re

                # First try to get qvai_token (new standard)
                match = re.search(r"qvai_token=([^;]+)", cookie_header)
                if match:
                    cookie_token = match.group(1)
                    # Remove 'Bearer ' prefix if present
                    if cookie_token.startswith("Bearer "):
                        cookie_token = cookie_token[len("Bearer ") :]
                    token = cookie_token
                    logger.info(f"Found token in qvai_token cookie")
                else:
                    # Fall back to access_token
                    match = re.search(r"access_token=([^;]+)", cookie_header)
                    if match:
                        cookie_token = match.group(1)
                        # Remove 'Bearer ' prefix if present
                        if cookie_token.startswith("Bearer "):
                            cookie_token = cookie_token[len("Bearer ") :]
                        token = cookie_token
                        logger.info(f"Found token in access_token cookie")
        # --- End: Extract token from cookie ---
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
