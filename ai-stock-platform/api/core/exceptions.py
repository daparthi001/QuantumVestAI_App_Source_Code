"""
Core Exceptions
Created: 2025-05-20 04:43:53
Updated: 2025-06-17 17:03:55
Author: daparthi001
"""
from fastapi import HTTPException, status

class AuthenticationError(HTTPException):
    """Authentication error."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class ValidationError(HTTPException):
    """Validation error."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class PermissionDeniedError(HTTPException):
    """Permission denied error."""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class NotFoundError(HTTPException):
    """Resource not found error."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )