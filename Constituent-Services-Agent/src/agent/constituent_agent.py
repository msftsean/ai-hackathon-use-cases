"""
Constituent Agent for NY State Services.

Main agent orchestration for handling constituent queries with
citation-backed responses and confidence scoring.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.agent.foundry_iq_client import AgentResponse, BaseFoundryIQKnowledgeBase
from src.models import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
    SupportedLanguage,
)
from src.models.knowledge_source import Citation

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from agent query processing."""

    response: str
    citations: list[Citation]
    confidence: float
    language: str
    processing_time_ms: int
    should_escalate: bool
    disclaimer: Optional[str] = None
    suggested_actions: Optional[list[dict]] = None


class ConstituentAgent:
    """
    AI agent for handling NY State constituent service inquiries.

    Provides citation-backed responses using Foundry IQ for RAG retrieval.
    Includes confidence scoring and escalation detection.
    """

    # System prompt for the agent
    SYSTEM_PROMPT = """You are a helpful AI assistant for New York State government services.
Your role is to help NY State residents find accurate information about government services,
benefits programs, and agency procedures.

IMPORTANT GUIDELINES:
1. Always provide accurate, factual information based on official sources
2. Cite your sources for any factual claims
3. If you're unsure about something, say so clearly
4. Never provide legal advice or make official eligibility determinations
5. For benefits questions, provide general guidance but clarify that official
   eligibility is determined through the application process
6. Be respectful and professional
7. Keep responses clear and well-organized

When discussing benefits eligibility (SNAP, Medicaid, HEAP, etc.):
- Ask clarifying questions about household size and income if needed
- Provide income guidelines as reference
- Always include a disclaimer that this is preliminary guidance only
- Direct users to apply through official channels for actual determination

If you cannot adequately help with a query:
- Acknowledge limitations
- Offer to connect with a human agent
- Provide relevant contact information"""

    # Confidence threshold for escalation
    CONFIDENCE_THRESHOLD = 0.5

    def __init__(
        self,
        knowledge_base: BaseFoundryIQKnowledgeBase,
        confidence_threshold: float = 0.5,
    ):
        """
        Initialize the constituent agent.

        Args:
            knowledge_base: Knowledge base service for RAG retrieval
            confidence_threshold: Minimum confidence before offering escalation
        """
        self.knowledge_base = knowledge_base
        self.confidence_threshold = confidence_threshold

    async def process_query(
        self,
        query: str,
        conversation: Optional[Conversation] = None,
        max_citations: int = 5,
    ) -> AgentResult:
        """
        Process a constituent query and generate a response.

        Args:
            query: User's question
            conversation: Existing conversation for context
            max_citations: Maximum citations to include

        Returns:
            AgentResult with response, citations, and metadata
        """
        start_time = datetime.utcnow()

        # Build conversation history for context
        history = []
        if conversation:
            for msg in conversation.messages[-10:]:  # Last 10 messages
                history.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })

        # Query knowledge base
        kb_response = await self.knowledge_base.query(
            question=query,
            conversation_history=history,
            max_citations=max_citations,
        )

        # Build citations
        citations = []
        for cite in kb_response.citations:
            citations.append(Citation(
                id=uuid4(),
                message_id=uuid4(),  # Will be updated when message is created
                source_id=UUID(cite.source_id) if self._is_uuid(cite.source_id) else uuid4(),
                quote=cite.quote,
                relevance_score=cite.relevance_score,
                title=cite.title,
                agency=cite.agency,
                url=cite.url,
            ))

        # Compute confidence using spec formula:
        # confidence = 0.6 * model_confidence + 0.4 * min(citation_count / 3, 1.0)
        citation_factor = min(len(citations) / 3, 1.0)
        computed_confidence = 0.6 * kb_response.confidence + 0.4 * citation_factor

        # Calculate processing time
        processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Determine if escalation should be offered
        should_escalate = computed_confidence < self.confidence_threshold

        # Generate disclaimer for low confidence or eligibility responses
        disclaimer = None
        if computed_confidence < 0.6:
            disclaimer = (
                "This information is provided for general guidance only. "
                "Please verify with official sources or contact the relevant agency directly."
            )
        elif self._is_eligibility_query(query):
            disclaimer = (
                "This is preliminary guidance only. Actual eligibility is determined "
                "through the official application process. Please apply through the "
                "appropriate agency to receive an official determination."
            )

        # Build suggested actions
        suggested_actions = []
        if should_escalate:
            suggested_actions.append({
                "type": "escalate",
                "label": "Talk to a human agent",
                "value": "escalate",
            })

        # Get language (default to English, actual detection in multilingual agent)
        language = SupportedLanguage.ENGLISH.value

        return AgentResult(
            response=kb_response.answer,
            citations=citations,
            confidence=round(computed_confidence, 3),
            language=language,
            processing_time_ms=processing_time_ms,
            should_escalate=should_escalate,
            disclaimer=disclaimer,
            suggested_actions=suggested_actions,
        )

    def _is_eligibility_query(self, query: str) -> bool:
        """Check if query is about benefits eligibility."""
        eligibility_keywords = [
            "eligible", "eligibility", "qualify", "qualification",
            "am i eligible", "can i get", "do i qualify",
            "medicaid", "snap", "food stamps", "heap", "tanf",
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in eligibility_keywords)

    def _is_uuid(self, value: str) -> bool:
        """Check if string is a valid UUID."""
        try:
            UUID(value)
            return True
        except (ValueError, TypeError):
            return False

    async def handle_escalation(
        self,
        conversation: Conversation,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Handle escalation to human agent.

        Args:
            conversation: Current conversation
            reason: Reason for escalation

        Returns:
            Escalation details
        """
        conversation.mark_escalated(reason or "User requested human assistance")

        # In production, would integrate with call center queue
        return {
            "escalation_id": str(uuid4()),
            "estimated_wait_time": 5,  # minutes
            "queue_position": 3,
            "message": (
                "You've been added to the queue for a human agent. "
                "Estimated wait time is approximately 5 minutes. "
                "Your conversation history will be available to the agent."
            ),
        }
