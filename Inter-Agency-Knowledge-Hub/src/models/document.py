"""Document models for Inter-Agency Knowledge Hub."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .enums import Agency, DocumentClassification


class DocumentCitation(BaseModel):
    """Citation metadata for LOADinG Act compliance."""

    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    agency: Agency = Field(..., description="Source agency")
    publication_date: datetime = Field(..., description="Original publication date")
    version: str = Field(default="1.0", description="Document version")
    direct_url: str = Field(..., description="Direct link to original document")
    citation_format: str = Field(
        default="",
        description="Formatted citation string",
    )

    def model_post_init(self, __context) -> None:
        """Generate citation format after initialization."""
        if not self.citation_format:
            self.citation_format = (
                f"{self.agency.full_name}. \"{self.title}.\" "
                f"Version {self.version}. "
                f"Published {self.publication_date.strftime('%B %d, %Y')}. "
                f"Retrieved from {self.direct_url}"
            )


class IndexedDocument(BaseModel):
    """Document indexed in Azure AI Search with permission metadata."""

    id: UUID = Field(default_factory=uuid4, description="Unique document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Full document content")
    summary: str = Field(default="", description="Document summary")
    agency: Agency = Field(..., description="Source agency")
    classification: DocumentClassification = Field(
        default=DocumentClassification.PUBLIC,
        description="Document classification level",
    )
    allowed_groups: list[str] = Field(
        default_factory=list,
        description="Entra ID groups allowed to access this document",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Document keywords for search",
    )
    publication_date: datetime = Field(
        default_factory=datetime.now,
        description="Document publication date",
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp",
    )
    version: str = Field(default="1.0", description="Document version")
    document_type: str = Field(default="policy", description="Type of document")
    source_url: str = Field(default="", description="Original document URL")
    embedding_vector: Optional[list[float]] = Field(
        default=None,
        description="Document embedding for semantic search",
    )

    @property
    def citation(self) -> DocumentCitation:
        """Generate citation for this document."""
        return DocumentCitation(
            document_id=str(self.id),
            title=self.title,
            agency=self.agency,
            publication_date=self.publication_date,
            version=self.version,
            direct_url=self.source_url or f"/api/v1/documents/{self.id}",
        )

    def to_search_document(self) -> dict:
        """Convert to Azure AI Search document format."""
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "agency": self.agency.value,
            "classification": self.classification.value,
            "allowed_groups": self.allowed_groups,
            "keywords": self.keywords,
            "publication_date": self.publication_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "version": self.version,
            "document_type": self.document_type,
            "source_url": self.source_url,
        }
