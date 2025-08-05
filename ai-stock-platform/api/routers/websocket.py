"""
WebSocket Router Implementation
Created: 2025-05-19 03:43:23
Author: daparthi001
"""
import logging
import urllib.parse
from datetime import datetime
from typing import Optional

from core.security import validate_token
from core.security.websocket_permissions import check_websocket_permissions
from core.middleware.cors import is_origin_allowed
from core.config import settings
from db.models.user import User
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt

# Import the local websocket manager using an absolute path so the module works
# both when the package is executed and when files are run directly.
from websocket.manager import ConnectionManager

logger = logging.getLogger("api")

router = APIRouter()

manager = ConnectionManager()


def _clean_token(token: Optional[str]) -> Optional[str]:
    """Normalize a JWT by URL decoding and stripping any Bearer prefix."""
    if not token:
        return None
    token = urllib.parse.unquote(token)
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    return token


@router.websocket("/ws/market-data")
async def market_data_ws(
    websocket: WebSocket, token: Optional[str] = Query(None), premium: Optional[str] = Query(None)
):
    """WebSocket endpoint for market data with /ws/ prefix.

    This implementation delegates to the generic :func:`websocket_endpoint`
    so that the same subscription and broadcasting logic is reused for market
    data clients.  Previously this function attempted to proxy connections to a
    separate Kubernetes service which caused failures when that service was not
    reachable (such as during tests).  By reusing the local endpoint we ensure
    consistent behaviour and allow tests to operate without external
    dependencies.
    """
    logger.info("WebSocket connection attempt to /ws/market-data")
    await websocket_endpoint(websocket, "market-data", token)
    
    # try:
    #     # Extract token from various sources
    #     if not token:
    #         # Try query params
    #         query_params = dict(websocket.query_params)
    #         token = query_params.get("token")
            
    #         # Try cookies
    #         if not token:
    #             cookie_header = websocket.headers.get("cookie")
    #             if cookie_header:
    #                 import re
    #                 # Try qvai_token (new standard)
    #                 match = re.search(r"qvai_token=([^;]+)", cookie_header)
    #                 if match:
    #                     token = match.group(1)
    #                     logger.info("Found token in qvai_token cookie")
    #                 else:
    #                     # Fall back to access_token
    #                     match = re.search(r"access_token=([^;]+)", cookie_header)
    #                     if match:
    #                         token = match.group(1)
    #                         logger.info("Found token in access_token cookie")
            
    #         # Try authorization header
    #         if not token:
    #             auth_header = websocket.headers.get("authorization")
    #             if auth_header and auth_header.lower().startswith("bearer "):
    #                 token = auth_header.split(" ", 1)[1]
    #                 logger.info("Found token in authorization header")
        
    #     # Clean token if present
    #     if token and token.startswith('Bearer '):
    #         token = token[7:]
        
    #     # URL decode the token if necessary
    #     if token and '%' in token:
    #         token = urllib.parse.unquote(token)
        
    #     # Try to validate token but continue regardless
    #     user_id = "anonymous"
    #     if token:
    #         try:
    #             is_valid = validate_token(token)
    #             logger.info(f"Market data token validation: {is_valid}")
                
    #             # Extract user ID if possible
    #             try:
    #                 payload = jwt.decode(
    #                     token,
    #                     settings.JWT_SECRET.get_secret_value(),
    #                     algorithms=[settings.JWT_ALGORITHM]
    #                 )
    #                 user_id = payload.get("sub", "anonymous")
                    
    #                 # Ensure free-tier users and anonymous connections are handled correctly
    #                 if user_id == "anonymous" or payload.get("role", "free") == "free":
    #                     logger.info("Granting unrestricted access for free-tier or anonymous user")
    #                     return
                    
    #                 # Use the permissions system to check access
    #                 premium_param = premium or websocket.query_params.get("premium")
    #                 if not check_websocket_permissions(payload, "/ws/market-data", premium_param):
    #                     logger.warning(f"WebSocket permission denied for user: {user_id}")
    #                     await websocket.close(code=4003, reason="Permission denied")
    #                     return
    #                 logger.info(f"WebSocket permission granted for user: {user_id}")
                    
    #             except Exception as e:
    #                 logger.warning(f"Error checking permissions: {str(e)}")
    #         except Exception as e:
    #             logger.warning(f"Token validation error: {str(e)}")
        
    #     # Connect to manager
    #     client_id = f"market-data:{user_id}"
    #     await manager.connect(websocket, client_id)
    #     logger.info(f"WebSocket connected: {client_id}")
        
    #     # Handle messages
    #     try:
    #         while True:
    #             data = await websocket.receive_json()
                
    #             # Add metadata
    #             data["timestamp"] = datetime.utcnow().isoformat()
    #             data["client_id"] = client_id
                
    #             # Process message based on type
    #             message_type = data.get("type")
    #             if message_type == "subscribe":
    #                 await handle_subscription(websocket, data, None)
    #             elif message_type == "unsubscribe":
    #                 await handle_unsubscription(websocket, data, None)
    #             else:
    #                 await websocket.send_json(
    #                     {
    #                         "error": "Unknown message type",
    #                         "timestamp": datetime.utcnow().isoformat(),
    #                     }
    #                 )
        
    #     except WebSocketDisconnect:
    #         await manager.disconnect(websocket, client_id)
    #         logger.info(f"WebSocket disconnected: {client_id}")
        
    #     except Exception as e:
    #         logger.error(f"WebSocket error: {str(e)}")
    #         try:
    #             await websocket.close(code=4000, reason=str(e))
    #         except:
    #             pass
    
    # except Exception as e:
    #     logger.error(f"Unhandled error in market_data_ws: {str(e)}")
    #     try:
    #         await websocket.close(code=4000, reason="Internal server error")
    #     except:
    #         pass
    
