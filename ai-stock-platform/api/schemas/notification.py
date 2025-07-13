"""
Notification Schemas
Created: 2025-05-20 04:50:55
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class NotificationBase(BaseModel):
    """Base notification schema."""
    category: str
    title: str
    message: str
    priority: str = "normal"
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[HttpUrl] = None

class NotificationResponse(NotificationBase):
    """Notification response schema."""
    id: int
    user_id: int
    status: str
    created_at: datetime
    read_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class NotificationChannel(BaseModel):
    """Notification channel schema."""
    channel: str
    enabled: bool
    config: Optional[Dict[str, Any]] = None

class NotificationSettingsUpdate(BaseModel):
    """Notification settings update schema."""
    channels: List[NotificationChannel]
    quiet_hours_start: Optional[str] = Field(None, regex="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, regex="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    categories: Dict[str, bool]
    minimum_priority: str = "normal"

class NotificationSettingsResponse(NotificationSettingsUpdate):
    """Notification settings response schema."""
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class AlertTrigger(BaseModel):
    """Alert trigger schema."""
    type: str
    condition: str
    value: Any
    comparison: Optional[str] = None
    cooldown: Optional[int] = None

class AlertConfigBase(BaseModel):
    """Base alert config schema."""
    name: str
    description: Optional[str] = None
    category: str
    trigger: AlertTrigger
    channels: List[str]
    is_active: bool = True

class AlertConfigCreate(AlertConfigBase):
    """Create alert config schema."""
    pass

class AlertConfigResponse(AlertConfigBase):
    """Alert config response schema."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    last_triggered: Optional[datetime]
    trigger_count: int

    class Config:
        from_attributes = True

class CategoryStats(BaseModel):
    """Category statistics schema."""
    total: int
    unread: int
    last_received: Optional[datetime]
    most_frequent_type: str

class NotificationStatsResponse(BaseModel):
    """Notification statistics response schema."""
    total_count: int
    unread_count: int
    categories: Dict[str, CategoryStats]
    recent_notifications: List[NotificationResponse]
    active_alerts_count: int
    notification_frequency: Dict[str, int]
