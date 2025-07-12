"""
Standardized API Response Formats
Created: 2025-01-09
Author: AI Assistant
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime


class APIResponse(BaseModel):
    """Standard API response format"""
    status: str  # "success", "error", "warning"
    message: Optional[str] = None
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    error_code: Optional[str] = None
    timestamp: str = datetime.now().isoformat()
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format"""
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str = datetime.now().isoformat()
    request_id: Optional[str] = None


class SuccessResponse(BaseModel):
    """Standard success response format"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    timestamp: str = datetime.now().isoformat()
    request_id: Optional[str] = None


def create_success_response(
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized success response"""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id
    }


def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        "status": "error",
        "message": message,
        "error_code": error_code,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id
    }


def create_validation_error_response(
    message: str = "Validation failed",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized validation error response"""
    return {
        "status": "error",
        "message": message,
        "error_code": "VALIDATION_ERROR",
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id
    }


def create_auth_error_response(
    message: str = "Authentication failed",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized authentication error response"""
    return {
        "status": "error",
        "message": message,
        "error_code": "AUTH_ERROR",
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id
    }


def create_not_found_response(
    message: str = "Resource not found",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized not found error response"""
    return {
        "status": "error",
        "message": message,
        "error_code": "NOT_FOUND",
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id
    }


def create_rate_limit_response(
    message: str = "Rate limit exceeded",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized rate limit error response"""
    return {
        "status": "error",
        "message": message,
        "error_code": "RATE_LIMIT_EXCEEDED",
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id
    }
