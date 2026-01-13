"""
Foundry IQ Knowledge Base client for Constituent Services Agent.

Provides RAG-based document retrieval using Azure AI Foundry IQ.
Includes mock implementation for offline development.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from knowledge base retrieval."""

    source_id: str
    title: str
    agency: str
    content: str
    url: str
    relevance_score: float
    quote: str


@dataclass
class AgentResponse:
    """Response from the knowledge base agent."""

    answer: str
    citations: list[RetrievalResult]
    confidence: float
    model_version: str
    token_count_input: int
    token_count_output: int


class BaseFoundryIQKnowledgeBase(ABC):
    """Abstract base class for Foundry IQ knowledge base."""

    @abstractmethod
    async def query(
        self,
        question: str,
        conversation_history: Optional[list[dict]] = None,
        max_citations: int = 5,
    ) -> AgentResponse:
        """
        Query the knowledge base with a question.

        Args:
            question: User's question
            conversation_history: Previous messages for context
            max_citations: Maximum citations to return

        Returns:
            AgentResponse with answer, citations, and metadata
        """
        pass


class MockFoundryIQKnowledgeBase(BaseFoundryIQKnowledgeBase):
    """
    Mock implementation for offline development.

    Returns pre-defined responses for common queries.
    """

    # Mock knowledge base with sample responses
    MOCK_RESPONSES = {
        "snap": {
            "answer": (
                "To apply for SNAP (Supplemental Nutrition Assistance Program) benefits "
                "in New York State, you can:\n\n"
                "1. **Online**: Apply through myBenefits.ny.gov\n"
                "2. **In Person**: Visit your local Department of Social Services office\n"
                "3. **By Phone**: Call the OTDA Hotline at 1-800-342-3009\n\n"
                "**Eligibility Requirements**:\n"
                "- Must be a NY State resident\n"
                "- Must meet income guidelines (varies by household size)\n"
                "- Must be a U.S. citizen or qualified non-citizen\n\n"
                "**Required Documents**:\n"
                "- Proof of identity\n"
                "- Proof of income\n"
                "- Proof of residency\n"
                "- Social Security numbers for household members"
            ),
            "citations": [
                {
                    "title": "SNAP Benefits Application Guide",
                    "agency": "OTDA",
                    "url": "https://otda.ny.gov/programs/snap/apply.asp",
                    "quote": "Apply online at myBenefits.ny.gov or visit your local DSS office.",
                    "relevance": 0.95,
                },
                {
                    "title": "SNAP Eligibility Requirements",
                    "agency": "OTDA",
                    "url": "https://otda.ny.gov/programs/snap/eligibility.asp",
                    "quote": "Income eligibility varies by household size and composition.",
                    "relevance": 0.88,
                },
            ],
            "confidence": 0.92,
        },
        "dmv": {
            "answer": (
                "To renew your driver's license in New York State:\n\n"
                "**Online Renewal** (Recommended):\n"
                "1. Visit dmv.ny.gov\n"
                "2. Sign in to your MyDMV account\n"
                "3. Follow the renewal prompts\n"
                "4. Pay the $64.50 renewal fee\n\n"
                "**In-Person Renewal**:\n"
                "1. Visit a DMV office\n"
                "2. Bring your current license\n"
                "3. Complete the vision test\n"
                "4. Pay the renewal fee\n\n"
                "**Important**: You can renew up to 1 year before expiration."
            ),
            "citations": [
                {
                    "title": "Driver License Renewal",
                    "agency": "DMV",
                    "url": "https://dmv.ny.gov/driver-license/renew-driver-license",
                    "quote": "Renew online at dmv.ny.gov or visit a DMV office in person.",
                    "relevance": 0.94,
                },
            ],
            "confidence": 0.90,
        },
        "unemployment": {
            "answer": (
                "To file for unemployment insurance in New York State:\n\n"
                "**Online Filing** (Fastest):\n"
                "1. Visit labor.ny.gov\n"
                "2. Create or sign in to your NY.gov ID account\n"
                "3. Complete the unemployment application\n"
                "4. Certify for benefits weekly\n\n"
                "**By Phone**: 1-888-209-8124\n"
                "- Monday-Friday, 8:00 AM - 5:00 PM\n\n"
                "**Eligibility**:\n"
                "- Must have lost job through no fault of your own\n"
                "- Must have earned enough wages\n"
                "- Must be ready, willing, and able to work\n"
                "- Must actively search for work"
            ),
            "citations": [
                {
                    "title": "Unemployment Insurance Filing Guide",
                    "agency": "DOL",
                    "url": "https://dol.ny.gov/unemployment/file-your-first-claim",
                    "quote": "File online at labor.ny.gov for fastest processing.",
                    "relevance": 0.93,
                },
                {
                    "title": "UI Eligibility Requirements",
                    "agency": "DOL",
                    "url": "https://dol.ny.gov/unemployment/eligibility",
                    "quote": "You must have lost your job through no fault of your own.",
                    "relevance": 0.85,
                },
            ],
            "confidence": 0.88,
        },
        "medicaid": {
            "answer": (
                "Medicaid provides free or low-cost health coverage for eligible "
                "New York residents.\n\n"
                "**How to Apply**:\n"
                "1. **Online**: NY State of Health (nystateofhealth.ny.gov)\n"
                "2. **Phone**: 1-855-355-5777\n"
                "3. **In Person**: Local Department of Social Services\n\n"
                "**Eligibility** (2026 Guidelines):\n"
                "- Single adult: Up to $20,121/year\n"
                "- Family of 4: Up to $41,400/year\n"
                "- Pregnant women and children: Higher limits apply\n\n"
                "**Note**: This is preliminary guidance only. Final eligibility "
                "is determined during the application process."
            ),
            "citations": [
                {
                    "title": "Medicaid Eligibility",
                    "agency": "DOH",
                    "url": "https://health.ny.gov/health_care/medicaid/",
                    "quote": "Apply through NY State of Health marketplace.",
                    "relevance": 0.91,
                },
            ],
            "confidence": 0.75,  # Lower confidence triggers eligibility disclaimer
        },
    }

    DEFAULT_RESPONSE = {
        "answer": (
            "I don't have specific information about that topic in my knowledge base. "
            "For the most accurate and up-to-date information, I recommend:\n\n"
            "1. Visiting NY.gov for general state services\n"
            "2. Contacting the relevant agency directly\n"
            "3. Calling 311 (in NYC) or your local government office\n\n"
            "Would you like me to help you find contact information for a specific agency?"
        ),
        "citations": [],
        "confidence": 0.3,  # Low confidence triggers escalation offer
    }

    async def query(
        self,
        question: str,
        conversation_history: Optional[list[dict]] = None,
        max_citations: int = 5,
    ) -> AgentResponse:
        """
        Query mock knowledge base.

        Matches question keywords to pre-defined responses.
        """
        question_lower = question.lower()

        # Find matching response
        response_data = None
        for keyword, data in self.MOCK_RESPONSES.items():
            if keyword in question_lower:
                response_data = data
                break

        if not response_data:
            response_data = self.DEFAULT_RESPONSE

        # Build citations
        citations = []
        for i, cite_data in enumerate(response_data.get("citations", [])[:max_citations]):
            citations.append(
                RetrievalResult(
                    source_id=str(uuid4()),
                    title=cite_data["title"],
                    agency=cite_data["agency"],
                    content="",  # Not needed for mock
                    url=cite_data["url"],
                    relevance_score=cite_data["relevance"],
                    quote=cite_data["quote"],
                )
            )

        return AgentResponse(
            answer=response_data["answer"],
            citations=citations,
            confidence=response_data["confidence"],
            model_version="mock-gpt-4",
            token_count_input=len(question.split()),
            token_count_output=len(response_data["answer"].split()),
        )


class FoundryIQKnowledgeBase(BaseFoundryIQKnowledgeBase):
    """
    Real implementation using Azure AI Projects SDK.

    Uses Foundry IQ for agentic RAG with citation tracking.
    """

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize Foundry IQ client.

        Args:
            connection_string: Azure AI Project connection string
        """
        self.connection_string = connection_string
        self._client = None
        self._initialized = False

    async def _initialize(self):
        """Lazy initialization of Azure AI client."""
        if self._initialized:
            return

        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential

            self._client = AIProjectClient.from_connection_string(
                conn_str=self.connection_string,
                credential=DefaultAzureCredential(),
            )
            self._initialized = True
            logger.info("Foundry IQ client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Foundry IQ client: {e}")
            raise

    async def query(
        self,
        question: str,
        conversation_history: Optional[list[dict]] = None,
        max_citations: int = 5,
    ) -> AgentResponse:
        """
        Query Foundry IQ knowledge base.

        Uses Azure AI Foundry IQ for RAG-based retrieval and response generation.
        """
        await self._initialize()

        # Build messages with conversation history
        messages = []
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })
        messages.append({"role": "user", "content": question})

        try:
            # Note: This is a simplified implementation
            # Real implementation would use Foundry IQ specific APIs
            response = await self._client.inference.chat.complete(
                model="gpt-4",
                messages=messages,
            )

            # Parse response and extract citations
            # In real implementation, Foundry IQ provides structured citations
            answer = response.choices[0].message.content
            citations = []  # Would be populated from Foundry IQ response

            return AgentResponse(
                answer=answer,
                citations=citations,
                confidence=0.8,  # Would be computed from model response
                model_version=response.model,
                token_count_input=response.usage.prompt_tokens,
                token_count_output=response.usage.completion_tokens,
            )

        except Exception as e:
            logger.error(f"Foundry IQ query failed: {e}")
            raise
