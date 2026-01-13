"""ValidationRule model for configurable document validation rules."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from . import DocumentType, RuleType, Severity


class ValidationRule(BaseModel):
    """
    Configurable validation rules for document processing.
    Rules are matched by document type and applied during validation phase.
    """

    # Primary key
    id: UUID = Field(default_factory=uuid4, description="Unique rule identifier")

    # Rule identification
    name: str = Field(..., description="Rule name for display")
    document_type: DocumentType = Field(..., description="Applicable document type")
    rule_type: RuleType = Field(..., description="Type of validation")

    # Rule configuration
    field_name: Optional[str] = Field(
        default=None, description="Field to validate (if field-level)"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Rule parameters"
    )

    # Error handling
    error_message: str = Field(..., description="Message shown on failure")
    severity: Severity = Field(
        default=Severity.ERROR, description="error, warning, or info"
    )

    # Status
    active: bool = Field(default=True, description="Whether rule is enabled")

    # Audit
    created_by: str = Field(..., description="Who created the rule")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="When created"
    )
    updated_at: Optional[datetime] = Field(default=None, description="Last update")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return self.model_dump(mode="json")

    def update(self, **kwargs) -> None:
        """Update rule with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


# Pre-defined validation rules from data-model.md
DEFAULT_VALIDATION_RULES = [
    # Document age rules
    ValidationRule(
        name="Pay Stub Age",
        document_type=DocumentType.PAYSTUB,
        rule_type=RuleType.AGE,
        parameters={"max_age_days": 60},
        error_message="Pay stub must be dated within the last 60 days",
        severity=Severity.ERROR,
        created_by="system",
    ),
    ValidationRule(
        name="Bank Statement Age",
        document_type=DocumentType.BANK_STATEMENT,
        rule_type=RuleType.AGE,
        parameters={"max_age_days": 30},
        error_message="Bank statement must be dated within the last 30 days",
        severity=Severity.ERROR,
        created_by="system",
    ),
    ValidationRule(
        name="Utility Bill Age",
        document_type=DocumentType.UTILITY_BILL,
        rule_type=RuleType.AGE,
        parameters={"max_age_days": 60},
        error_message="Utility bill must be dated within the last 60 days",
        severity=Severity.ERROR,
        created_by="system",
    ),
    ValidationRule(
        name="W-2 Tax Year",
        document_type=DocumentType.W2,
        rule_type=RuleType.AGE,
        parameters={"max_age_years": 2},
        error_message="W-2 must be from the current or previous tax year",
        severity=Severity.ERROR,
        created_by="system",
    ),
    # Required field rules
    ValidationRule(
        name="W-2 Employer Name Required",
        document_type=DocumentType.W2,
        rule_type=RuleType.REQUIRED_FIELD,
        field_name="employer_name",
        parameters={},
        error_message="Employer name is required on W-2",
        severity=Severity.ERROR,
        created_by="system",
    ),
    ValidationRule(
        name="W-2 Wages Required",
        document_type=DocumentType.W2,
        rule_type=RuleType.REQUIRED_FIELD,
        field_name="wages",
        parameters={},
        error_message="Wages amount is required on W-2",
        severity=Severity.ERROR,
        created_by="system",
    ),
    ValidationRule(
        name="Pay Stub Employer Required",
        document_type=DocumentType.PAYSTUB,
        rule_type=RuleType.REQUIRED_FIELD,
        field_name="employer_name",
        parameters={},
        error_message="Employer name is required on pay stub",
        severity=Severity.ERROR,
        created_by="system",
    ),
    ValidationRule(
        name="Pay Stub Gross Pay Required",
        document_type=DocumentType.PAYSTUB,
        rule_type=RuleType.REQUIRED_FIELD,
        field_name="gross_pay",
        parameters={},
        error_message="Gross pay amount is required on pay stub",
        severity=Severity.ERROR,
        created_by="system",
    ),
    # Format validation rules
    ValidationRule(
        name="W-2 EIN Format",
        document_type=DocumentType.W2,
        rule_type=RuleType.FORMAT,
        field_name="employer_ein",
        parameters={"pattern": r"^\d{2}-\d{7}$"},
        error_message="Employer EIN must be in format XX-XXXXXXX",
        severity=Severity.WARNING,
        created_by="system",
    ),
    ValidationRule(
        name="SSN Format",
        document_type=DocumentType.W2,
        rule_type=RuleType.FORMAT,
        field_name="employee_ssn",
        parameters={"pattern": r"^\d{3}-\d{2}-\d{4}$"},
        error_message="SSN must be in format XXX-XX-XXXX",
        severity=Severity.WARNING,
        created_by="system",
    ),
    # Range validation rules
    ValidationRule(
        name="Wages Non-Negative",
        document_type=DocumentType.W2,
        rule_type=RuleType.RANGE,
        field_name="wages",
        parameters={"min": 0},
        error_message="Wages amount cannot be negative",
        severity=Severity.ERROR,
        created_by="system",
    ),
    ValidationRule(
        name="Gross Pay Non-Negative",
        document_type=DocumentType.PAYSTUB,
        rule_type=RuleType.RANGE,
        field_name="gross_pay",
        parameters={"min": 0},
        error_message="Gross pay cannot be negative",
        severity=Severity.ERROR,
        created_by="system",
    ),
]


def get_rules_for_document_type(doc_type: DocumentType) -> list[ValidationRule]:
    """Get all active validation rules for a document type."""
    return [
        rule for rule in DEFAULT_VALIDATION_RULES
        if rule.document_type == doc_type and rule.active
    ]
