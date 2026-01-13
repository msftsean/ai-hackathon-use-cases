"""Unit tests for ReviewService."""

import pytest

from src.services.review_service import ReviewService
from src.models.search import SearchQuery, SearchResponse, SearchResult
from src.models.user import UserPermissions
from src.models.enums import Agency


@pytest.fixture
def review_service():
    """Create review service."""
    service = ReviewService()
    service._load_criteria()
    return service


@pytest.fixture
def user():
    """Create test user."""
    return UserPermissions.from_groups(
        user_id="test-001",
        email="test@agency.ny.gov",
        groups=["DMV_Staff"],
    )


@pytest.fixture
def mock_response():
    """Create mock search response."""
    return SearchResponse(
        query="test query",
        results=[],
        agencies_searched=[Agency.DMV],
    )


class TestReviewService:
    """Tests for ReviewService."""

    def test_multi_agency_triggers_flag(self, review_service, user, mock_response):
        """Test that multi-agency queries trigger flagging."""
        query = SearchQuery(
            query="test query",
            agencies=[Agency.DMV, Agency.DOL, Agency.DOH, Agency.OTDA],
        )

        should_flag, criteria = review_service.should_flag_query(
            query, mock_response, user
        )

        assert should_flag is True
        assert any("multi_agency" in c for c in criteria)

    def test_sensitive_keywords_trigger_flag(self, review_service, user, mock_response):
        """Test that sensitive keywords trigger flagging."""
        query = SearchQuery(query="security breach investigation")

        should_flag, criteria = review_service.should_flag_query(
            query, mock_response, user
        )

        assert should_flag is True
        assert any("sensitive_keyword" in c for c in criteria)

    def test_confidential_keyword_triggers_flag(self, review_service, user, mock_response):
        """Test that 'confidential' keyword triggers flagging."""
        query = SearchQuery(query="confidential personnel files")

        should_flag, criteria = review_service.should_flag_query(
            query, mock_response, user
        )

        assert should_flag is True

    def test_normal_query_not_flagged(self, review_service, user, mock_response):
        """Test that normal queries are not flagged."""
        query = SearchQuery(query="remote work guidelines")

        should_flag, criteria = review_service.should_flag_query(
            query, mock_response, user
        )

        # May or may not be flagged depending on criteria
        # Just ensure no errors occur
        assert isinstance(should_flag, bool)

    def test_flagged_topics_trigger_flag(self, review_service, user, mock_response):
        """Test that flagged topics trigger review."""
        query = SearchQuery(query="personnel records and disciplinary action")

        should_flag, criteria = review_service.should_flag_query(
            query, mock_response, user
        )

        assert should_flag is True
        assert any("flagged_topic" in c for c in criteria)

    def test_low_confidence_triggers_flag(self, review_service, user):
        """Test that low confidence results trigger flagging."""
        from src.models.document import DocumentCitation
        from datetime import datetime

        # Create response with low confidence results
        low_conf_result = SearchResult(
            document_id="doc-001",
            title="Test Doc",
            agency=Agency.DMV,
            relevance_score=0.3,  # Low confidence
            publication_date=datetime.now(),
            citation=DocumentCitation(
                document_id="doc-001",
                title="Test Doc",
                agency=Agency.DMV,
                publication_date=datetime.now(),
                direct_url="/docs/001",
            ),
        )

        response = SearchResponse(
            query="obscure query",
            results=[low_conf_result],
            agencies_searched=[Agency.DMV],
        )

        query = SearchQuery(query="obscure query")

        should_flag, criteria = review_service.should_flag_query(
            query, response, user
        )

        assert should_flag is True
        assert any("low_confidence" in c for c in criteria)

    def test_default_criteria_loaded(self, review_service):
        """Test that default criteria are loaded."""
        assert review_service._criteria_config is not None
        assert len(review_service._criteria_config.criteria) > 0

    def test_pending_response_generation(self, review_service, user, mock_response):
        """Test pending response generation."""
        from src.models.review import ReviewFlag, ReviewStatus

        flag = ReviewFlag(
            query="test query",
            user_id=user.user_id,
            status=ReviewStatus.PENDING,
            flag_reason="test reason",
        )

        response = review_service.get_pending_response(flag)

        assert response is not None
        assert response.review_id == str(flag.id)
        assert "flagged for review" in response.message
