"""Compliance rule models."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import Severity, RuleCategory


class ComplianceRule(BaseModel):
    """A compliance rule for policy checking."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    pattern: str  # Regex pattern
    severity: Severity
    category: RuleCategory
    recommendation_template: str
    is_builtin: bool = True
    enabled: bool = True
    keywords: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RuleCreateRequest(BaseModel):
    """Request to create a custom rule."""

    name: str
    description: str
    pattern: str
    severity: Severity
    category: RuleCategory = RuleCategory.CUSTOM
    recommendation_template: str
    keywords: list[str] = Field(default_factory=list)


class RuleUpdateRequest(BaseModel):
    """Request to update a rule."""

    name: Optional[str] = None
    description: Optional[str] = None
    pattern: Optional[str] = None
    severity: Optional[Severity] = None
    recommendation_template: Optional[str] = None
    keywords: Optional[list[str]] = None
    enabled: Optional[bool] = None


class RuleResponse(BaseModel):
    """Response for a compliance rule."""

    id: str
    name: str
    description: str
    severity: str
    category: str
    is_builtin: bool
    enabled: bool


class RuleListResponse(BaseModel):
    """Response for rule listing."""

    rules: list[RuleResponse]
    total: int


__all__ = [
    "ComplianceRule",
    "RuleCreateRequest",
    "RuleUpdateRequest",
    "RuleResponse",
    "RuleListResponse",
]
