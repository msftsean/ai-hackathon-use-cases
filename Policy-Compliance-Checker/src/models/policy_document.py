"""Policy document models."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import DocumentFormat, AnalysisStatus


class DocumentSection(BaseModel):
    """A section within a policy document."""

    title: str
    content: str
    page_number: Optional[int] = None
    start_offset: int = 0
    end_offset: int = 0


class PolicyDocument(BaseModel):
    """A policy document for compliance checking."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    format: DocumentFormat
    title: Optional[str] = None
    content: str
    sections: list[DocumentSection] = Field(default_factory=list)
    word_count: int = 0
    page_count: int = 1
    file_size_bytes: int = 0
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING
    metadata: dict = Field(default_factory=dict)

    def model_post_init(self, __context):
        """Calculate word count after initialization."""
        if self.content and not self.word_count:
            self.word_count = len(self.content.split())


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""

    id: str
    filename: str
    format: str
    word_count: int
    page_count: int
    uploaded_at: str


class DocumentListResponse(BaseModel):
    """Response for document listing."""

    documents: list[DocumentUploadResponse]
    total: int


__all__ = [
    "DocumentSection",
    "PolicyDocument",
    "DocumentUploadResponse",
    "DocumentListResponse",
]
