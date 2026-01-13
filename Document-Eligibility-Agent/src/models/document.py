"""Document model representing a submitted document with metadata and status tracking."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from . import DocumentPriority, DocumentSource, DocumentStatus, DocumentType, ValidationStatus


class Document(BaseModel):
    """
    Represents a submitted document with metadata, extracted content, and processing status.
    Linked to constituent case.
    """

    # Primary key
    id: UUID = Field(default_factory=uuid4, description="Unique document identifier")

    # Case linkage
    case_id: str = Field(..., description="Reference to eligibility case")

    # Document classification
    document_type: DocumentType = Field(..., description="Type of document")
    status: DocumentStatus = Field(
        default=DocumentStatus.UPLOADED, description="Processing status"
    )
    source: DocumentSource = Field(
        default=DocumentSource.UPLOAD, description="How document was received"
    )

    # File information
    filename: str = Field(..., description="Original filename")
    blob_url: Optional[str] = Field(default=None, description="Azure Blob Storage URL")
    content_hash: Optional[str] = Field(
        default=None, description="SHA-256 hash for deduplication"
    )
    file_size_bytes: int = Field(default=0, description="File size in bytes")
    mime_type: str = Field(default="application/pdf", description="MIME type")
    page_count: Optional[int] = Field(default=None, description="Number of pages")

    # Timestamps
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow, description="When document was received"
    )
    processed_at: Optional[datetime] = Field(
        default=None, description="When extraction completed"
    )

    # Assignment tracking
    assigned_to: Optional[str] = Field(default=None, description="Worker ID for review")
    assigned_at: Optional[datetime] = Field(default=None, description="When assigned")
    reviewed_at: Optional[datetime] = Field(
        default=None, description="When review completed"
    )
    reviewed_by: Optional[str] = Field(default=None, description="Reviewer ID")

    # Priority
    priority: DocumentPriority = Field(
        default=DocumentPriority.STANDARD, description="Processing priority"
    )

    # Duplicate detection
    is_duplicate: bool = Field(default=False, description="Flagged as duplicate")
    duplicate_of: Optional[UUID] = Field(
        default=None, description="Reference to original document"
    )

    # Processing results
    overall_confidence: Optional[float] = Field(
        default=None, description="Combined confidence score (0.0-1.0)"
    )
    validation_status: Optional[ValidationStatus] = Field(
        default=None, description="Overall validation result"
    )
    notes: Optional[str] = Field(default=None, description="Worker notes")

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

    def update_status(self, new_status: DocumentStatus) -> None:
        """Update document status with timestamp tracking."""
        self.status = new_status
        if new_status == DocumentStatus.EXTRACTED:
            self.processed_at = datetime.utcnow()

    def assign_to(self, worker_id: str) -> None:
        """Assign document to a worker for review."""
        self.assigned_to = worker_id
        self.assigned_at = datetime.utcnow()

    def mark_reviewed(self, reviewer_id: str, approved: bool, notes: Optional[str] = None) -> None:
        """Mark document as reviewed."""
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.status = DocumentStatus.APPROVED if approved else DocumentStatus.REJECTED
        if notes:
            self.notes = notes
