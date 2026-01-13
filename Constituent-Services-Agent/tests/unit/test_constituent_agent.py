"""Unit tests for ConstituentAgent."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.agent.constituent_agent import ConstituentAgent, AgentResult
from src.agent.foundry_iq_client import (
    AgentResponse,
    BaseFoundryIQKnowledgeBase,
    MockFoundryIQKnowledgeBase,
    RetrievalResult,
)
from src.models import Conversation, Message, MessageRole


class TestConstituentAgent:
    """Tests for ConstituentAgent functionality."""

    @pytest.fixture
    def mock_knowledge_base(self):
        """Create mock knowledge base."""
        return MockFoundryIQKnowledgeBase()

    @pytest.fixture
    def agent(self, mock_knowledge_base):
        """Create agent instance."""
        return ConstituentAgent(
            knowledge_base=mock_knowledge_base,
            confidence_threshold=0.5,
        )

    @pytest.mark.asyncio
    async def test_process_query_returns_result(self, agent):
        """Test that process_query returns AgentResult."""
        result = await agent.process_query("How do I apply for SNAP benefits?")

        assert isinstance(result, AgentResult)
        assert result.response is not None
        assert isinstance(result.confidence, float)
        assert result.language == "en"

    @pytest.mark.asyncio
    async def test_process_query_includes_citations(self, agent):
        """Test that responses include citations."""
        result = await agent.process_query("How do I renew my DMV license?")

        assert isinstance(result.citations, list)
        assert len(result.citations) > 0

    @pytest.mark.asyncio
    async def test_process_query_calculates_confidence(self, agent):
        """Test confidence calculation."""
        result = await agent.process_query("How do I apply for SNAP?")

        assert 0 <= result.confidence <= 1

    @pytest.mark.asyncio
    async def test_low_confidence_triggers_escalation(self, agent):
        """Test that low confidence triggers escalation offer."""
        result = await agent.process_query("Something completely random xyz123")

        assert result.should_escalate is True
        assert result.suggested_actions is not None
        assert len(result.suggested_actions) > 0

    @pytest.mark.asyncio
    async def test_high_confidence_no_escalation(self, agent):
        """Test that high confidence doesn't trigger escalation."""
        result = await agent.process_query("How do I apply for SNAP benefits?")

        assert result.should_escalate is False

    @pytest.mark.asyncio
    async def test_eligibility_query_adds_disclaimer(self, agent):
        """Test that eligibility queries add disclaimers."""
        result = await agent.process_query("Am I eligible for Medicaid?")

        assert result.disclaimer is not None
        assert "eligibility" in result.disclaimer.lower() or "guidance" in result.disclaimer.lower()

    @pytest.mark.asyncio
    async def test_process_query_with_conversation_context(self, agent):
        """Test processing query with conversation history."""
        conversation = Conversation(session_id="test-session-123")
        conversation.messages.append(
            Message(
                id=uuid4(),
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content="I need help with SNAP",
            )
        )

        result = await agent.process_query(
            "What documents do I need?",
            conversation=conversation,
        )

        assert result.response is not None

    @pytest.mark.asyncio
    async def test_process_query_tracks_processing_time(self, agent):
        """Test that processing time is tracked."""
        result = await agent.process_query("How do I apply for unemployment?")

        assert result.processing_time_ms >= 0

    def test_is_eligibility_query_positive(self, agent):
        """Test eligibility query detection - positive cases."""
        assert agent._is_eligibility_query("Am I eligible for benefits?") is True
        assert agent._is_eligibility_query("Do I qualify for Medicaid?") is True
        assert agent._is_eligibility_query("Can I get food stamps?") is True

    def test_is_eligibility_query_negative(self, agent):
        """Test eligibility query detection - negative cases."""
        assert agent._is_eligibility_query("Office hours for DMV") is False
        assert agent._is_eligibility_query("How do I renew my license?") is False

    def test_is_uuid_valid(self, agent):
        """Test UUID validation - valid cases."""
        valid_uuid = str(uuid4())
        assert agent._is_uuid(valid_uuid) is True

    def test_is_uuid_invalid(self, agent):
        """Test UUID validation - invalid cases."""
        assert agent._is_uuid("not-a-uuid") is False
        assert agent._is_uuid("123") is False
        assert agent._is_uuid("") is False

    @pytest.mark.asyncio
    async def test_handle_escalation(self, agent):
        """Test escalation handling."""
        conversation = Conversation(session_id="test-session-456")

        result = await agent.handle_escalation(
            conversation=conversation,
            reason="User requested help",
        )

        assert "escalation_id" in result
        assert "estimated_wait_time" in result
        assert "queue_position" in result
        assert "message" in result


class TestMockFoundryIQKnowledgeBase:
    """Tests for MockFoundryIQKnowledgeBase."""

    @pytest.fixture
    def mock_kb(self):
        """Create mock knowledge base instance."""
        return MockFoundryIQKnowledgeBase()

    @pytest.mark.asyncio
    async def test_query_snap(self, mock_kb):
        """Test SNAP query response."""
        response = await mock_kb.query("How do I apply for SNAP?")

        assert isinstance(response, AgentResponse)
        assert "SNAP" in response.answer
        assert len(response.citations) > 0
        assert response.confidence > 0.5

    @pytest.mark.asyncio
    async def test_query_dmv(self, mock_kb):
        """Test DMV query response."""
        response = await mock_kb.query("How do I renew my driver license at DMV?")

        assert "renew" in response.answer.lower() or "dmv" in response.answer.lower()
        assert response.confidence > 0.5

    @pytest.mark.asyncio
    async def test_query_unemployment(self, mock_kb):
        """Test unemployment query response."""
        response = await mock_kb.query("How do I file for unemployment?")

        assert "unemployment" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_query_unknown_returns_default(self, mock_kb):
        """Test unknown query returns default response."""
        response = await mock_kb.query("completely random query xyz")

        assert response.confidence < 0.5
        assert len(response.citations) == 0

    @pytest.mark.asyncio
    async def test_query_respects_max_citations(self, mock_kb):
        """Test max_citations parameter."""
        response = await mock_kb.query("SNAP benefits", max_citations=1)

        assert len(response.citations) <= 1

    @pytest.mark.asyncio
    async def test_query_includes_model_info(self, mock_kb):
        """Test response includes model info."""
        response = await mock_kb.query("test query")

        assert response.model_version is not None
        assert response.token_count_input >= 0
        assert response.token_count_output >= 0
