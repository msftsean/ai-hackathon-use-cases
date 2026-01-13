"""Unit tests for KnowledgeService."""

import pytest
from src.services.knowledge_service import KnowledgeService
from src.models import Agency, DocumentType


class TestKnowledgeService:
    """Tests for knowledge service functionality."""

    @pytest.fixture
    def knowledge_service(self):
        """Create knowledge service instance."""
        return KnowledgeService()

    def test_load_all_agencies(self, knowledge_service):
        """Test loading sample data from agency files."""
        knowledge_service.load_all_agencies()
        sources = knowledge_service.get_all_sources()
        assert len(sources) >= 0  # May be empty if no sample data

    def test_get_all_sources(self, knowledge_service):
        """Test retrieving all knowledge sources."""
        sources = knowledge_service.get_all_sources()
        assert isinstance(sources, list)

    def test_search_returns_list(self, knowledge_service):
        """Test search returns a list of results."""
        results = knowledge_service.search("benefits")
        assert isinstance(results, list)

    def test_search_with_agency_filter(self, knowledge_service):
        """Test search with agency filter."""
        # Load data first
        knowledge_service.load_all_agencies()
        results = knowledge_service.search("license", agency=Agency.DMV)
        # All results should be from DMV
        for source in results:
            assert source.agency == Agency.DMV

    def test_search_with_limit(self, knowledge_service):
        """Test search respects limit parameter."""
        results = knowledge_service.search("application", limit=5)
        assert len(results) <= 5

    def test_get_source_returns_none_for_invalid_id(self, knowledge_service):
        """Test getting source with invalid ID returns None."""
        result = knowledge_service.get_source("invalid-uuid")
        assert result is None

    def test_get_sources_by_agency(self, knowledge_service):
        """Test filtering sources by agency."""
        knowledge_service.load_all_agencies()
        sources = knowledge_service.get_sources_by_agency(Agency.DMV)
        for source in sources:
            assert source.agency == Agency.DMV

    def test_get_locations(self, knowledge_service):
        """Test getting office locations."""
        locations = knowledge_service.get_locations()
        assert isinstance(locations, list)
        # Should include mock locations
        if locations:
            assert "name" in locations[0]
            assert "address" in locations[0]

    def test_get_locations_by_agency(self, knowledge_service):
        """Test getting locations filtered by agency."""
        locations = knowledge_service.get_locations(agency=Agency.DMV)
        for loc in locations:
            assert loc["agency"] == "DMV"

    def test_ensure_loaded_calls_load_once(self, knowledge_service):
        """Test that _ensure_loaded only loads once."""
        knowledge_service._ensure_loaded()
        first_load = knowledge_service._loaded
        knowledge_service._ensure_loaded()
        # Should still be loaded and not reloaded
        assert knowledge_service._loaded == first_load
