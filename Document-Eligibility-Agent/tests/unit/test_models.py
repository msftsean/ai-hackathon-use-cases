"""Unit tests for data models."""

import pytest
from datetime import datetime
from uuid import uuid4

from src.models import (
    DocumentType,
    DocumentStatus,
    DocumentSource,
    DocumentPriority,
    ValidationStatus,
    PIIType,
    RuleType,
    Severity,
)
from src.models.document import Document
from src.models.extraction import Extraction, BoundingBox
from src.models.validation_rule import ValidationRule, get_rules_for_document_type


class TestDocumentModel:
    """Tests for Document model."""

    def test_document_creation(self):
        """Test basic document creation."""
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.W2,
            source=DocumentSource.UPLOAD,
            filename="w2.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
        )

        assert doc.case_id == "CASE-001"
        assert doc.document_type == DocumentType.W2
        assert doc.source == DocumentSource.UPLOAD
        assert doc.filename == "w2.pdf"
        assert doc.status == DocumentStatus.UPLOADED

    def test_document_to_dict(self):
        """Test document serialization."""
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.PAYSTUB,
            source=DocumentSource.EMAIL,
            filename="paystub.pdf",
            file_size_bytes=2048,
            mime_type="application/pdf",
            priority=DocumentPriority.EXPEDITED,
        )

        d = doc.to_dict()

        assert d["case_id"] == "CASE-001"
        assert d["document_type"] == "paystub"
        assert d["source"] == "email"
        assert d["priority"] == "expedited"
        assert "id" in d

    def test_document_update_status(self):
        """Test status update."""
        doc = Document(
            case_id="CASE-001",
            document_type=DocumentType.W2,
            source=DocumentSource.UPLOAD,
            filename="w2.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
        )

        doc.update_status(DocumentStatus.PROCESSING)

        assert doc.status == DocumentStatus.PROCESSING


class TestExtractionModel:
    """Tests for Extraction model."""

    def test_extraction_creation(self):
        """Test basic extraction creation."""
        doc_id = uuid4()
        ext = Extraction(
            document_id=doc_id,
            field_name="employer_name",
            field_value="ACME Corp",
            confidence=0.95,
        )

        assert ext.document_id == doc_id
        assert ext.field_name == "employer_name"
        assert ext.field_value == "ACME Corp"
        assert ext.confidence == 0.95

    def test_extraction_confidence_validation(self):
        """Test confidence must be between 0 and 1."""
        doc_id = uuid4()

        with pytest.raises(ValueError):
            Extraction(
                document_id=doc_id,
                field_name="test",
                field_value="value",
                confidence=1.5,  # Invalid
            )

    def test_extraction_mask_ssn(self):
        """Test SSN masking."""
        doc_id = uuid4()
        ext = Extraction(
            document_id=doc_id,
            field_name="ssn",
            field_value="123-45-6789",
            confidence=0.95,
            is_pii=True,
            pii_type=PIIType.SSN,
        )

        masked = ext._mask_value()

        assert masked == "XXX-XX-6789"

    def test_extraction_mask_bank_account(self):
        """Test bank account masking."""
        doc_id = uuid4()
        ext = Extraction(
            document_id=doc_id,
            field_name="account",
            field_value="123456789012",
            confidence=0.95,
            is_pii=True,
            pii_type=PIIType.BANK_ACCOUNT,
        )

        masked = ext._mask_value()

        assert masked == "****9012"

    def test_extraction_get_display_value_pii(self):
        """Test display value masking for PII."""
        doc_id = uuid4()
        ext = Extraction(
            document_id=doc_id,
            field_name="ssn",
            field_value="123-45-6789",
            confidence=0.95,
            is_pii=True,
            pii_type=PIIType.SSN,
        )

        # Without PII access
        masked = ext.get_display_value(include_pii=False)
        assert "XXX" in masked

        # With PII access
        unmasked = ext.get_display_value(include_pii=True)
        assert unmasked == "123-45-6789"

    def test_extraction_correct(self):
        """Test manual correction."""
        doc_id = uuid4()
        ext = Extraction(
            document_id=doc_id,
            field_name="employer_name",
            field_value="ACME Corp",
            confidence=0.85,
        )

        ext.correct("ACME Corporation", "user-123")

        assert ext.field_value == "ACME Corporation"
        assert ext.original_value == "ACME Corp"
        assert ext.manually_corrected is True
        assert ext.corrected_by == "user-123"
        assert ext.confidence == 1.0

    def test_extraction_set_validation_result(self):
        """Test setting validation result."""
        doc_id = uuid4()
        ext = Extraction(
            document_id=doc_id,
            field_name="test",
            field_value="value",
            confidence=0.95,
        )

        ext.set_validation_result(ValidationStatus.PASSED)

        assert ext.validated is True
        assert ext.validation_status == ValidationStatus.PASSED


