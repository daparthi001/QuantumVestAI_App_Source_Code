"""
Alerting Schemas
Created: 2025-05-20 04:59:13
Author: daparthi001
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class AlertCondition(BaseModel):
    """Alert condition schema."""
    metric: str
    operator: str
    value: Union[float, int, str]
    comparison_period: Optional[str]
    lookback_window: Optional[int]
    threshold_type: str = "absolute"  # or "percentage"
    additional_params: Optional[Dict[str, Any]]

class AlertChannel(BaseModel):
    """Alert channel schema."""
    type: str
    config: Dict[str, Any]
    enabled: bool = True
    priority: Optional[str]

class AlertSchedule(BaseModel):
    """Alert schedule schema."""
    active_hours: Optional[Dict[str, List[str]]]
    time_zone: str = "UTC"
    quiet_hours: Optional[Dict[str, List[str]]]
    maintenance_windows: Optional[List[Dict[str, Any]]]

class AlertCreate(BaseModel):
    """Create alert schema."""
    name: str
    description: Optional[str]
    condition: AlertCondition
    channels: List[AlertChannel]
    severity: str = "medium"
    schedule: Optional[AlertSchedule]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]

class AlertResponse(BaseModel):
    """Alert response schema."""
    id: int
    user_id: int
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_triggered: Optional[datetime]
    trigger_count: int
    next_evaluation: datetime

    class Config:
        from_attributes = True

class AlertRuleMetadata(BaseModel):
    """Alert rule metadata schema."""
    description: str
    supported_operators: List[str]
    value_type: str
    example: Any
    constraints: Optional[Dict[str, Any]]

class AlertRuleResponse(BaseModel):
    """Alert rule response schema."""
    id: int
    name: str
    category: str
    asset_types: List[str]
    metadata: AlertRuleMetadata
    template: Optional[Dict[str, Any]]
    required_data: List[str]

class AlertEvent(BaseModel):
    """Alert event schema."""
    timestamp: datetime
    type: str
    data: Dict[str, Any]
    source: str
    severity: str

class AlertHistoryResponse(BaseModel):
    """Alert history response schema."""
    alert_id: int
    events: List[AlertEvent]
    status_changes: List[Dict[str, Any]]
    acknowledgments: List[Dict[str, Any]]
    resolution_time: Optional[timedelta]

class AlertTriggerData(BaseModel):
    """Alert trigger data schema."""
    values: Dict[str, Any]
    threshold_breach: Dict[str, Any]
    context: Optional[Dict[str, Any]]

class AlertTriggerResponse(BaseModel):
    """Alert trigger response schema."""
    trigger_id: str
    alert_id: int
    timestamp: datetime
    data: AlertTriggerData
    notification_status: Dict[str, str]
    processing_time: float

class ChannelConfig(BaseModel):
    """Channel configuration schema."""
    name: str
    type: str
    config_schema: Dict[str, Any]
    capabilities: List[str]
    rate_limits: Optional[Dict[str, int]]

class AlertChannelResponse(BaseModel):
    """Alert channel response schema."""
    channel_id: str
    name: str
    type: str
    status: str
    config: ChannelConfig
    supported_severities: List[str]
    delivery_stats: Dict[str, int]

class AlertMetrics(BaseModel):
    """Alert metrics schema."""
    evaluation_time: float
    trigger_rate: float
    false_positives: int
    notification_success_rate: float
    average_resolution_time: Optional[float]

class AlertStatusResponse(BaseModel):
    """Alert status response schema."""
    alert_id: int
    current_status: str
    last_evaluation: datetime
    next_evaluation: datetime
    current_value: Optional[Any]
    threshold_value: Any
    metrics: AlertMetrics
    health_status: str

class AlertGroup(BaseModel):
    """Alert group schema."""
    name: str
    count: int
    percentage: float
    triggered_count: int
    critical_count: int

class AlertAggregationResponse(BaseModel):
    """Alert aggregation response schema."""
    timestamp: datetime
    time_range: str
    group_by: str
    total_alerts: int
    active_alerts: int
    groups: List[AlertGroup]
    trend: Dict[str, List[int]]
