"""
Data models for Constituent Services Agent.

Contains enums and Pydantic models for all domain entities.
"""

from enum import Enum


class MessageRole(str, Enum):
    """Role of message sender in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    """Status of a conversation session."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    EXPIRED = "expired"


class Agency(str, Enum):
    """NY State agency codes."""

    DMV = "DMV"
    DOL = "DOL"
    OTDA = "OTDA"
    DOH = "DOH"
    OGS = "OGS"


class SupportedLanguage(str, Enum):
    """Supported language codes (ISO 639-1)."""

    ENGLISH = "en"
    SPANISH = "es"
    CHINESE = "zh"
    ARABIC = "ar"
    RUSSIAN = "ru"
    KOREAN = "ko"
    HAITIAN_CREOLE = "ht"
    BENGALI = "bn"

    @classmethod
    def from_code(cls, code: str) -> "SupportedLanguage":
        """Get language enum from ISO code."""
        for lang in cls:
            if lang.value == code.lower():
                return lang
        raise ValueError(f"Unsupported language code: {code}")

    @classmethod
    def is_supported(cls, code: str) -> bool:
        """Check if a language code is supported."""
        return code.lower() in [lang.value for lang in cls]


class DocumentType(str, Enum):
    """Type of knowledge source document."""

    FAQ = "faq"
    POLICY = "policy"
    FORM = "form"
    GUIDE = "guide"
    WEBPAGE = "webpage"


class IndexingStatus(str, Enum):
    """Status of document indexing."""

    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"


# Import models after enums to avoid circular imports
from .conversation import Conversation, Message
from .knowledge_source import Citation, KnowledgeSource

__all__ = [
    # Enums
    "MessageRole",
    "ConversationStatus",
    "Agency",
    "SupportedLanguage",
    "DocumentType",
    "IndexingStatus",
    # Models
    "Conversation",
    "Message",
    "KnowledgeSource",
    "Citation",
]
