"""Extraction model representing extracted data fields from a document."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from . import PIIType, ValidationStatus


class BoundingBox(BaseModel):
    """Location of extracted field in the document."""

    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    width: float = Field(..., description="Width of bounding box")
    height: float = Field(..., description="Height of bounding box")
    page: int = Field(default=1, description="Page number (1-indexed)")


class Extraction(BaseModel):
    """
    Represents an extracted data field from a document with confidence and validation status.
    """

    # Primary key
    id: UUID = Field(default_factory=uuid4, description="Unique extraction identifier")

    # Document linkage
    document_id: UUID = Field(..., description="Foreign key to Document")

    # Extracted field data
    field_name: str = Field(..., description="Name of extracted field")
    field_value: str = Field(..., description="Extracted value")
    display_value: Optional[str] = Field(
        default=None, description="Formatted/masked value for display"
    )

    # Confidence scoring
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Extraction confidence (0.0-1.0)"
    )

    # Location in document
    bounding_box: Optional[BoundingBox] = Field(
        default=None, description="Location in document"
    )

    # PII handling
    is_pii: bool = Field(default=False, description="Whether field contains PII")
    pii_type: Optional[PIIType] = Field(default=None, description="Type of PII")

    # Validation
    validated: bool = Field(default=False, description="Whether validation was run")
    validation_status: Optional[ValidationStatus] = Field(
        default=None, description="Validation result"
    )
    validation_message: Optional[str] = Field(
        default=None, description="Validation error/warning message"
    )

    # Manual corrections
    manually_corrected: bool = Field(
        default=False, description="Whether worker corrected value"
    )
    original_value: Optional[str] = Field(
        default=None, description="Value before correction"
    )
    corrected_by: Optional[str] = Field(
        default=None, description="Worker who made correction"
    )
    corrected_at: Optional[datetime] = Field(
        default=None, description="When correction was made"
    )

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

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

    def get_display_value(self, include_pii: bool = False) -> str:
        """Get the display value, masking PII if not authorized."""
        if self.is_pii and not include_pii:
            return self.display_value or self._mask_value()
        return self.field_value

    def _mask_value(self) -> str:
        """Mask PII value for display."""
        if self.pii_type == PIIType.SSN:
            # Show only last 4 digits: XXX-XX-1234
            if len(self.field_value) >= 4:
                return f"XXX-XX-{self.field_value[-4:]}"
            return "XXX-XX-XXXX"
        elif self.pii_type == PIIType.BANK_ACCOUNT:
            # Show only last 4 digits
            if len(self.field_value) >= 4:
                return f"****{self.field_value[-4:]}"
            return "********"
        elif self.pii_type == PIIType.DATE_OF_BIRTH:
            # Show only year
            if "/" in self.field_value:
                parts = self.field_value.split("/")
                if len(parts) >= 3:
                    return f"**/**/****"
            return "**/**/****"
        else:
            # Generic masking
            if len(self.field_value) > 4:
                return "*" * (len(self.field_value) - 4) + self.field_value[-4:]
            return "*" * len(self.field_value)

    def correct(self, new_value: str, corrector_id: str) -> None:
        """Apply a manual correction to the extracted value."""
        if not self.manually_corrected:
            self.original_value = self.field_value
        self.field_value = new_value
        self.manually_corrected = True
        self.corrected_by = corrector_id
        self.corrected_at = datetime.utcnow()
        # Update confidence to 1.0 for manually corrected values
        self.confidence = 1.0

    def set_validation_result(
        self, status: ValidationStatus, message: Optional[str] = None
    ) -> None:
        """Set the validation result for this extraction."""
        self.validated = True
        self.validation_status = status
        self.validation_message = message
