"""Document service for managing uploaded documents."""

from typing import Optional

from ..config import logger
from ..models.policy_document import PolicyDocument
from ..models.enums import AnalysisStatus


class DocumentService:
    """Service for document storage and retrieval."""

    def __init__(self):
        """Initialize document service with in-memory storage."""
        self.documents: dict[str, PolicyDocument] = {}

    def store(self, document: PolicyDocument) -> PolicyDocument:
        """
        Store a document.

        Args:
            document: PolicyDocument to store

        Returns:
            Stored document
        """
        self.documents[document.id] = document
        logger.info(f"Stored document: {document.id} ({document.filename})")
        return document

    def get(self, document_id: str) -> Optional[PolicyDocument]:
        """
        Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            PolicyDocument if found, None otherwise
        """
        return self.documents.get(document_id)

    def list(self, limit: int = 100, offset: int = 0) -> tuple[list[PolicyDocument], int]:
        """
        List documents with pagination.

        Args:
            limit: Maximum number of documents
            offset: Pagination offset

        Returns:
            Tuple of (documents, total_count)
        """
        docs = list(self.documents.values())
        docs.sort(key=lambda d: d.uploaded_at, reverse=True)

        return docs[offset:offset + limit], len(docs)

    def delete(self, document_id: str) -> bool:
        """
        Delete a document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        if document_id in self.documents:
            del self.documents[document_id]
            logger.info(f"Deleted document: {document_id}")
            return True
        return False

    def update_status(
        self,
        document_id: str,
        status: AnalysisStatus
    ) -> Optional[PolicyDocument]:
        """
        Update document analysis status.

        Args:
            document_id: Document ID
            status: New status

        Returns:
            Updated document if found
        """
        doc = self.documents.get(document_id)
        if doc:
            doc.analysis_status = status
            logger.info(f"Updated document {document_id} status to {status.value}")
        return doc


__all__ = ["DocumentService"]
