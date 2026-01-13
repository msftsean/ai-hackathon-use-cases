"""Unit tests for DocumentProcessor."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

from src.agent.document_processor import DocumentProcessor
from src.models import DocumentType, DocumentStatus, DocumentPriority, DocumentSource
from src.models.document import Document


class TestDocumentProcessor:
    """Tests for DocumentProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create DocumentProcessor instance with mocked services."""
        with patch("src.agent.document_processor.get_storage_service") as mock_storage, \
             patch("src.agent.document_processor.get_audit_service") as mock_audit, \
             patch("src.agent.document_processor.get_document_intelligence_service") as mock_intel, \
             patch("src.agent.document_processor.get_email_service") as mock_email:

            # Set up mock storage
            storage_instance = MagicMock()
            storage_instance.compute_hash = MagicMock(return_value="abc123hash")
            storage_instance.upload_document = AsyncMock(return_value="https://storage.blob/doc.pdf")
            storage_instance.download_document = AsyncMock(return_value=b"document content")
            mock_storage.return_value = storage_instance

            # Set up mock audit
            audit_instance = MagicMock()
            audit_instance.log = AsyncMock()
            mock_audit.return_value = audit_instance

            # Set up mock document intelligence
            intel_instance = MagicMock()
            intel_instance.classify_document = AsyncMock(return_value=DocumentType.W2)
            intel_instance.analyze_document = AsyncMock()
            mock_intel.return_value = intel_instance

            # Set up mock email service
            email_instance = MagicMock()
            email_instance.get_new_messages = AsyncMock(return_value=[])
            mock_email.return_value = email_instance

            processor = DocumentProcessor()
            return processor

    def test_categorize_document_w2(self, processor):
        """Test categorizing W-2 as income document."""
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.W2,
            source=DocumentSource.UPLOAD,
            filename="w2.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
        )

        category = processor.categorize_document(doc)

        assert category == processor.CATEGORY_INCOME

    def test_categorize_document_paystub(self, processor):
        """Test categorizing paystub as income document."""
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.PAYSTUB,
            source=DocumentSource.UPLOAD,
            filename="paystub.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
        )

        category = processor.categorize_document(doc)

        assert category == processor.CATEGORY_INCOME

    def test_categorize_document_drivers_license(self, processor):
        """Test categorizing driver's license as identity document."""
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.DRIVERS_LICENSE,
            source=DocumentSource.UPLOAD,
            filename="license.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
        )

        category = processor.categorize_document(doc)

        assert category == processor.CATEGORY_IDENTITY

    def test_categorize_document_utility_bill(self, processor):
        """Test categorizing utility bill as residency document."""
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.UTILITY_BILL,
            source=DocumentSource.UPLOAD,
            filename="utility.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
        )

        category = processor.categorize_document(doc)

        assert category == processor.CATEGORY_RESIDENCY

    def test_categorize_document_other(self, processor):
        """Test categorizing unknown type as other."""
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.OTHER,
            source=DocumentSource.UPLOAD,
            filename="misc.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
        )

        category = processor.categorize_document(doc)

        assert category == processor.CATEGORY_OTHER

    def test_is_supported_content_type_pdf(self, processor):
        """Test PDF is supported content type."""
        assert processor._is_supported_content_type("application/pdf") is True

    def test_is_supported_content_type_jpeg(self, processor):
        """Test JPEG is supported content type."""
        assert processor._is_supported_content_type("image/jpeg") is True

    def test_is_supported_content_type_png(self, processor):
        """Test PNG is supported content type."""
        assert processor._is_supported_content_type("image/png") is True

    def test_is_supported_content_type_unsupported(self, processor):
        """Test unsupported content type returns False."""
        assert processor._is_supported_content_type("text/plain") is False
        assert processor._is_supported_content_type("application/zip") is False

    def test_get_document_not_found(self, processor):
        """Test getting non-existent document returns None."""
        result = processor.get_document("nonexistent-id")
        assert result is None

    def test_get_extractions_empty(self, processor):
        """Test getting extractions for document with none returns empty list."""
        result = processor.get_extractions("nonexistent-id")
        assert result == []

    def test_get_all_documents_empty(self, processor):
        """Test getting all documents when empty."""
        result = processor.get_all_documents()
        assert result == []

    def test_get_documents_by_status_empty(self, processor):
        """Test getting documents by status when none match."""
        result = processor.get_documents_by_status(DocumentStatus.UPLOADED)
        assert result == []

    def test_get_documents_by_category_empty(self, processor):
        """Test getting documents by category when none match."""
        result = processor.get_documents_by_category(processor.CATEGORY_INCOME)
        assert result == []


