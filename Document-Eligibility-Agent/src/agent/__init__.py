"""Agent module for document processing."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .document_processor import DocumentProcessor
    from .extraction_agent import ExtractionAgent
    from .validation_agent import ValidationAgent

__all__ = [
    "DocumentProcessor",
    "ExtractionAgent",
    "ValidationAgent",
]


def __getattr__(name: str):
    """Lazy import agents to avoid circular imports."""
    if name == "DocumentProcessor":
        from .document_processor import DocumentProcessor
        return DocumentProcessor
    elif name == "ExtractionAgent":
        from .extraction_agent import ExtractionAgent
        return ExtractionAgent
    elif name == "ValidationAgent":
        from .validation_agent import ValidationAgent
        return ValidationAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
