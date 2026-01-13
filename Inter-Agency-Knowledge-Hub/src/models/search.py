"""Search models for Inter-Agency Knowledge Hub."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .enums import Agency
from .document import DocumentCitation


class SearchQuery(BaseModel):
    """Search query request model."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    agencies: Optional[list[Agency]] = Field(
        default=None,
        description="Agencies to search (None = all accessible)",
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Results per page")
    include_snippets: bool = Field(default=True, description="Include text snippets")
    date_from: Optional[datetime] = Field(default=None, description="Filter by date from")
    date_to: Optional[datetime] = Field(default=None, description="Filter by date to")
    document_types: Optional[list[str]] = Field(
        default=None,
        description="Filter by document types",
    )


class SearchResult(BaseModel):
    """Individual search result."""

    document_id: str = Field(..., description="Document identifier")
    title: str = Field(..., description="Document title")
    agency: Agency = Field(..., description="Source agency")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")
    snippet: str = Field(default="", description="Highlighted text snippet")
    publication_date: datetime = Field(..., description="Document publication date")
    document_type: str = Field(default="policy", description="Type of document")
    citation: DocumentCitation = Field(..., description="Full citation metadata")

    @classmethod
    def from_search_hit(cls, hit: dict, score: float) -> "SearchResult":
        """Create SearchResult from Azure AI Search hit."""
        agency = Agency(hit.get("agency", "dmv"))
        pub_date = datetime.fromisoformat(hit.get("publication_date", datetime.now().isoformat()))

        citation = DocumentCitation(
            document_id=hit.get("id", ""),
            title=hit.get("title", ""),
            agency=agency,
            publication_date=pub_date,
            version=hit.get("version", "1.0"),
            direct_url=hit.get("source_url", f"/api/v1/documents/{hit.get('id', '')}"),
        )

        return cls(
            document_id=hit.get("id", ""),
            title=hit.get("title", ""),
            agency=agency,
            relevance_score=score,
            snippet=hit.get("@search.highlights", {}).get("content", [""])[0] if "@search.highlights" in hit else hit.get("summary", ""),
            publication_date=pub_date,
            document_type=hit.get("document_type", "policy"),
            citation=citation,
        )


class SearchResponse(BaseModel):
    """Search response with results and metadata."""

    query_id: UUID = Field(default_factory=uuid4, description="Unique query identifier")
    query: str = Field(..., description="Original search query")
    results: list[SearchResult] = Field(default_factory=list, description="Search results")
    total_results: int = Field(default=0, description="Total matching documents")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=10, description="Results per page")
    total_pages: int = Field(default=0, description="Total pages")
    agencies_searched: list[Agency] = Field(
        default_factory=list,
        description="Agencies included in search",
    )
    processing_time_ms: int = Field(default=0, description="Processing time in milliseconds")
    suggestions: list[str] = Field(
        default_factory=list,
        description="Query suggestions for empty results",
    )
    requires_review: bool = Field(
        default=False,
        description="Whether query was flagged for review",
    )
    review_id: Optional[str] = Field(
        default=None,
        description="Review flag ID if requires_review is True",
    )


class SearchQuerySummary(BaseModel):
    """Summary of a search query for history tracking."""

    query_id: str = Field(..., description="Query identifier")
    query: str = Field(..., description="Search query text")
    result_count: int = Field(default=0, description="Number of results")
    agencies_searched: list[Agency] = Field(
        default_factory=list,
        description="Agencies searched",
    )
    searched_at: datetime = Field(
        default_factory=datetime.now,
        description="When search was performed",
    )
    user_id: str = Field(..., description="User who performed search")
