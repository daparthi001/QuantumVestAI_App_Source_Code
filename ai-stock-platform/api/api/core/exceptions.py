"""
Custom exceptions for the API.
"""
from fastapi import HTTPException
from typing import Any, Dict, Optional

class APIError(HTTPException):
    """Base API exception."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class AuthenticationError(APIError):
    """Authentication error."""
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=401, detail=detail)

class AuthorizationError(APIError):
    """Authorization error."""
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=403, detail=detail)

class ValidationError(APIError):
    """Validation error."""
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)

class NotFoundError(APIError):
    """Resource not found error."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class DatabaseError(APIError):
    """Database error."""
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(status_code=500, detail=detail)

class ExternalAPIError(APIError):
    """External API error."""
    def __init__(self, detail: str = "External API error occurred"):
        super().__init__(status_code=502, detail=detail)