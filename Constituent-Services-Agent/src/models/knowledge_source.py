"""
KnowledgeSource and Citation models for Constituent Services Agent.

Represents indexed documents from agency knowledge bases and
citations linking agent responses to source documents.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from . import Agency, DocumentType, IndexingStatus


class KnowledgeSource(BaseModel):
    """
    Indexed document from agency knowledge base.

    Represents a document or webpage that has been indexed for
    retrieval by the AI agent.
    """

    id: UUID = Field(default_factory=uuid4, description="Document unique identifier")
    agency: Agency = Field(description="Agency code")
    title: str = Field(max_length=500, description="Document title")
    content: str = Field(description="Full document content")
    summary: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="AI-generated summary"
    )
    url: str = Field(description="Source URL for citation")
    document_type: DocumentType = Field(description="Type of document")
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last content update"
    )
    indexing_status: IndexingStatus = Field(
        default=IndexingStatus.PENDING,
        description="Indexing status"
    )
    chunk_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of indexed chunks"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format (relaxed for hackathon)."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "agency": "OTDA",
                "title": "SNAP Benefits Application Guide",
                "content": "To apply for SNAP benefits in New York State...",
                "url": "https://otda.ny.gov/programs/snap/apply.asp",
                "document_type": "guide",
                "last_updated": "2026-01-01T00:00:00Z",
                "indexing_status": "indexed",
                "chunk_count": 15,
            }
        }
    }


class Citation(BaseModel):
    """
    Links agent responses to source documents.

    Represents a citation to a specific passage in a knowledge source
    that supports a claim in an agent response.
    """

    id: UUID = Field(default_factory=uuid4, description="Citation unique identifier")
    message_id: UUID = Field(description="Foreign key to Message")
    source_id: UUID = Field(description="Foreign key to KnowledgeSource")
    quote: str = Field(max_length=500, description="Relevant quote from source")
    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Relevance to query (0.0-1.0)"
    )
    start_offset: Optional[int] = Field(
        default=None,
        ge=0,
        description="Character offset in source"
    )
    end_offset: Optional[int] = Field(
        default=None,
        ge=0,
        description="End character offset"
    )

    # Additional fields for display (not persisted, computed at response time)
    title: Optional[str] = Field(default=None, description="Source title for display")
    agency: Optional[str] = Field(default=None, description="Agency code for display")
    url: Optional[str] = Field(default=None, description="Source URL for display")

    @field_validator("end_offset")
    @classmethod
    def validate_offset_order(cls, v: Optional[int], info) -> Optional[int]:
        """Validate end_offset is greater than start_offset."""
        if v is not None and info.data.get("start_offset") is not None:
            if v <= info.data["start_offset"]:
                raise ValueError("end_offset must be greater than start_offset")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "8a6e0804-2bd0-4672-b79d-d97027f9071a",
                "message_id": "550e8400-e29b-41d4-a716-446655440000",
                "source_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "quote": "To apply for SNAP, you must complete an application form...",
                "relevance_score": 0.92,
                "title": "SNAP Benefits Application Guide",
                "agency": "OTDA",
                "url": "https://otda.ny.gov/programs/snap/apply.asp",
            }
        }
    }
