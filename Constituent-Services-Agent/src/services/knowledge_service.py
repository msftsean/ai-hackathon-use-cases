"""
Knowledge Service for Constituent Services Agent.

Loads and manages agency content from sample_data directory.
"""

import json
import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4

from src.models import Agency, DocumentType, IndexingStatus, KnowledgeSource

logger = logging.getLogger(__name__)

# Path to sample data directory
SAMPLE_DATA_DIR = Path(__file__).parent.parent.parent / "sample_data" / "nys_agencies"


class KnowledgeService:
    """
    Service for loading and managing agency knowledge content.

    Loads sample data from JSON files for offline development.
    """

    def __init__(self):
        """Initialize knowledge service."""
        self._sources: dict[str, KnowledgeSource] = {}
        self._loaded = False

    def _ensure_loaded(self):
        """Ensure sample data is loaded."""
        if not self._loaded:
            self.load_all_agencies()

    def load_all_agencies(self):
        """Load sample data from all agency JSON files."""
        if not SAMPLE_DATA_DIR.exists():
            logger.warning(f"Sample data directory not found: {SAMPLE_DATA_DIR}")
            return

        for json_file in SAMPLE_DATA_DIR.glob("*.json"):
            try:
                self._load_agency_file(json_file)
            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")

        self._loaded = True
        logger.info(f"Loaded {len(self._sources)} knowledge sources")

    def _load_agency_file(self, file_path: Path):
        """Load knowledge sources from a single agency JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        agency_code = data.get("agency", file_path.stem.upper())

        for doc in data.get("documents", []):
            source = KnowledgeSource(
                id=uuid4(),
                agency=Agency(agency_code),
                title=doc.get("title", "Untitled"),
                content=doc.get("content", ""),
                summary=doc.get("summary"),
                url=doc.get("url", f"https://{agency_code.lower()}.ny.gov"),
                document_type=DocumentType(doc.get("type", "webpage")),
                indexing_status=IndexingStatus.INDEXED,
                chunk_count=len(doc.get("content", "")) // 500 + 1,
            )
            self._sources[str(source.id)] = source

    def get_source(self, source_id: str) -> Optional[KnowledgeSource]:
        """
        Get a knowledge source by ID.

        Args:
            source_id: UUID of the knowledge source

        Returns:
            KnowledgeSource if found, None otherwise
        """
        self._ensure_loaded()
        return self._sources.get(source_id)

    def get_sources_by_agency(self, agency: Agency) -> list[KnowledgeSource]:
        """
        Get all knowledge sources for an agency.

        Args:
            agency: Agency enum value

        Returns:
            List of knowledge sources for the agency
        """
        self._ensure_loaded()
        return [s for s in self._sources.values() if s.agency == agency]

    def search(
        self,
        query: str,
        agency: Optional[Agency] = None,
        document_type: Optional[DocumentType] = None,
        limit: int = 10,
    ) -> list[KnowledgeSource]:
        """
        Simple keyword search across knowledge sources.

        Args:
            query: Search query
            agency: Optional agency filter
            document_type: Optional document type filter
            limit: Maximum results to return

        Returns:
            List of matching knowledge sources
        """
        self._ensure_loaded()

        query_lower = query.lower()
        results = []

        for source in self._sources.values():
            # Apply filters
            if agency and source.agency != agency:
                continue
            if document_type and source.document_type != document_type:
                continue

            # Simple keyword matching
            if (
                query_lower in source.title.lower()
                or query_lower in source.content.lower()
                or (source.summary and query_lower in source.summary.lower())
            ):
                results.append(source)

            if len(results) >= limit:
                break

        return results

    def get_all_sources(self) -> list[KnowledgeSource]:
        """Get all knowledge sources."""
        self._ensure_loaded()
        return list(self._sources.values())

    def get_locations(
        self,
        agency: Optional[Agency] = None,
        service_type: Optional[str] = None,
        near_location: Optional[str] = None,
    ) -> list[dict]:
        """
        Get office locations for agencies.

        Args:
            agency: Optional agency filter
            service_type: Optional service type filter
            near_location: Optional location for proximity search

        Returns:
            List of location dictionaries
        """
        self._ensure_loaded()

        # For MVP, return mock locations
        locations = []

        if agency == Agency.DMV or agency is None:
            locations.extend([
                {
                    "agency": "DMV",
                    "name": "Albany DMV",
                    "address": "260 S Pearl St, Albany, NY 12202",
                    "hours": "Mon-Fri 8:30 AM - 4:00 PM",
                    "phone": "(518) 486-9786",
                    "accessibility": True,
                    "services": ["License Renewal", "Registration", "ID Cards"],
                },
                {
                    "agency": "DMV",
                    "name": "Troy DMV",
                    "address": "125 Adams St, Troy, NY 12180",
                    "hours": "Mon-Fri 9:00 AM - 4:00 PM",
                    "phone": "(518) 270-5340",
                    "accessibility": True,
                    "services": ["License Renewal", "Registration"],
                },
            ])

        if agency == Agency.OTDA or agency is None:
            locations.extend([
                {
                    "agency": "OTDA",
                    "name": "Albany County DSS",
                    "address": "162 Washington Ave, Albany, NY 12210",
                    "hours": "Mon-Fri 8:00 AM - 5:00 PM",
                    "phone": "(518) 447-7300",
                    "accessibility": True,
                    "services": ["SNAP", "Medicaid", "TANF"],
                },
            ])

        return locations
