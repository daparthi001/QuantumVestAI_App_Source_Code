import time
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from config.settings import SECRET_KEY
import logging

logger = logging.getLogger(__name__)

async def authorize_websocket(token: str) -> bool:
    try:
        # Decode the JWT token
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        logger.debug(f"Decoded token payload: {payload}")
        
        # Check token expiry
        current_time = int(time.time())
        exp = payload.get("exp")
        if exp and exp < current_time:
            # Match the log format from the error logs
            logger.warning("Token verification failed: Signature has expired.")
            return False
        
        # Accept both 'premium' and 'free' roles for WebSocket access
        role = payload.get("role")
        if role not in ("premium", "free"):
            logger.error(f"Unauthorized role: {role}")
            return False
        
        logger.info("Token authorization successful")
        return True
    except ExpiredSignatureError:
        logger.warning("Token verification failed: Signature has expired.")
        return False
    except InvalidTokenError:
        logger.error("Invalid token")
        return False
    except Exception as e:
        logger.error(f"Authorization failed: {e}")
        return False

# WebSocket handler
async def websocket_handler(request):
    token = request.query.get("token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        logger.info("connection rejected (403 Forbidden)")
        return web.Response(status=403, text="Forbidden: No token provided")
    
    if not await authorize_websocket(token):
        logger.info("connection rejected (403 Forbidden)")
        return web.Response(status=403, text="Forbidden: Invalid token")
    
    # Rate limiting logic
    rate_limit_remaining = request.headers.get("x-ratelimit-remaining")
    if rate_limit_remaining and int(rate_limit_remaining) <= 0:
        logger.error("Rate limit exceeded")
        return web.Response(status=429, text="Too Many Requests: Rate limit exceeded")
    
    logger.info("WebSocket connection authorized")
    # Proceed with WebSocket connection
    # ...existing code...
