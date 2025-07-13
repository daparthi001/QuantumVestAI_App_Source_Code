"""
API Response Models
Created: 2025-06-19 03:06:29
Author: daparthi001
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    """Standard API response model"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Standard API error response model"""
    status: str = "error"
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(StandardResponse, Generic[T]):
    """Paginated API response model"""
    data: List[T]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
