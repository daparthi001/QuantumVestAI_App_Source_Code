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
        error_code: Optional[str] = None,
        headers: Optional[dict] = None
    ):
        """Initialize API exception with error code."""
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code or f"ERR_{status_code}"
        self.headers = headers
        super().__init__(status_code, detail, headers)

# Auth exceptions
class AuthenticationError(APIException):
    """Exception raised when authentication fails."""
    
    def __init__(self, detail: str = "Could not validate credentials"):
        """Initialize authentication error."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_ERROR",
            headers={"WWW-Authenticate": "Bearer"}
        )

class PermissionDeniedError(APIException):
    """Exception raised when user doesn't have permission."""
    
    def __init__(self, detail: str = "Not enough permissions"):
        """Initialize permission denied error."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED"
        )

# Resource exceptions
class ResourceNotFoundError(APIException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, detail: str = "Resource not found"):
        """Initialize resource not found error."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND"
        )

class ResourceAlreadyExistsError(APIException):
    """Exception raised when a resource already exists."""
    
    def __init__(self, detail: str = "Resource already exists"):
        """Initialize resource already exists error."""
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="ALREADY_EXISTS"
        )

# Validation exceptions
class ValidationError(APIException):
    """Exception raised when validation fails."""
    
    def __init__(self, detail: str = "Validation error"):
        """Initialize validation error."""
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )

# Rate limiting exceptions
class RateLimitError(APIException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        """Initialize rate limit error."""
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            headers={"Retry-After": "60"}
        )

# Service exceptions
class ServiceUnavailableError(APIException):
    """Exception raised when a service is unavailable."""
    
    def __init__(self, detail: str = "Service temporarily unavailable"):
        """Initialize service unavailable error."""
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="SERVICE_UNAVAILABLE"
        )

class ExternalAPIError(APIException):
    """Exception raised when an external API call fails."""
    
    def __init__(self, detail: str = "External API error"):
        """Initialize external API error."""
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code="EXTERNAL_API_ERROR"
        )

# Business logic exceptions
class InsufficientCreditsError(APIException):
    """Exception raised when user has insufficient credits."""
    
    def __init__(self, detail: str = "Insufficient credits"):
        """Initialize insufficient credits error."""
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
            error_code="INSUFFICIENT_CREDITS"
        )

class SubscriptionRequiredError(APIException):
    """Exception raised when a subscription is required."""
    
    def __init__(self, detail: str = "Subscription required"):
        """Initialize subscription required error."""
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
            error_code="SUBSCRIPTION_REQUIRED"
        )