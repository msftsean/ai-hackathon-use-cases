"""Cross-reference models for Inter-Agency Knowledge Hub."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .enums import Agency, RelationshipType
from .document import DocumentCitation


class CrossReference(BaseModel):
    """Cross-reference between related documents."""

    id: UUID = Field(default_factory=uuid4, description="Unique cross-reference ID")
    source_document_id: str = Field(..., description="Source document ID")
    source_agency: Agency = Field(..., description="Source document agency")
    related_document_id: str = Field(..., description="Related document ID")
    related_agency: Agency = Field(..., description="Related document agency")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score")
    similarity_score: float = Field(default=0.0, ge=0, le=1, description="Vector similarity")
    explanation: str = Field(default="", description="Explanation of relationship")
    related_title: str = Field(default="", description="Related document title")
    related_snippet: str = Field(default="", description="Snippet from related document")
    related_citation: Optional[DocumentCitation] = Field(
        default=None,
        description="Citation for related document",
    )
    detected_at: datetime = Field(
        default_factory=datetime.now,
        description="When relationship was detected",
    )

    @property
    def is_cross_agency(self) -> bool:
        """Check if this is a cross-agency reference."""
        return self.source_agency != self.related_agency


class CrossReferenceRequest(BaseModel):
    """Request for finding cross-references."""

    document_id: str = Field(..., description="Document ID to find references for")
    relationship_types: Optional[list[RelationshipType]] = Field(
        default=None,
        description="Types of relationships to find",
    )
    min_confidence: float = Field(
        default=0.7,
        ge=0,
        le=1,
        description="Minimum confidence threshold",
    )
    max_results: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results",
    )
    include_same_agency: bool = Field(
        default=True,
        description="Include references within same agency",
    )
    agencies: Optional[list[Agency]] = Field(
        default=None,
        description="Limit to specific agencies",
    )


class CrossReferenceResponse(BaseModel):
    """Response containing cross-references for a document."""

    document_id: str = Field(..., description="Source document ID")
    document_title: str = Field(default="", description="Source document title")
    source_agency: Agency = Field(..., description="Source document agency")
    cross_references: list[CrossReference] = Field(
        default_factory=list,
        description="Found cross-references",
    )
    total_found: int = Field(default=0, description="Total references found")
    processing_time_ms: int = Field(default=0, description="Processing time")

    @property
    def cross_agency_count(self) -> int:
        """Count of cross-agency references."""
        return sum(1 for ref in self.cross_references if ref.is_cross_agency)

    @property
    def by_relationship_type(self) -> dict[RelationshipType, list[CrossReference]]:
        """Group references by relationship type."""
        result: dict[RelationshipType, list[CrossReference]] = {}
        for ref in self.cross_references:
            if ref.relationship_type not in result:
                result[ref.relationship_type] = []
            result[ref.relationship_type].append(ref)
        return result
