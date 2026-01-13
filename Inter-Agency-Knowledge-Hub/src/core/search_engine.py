"""Search engine for Inter-Agency Knowledge Hub."""

import logging
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..config import get_settings
from ..models.enums import Agency, DocumentClassification
from ..models.search import SearchQuery, SearchResult, SearchResponse
from ..models.user import UserPermissions
from .citation_builder import CitationBuilder

logger = logging.getLogger("knowledge_hub")


class BaseSearchEngine(ABC):
    """Base class for search engine implementations."""

    def __init__(self):
        """Initialize search engine."""
        self.citation_builder = CitationBuilder()

    @abstractmethod
    async def search(
        self,
        query: SearchQuery,
        security_filter: str = "",
    ) -> SearchResponse:
        """Execute a search query."""
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[dict]:
        """Get a document by ID."""
        pass

    @abstractmethod
    async def index_document(self, document: dict, agency: Agency) -> bool:
        """Index a document."""
        pass


class SearchEngine(BaseSearchEngine):
    """Azure AI Search implementation."""

    def __init__(self):
        """Initialize Azure AI Search client."""
        super().__init__()
        settings = get_settings()
        self.endpoint = settings.azure_search_endpoint
        self.api_key = settings.azure_search_api_key
        self.index_prefix = settings.azure_search_index_prefix

        # In production, initialize Azure Search client
        # self.client = SearchClient(endpoint, index_name, credential)
        logger.info(f"Search engine initialized with endpoint: {self.endpoint}")

    def _get_index_name(self, agency: Agency) -> str:
        """Get index name for an agency."""
        return f"{self.index_prefix}-{agency.value}"

    async def search(
        self,
        query: SearchQuery,
        security_filter: str = "",
    ) -> SearchResponse:
        """Execute search across agency indexes."""
        start_time = time.time()

        # In production, use Azure AI Search client
        # results = await self.client.search(query.query, filter=security_filter, ...)

        # For now, return empty response (mock service should be used)
        processing_time = int((time.time() - start_time) * 1000)

        return SearchResponse(
            query_id=uuid4(),
            query=query.query,
            results=[],
            total_results=0,
            page=query.page,
            page_size=query.page_size,
            total_pages=0,
            agencies_searched=query.agencies or list(Agency),
            processing_time_ms=processing_time,
        )

    async def get_document(self, document_id: str) -> Optional[dict]:
        """Get a document by ID from any agency index."""
        # In production, search across all indexes for the document
        return None

    async def index_document(self, document: dict, agency: Agency) -> bool:
        """Index a document in the agency's index."""
        # In production, use Azure AI Search client to index
        return False


