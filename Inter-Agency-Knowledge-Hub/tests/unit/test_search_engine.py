"""Unit tests for SearchEngine."""

import pytest
from datetime import datetime

from src.core.search_engine import MockSearchEngine
from src.models.search import SearchQuery
from src.models.enums import Agency


@pytest.fixture
def search_engine():
    """Create mock search engine."""
    return MockSearchEngine()


class TestMockSearchEngine:
    """Tests for MockSearchEngine."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self, search_engine):
        """Test that search returns results."""
        query = SearchQuery(query="remote work")
        response = await search_engine.search(query)

        assert response is not None
        assert response.query == "remote work"
        assert response.total_results > 0
        assert len(response.results) > 0

    @pytest.mark.asyncio
    async def test_search_filters_by_agency(self, search_engine):
        """Test search filters by agency."""
        query = SearchQuery(query="remote work", agencies=[Agency.DMV])
        response = await search_engine.search(query)

        for result in response.results:
            assert result.agency == Agency.DMV

    @pytest.mark.asyncio
    async def test_search_pagination(self, search_engine):
        """Test search pagination."""
        query = SearchQuery(query="policy", page=1, page_size=2)
        response = await search_engine.search(query)

        assert response.page == 1
        assert response.page_size == 2
        assert len(response.results) <= 2

    @pytest.mark.asyncio
    async def test_search_includes_snippets(self, search_engine):
        """Test search includes snippets when requested."""
        query = SearchQuery(query="remote work", include_snippets=True)
        response = await search_engine.search(query)

        if response.results:
            assert response.results[0].snippet != ""

    @pytest.mark.asyncio
    async def test_search_no_results_returns_suggestions(self, search_engine):
        """Test empty results include suggestions."""
        query = SearchQuery(query="xyznonexistent123")
        response = await search_engine.search(query)

        assert response.total_results == 0
        assert len(response.suggestions) > 0

    @pytest.mark.asyncio
    async def test_search_results_have_citations(self, search_engine):
        """Test search results include citations."""
        query = SearchQuery(query="remote work")
        response = await search_engine.search(query)

        if response.results:
            result = response.results[0]
            assert result.citation is not None
            assert result.citation.title != ""
            assert result.citation.direct_url != ""

    @pytest.mark.asyncio
    async def test_get_document_returns_document(self, search_engine):
        """Test getting a document by ID."""
        doc = await search_engine.get_document("dmv-001")

        assert doc is not None
        assert doc["id"] == "dmv-001"
        assert doc["agency"] == "dmv"

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, search_engine):
        """Test getting non-existent document."""
        doc = await search_engine.get_document("nonexistent")

        assert doc is None

    @pytest.mark.asyncio
    async def test_relevance_scoring(self, search_engine):
        """Test results are sorted by relevance."""
        query = SearchQuery(query="remote work policy")
        response = await search_engine.search(query)

        if len(response.results) > 1:
            scores = [r.relevance_score for r in response.results]
            assert scores == sorted(scores, reverse=True)
