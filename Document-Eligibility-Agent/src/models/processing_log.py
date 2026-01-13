"""ProcessingLog model for audit trail (LOADinG Act compliance)."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from . import LogAction


class ProcessingLog(BaseModel):
    """
    Audit trail for LOADinG Act compliance.
    Records all processing steps and user actions.

    These records are immutable - no updates allowed.
    Retention: 7 years per compliance requirement.
    """

    # Primary key
    id: UUID = Field(default_factory=uuid4, description="Unique log entry identifier")

    # Document linkage
    document_id: UUID = Field(..., description="Foreign key to Document")

    # Action details
    action: LogAction = Field(..., description="Action performed")
    actor: str = Field(
        ..., description="User ID or 'system' for automated actions"
    )
    actor_role: Optional[str] = Field(
        default=None, description="Role of actor at time of action"
    )
    details: dict[str, Any] = Field(
        default_factory=dict, description="Action-specific details"
    )

    # Timing
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When action occurred"
    )
    duration_ms: Optional[int] = Field(
        default=None, description="Processing duration in milliseconds"
    )

    # Request context
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    session_id: Optional[str] = Field(default=None, description="User session ID")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        frozen = True  # Immutable after creation
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return self.model_dump(mode="json")

    @classmethod
    def create_upload_log(
        cls,
        document_id: UUID,
        actor: str,
        filename: str,
        file_size: int,
        source: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "ProcessingLog":
        """Create a log entry for document upload."""
        return cls(
            document_id=document_id,
            action=LogAction.UPLOADED,
            actor=actor,
            details={
                "filename": filename,
                "file_size_bytes": file_size,
                "source": source,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    def create_processing_log(
        cls,
        document_id: UUID,
        success: bool,
        duration_ms: int,
        extraction_count: int = 0,
        error_message: Optional[str] = None,
    ) -> "ProcessingLog":
        """Create a log entry for document processing."""
        action = LogAction.PROCESSING_COMPLETED if success else LogAction.PROCESSING_FAILED
        details = {
            "success": success,
            "extraction_count": extraction_count,
        }
        if error_message:
            details["error"] = error_message

        return cls(
            document_id=document_id,
            action=action,
            actor="system",
            details=details,
            duration_ms=duration_ms,
        )

    @classmethod
    def create_validation_log(
        cls,
        document_id: UUID,
        passed: bool,
        warnings: int = 0,
        errors: int = 0,
        duration_ms: Optional[int] = None,
    ) -> "ProcessingLog":
        """Create a log entry for validation completion."""
        return cls(
            document_id=document_id,
            action=LogAction.VALIDATION_COMPLETED,
            actor="system",
            details={
                "passed": passed,
                "warnings": warnings,
                "errors": errors,
            },
            duration_ms=duration_ms,
        )

    @classmethod
    def create_pii_access_log(
        cls,
        document_id: UUID,
        actor: str,
        actor_role: str,
        field_name: str,
        pii_type: str,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> "ProcessingLog":
        """Create a log entry for PII access."""
        return cls(
            document_id=document_id,
            action=LogAction.PII_ACCESSED,
            actor=actor,
            actor_role=actor_role,
            details={
                "field_name": field_name,
                "pii_type": pii_type,
            },
            ip_address=ip_address,
            session_id=session_id,
        )

    @classmethod
    def create_review_log(
        cls,
        document_id: UUID,
        actor: str,
        actor_role: str,
        approved: bool,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> "ProcessingLog":
        """Create a log entry for document review."""
        action = LogAction.APPROVED if approved else LogAction.REJECTED
        details = {"approved": approved}
        if notes:
            details["notes"] = notes

        return cls(
            document_id=document_id,
            action=action,
            actor=actor,
            actor_role=actor_role,
            details=details,
            ip_address=ip_address,
        )

    @classmethod
    def create_correction_log(
        cls,
        document_id: UUID,
        actor: str,
        field_name: str,
        original_value: str,
        new_value: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> "ProcessingLog":
        """Create a log entry for field correction."""
        return cls(
            document_id=document_id,
            action=LogAction.FIELD_CORRECTED,
            actor=actor,
            details={
                "field_name": field_name,
                "original_value": original_value,
                "new_value": new_value,
                "reason": reason,
            },
            ip_address=ip_address,
        )
