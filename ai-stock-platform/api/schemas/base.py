"""
Base schema models.
Created: 2025-05-17 14:29:46 UTC
Author: daparthi001
"""
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class TimestampModel(BaseModel):
    """Base model with timestamp fields."""
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    @validator('created_at', 'updated_at', pre=True)
    def default_datetime(cls, value: datetime) -> datetime:
        """Ensure datetime fields are UTC."""
        return value or datetime.utcnow()

class ApiResponse(BaseModel):
    """Standard API response model."""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
