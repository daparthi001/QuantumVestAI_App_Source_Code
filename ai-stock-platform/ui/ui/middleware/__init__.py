"""
UI Middleware Module - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.middleware.
New code should import directly from middleware.
"""

# Import all middleware components from the correct ui.middleware path with error handling
try:
    from ui.middleware.auth_middleware import *
    _auth_import_success = True
except Exception as e:
    _auth_import_success = False
    import logging
    logging.getLogger(__name__).warning(f"Failed to import auth_middleware: {e}")

try:
    from ui.middleware.error_handlers import *
    _error_handlers_import_success = True
except Exception as e:
    _error_handlers_import_success = False
    import logging
    logging.getLogger(__name__).warning(f"Failed to import error_handlers: {e}")

# Provide a fallback if imports fail
if not _auth_import_success:
    # Define minimal fallback AuthMiddleware
    class AuthMiddleware:
        def __init__(self, app):
            self.app = app
        
        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

if not _error_handlers_import_success:
    # Define minimal fallback error handler setup
    def setup_error_handlers(app):
        """Fallback no-op error handler setup."""
        pass

__all__ = []
