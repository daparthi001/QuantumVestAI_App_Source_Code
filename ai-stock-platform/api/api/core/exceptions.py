"""
Custom Exceptions
Created: 2025-05-20 04:40:55
Author: daparthi001
"""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any

class APIException(HTTPException):
    """Base API exception."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize API exception."""
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or f"ERR_{status_code}"
        self.headers = headers

class AuthenticationError(APIException):
    """Authentication error."""
    
    def __init__(self, detail: str = "Authentication failed") -> None:
        """Initialize authentication error."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_ERROR",
            headers={"WWW-Authenticate": "Bearer"}
        )

class PermissionDeniedError(APIException):
    """Permission denied error."""
    
    def __init__(self, detail: str = "Permission denied") -> None:
        """Initialize permission denied error."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED"
        )

class ResourceNotFoundError(APIException):
    """Resource not found error."""
    
    def __init__(self, detail: str = "Resource not found") -> None:
        """Initialize not found error."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND"
        )

class ValidationError(APIException):
    """Validation error."""
    
    def __init__(self, detail: str = "Validation failed") -> None:
        """Initialize validation error."""
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )