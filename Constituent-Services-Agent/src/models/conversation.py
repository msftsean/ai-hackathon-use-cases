"""
Conversation and Message models for Constituent Services Agent.

Represents chat sessions and individual messages between constituents
and the AI agent.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from . import ConversationStatus, MessageRole, SupportedLanguage


class Message(BaseModel):
    """Individual message within a conversation."""

    id: UUID = Field(default_factory=uuid4, description="Message unique identifier")
    conversation_id: UUID = Field(description="Foreign key to Conversation")
    role: MessageRole = Field(description="Message sender role")
    content: str = Field(max_length=10000, description="Message text content")
    original_content: Optional[str] = Field(
        default=None,
        max_length=10000,
        description="Original text before translation"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Message timestamp (UTC)"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Agent confidence score (assistant messages only)"
    )
    processing_time_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Response generation time in milliseconds"
    )

    @field_validator("confidence")
    @classmethod
    def confidence_only_for_assistant(cls, v: Optional[float], info) -> Optional[float]:
        """Confidence should only be set for assistant messages."""
        # Note: validation would need role context which isn't available here
        # This is a documentation reminder rather than enforced rule
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "6fa459ea-ee8a-3ca4-894e-db77e160355e",
                "role": "user",
                "content": "How do I apply for SNAP benefits?",
                "timestamp": "2026-01-12T10:30:00Z",
            }
        }
    }


class Conversation(BaseModel):
    """
    Represents a chat session between a constituent and the agent.

    A conversation tracks the entire interaction including language,
    status, and optional escalation to human agents.
    """

    id: UUID = Field(default_factory=uuid4, description="Conversation unique identifier")
    session_id: str = Field(description="Browser session identifier")
    language: str = Field(
        default=SupportedLanguage.ENGLISH.value,
        description="Detected/selected language code (ISO 639-1)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session start time (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last activity time (UTC)"
    )
    status: ConversationStatus = Field(
        default=ConversationStatus.ACTIVE,
        description="Conversation status"
    )
    escalated: bool = Field(
        default=False,
        description="True if escalated to human agent"
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Reason for escalation"
    )
    messages: list[Message] = Field(
        default_factory=list,
        description="Messages in this conversation"
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language is supported."""
        if not SupportedLanguage.is_supported(v):
            raise ValueError(
                f"Unsupported language: {v}. "
                f"Supported: {[lang.value for lang in SupportedLanguage]}"
            )
        return v.lower()

    def add_message(
        self,
        role: MessageRole,
        content: str,
        original_content: Optional[str] = None,
        confidence: Optional[float] = None,
        processing_time_ms: Optional[int] = None,
    ) -> Message:
        """
        Add a new message to the conversation.

        Args:
            role: Message sender role
            content: Message text
            original_content: Original text before translation
            confidence: Agent confidence score (assistant only)
            processing_time_ms: Response generation time

        Returns:
            The created Message instance
        """
        message = Message(
            conversation_id=self.id,
            role=role,
            content=content,
            original_content=original_content,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        return message

    def mark_escalated(self, reason: str) -> None:
        """Mark conversation as escalated to human agent."""
        self.status = ConversationStatus.ESCALATED
        self.escalated = True
        self.escalation_reason = reason
        self.updated_at = datetime.utcnow()

    def mark_completed(self) -> None:
        """Mark conversation as completed."""
        self.status = ConversationStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def mark_expired(self) -> None:
        """Mark conversation as expired due to inactivity."""
        self.status = ConversationStatus.EXPIRED
        self.updated_at = datetime.utcnow()

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "6fa459ea-ee8a-3ca4-894e-db77e160355e",
                "session_id": "abc123def456",
                "language": "en",
                "status": "active",
                "created_at": "2026-01-12T10:00:00Z",
                "updated_at": "2026-01-12T10:30:00Z",
                "escalated": False,
            }
        }
    }
