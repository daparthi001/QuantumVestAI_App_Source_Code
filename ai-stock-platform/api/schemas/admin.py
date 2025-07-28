"""
Admin Schemas
Created: 2025-05-20 04:45:46
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from .base import SafeBaseModel


class SystemMetrics(BaseModel):
    """System metrics schema."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    api_latency: float
    db_connections: int
    cache_hits: int
    cache_misses: int
    active_users: int

class SystemStatusResponse(BaseModel):
    """System status response schema."""
    status: str
    version: str
    environment: str
    uptime: str
    last_deploy: datetime
    metrics: SystemMetrics
    components_status: Dict[str, str]

class UserManagementResponse(BaseModel):
    """User management response schema."""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    subscription_status: str
    api_requests_count: int
    api_keys_count: int

    class Config:
        from_attributes = True

class APIKeyResponse(BaseModel):
    """API key response schema."""
    key: str
    user_id: int
    expires_at: datetime
    created_at: datetime
    last_used: Optional[datetime]
    permissions: List[str]

class UsageMetrics(SafeBaseModel):
    """Usage metrics schema."""
    total_requests: int
    unique_users: int
    api_keys_active: int
    premium_conversions: int
    forecast_requests: int
    model_accuracy: float
    average_response_time: float

class UsageStatsResponse(SafeBaseModel):
    """Usage statistics response schema."""
    period_start: datetime
    period_end: datetime
    metrics: UsageMetrics
    top_users: List[Dict[str, Any]]
    popular_endpoints: List[Dict[str, Any]]
    error_rates: Dict[str, float]

class ModelMetrics(SafeBaseModel):
    """Model metrics schema."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    latency: float
    throughput: int

class ModelPerformanceResponse(SafeBaseModel):
    """Model performance response schema."""
    model_name: str
    model_version: str
    last_trained: datetime
    total_predictions: int
    metrics: ModelMetrics
    performance_trend: List[Dict[str, Any]]

class AuditLogResponse(BaseModel):
    """Audit log response schema."""
    id: int
    timestamp: datetime
    log_type: str
    user_id: Optional[int]
    action: str
    resource: str
    status: str
    ip_address: str
    user_agent: str
    details: Dict[str, Any]

    class Config:
        from_attributes = True
