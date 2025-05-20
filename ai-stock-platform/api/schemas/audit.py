"""
Audit Schemas
Created: 2025-05-20 05:02:05
Author: daparthi001
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Any
from datetime import datetime

class AuditEvent(BaseModel):
    """Audit event schema."""
    id: str
    timestamp: datetime
    event_type: str
    severity: str
    description: str
    user_id: Optional[int]
    resource_type: Optional[str]
    resource_id: Optional[str]
    ip_address: Optional[str]
    metadata: Dict[str, Any]

class AuditLogResponse(AuditEvent):
    """Audit log response schema."""
    correlation_id: str
    session_id: Optional[str]
    user_agent: Optional[str]
    location: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

class ResourceChange(BaseModel):
    """Resource change schema."""
    field: str
    old_value: Any
    new_value: Any
    changed_by: str
    change_type: str

class AuditTrailResponse(BaseModel):
    """Audit trail response schema."""
    resource_id: str
    resource_type: str
    created_at: datetime
    created_by: str
    changes: List[ResourceChange]
    current_state: Dict[str, Any]
    previous_states: List[Dict[str, Any]]
    related_events: List[str]

class EventContext(BaseModel):
    """Event context schema."""
    request_id: str
    session_data: Dict[str, Any]
    environment: Dict[str, Any]
    related_resources: List[Dict[str, Any]]

class AuditEventResponse(BaseModel):
    """Audit event response schema."""
    event: AuditEvent
    context: Optional[EventContext]
    impact: Optional[Dict[str, Any]]
    related_events: List[Dict[str, Any]]
    resolution: Optional[Dict[str, Any]]

class FilterOption(BaseModel):
    """Filter option schema."""
    name: str
    type: str
    values: List[Any]
    description: str

class AuditFilterResponse(BaseModel):
    """Audit filter response schema."""
    event_types: List[str]
    severities: List[str]
    resource_types: List[str]
    user_roles: List[str]
    custom_filters: List[FilterOption]
    time_ranges: List[Dict[str, Any]]

class ExportJob(BaseModel):
    """Export job schema."""
    id: str
    status: str
    progress: float
    total_records: int
    file_size: Optional[int]

class AuditExportResponse(BaseModel):
    """Audit export response schema."""
    export_id: str
    created_at: datetime
    status: str
    format: str
    filters: Dict[str, Any]
    job: ExportJob
    download_url: Optional[HttpUrl]
    expires_at: Optional[datetime]

class MetricGroup(BaseModel):
    """Metric group schema."""
    name: str
    count: int
    percentage: float
    trend: Optional[float]

class AuditStatisticsResponse(BaseModel):
    """Audit statistics response schema."""
    time_range: str
    total_events: int
    unique_users: int
    event_distribution: List[MetricGroup]
    severity_distribution: List[MetricGroup]
    top_resources: List[Dict[str, Any]]
    activity_timeline: List[Dict[str, Any]]

class SearchResult(BaseModel):
    """Search result schema."""
    event: AuditEvent
    score: float
    highlights: Dict[str, List[str]]

class AuditSearchResponse(BaseModel):
    """Audit search response schema."""
    query: str
    total_results: int
    page: int
    page_size: int
    results: List[SearchResult]
    facets: Dict[str, Dict[str, int]]
    suggestion: Optional[str]

class ActivitySession(BaseModel):
    """Activity session schema."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    ip_address: str
    user_agent: str
    events: List[AuditEvent]

class UserActivityResponse(BaseModel):
    """User activity response schema."""
    user_id: int
    period_start: datetime
    period_end: datetime
    total_sessions: int
    total_events: int
    sessions: List[ActivitySession]
    activity_summary: Dict[str, Any]
    risk_indicators: Optional[Dict[str, Any]]