class MockSearchEngine(BaseSearchEngine):
    """Mock search engine for offline development."""

    # Sample documents for demonstration
    MOCK_DOCUMENTS = [
        {
            "id": "dmv-001",
            "title": "Remote Work Policy for DMV Employees",
            "content": "This policy outlines the guidelines for remote work arrangements at the Department of Motor Vehicles. Employees may work remotely up to 3 days per week with supervisor approval.",
            "summary": "Guidelines for remote work arrangements at DMV.",
            "agency": "dmv",
            "classification": "internal",
            "allowed_groups": ["DMV_Staff", "DMV_Manager", "AllAgencies_Admin"],
            "keywords": ["remote work", "telework", "work from home", "flexible work"],
            "publication_date": "2024-01-15T00:00:00",
            "version": "2.0",
            "document_type": "policy",
            "source_url": "https://dmv.ny.gov/documents/remote-work-policy",
        },
        {
            "id": "dol-001",
            "title": "Remote Work Guidelines for State Employees",
            "content": "The Department of Labor establishes these guidelines for remote work across all state agencies. Remote work must not interfere with service delivery.",
            "summary": "State-wide remote work guidelines from DOL.",
            "agency": "dol",
            "classification": "public",
            "allowed_groups": [],
            "keywords": ["remote work", "telework", "state employees", "guidelines"],
            "publication_date": "2024-02-01T00:00:00",
            "version": "1.0",
            "document_type": "guideline",
            "source_url": "https://dol.ny.gov/policies/remote-work-guidelines",
        },
        {
            "id": "doh-001",
            "title": "Health and Safety Requirements for Remote Workers",
            "content": "Department of Health guidelines for maintaining health and safety standards while working remotely. Includes ergonomic recommendations.",
            "summary": "Health and safety standards for remote work.",
            "agency": "doh",
            "classification": "public",
            "allowed_groups": [],
            "keywords": ["health", "safety", "ergonomics", "remote work"],
            "publication_date": "2024-01-20T00:00:00",
            "version": "1.0",
            "document_type": "guideline",
            "source_url": "https://health.ny.gov/regulations/remote-work-safety",
        },
        {
            "id": "otda-001",
            "title": "Public Assistance Eligibility Guidelines",
            "content": "This document outlines eligibility requirements for public assistance programs administered by OTDA, including income limits and documentation requirements.",
            "summary": "Eligibility requirements for OTDA assistance programs.",
            "agency": "otda",
            "classification": "public",
            "allowed_groups": [],
            "keywords": ["public assistance", "eligibility", "income limits", "benefits"],
            "publication_date": "2024-03-01T00:00:00",
            "version": "3.0",
            "document_type": "policy",
            "source_url": "https://otda.ny.gov/resources/eligibility-guidelines",
        },
        {
            "id": "ogs-001",
            "title": "State Procurement Procedures",
            "content": "Office of General Services procurement procedures for state agencies. Includes competitive bidding requirements and contract management.",
            "summary": "Procurement procedures for state agencies.",
            "agency": "ogs",
            "classification": "internal",
            "allowed_groups": ["OGS_Staff", "AllAgencies_Admin"],
            "keywords": ["procurement", "bidding", "contracts", "purchasing"],
            "publication_date": "2024-02-15T00:00:00",
            "version": "4.0",
            "document_type": "procedure",
            "source_url": "https://ogs.ny.gov/procurement/procedures",
        },
        {
            "id": "dmv-002",
            "title": "Driver License Renewal Procedures - Confidential",
            "content": "Internal procedures for processing driver license renewals including security verification steps and fraud detection measures.",
            "summary": "Internal procedures for license renewal processing.",
            "agency": "dmv",
            "classification": "confidential",
            "allowed_groups": ["DMV_Admin"],
            "keywords": ["license renewal", "security", "fraud detection", "procedures"],
            "publication_date": "2024-01-10T00:00:00",
            "version": "5.0",
            "document_type": "procedure",
            "source_url": "https://dmv.ny.gov/internal/license-renewal",
        },
        {
            "id": "dol-002",
            "title": "Unemployment Insurance Claims Processing",
            "content": "Guidelines for processing unemployment insurance claims including verification procedures and appeal handling.",
            "summary": "UI claims processing guidelines.",
            "agency": "dol",
            "classification": "restricted",
            "allowed_groups": ["DOL_Manager", "DOL_Admin"],
            "keywords": ["unemployment", "claims", "benefits", "appeals"],
            "publication_date": "2024-02-20T00:00:00",
            "version": "2.0",
            "document_type": "guideline",
            "source_url": "https://dol.ny.gov/policies/ui-claims-processing",
        },
        {
            "id": "doh-002",
            "title": "Healthcare Facility Inspection Standards",
            "content": "Standards and procedures for inspecting healthcare facilities in New York State.",
            "summary": "Healthcare facility inspection standards.",
            "agency": "doh",
            "classification": "internal",
            "allowed_groups": ["DOH_Staff", "DOH_Manager"],
            "keywords": ["inspection", "healthcare", "facilities", "standards"],
            "publication_date": "2024-03-15T00:00:00",
            "version": "1.5",
            "document_type": "standard",
            "source_url": "https://health.ny.gov/regulations/facility-inspection",
        },
    ]

    def __init__(self):
        """Initialize mock search engine."""
        super().__init__()
        self._documents = {doc["id"]: doc for doc in self.MOCK_DOCUMENTS}
        logger.info("Mock search engine initialized with sample documents")

    async def search(
        self,
        query: SearchQuery,
        security_filter: str = "",
    ) -> SearchResponse:
        """Execute mock search."""
        start_time = time.time()

        # Filter documents by agencies if specified
        agencies = query.agencies or list(Agency)
        agency_values = [a.value for a in agencies]

        # Simple text search
        search_terms = query.query.lower().split()
        results = []

        for doc in self.MOCK_DOCUMENTS:
            # Filter by agency
            if doc["agency"] not in agency_values:
                continue

            # Calculate relevance score based on term matches
            score = self._calculate_relevance(doc, search_terms)
            if score > 0:
                results.append((doc, score))

        # Sort by relevance
        results.sort(key=lambda x: x[1], reverse=True)

        # Apply pagination
        total_results = len(results)
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        page_results = results[start_idx:end_idx]

        # Convert to SearchResult objects
        search_results = []
        for doc, score in page_results:
            citation = self.citation_builder.build_citation_from_search_hit(doc)
            snippet = self._generate_snippet(doc["content"], search_terms)

            search_results.append(
                SearchResult(
                    document_id=doc["id"],
                    title=doc["title"],
                    agency=Agency(doc["agency"]),
                    relevance_score=min(score / 10, 1.0),  # Normalize score
                    snippet=snippet if query.include_snippets else "",
                    publication_date=datetime.fromisoformat(doc["publication_date"]),
                    document_type=doc["document_type"],
                    citation=citation,
                )
            )

        processing_time = int((time.time() - start_time) * 1000)
        total_pages = (total_results + query.page_size - 1) // query.page_size

        # Generate suggestions if no results
        suggestions = []
        if not search_results:
            suggestions = self._generate_suggestions(query.query)

        return SearchResponse(
            query_id=uuid4(),
            query=query.query,
            results=search_results,
            total_results=total_results,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages,
            agencies_searched=agencies,
            processing_time_ms=processing_time,
            suggestions=suggestions,
        )

    def _calculate_relevance(self, doc: dict, search_terms: list[str]) -> float:
        """Calculate relevance score for a document."""
        score = 0.0
        searchable_text = (
            f"{doc['title']} {doc['content']} {doc['summary']} "
            f"{' '.join(doc['keywords'])}"
        ).lower()

        for term in search_terms:
            # Title match (highest weight)
            if term in doc["title"].lower():
                score += 5.0
            # Keyword match
            if any(term in kw.lower() for kw in doc["keywords"]):
                score += 3.0
            # Content match
            if term in doc["content"].lower():
                score += 1.0
            # Summary match
            if term in doc["summary"].lower():
                score += 2.0

        return score

    def _generate_snippet(self, content: str, search_terms: list[str]) -> str:
        """Generate a highlighted snippet from content."""
        # Find the first occurrence of any search term
        content_lower = content.lower()
        best_pos = len(content)

        for term in search_terms:
            pos = content_lower.find(term)
            if pos != -1 and pos < best_pos:
                best_pos = pos

        # Extract snippet around the match
        start = max(0, best_pos - 50)
        end = min(len(content), best_pos + 150)
        snippet = content[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        # Highlight search terms
        for term in search_terms:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            snippet = pattern.sub(f"**{term}**", snippet)

        return snippet

    def _generate_suggestions(self, query: str) -> list[str]:
        """Generate search suggestions for empty results."""
        suggestions = []

        # Check for common misspellings or alternatives
        query_lower = query.lower()

        if "remote" in query_lower:
            suggestions.append("Try 'telework' or 'work from home'")
        if "license" in query_lower:
            suggestions.append("Try 'driver license' or 'permit'")
        if "benefit" in query_lower:
            suggestions.append("Try 'public assistance' or 'eligibility'")

        if not suggestions:
            suggestions = [
                "Try using different keywords",
                "Broaden your search to more agencies",
                "Check spelling of search terms",
            ]

        return suggestions[:3]

    async def get_document(self, document_id: str) -> Optional[dict]:
        """Get a document by ID."""
        return self._documents.get(document_id)

    async def index_document(self, document: dict, agency: Agency) -> bool:
        """Index a new document."""
        doc_id = document.get("id", str(uuid4()))
        document["id"] = doc_id
        document["agency"] = agency.value
        self._documents[doc_id] = document
        logger.info(f"Indexed document {doc_id} for agency {agency.value}")
        return True


def get_search_engine() -> BaseSearchEngine:
    """Get the appropriate search engine based on settings."""
    settings = get_settings()
    if settings.use_mock_services:
        return MockSearchEngine()
    return SearchEngine()
