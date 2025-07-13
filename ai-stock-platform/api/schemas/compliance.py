"""
Compliance Schemas
Created: 2025-05-20 05:00:34
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ComplianceRule(BaseModel):
    """Compliance rule schema."""
    name: str
    category: str
    description: str
    parameters: Dict[str, Any]
    validation_logic: str
    severity: str
    active: bool

class ComplianceRuleResponse(ComplianceRule):
    """Compliance rule response schema."""
    id: int
    created_at: datetime
    updated_at: datetime
    last_triggered: Optional[datetime]
    violation_count: int

    class Config:
        from_attributes = True

class ComplianceViolation(BaseModel):
    """Compliance violation schema."""
    rule_id: int
    description: str
    severity: str
    action_required: str
    resolution_deadline: Optional[datetime]

class ComplianceCheckResponse(BaseModel):
    """Compliance check response schema."""
    timestamp: datetime
    action_type: str
    compliant: bool
    violations: List[ComplianceViolation]
    warnings: List[Dict[str, Any]]
    approval_required: bool
    audit_trail: Dict[str, Any]

class ReportMetrics(BaseModel):
    """Report metrics schema."""
    total_checks: int
    violation_count: int
    approval_rate: float
    average_resolution_time: float
    risk_score: float

class ComplianceReportResponse(BaseModel):
    """Compliance report response schema."""
    id: int
    report_type: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    metrics: ReportMetrics
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    file_url: Optional[HttpUrl]

class ViolationEvidence(BaseModel):
    """Violation evidence schema."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str

class ComplianceViolationResponse(BaseModel):
    """Compliance violation response schema."""
    id: int
    rule_id: int
    timestamp: datetime
    severity: str
    description: str
    status: str
    evidence: List[ViolationEvidence]
    resolution: Optional[Dict[str, Any]]
    assigned_to: Optional[str]

class ComplianceThresholds(BaseModel):
    """Compliance thresholds schema."""
    category: str
    limits: Dict[str, Any]
    escalation_levels: List[Dict[str, Any]]

class ComplianceConfigResponse(BaseModel):
    """Compliance configuration response schema."""
    version: str
    last_updated: datetime
    thresholds: List[ComplianceThresholds]
    rules_version: str
    regulatory_requirements: Dict[str, Any]
    approval_workflows: List[Dict[str, Any]]

class AuditScope(BaseModel):
    """Audit scope schema."""
    areas: List[str]
    time_range: Dict[str, datetime]
    depth: str
    exclusions: Optional[List[str]]

class ComplianceAuditResponse(BaseModel):
    """Compliance audit response schema."""
    id: int
    audit_type: str
    status: str
    scope: AuditScope
    progress: float
    start_time: datetime
    end_time: Optional[datetime]
    findings: Optional[List[Dict[str, Any]]]
    recommendations: Optional[List[str]]

class FilingRequirement(BaseModel):
    """Filing requirement schema."""
    form_type: str
    due_date: datetime
    requirements: List[str]
    attachments: List[Dict[str, Any]]

class RegulatoryFilingResponse(BaseModel):
    """Regulatory filing response schema."""
    filing_id: str
    status: str
    submitted_at: datetime
    form_type: str
    period: str
    confirmation_number: Optional[str]
    validation_results: List[Dict[str, Any]]
    next_filing_date: datetime

class ComplianceMetrics(BaseModel):
    """Compliance metrics schema."""
    overall_score: float
    risk_level: str
    violation_trend: List[Dict[str, Any]]
    resolution_rate: float
    pending_approvals: int

class ComplianceStatusResponse(BaseModel):
    """Compliance status response schema."""
    timestamp: datetime
    metrics: ComplianceMetrics
    active_violations: int
    pending_tasks: List[Dict[str, Any]]
    upcoming_deadlines: List[Dict[str, Any]]
    recent_changes: List[Dict[str, Any]]
