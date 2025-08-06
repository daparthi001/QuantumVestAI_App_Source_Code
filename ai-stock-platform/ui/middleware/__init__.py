"""
Middleware initialization
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-16 03:41:30 by daparthi001
"""
import logging

logger = logging.getLogger(__name__)

# Safely export middleware components
try:
    from .auth_middleware import AuthMiddleware
    from .error_handlers import setup_error_handlers
    from .metrics_middleware import MetricsMiddleware
    logger.info("Successfully imported middleware components")
except Exception as e:
    logger.error(f"Error importing middleware components: {e}")

    # Define fallback middleware classes and functions
    class AuthMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

    class MetricsMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

    def setup_error_handlers(app):
        """Fallback no-op error handler setup."""
        pass

    logger.warning("Using fallback middleware components")

__all__ = ["AuthMiddleware", "MetricsMiddleware", "setup_error_handlers"]
