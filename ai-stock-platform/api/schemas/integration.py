"""
Integration Schemas
Created: 2025-05-20 04:56:23
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, HttpUrl, SecretStr


class IntegrationConfig(BaseModel):
    """Integration configuration schema."""
    api_key: Optional[SecretStr]
    api_secret: Optional[SecretStr]
    base_url: Optional[HttpUrl]
    webhook_url: Optional[HttpUrl]
    oauth_token: Optional[SecretStr]
    custom_settings: Optional[Dict[str, Any]]

class IntegrationCreate(BaseModel):
    """Create integration schema."""
    name: str
    type: str
    provider: str
    config: IntegrationConfig
    description: Optional[str]
    is_active: bool = True

class IntegrationResponse(BaseModel):
    """Integration response schema."""
    id: int
    user_id: int
    name: str
    type: str
    provider: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime]
    health_status: str
    error_count: int

    class Config:
        from_attributes = True

class WebhookPayload(BaseModel):
    """Webhook payload schema."""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]

class WebhookResponse(BaseModel):
    """Webhook response schema."""
    integration_id: int
    event_id: str
    status: str
    processed_at: datetime
    result: Optional[Dict[str, Any]]

class ExportConfig(BaseModel):
    """Export configuration schema."""
    format: str
    compression: Optional[str]
    encryption: Optional[bool]
    include_metadata: bool

class ExportResponse(BaseModel):
    """Export response schema."""
    integration_id: int
    export_id: str
    status: str
    url: Optional[HttpUrl]
    expires_at: Optional[datetime]
    file_size: Optional[int]
    checksum: Optional[str]

class SyncStatus(BaseModel):
    """Sync status schema."""
    resource: str
    status: str
    records_processed: int
    errors: List[Dict[str, Any]]
    last_sync_id: Optional[str]

class DataSyncResponse(BaseModel):
    """Data sync response schema."""
    integration_id: int
    sync_id: str
    sync_type: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    resources: List[SyncStatus]
    summary: Dict[str, Any]

class HealthCheck(BaseModel):
    """Health check schema."""
    component: str
    status: str
    latency: float
    last_checked: datetime
    error_message: Optional[str]

class IntegrationStatusResponse(BaseModel):
    """Integration status response schema."""
    integration_id: int
    status: str
    uptime: float
    health_checks: List[HealthCheck]
    rate_limits: Dict[str, Any]
    usage_metrics: Dict[str, Any]
    active_processes: List[Dict[str, Any]]

class ApiKeyResponse(BaseModel):
    """API key response schema."""
    integration_id: int
    key: str
    created_at: datetime
    expires_at: datetime
    permissions: List[str]
    rate_limit: Dict[str, int]

class OAuthConfig(BaseModel):
    """OAuth configuration schema."""
    client_id: str
    authorize_url: HttpUrl
    token_url: HttpUrl
    scope: List[str]
    redirect_uri: HttpUrl

class OAuthConfigResponse(BaseModel):
    """OAuth configuration response schema."""
    provider: str
    config: OAuthConfig
    requirements: Dict[str, Any]
    documentation_url: HttpUrl