# Additional direct endpoint for /market-data (without /ws/ prefix)
@router.websocket("/market-data")
async def direct_market_data_ws(websocket: WebSocket, token: Optional[str] = Query(None), premium: Optional[str] = Query(None)):
    """Direct market data WebSocket endpoint to handle connections without the /ws/ prefix."""
    logger.info("Connection to /market-data endpoint (without /ws/ prefix)")
    
    # Accept all connections to the direct endpoint to fix 403 errors
    await websocket.accept()
    logger.info("Direct market-data WebSocket connection accepted immediately")
    
    # Extract token from various sources
    if not token:
        # Try query params
        query_params = dict(websocket.query_params)
        token = query_params.get("token")

        # Try cookies
        if not token:
            cookie_header = websocket.headers.get("cookie")
            if cookie_header:
                import re
                # Try qvai_token (new standard)
                match = re.search(r"qvai_token=([^;]+)", cookie_header)
                if match:
                    token = match.group(1)
                    logger.info("Found token in qvai_token cookie")
                else:
                    # Fall back to access_token
                    match = re.search(r"access_token=([^;]+)", cookie_header)
                    if match:
                        token = match.group(1)
                        logger.info("Found token in access_token cookie")

        # Try authorization header
        if not token:
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
                logger.info("Found token in authorization header")

    token = _clean_token(token)
    
    # Log token status but don't close connection regardless of validation result
    if token:
        try:
            # First, validate the token structure
            valid = validate_token(token)
            
            # Even if token is valid, extract premium parameter
            # Premium parameter can override role-based access control
            query_params = dict(websocket.query_params)
            premium_param = premium or query_params.get("premium")
            logger.info(f"Direct market-data token validation: {valid}")
            user_id = "anonymous"
            
            # Get user info if possible but don't fail if we can't
            try:
                from jose import jwt
                from core.config import settings
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET.get_secret_value(),
                    algorithms=[settings.JWT_ALGORITHM]
                )
                user_id = payload.get("sub", "anonymous")
            except Exception:
                pass
                
            # Check permissions using the new permissions system
            from jose import jwt
            from core.config import settings
            
            # Extract token payload
            payload = jwt.decode(
                token,
                settings.JWT_SECRET.get_secret_value(),
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Ensure free-tier users and anonymous connections are handled correctly
            if user_id == "anonymous" or payload.get("role", "free") == "free":
                logger.info("Granting unrestricted access for free-tier or anonymous user")
                return
            
            # Check if user has permission to access this endpoint
            if not check_websocket_permissions(payload, "/market-data", premium):
                logger.warning(f"WebSocket permission denied for user: {user_id}")
                await websocket.close(code=4003, reason="Permission denied")
                return
                
            # Connect to WebSocket manager
            await manager.connect(websocket, f"market-data:{user_id}")
            
            # Process messages until client disconnects
            while True:
                data = await websocket.receive_json()
                
                # Add metadata
                data["timestamp"] = datetime.utcnow().isoformat()
                data["client_id"] = f"market-data:{user_id}"
                
                # Process message based on type
                message_type = data.get("type")
                if message_type == "subscribe":
                    await handle_subscription(websocket, data, None)
                elif message_type == "unsubscribe":
                    await handle_unsubscription(websocket, data, None)
                else:
                    await websocket.send_json(
                        {
                            "error": "Unknown message type",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                    
        except Exception as e:
            logger.warning(f"Error in direct market-data endpoint: {str(e)}")
    else:
        logger.info("No token provided for direct market-data endpoint - continuing anonymously")
        
        try:
            # Connect anonymously
            await manager.connect(websocket, "market-data:anonymous")
            
            # Process messages until client disconnects
            while True:
                data = await websocket.receive_json()
                
                # Add metadata
                data["timestamp"] = datetime.utcnow().isoformat()
                data["client_id"] = "market-data:anonymous"
                
                # Process message based on type
                message_type = data.get("type")
                if message_type == "subscribe":
                    await handle_subscription(websocket, data, None)
                elif message_type == "unsubscribe":
                    await handle_unsubscription(websocket, data, None)
                else:
                    await websocket.send_json(
                        {
                            "error": "Unknown message type",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
        except WebSocketDisconnect:
            logger.info("Anonymous WebSocket disconnected")
            await manager.disconnect(websocket, "market-data:anonymous")
        except Exception as e:
            logger.error(f"Error in anonymous WebSocket connection: {str(e)}")
            try:
                await websocket.close(code=4000)
            except:
                pass


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
        if not token and auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

        token = _clean_token(token)

        # Require and verify token, except for public market data stream
        # --- Begin: Extract token from cookie if not present in query param ---
        if not token:
            cookie_header = websocket.headers.get("cookie")
            if cookie_header:
                import re

                # First try to get qvai_token (new standard)
                match = re.search(r"qvai_token=([^;]+)", cookie_header)
                if match:
                    token = _clean_token(match.group(1))
                    logger.info(f"Found token in qvai_token cookie")
                else:
                    # Fall back to access_token
                    match = re.search(r"access_token=([^;]+)", cookie_header)
                    if match:
                        token = _clean_token(match.group(1))
                        logger.info(f"Found token in access_token cookie")
        # --- End: Extract token from cookie ---

        # Debug logging for token presence after all extraction attempts
        if token:
            logger.info(f"Token provided for WebSocket connection: {client_id[:10]}...")
        else:
            logger.warning(f"No token provided for WebSocket connection: {client_id}")
        if not token:
            if client_id == "market-data":
                logger.info("Allowing anonymous WebSocket connection for market-data")
            else:
                await websocket.close(code=4001, reason="Token required")
                return
        elif not validate_token(token):
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

                # Process message based on type
                message_type = data.get("type")
                if message_type == "subscribe":
                    # Handle subscription
                    await handle_subscription(websocket, data, None)
                elif message_type == "unsubscribe":
                    # Handle unsubscription
                    await handle_unsubscription(websocket, data, None)
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
