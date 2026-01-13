"""Enumerations for Policy Compliance Checker."""

from enum import Enum


class Severity(str, Enum):
    """Severity levels for compliance violations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def weight(self) -> int:
        """Get severity weight for scoring."""
        weights = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 5,
            Severity.LOW: 1,
        }
        return weights[self]


class DocumentFormat(str, Enum):
    """Supported document formats."""

    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    TEXT = "text"


class RuleCategory(str, Enum):
    """Categories for compliance rules."""

    DATA_PROTECTION = "data_protection"
    HR_POLICY = "hr_policy"
    IT_SECURITY = "it_security"
    LEGAL_COMPLIANCE = "legal_compliance"
    ACCESSIBILITY = "accessibility"
    CUSTOM = "custom"


class AnalysisStatus(str, Enum):
    """Status of document analysis."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


__all__ = ["Severity", "DocumentFormat", "RuleCategory", "AnalysisStatus"]