class TestDetermineEmailPriority:
    """Tests for email priority determination."""

    @pytest.fixture
    def processor(self):
        """Create DocumentProcessor instance with mocked services."""
        with patch("src.agent.document_processor.get_storage_service") as mock_storage, \
             patch("src.agent.document_processor.get_audit_service") as mock_audit, \
             patch("src.agent.document_processor.get_document_intelligence_service") as mock_intel, \
             patch("src.agent.document_processor.get_email_service") as mock_email:

            storage_instance = MagicMock()
            mock_storage.return_value = storage_instance
            audit_instance = MagicMock()
            mock_audit.return_value = audit_instance
            intel_instance = MagicMock()
            mock_intel.return_value = intel_instance
            email_instance = MagicMock()
            mock_email.return_value = email_instance

            processor = DocumentProcessor()
            return processor

    def test_determine_priority_urgent(self, processor):
        """Test urgent email gets expedited priority."""
        from src.services.email_service import IncomingEmail

        email = MagicMock()
        email.subject = "URGENT: Need documents processed"

        priority = processor._determine_priority(email)

        assert priority == DocumentPriority.EXPEDITED

    def test_determine_priority_expedited(self, processor):
        """Test expedited email gets expedited priority."""
        email = MagicMock()
        email.subject = "Expedited processing request"

        priority = processor._determine_priority(email)

        assert priority == DocumentPriority.EXPEDITED

    def test_determine_priority_resubmission(self, processor):
        """Test resubmission email gets resubmission priority."""
        email = MagicMock()
        email.subject = "Resubmit: Updated W-2 document"

        priority = processor._determine_priority(email)

        assert priority == DocumentPriority.RESUBMISSION

    def test_determine_priority_correction(self, processor):
        """Test correction email gets resubmission priority."""
        email = MagicMock()
        email.subject = "Correction: Fixed pay stub"

        priority = processor._determine_priority(email)

        assert priority == DocumentPriority.RESUBMISSION

    def test_determine_priority_standard(self, processor):
        """Test normal email gets standard priority."""
        email = MagicMock()
        email.subject = "Document submission for case 12345"

        priority = processor._determine_priority(email)

        assert priority == DocumentPriority.STANDARD


class TestCheckDuplicate:
    """Tests for duplicate document detection."""

    @pytest.fixture
    def processor(self):
        """Create DocumentProcessor instance with mocked services."""
        with patch("src.agent.document_processor.get_storage_service") as mock_storage, \
             patch("src.agent.document_processor.get_audit_service") as mock_audit, \
             patch("src.agent.document_processor.get_document_intelligence_service") as mock_intel, \
             patch("src.agent.document_processor.get_email_service") as mock_email:

            storage_instance = MagicMock()
            storage_instance.compute_hash = MagicMock(return_value="abc123hash")
            mock_storage.return_value = storage_instance
            audit_instance = MagicMock()
            mock_audit.return_value = audit_instance
            intel_instance = MagicMock()
            mock_intel.return_value = intel_instance
            email_instance = MagicMock()
            mock_email.return_value = email_instance

            processor = DocumentProcessor()
            return processor

    def test_check_duplicate_no_match(self, processor):
        """Test no duplicate when hash doesn't exist."""
        result = processor.check_duplicate(b"content", "CASE-001")
        assert result is None

    def test_check_duplicate_same_case(self, processor):
        """Test duplicate detected for same case."""
        # Add a document to the processor
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.W2,
            source=DocumentSource.UPLOAD,
            filename="w2.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
        )
        processor._documents[str(doc.id)] = doc
        processor._content_hashes["abc123hash"] = str(doc.id)

        result = processor.check_duplicate(b"content", "CASE-001")

        assert result == str(doc.id)

    def test_check_duplicate_different_case(self, processor):
        """Test no duplicate detected for different case."""
        # Add a document to the processor
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.W2,
            source=DocumentSource.UPLOAD,
            filename="w2.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
        )
        processor._documents[str(doc.id)] = doc
        processor._content_hashes["abc123hash"] = str(doc.id)

        result = processor.check_duplicate(b"content", "CASE-002")  # Different case

        # Should NOT be flagged as duplicate for different case
        assert result is None
