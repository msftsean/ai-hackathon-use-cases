"""Document processor for orchestrating document intake and processing."""

import logging
import time
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.config import get_settings
from src.models import (
    DocumentPriority,
    DocumentSource,
    DocumentStatus,
    DocumentType,
    LogAction,
)
from src.models.document import Document
from src.models.extraction import BoundingBox, Extraction
from src.models.processing_log import ProcessingLog
from src.services import get_audit_service, get_storage_service
from src.services.document_intelligence import (
    ExtractionResult,
    get_document_intelligence_service,
)
from src.services.email_service import EmailAttachment, IncomingEmail, get_email_service

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Main document processing orchestrator.

    Handles:
    - Email polling and attachment extraction
    - Document upload and storage
    - Document type classification
    - Data extraction via Document Intelligence
    - Duplicate detection
    - Audit logging
    """

    # Document categories for routing
    CATEGORY_INCOME = "income"
    CATEGORY_IDENTITY = "identity"
    CATEGORY_RESIDENCY = "residency"
    CATEGORY_MEDICAL = "medical"
    CATEGORY_OTHER = "other"

    # Document type to category mapping
    TYPE_CATEGORIES = {
        DocumentType.W2: CATEGORY_INCOME,
        DocumentType.PAYSTUB: CATEGORY_INCOME,
        DocumentType.BANK_STATEMENT: CATEGORY_INCOME,
        DocumentType.DRIVERS_LICENSE: CATEGORY_IDENTITY,
        DocumentType.BIRTH_CERTIFICATE: CATEGORY_IDENTITY,
        DocumentType.UTILITY_BILL: CATEGORY_RESIDENCY,
        DocumentType.LEASE_AGREEMENT: CATEGORY_RESIDENCY,
    }

    def __init__(self):
        """Initialize document processor with services."""
        self._storage = get_storage_service()
        self._audit = get_audit_service()
        self._doc_intelligence = get_document_intelligence_service()
        self._email = get_email_service()

        # In-memory document store (would be Cosmos DB in production)
        self._documents: dict[str, Document] = {}
        self._extractions: dict[str, list[Extraction]] = {}
        self._content_hashes: dict[str, str] = {}  # hash -> document_id

        logger.info("DocumentProcessor initialized")

    # =========================================================================
    # Email Processing
    # =========================================================================

    async def poll_email_inbox(self, since: Optional[datetime] = None) -> list[Document]:
        """
        Poll email inbox for new document submissions.

        Returns list of documents created from email attachments.
        """
        logger.info("Polling email inbox for new messages")

        try:
            messages = await self._email.get_new_messages(since=since)
            documents = []

            for message in messages:
                logger.info(
                    f"Processing email: {message.subject} from {message.sender}"
                )

                for attachment in message.attachments:
                    try:
                        doc = await self._process_email_attachment(
                            attachment=attachment,
                            email=message,
                        )
                        if doc:
                            documents.append(doc)
                    except Exception as e:
                        logger.error(
                            f"Failed to process attachment {attachment.name}: {e}"
                        )

                # Mark email as processed
                await self._email.mark_as_processed(message.message_id)

            logger.info(f"Processed {len(documents)} documents from email")
            return documents

        except Exception as e:
            logger.error(f"Email polling failed: {e}")
            raise

    async def _process_email_attachment(
        self, attachment: EmailAttachment, email: IncomingEmail
    ) -> Optional[Document]:
        """Process a single email attachment."""
        # Skip non-document attachments
        if not self._is_supported_content_type(attachment.content_type):
            logger.warning(f"Skipping unsupported attachment type: {attachment.content_type}")
            return None

        # Create document
        case_id = email.case_id or "UNKNOWN"
        document = Document(
            case_id=case_id,
            document_type=DocumentType.OTHER,  # Will be classified
            source=DocumentSource.EMAIL,
            filename=attachment.name,
            file_size_bytes=attachment.size,
            mime_type=attachment.content_type,
            priority=self._determine_priority(email),
        )

        # Check for duplicate
        content_hash = self._storage.compute_hash(attachment.content)
        existing_doc_id = self._content_hashes.get(content_hash)
        if existing_doc_id:
            document.is_duplicate = True
            document.duplicate_of = UUID(existing_doc_id)
            logger.info(f"Duplicate detected: {document.id} matches {existing_doc_id}")

        # Upload to storage
        blob_url = await self._storage.upload_document(
            case_id=case_id,
            document_id=document.id,
            file_content=attachment.content,
            filename=attachment.name,
            content_type=attachment.content_type,
        )
        document.blob_url = blob_url
        document.content_hash = content_hash

        # Store document
        self._documents[str(document.id)] = document
        self._content_hashes[content_hash] = str(document.id)

        # Log upload
        await self._audit.log(
            ProcessingLog.create_upload_log(
                document_id=document.id,
                actor="email_processor",
                filename=attachment.name,
                file_size=attachment.size,
                source=DocumentSource.EMAIL.value,
            )
        )

        logger.info(f"Document created from email: {document.id}")
        return document

    def _is_supported_content_type(self, content_type: str) -> bool:
        """Check if content type is supported for processing."""
        supported = [
            "application/pdf",
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff",
        ]
        return any(s in content_type.lower() for s in supported)

    def _determine_priority(self, email: IncomingEmail) -> DocumentPriority:
        """Determine document priority based on email content."""
        subject_lower = email.subject.lower()

        if "urgent" in subject_lower or "expedited" in subject_lower:
            return DocumentPriority.EXPEDITED
        elif "resubmit" in subject_lower or "correction" in subject_lower:
            return DocumentPriority.RESUBMISSION

        return DocumentPriority.STANDARD

    # =========================================================================
    # Document Processing Pipeline
    # =========================================================================

    async def process_document(self, document_id: str) -> Document:
        """
        Run the full processing pipeline on a document.

        Pipeline steps:
        1. Download document from storage
        2. Classify document type
        3. Extract data fields
        4. Store extraction results
        5. Update document status
        """
        start_time = time.time()

        document = self._documents.get(document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")

        logger.info(f"Starting processing for document: {document_id}")

        # Update status to processing
        document.update_status(DocumentStatus.PROCESSING)
        await self._audit.log(
            ProcessingLog(
                document_id=document.id,
                action=LogAction.PROCESSING_STARTED,
                actor="system",
                details={"document_type": document.document_type.value},
            )
        )

        try:
            # Download document content
            content = await self._storage.download_document(document.blob_url)

            # Classify document type if not already set
            if document.document_type == DocumentType.OTHER:
                document.document_type = await self._doc_intelligence.classify_document(
                    content=content,
                    content_type=document.mime_type,
                )
                logger.info(f"Document classified as: {document.document_type.value}")

            # Extract data
            extraction_result = await self._doc_intelligence.analyze_document(
                content=content,
                content_type=document.mime_type,
                document_type=document.document_type,
            )

            # Store extractions
            extractions = self._convert_extraction_result(document.id, extraction_result)
            self._extractions[document_id] = extractions

            # Update document with extraction results
            document.overall_confidence = extraction_result.overall_confidence
            document.page_count = extraction_result.page_count
            document.update_status(DocumentStatus.EXTRACTED)

            # Calculate processing duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log completion
            await self._audit.log(
                ProcessingLog.create_processing_log(
                    document_id=document.id,
                    success=True,
                    duration_ms=duration_ms,
                    extraction_count=len(extractions),
                )
            )

            logger.info(
                f"Processing complete for {document_id}: "
                f"{len(extractions)} fields extracted, "
                f"confidence: {document.overall_confidence:.2f}"
            )

            return document

        except Exception as e:
            logger.error(f"Processing failed for {document_id}: {e}")

            # Update status to failed
            document.update_status(DocumentStatus.FAILED)

            # Log failure
            duration_ms = int((time.time() - start_time) * 1000)
            await self._audit.log(
                ProcessingLog.create_processing_log(
                    document_id=document.id,
                    success=False,
                    duration_ms=duration_ms,
                    error_message=str(e),
                )
            )

            raise

    def _convert_extraction_result(
        self, document_id: UUID, result: ExtractionResult
    ) -> list[Extraction]:
        """Convert extraction result to Extraction models."""
        extractions = []

        for field in result.fields:
            bounding_box = None
            if field.bounding_box:
                bounding_box = BoundingBox(**field.bounding_box)

            extraction = Extraction(
                document_id=document_id,
                field_name=field.name,
                field_value=field.value,
                confidence=field.confidence,
                bounding_box=bounding_box,
                is_pii=field.is_pii,
                pii_type=field.pii_type,
            )

            # Generate masked display value for PII
            if field.is_pii:
                extraction.display_value = extraction._mask_value()

            extractions.append(extraction)

        return extractions

    # =========================================================================
    # Document Categorization
    # =========================================================================

    def categorize_document(self, document: Document) -> str:
        """
        Categorize a document into a processing category.

        Categories: income, identity, residency, medical, other
        """
        return self.TYPE_CATEGORIES.get(document.document_type, self.CATEGORY_OTHER)

    # =========================================================================
    # Duplicate Detection
    # =========================================================================

    def check_duplicate(self, content: bytes, case_id: str) -> Optional[str]:
        """
        Check if document content is a duplicate.

        Returns document ID of original if duplicate, None otherwise.
        """
        content_hash = self._storage.compute_hash(content)
        existing_doc_id = self._content_hashes.get(content_hash)

        if existing_doc_id:
            existing_doc = self._documents.get(existing_doc_id)
            # Only flag as duplicate if same case
            if existing_doc and existing_doc.case_id == case_id:
                return existing_doc_id

        return None

    # =========================================================================
    # Document Access
    # =========================================================================

    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self._documents.get(document_id)

    def get_extractions(self, document_id: str) -> list[Extraction]:
        """Get extractions for a document."""
        return self._extractions.get(document_id, [])

    def get_all_documents(self) -> list[Document]:
        """Get all documents."""
        return list(self._documents.values())

    def get_documents_by_status(self, status: DocumentStatus) -> list[Document]:
        """Get documents by status."""
        return [d for d in self._documents.values() if d.status == status]

    def get_documents_by_category(self, category: str) -> list[Document]:
        """Get documents by category."""
        return [
            d for d in self._documents.values()
            if self.categorize_document(d) == category
        ]

    # =========================================================================
    # Batch Processing
    # =========================================================================

    async def process_pending_documents(self, limit: int = 10) -> list[Document]:
        """Process pending documents in batch."""
        pending = [
            d for d in self._documents.values()
            if d.status == DocumentStatus.UPLOADED
        ]

        # Sort by priority
        priority_order = {
            DocumentPriority.EXPEDITED: 0,
            DocumentPriority.RESUBMISSION: 1,
            DocumentPriority.STANDARD: 2,
            DocumentPriority.LOW: 3,
        }
        pending.sort(key=lambda d: priority_order.get(d.priority, 99))

        # Process up to limit
        processed = []
        for doc in pending[:limit]:
            try:
                result = await self.process_document(str(doc.id))
                processed.append(result)
            except Exception as e:
                logger.error(f"Batch processing failed for {doc.id}: {e}")

        logger.info(f"Batch processed {len(processed)}/{len(pending[:limit])} documents")
        return processed
