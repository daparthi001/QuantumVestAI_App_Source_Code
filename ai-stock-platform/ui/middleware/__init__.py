"""
Middleware Module Initialization
Created: 2025-05-22 05:06:41
Author: daparthi001
Updated: 2025-06-15 02:44:55 by daparthi001
"""
# Replace this incorrect import
# from ui.middleware.auth_middleware import (
#     # whatever imports were here
# )

# With a proper relative import
from .auth_middleware import AuthMiddleware, get_current_user

# Add any other middleware components you need
__all__ = ['AuthMiddleware', 'get_current_user']