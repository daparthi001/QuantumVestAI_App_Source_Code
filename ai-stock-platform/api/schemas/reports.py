"""
Reports Schemas
Created: 2025-05-20 04:57:51
Author: daparthi001
"""
from pydantic import BaseModel, HttpUrl, EmailStr
from typing import List, Dict, Optional, Any
from datetime import datetime

class ReportParameters(BaseModel):
    """Report parameters schema."""
    start_date: datetime
    end_date: datetime
    portfolio_ids: Optional[List[int]]
    metrics: List[str]
    grouping: Optional[str]
    filters: Optional[Dict[str, Any]]
    custom_parameters: Optional[Dict[str, Any]]

class ReportFormat(BaseModel):
    """Report format schema."""
    type: str
    template: Optional[str]
    orientation: Optional[str]
    paper_size: Optional[str]
    custom_styling: Optional[Dict[str, Any]]

class ReportCreate(BaseModel):
    """Create report schema."""
    name: str
    description: Optional[str]
    report_type: str
    parameters: ReportParameters
    format: ReportFormat
    tags: Optional[List[str]]

class ReportResponse(BaseModel):
    """Report response schema."""
    id: int
    user_id: int
    name: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    file_url: Optional[HttpUrl]
    file_size: Optional[int]
    error_message: Optional[str]

    class Config:
        from_attributes = True

class TemplateSection(BaseModel):
    """Template section schema."""
    name: str
    type: str
    required: bool
    parameters: Dict[str, Any]
    visualization: Optional[str]

class ReportTemplateResponse(BaseModel):
    """Report template response schema."""
    id: int
    name: str
    category: str
    description: str
    sections: List[TemplateSection]
    required_data: List[str]
    supported_formats: List[str]
    example_url: Optional[HttpUrl]

    class Config:
        from_attributes = True

class Schedule(BaseModel):
    """Schedule schema."""
    frequency: str
    day_of_week: Optional[int]
    day_of_month: Optional[int]
    hour: int
    minute: int
    timezone: str

class DeliveryOptions(BaseModel):
    """Delivery options schema."""
    method: str
    recipients: List[EmailStr]
    format: str
    compress: bool = False
    encrypt: bool = False

class ReportScheduleResponse(BaseModel):
    """Report schedule response schema."""
    id: int
    user_id: int
    template_id: int
    schedule: Schedule
    delivery_options: DeliveryOptions
    next_run: datetime
    last_run: Optional[datetime]
    status: str

    class Config:
        from_attributes = True

class GenerationProgress(BaseModel):
    """Generation progress schema."""
    stage: str
    progress: float
    message: str
    started_at: datetime
    estimated_completion: datetime

class ReportGenerationResponse(BaseModel):
    """Report generation response schema."""
    report_id: int
    status: str
    progress: GenerationProgress
    errors: List[Dict[str, Any]]
    output_files: List[Dict[str, Any]]
    processing_time: float

class CustomMetric(BaseModel):
    """Custom metric schema."""
    name: str
    calculation: str
    parameters: Dict[str, Any]
    visualization: Optional[str]

class CustomReportResponse(BaseModel):
    """Custom report response schema."""
    id: int
    user_id: int
    metrics: List[CustomMetric]
    generated_at: datetime
    data: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    format: str
    file_url: Optional[HttpUrl]

class DeliveryAttempt(BaseModel):
    """Delivery attempt schema."""
    timestamp: datetime
    method: str
    status: str
    recipient: str
    error_message: Optional[str]

class ReportDeliveryResponse(BaseModel):
    """Report delivery response schema."""
    report_id: int
    delivery_id: str
    status: str
    timestamp: datetime
    method: str
    recipients: List[str]
    attempts: List[DeliveryAttempt]
    success_count: int
    failure_count: int