class TestBoundingBox:
    """Tests for BoundingBox model."""

    def test_bounding_box_creation(self):
        """Test bounding box creation."""
        box = BoundingBox(x=100.0, y=200.0, width=150.0, height=50.0, page=1)

        assert box.x == 100.0
        assert box.y == 200.0
        assert box.width == 150.0
        assert box.height == 50.0
        assert box.page == 1


class TestValidationRule:
    """Tests for ValidationRule model."""

    def test_validation_rule_creation(self):
        """Test validation rule creation."""
        rule = ValidationRule(
            name="Test Rule",
            document_type=DocumentType.W2,
            rule_type=RuleType.REQUIRED_FIELD,
            field_name="employer_name",
            error_message="Employer name is required",
            created_by="admin",
        )

        assert rule.name == "Test Rule"
        assert rule.document_type == DocumentType.W2
        assert rule.rule_type == RuleType.REQUIRED_FIELD

    def test_validation_rule_to_dict(self):
        """Test rule serialization."""
        rule = ValidationRule(
            name="Format Rule",
            document_type=DocumentType.W2,
            rule_type=RuleType.FORMAT,
            field_name="ssn",
            parameters={"pattern": r"^\d{3}-\d{2}-\d{4}$"},
            error_message="Invalid SSN format",
            created_by="admin",
        )

        d = rule.to_dict()

        assert d["name"] == "Format Rule"
        assert d["rule_type"] == "format"
        assert "pattern" in d["parameters"]

    def test_get_rules_for_document_type_w2(self):
        """Test getting rules for W-2 documents."""
        rules = get_rules_for_document_type(DocumentType.W2)

        assert len(rules) > 0
        assert all(r.document_type == DocumentType.W2 for r in rules)

    def test_get_rules_for_document_type_paystub(self):
        """Test getting rules for paystub documents."""
        rules = get_rules_for_document_type(DocumentType.PAYSTUB)

        assert len(rules) > 0
        assert all(r.document_type == DocumentType.PAYSTUB for r in rules)


class TestEnums:
    """Tests for enum values."""

    def test_document_type_values(self):
        """Test DocumentType enum values."""
        assert DocumentType.W2.value == "w2"
        assert DocumentType.PAYSTUB.value == "paystub"
        assert DocumentType.UTILITY_BILL.value == "utility_bill"

    def test_document_status_values(self):
        """Test DocumentStatus enum values."""
        assert DocumentStatus.UPLOADED.value == "uploaded"
        assert DocumentStatus.PROCESSING.value == "processing"
        assert DocumentStatus.APPROVED.value == "approved"

    def test_validation_status_values(self):
        """Test ValidationStatus enum values."""
        assert ValidationStatus.PASSED.value == "passed"
        assert ValidationStatus.FAILED.value == "failed"
        assert ValidationStatus.WARNING.value == "warning"

    def test_severity_values(self):
        """Test Severity enum values."""
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"
