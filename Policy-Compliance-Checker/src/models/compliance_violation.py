"""Compliance violation models."""

from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .compliance_rule import ComplianceRule


class ComplianceViolation(BaseModel):
    """A compliance violation found in a document."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    rule_id: str
    rule_name: str
    severity: str
    category: str
    matched_text: str
    context: str  # Surrounding text for context
    location: str  # Section or page reference
    start_offset: int
    end_offset: int
    recommendation: str


class ViolationSummary(BaseModel):
    """Summary of violations by severity."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0


__all__ = ["ComplianceViolation", "ViolationSummary"]
