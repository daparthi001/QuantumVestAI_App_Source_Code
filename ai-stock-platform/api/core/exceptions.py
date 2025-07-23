"""
Custom exception classes for QuantumVestAI
Created: 2025-07-23
Author: daparthi001
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class QuantumVestAIException(Exception):
    """Base exception class for QuantumVestAI"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(QuantumVestAIException):
    """Raised when validation fails"""
    pass


class NotFoundError(HTTPException):
    """Raised when a resource is not found"""
    
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers={"X-Error-Code": error_code}
        )


class PermissionError(HTTPException):
    """Raised when user lacks sufficient permissions"""
    
    def __init__(self, detail: str = "Insufficient permissions", error_code: str = "PERMISSION_DENIED"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers={"X-Error-Code": error_code}
        )


class AuthenticationError(HTTPException):
    """Raised when authentication fails"""
    
    def __init__(self, detail: str = "Authentication failed", error_code: str = "AUTHENTICATION_FAILED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Error-Code": error_code
            }
        )


class ConflictError(HTTPException):
    """Raised when there's a conflict (e.g., duplicate resources)"""
    
    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers={"X-Error-Code": error_code}
        )


class BusinessLogicError(HTTPException):
    """Raised when business logic rules are violated"""
    
    def __init__(self, detail: str = "Business logic error", error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers={"X-Error-Code": error_code}
        )


class RateLimitError(HTTPException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, detail: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"X-Error-Code": error_code}
        )


class ServiceUnavailableError(HTTPException):
    """Raised when service is temporarily unavailable"""
    
    def __init__(self, detail: str = "Service temporarily unavailable", error_code: str = "SERVICE_UNAVAILABLE"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers={"X-Error-Code": error_code}
        )


# User-specific exceptions
class UserNotFoundError(NotFoundError):
    """Raised when user is not found"""
    
    def __init__(self):
        super().__init__(detail="User not found", error_code="USER_NOT_FOUND")


class UserAlreadyExistsError(ConflictError):
    """Raised when trying to create a user that already exists"""
    
    def __init__(self, field: str = "user"):
        super().__init__(detail=f"{field.title()} already exists", error_code="USER_ALREADY_EXISTS")


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid"""
    
    def __init__(self):
        super().__init__(detail="Invalid username/email or password", error_code="INVALID_CREDENTIALS")


class AccountDisabledError(AuthenticationError):
    """Raised when trying to authenticate with a disabled account"""
    
    def __init__(self):
        super().__init__(detail="Account is disabled", error_code="ACCOUNT_DISABLED")


class EmailNotVerifiedError(AuthenticationError):
    """Raised when email is not verified"""
    
    def __init__(self):
        super().__init__(detail="Email address not verified", error_code="EMAIL_NOT_VERIFIED")


class SessionExpiredError(AuthenticationError):
    """Raised when session has expired"""
    
    def __init__(self):
        super().__init__(detail="Session has expired", error_code="SESSION_EXPIRED")


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid"""
    
    def __init__(self):
        super().__init__(detail="Invalid or expired token", error_code="INVALID_TOKEN")


# Role and permission exceptions
class RoleNotFoundError(NotFoundError):
    """Raised when role is not found"""
    
    def __init__(self):
        super().__init__(detail="Role not found", error_code="ROLE_NOT_FOUND")


class InsufficientPermissionsError(PermissionError):
    """Raised when user lacks specific permissions"""
    
    def __init__(self, permission: str):
        super().__init__(
            detail=f"Permission '{permission}' required",
            error_code="INSUFFICIENT_PERMISSIONS"
        )


class RoleAssignmentError(BusinessLogicError):
    """Raised when role assignment fails"""
    
    def __init__(self, reason: str = "Role assignment failed"):
        super().__init__(detail=reason, error_code="ROLE_ASSIGNMENT_ERROR")


# File and upload exceptions
class FileUploadError(BusinessLogicError):
    """Raised when file upload fails"""
    
    def __init__(self, reason: str = "File upload failed"):
        super().__init__(detail=reason, error_code="FILE_UPLOAD_ERROR")


class InvalidFileTypeError(ValidationError):
    """Raised when file type is not allowed"""
    
    def __init__(self, allowed_types: list = None):
        message = "Invalid file type"
        if allowed_types:
            message += f". Allowed types: {', '.join(allowed_types)}"
        super().__init__(message, error_code="INVALID_FILE_TYPE")


class FileSizeExceededError(ValidationError):
    """Raised when file size exceeds limit"""
    
    def __init__(self, max_size: str = "5MB"):
        super().__init__(f"File size exceeds maximum allowed size of {max_size}", error_code="FILE_SIZE_EXCEEDED")


# Database exceptions
class DatabaseError(QuantumVestAIException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, error_code="DATABASE_ERROR")


class IntegrityConstraintError(ConflictError):
    """Raised when database integrity constraint is violated"""
    
    def __init__(self, constraint: str = "data"):
        super().__init__(detail=f"Integrity constraint violation: {constraint}", error_code="INTEGRITY_CONSTRAINT_ERROR")


# Portfolio-specific exceptions (for future use)
class PortfolioNotFoundError(NotFoundError):
    """Raised when portfolio is not found"""
    
    def __init__(self):
        super().__init__(detail="Portfolio not found", error_code="PORTFOLIO_NOT_FOUND")


class PortfolioLimitExceededError(BusinessLogicError):
    """Raised when portfolio limit is exceeded"""
    
    def __init__(self, limit: int):
        super().__init__(
            detail=f"Portfolio limit of {limit} exceeded",
            error_code="PORTFOLIO_LIMIT_EXCEEDED"
        )


class AssetNotFoundError(NotFoundError):
    """Raised when asset is not found"""
    
    def __init__(self):
        super().__init__(detail="Asset not found", error_code="ASSET_NOT_FOUND")


# Utility function to convert validation errors to HTTP exceptions
def convert_validation_error(error: ValidationError) -> HTTPException:
    """Convert ValidationError to HTTPException"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=error.message,
        headers={"X-Error-Code": error.error_code or "VALIDATION_ERROR"}
    )