"""Compliance report models."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .compliance_violation import ComplianceViolation, ViolationSummary


class ReportSummary(BaseModel):
    """Summary section of a compliance report."""

    document_id: str
    document_name: str
    total_rules_applied: int
    violations: ViolationSummary
    compliance_score: float  # 0-100
    analysis_time_ms: int
    ai_insights_available: bool = False


class ComplianceReport(BaseModel):
    """A complete compliance analysis report."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    document_name: str
    summary: ReportSummary
    violations: list[ComplianceViolation] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    ai_insights: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: int = 0


class ReportExportRequest(BaseModel):
    """Request to export a report."""

    format: str = "json"  # json, html


class ReportResponse(BaseModel):
    """Response for a compliance report."""

    id: str
    document_id: str
    document_name: str
    compliance_score: float
    violation_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    generated_at: str


__all__ = [
    "ReportSummary",
    "ComplianceReport",
    "ReportExportRequest",
    "ReportResponse",
]
