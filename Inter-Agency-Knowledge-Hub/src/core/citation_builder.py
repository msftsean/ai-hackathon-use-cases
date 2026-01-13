"""Citation builder for LOADinG Act compliance."""

import logging
from datetime import datetime
from typing import Optional

from ..models.document import DocumentCitation, IndexedDocument
from ..models.enums import Agency

logger = logging.getLogger("knowledge_hub")


class CitationBuilder:
    """Build standardized citations for documents."""

    # Agency base URLs for document links
    AGENCY_BASE_URLS = {
        Agency.DMV: "https://dmv.ny.gov/documents",
        Agency.DOL: "https://dol.ny.gov/policies",
        Agency.OTDA: "https://otda.ny.gov/resources",
        Agency.DOH: "https://health.ny.gov/regulations",
        Agency.OGS: "https://ogs.ny.gov/procurement",
    }

    def __init__(self):
        """Initialize citation builder."""
        self.default_format = "chicago"

    def build_citation(
        self,
        document_id: str,
        title: str,
        agency: Agency,
        publication_date: datetime,
        version: str = "1.0",
        source_url: Optional[str] = None,
    ) -> DocumentCitation:
        """Build a citation for a document."""
        # Generate URL if not provided
        if not source_url:
            base_url = self.AGENCY_BASE_URLS.get(agency, "https://ny.gov")
            source_url = f"{base_url}/{document_id}"

        citation = DocumentCitation(
            document_id=document_id,
            title=title,
            agency=agency,
            publication_date=publication_date,
            version=version,
            direct_url=source_url,
        )

        return citation

    def build_citation_from_document(
        self, document: IndexedDocument
    ) -> DocumentCitation:
        """Build a citation from an IndexedDocument."""
        return self.build_citation(
            document_id=str(document.id),
            title=document.title,
            agency=document.agency,
            publication_date=document.publication_date,
            version=document.version,
            source_url=document.source_url,
        )

    def build_citation_from_search_hit(self, hit: dict) -> DocumentCitation:
        """Build a citation from an Azure AI Search hit."""
        try:
            agency = Agency(hit.get("agency", "dmv"))
        except ValueError:
            agency = Agency.DMV

        try:
            pub_date = datetime.fromisoformat(
                hit.get("publication_date", datetime.now().isoformat())
            )
        except ValueError:
            pub_date = datetime.now()

        return self.build_citation(
            document_id=hit.get("id", ""),
            title=hit.get("title", "Untitled Document"),
            agency=agency,
            publication_date=pub_date,
            version=hit.get("version", "1.0"),
            source_url=hit.get("source_url"),
        )

    def format_citation(
        self,
        citation: DocumentCitation,
        style: str = "chicago",
    ) -> str:
        """Format a citation in the specified style."""
        if style == "chicago":
            return self._format_chicago(citation)
        elif style == "apa":
            return self._format_apa(citation)
        elif style == "mla":
            return self._format_mla(citation)
        elif style == "plain":
            return self._format_plain(citation)
        else:
            return citation.citation_format

    def _format_chicago(self, citation: DocumentCitation) -> str:
        """Format citation in Chicago style."""
        return (
            f'{citation.agency.full_name}. "{citation.title}." '
            f"Version {citation.version}. "
            f"Published {citation.publication_date.strftime('%B %d, %Y')}. "
            f"{citation.direct_url}"
        )

    def _format_apa(self, citation: DocumentCitation) -> str:
        """Format citation in APA style."""
        return (
            f"{citation.agency.full_name}. "
            f"({citation.publication_date.strftime('%Y')}). "
            f"{citation.title} "
            f"(Version {citation.version}). "
            f"Retrieved from {citation.direct_url}"
        )

    def _format_mla(self, citation: DocumentCitation) -> str:
        """Format citation in MLA style."""
        return (
            f'"{citation.title}." '
            f"{citation.agency.full_name}, "
            f"{citation.publication_date.strftime('%d %b. %Y')}, "
            f"{citation.direct_url}."
        )

    def _format_plain(self, citation: DocumentCitation) -> str:
        """Format citation in plain text."""
        return (
            f"{citation.title} - {citation.agency.full_name} "
            f"({citation.publication_date.strftime('%Y-%m-%d')}) "
            f"[{citation.direct_url}]"
        )

    def build_citation_list(
        self,
        citations: list[DocumentCitation],
        style: str = "chicago",
    ) -> str:
        """Build a formatted list of citations."""
        formatted = []
        for i, citation in enumerate(citations, 1):
            formatted_citation = self.format_citation(citation, style)
            formatted.append(f"[{i}] {formatted_citation}")
        return "\n".join(formatted)

    def validate_citation(self, citation: DocumentCitation) -> list[str]:
        """Validate a citation for completeness."""
        issues = []

        if not citation.document_id:
            issues.append("Missing document ID")
        if not citation.title:
            issues.append("Missing title")
        if not citation.direct_url:
            issues.append("Missing document URL")
        if citation.publication_date > datetime.now():
            issues.append("Publication date is in the future")

        return issues
