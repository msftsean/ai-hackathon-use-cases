"""Azure Document Intelligence service for OCR and data extraction."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from src.config import get_settings
from src.models import DocumentType, PIIType

logger = logging.getLogger(__name__)


@dataclass
class ExtractedField:
    """Represents a field extracted from a document."""

    name: str
    value: str
    confidence: float
    bounding_box: Optional[dict] = None
    is_pii: bool = False
    pii_type: Optional[PIIType] = None


@dataclass
class ExtractionResult:
    """Result of document extraction."""

    document_type: DocumentType
    fields: list[ExtractedField]
    raw_text: str
    page_count: int
    overall_confidence: float
    model_id: str


class DocumentIntelligenceService(ABC):
    """Abstract base class for document intelligence service."""

    @abstractmethod
    async def analyze_document(
        self, content: bytes, content_type: str, document_type: Optional[DocumentType] = None
    ) -> ExtractionResult:
        """Analyze a document and extract structured data."""
        pass

    @abstractmethod
    async def classify_document(self, content: bytes, content_type: str) -> DocumentType:
        """Classify the type of document."""
        pass


class MockDocumentIntelligenceService(DocumentIntelligenceService):
    """Mock document intelligence service for development/testing."""

    # Pre-defined mock extractions for different document types
    MOCK_EXTRACTIONS = {
        DocumentType.W2: {
            "model_id": "prebuilt-tax.us.w2",
            "fields": [
                ExtractedField("employer_name", "ACME Corporation", 0.95),
                ExtractedField("employer_ein", "12-3456789", 0.92),
                ExtractedField("employee_ssn", "123-45-6789", 0.98, is_pii=True, pii_type=PIIType.SSN),
                ExtractedField("wages", "52500.00", 0.96),
                ExtractedField("federal_tax", "7875.00", 0.94),
                ExtractedField("tax_year", "2025", 0.99),
            ],
            "raw_text": "W-2 Wage and Tax Statement\nACME Corporation\nEIN: 12-3456789\nWages: $52,500.00",
        },
        DocumentType.PAYSTUB: {
            "model_id": "prebuilt-document",
            "fields": [
                ExtractedField("employer_name", "ACME Corporation", 0.93),
                ExtractedField("employee_name", "John Doe", 0.91),
                ExtractedField("gross_pay", "2187.50", 0.95),
                ExtractedField("net_pay", "1750.00", 0.94),
                ExtractedField("pay_period_start", "12/01/2025", 0.89),
                ExtractedField("pay_period_end", "12/15/2025", 0.89),
                ExtractedField("pay_date", "12/20/2025", 0.92),
            ],
            "raw_text": "Pay Stub\nACME Corporation\nEmployee: John Doe\nGross Pay: $2,187.50",
        },
        DocumentType.UTILITY_BILL: {
            "model_id": "prebuilt-document",
            "fields": [
                ExtractedField("provider_name", "Con Edison", 0.94),
                ExtractedField("account_number", "9876543210", 0.91, is_pii=True, pii_type=PIIType.BANK_ACCOUNT),
                ExtractedField("service_address", "123 Main St, Albany, NY 12207", 0.93, is_pii=True, pii_type=PIIType.ADDRESS),
                ExtractedField("billing_date", "12/15/2025", 0.96),
                ExtractedField("amount_due", "145.67", 0.97),
            ],
            "raw_text": "Con Edison Bill\n123 Main St, Albany, NY 12207\nAmount Due: $145.67",
        },
        DocumentType.BANK_STATEMENT: {
            "model_id": "prebuilt-document",
            "fields": [
                ExtractedField("institution_name", "First National Bank", 0.94),
                ExtractedField("account_number", "****5678", 0.90, is_pii=True, pii_type=PIIType.BANK_ACCOUNT),
                ExtractedField("statement_date", "12/31/2025", 0.95),
                ExtractedField("ending_balance", "3456.78", 0.93),
            ],
            "raw_text": "First National Bank Statement\nAccount: ****5678\nBalance: $3,456.78",
        },
        DocumentType.DRIVERS_LICENSE: {
            "model_id": "prebuilt-idDocument",
            "fields": [
                ExtractedField("full_name", "JOHN DOE", 0.96),
                ExtractedField("date_of_birth", "01/15/1985", 0.94, is_pii=True, pii_type=PIIType.DATE_OF_BIRTH),
                ExtractedField("license_number", "D123-4567-8901", 0.95, is_pii=True, pii_type=PIIType.DRIVERS_LICENSE_NUMBER),
                ExtractedField("address", "123 Main St, Albany, NY 12207", 0.92, is_pii=True, pii_type=PIIType.ADDRESS),
                ExtractedField("expiration_date", "01/15/2028", 0.97),
            ],
            "raw_text": "NEW YORK STATE DRIVER LICENSE\nJOHN DOE\nDOB: 01/15/1985",
        },
    }

    def __init__(self):
        """Initialize mock document intelligence service."""
        logger.info("MockDocumentIntelligenceService initialized")

    async def analyze_document(
        self, content: bytes, content_type: str, document_type: Optional[DocumentType] = None
    ) -> ExtractionResult:
        """Analyze a document using mock extraction data."""
        # If document type not provided, classify first
        if document_type is None:
            document_type = await self.classify_document(content, content_type)

        # Get mock data for this document type
        mock_data = self.MOCK_EXTRACTIONS.get(document_type, {
            "model_id": "prebuilt-document",
            "fields": [ExtractedField("content", "Unknown document content", 0.5)],
            "raw_text": "Document content not recognized",
        })

        # Calculate overall confidence
        fields = mock_data["fields"]
        overall_confidence = sum(f.confidence for f in fields) / len(fields) if fields else 0.0

        result = ExtractionResult(
            document_type=document_type,
            fields=fields,
            raw_text=mock_data["raw_text"],
            page_count=1,
            overall_confidence=overall_confidence,
            model_id=mock_data["model_id"],
        )

        logger.info(
            f"Mock extraction complete: {document_type.value}, "
            f"{len(fields)} fields, confidence: {overall_confidence:.2f}"
        )

        return result

    async def classify_document(self, content: bytes, content_type: str) -> DocumentType:
        """Classify document type based on content (mock implementation)."""
        # Simple heuristic based on content size and type
        content_lower = content.decode("utf-8", errors="ignore").lower()

        if "w-2" in content_lower or "wage and tax" in content_lower:
            return DocumentType.W2
        elif "pay stub" in content_lower or "gross pay" in content_lower:
            return DocumentType.PAYSTUB
        elif "utility" in content_lower or "electric" in content_lower or "con edison" in content_lower:
            return DocumentType.UTILITY_BILL
        elif "bank statement" in content_lower or "balance" in content_lower:
            return DocumentType.BANK_STATEMENT
        elif "driver" in content_lower or "license" in content_lower:
            return DocumentType.DRIVERS_LICENSE

        # Default to other
        return DocumentType.OTHER


class AzureDocumentIntelligenceService(DocumentIntelligenceService):
    """Azure Document Intelligence service for production."""

    def __init__(self):
        """Initialize Azure Document Intelligence client."""
        settings = get_settings()
        self._endpoint = settings.azure_doc_intelligence_endpoint
        self._key = settings.azure_doc_intelligence_key
        self._client = None
        logger.info("AzureDocumentIntelligenceService initialized")

    def _get_client(self):
        """Get or create Document Intelligence client."""
        if self._client is None:
            try:
                from azure.ai.documentintelligence import DocumentIntelligenceClient
                from azure.core.credentials import AzureKeyCredential

                self._client = DocumentIntelligenceClient(
                    endpoint=self._endpoint,
                    credential=AzureKeyCredential(self._key),
                )
            except ImportError:
                raise RuntimeError(
                    "azure-ai-documentintelligence package not installed. "
                    "Run: pip install azure-ai-documentintelligence"
                )
        return self._client

    def _get_model_id(self, document_type: DocumentType) -> str:
        """Get the appropriate model ID for a document type."""
        model_map = {
            DocumentType.W2: "prebuilt-tax.us.w2",
            DocumentType.DRIVERS_LICENSE: "prebuilt-idDocument",
        }
        return model_map.get(document_type, "prebuilt-document")

    async def analyze_document(
        self, content: bytes, content_type: str, document_type: Optional[DocumentType] = None
    ) -> ExtractionResult:
        """Analyze a document using Azure Document Intelligence."""
        client = self._get_client()

        # If document type not provided, classify first
        if document_type is None:
            document_type = await self.classify_document(content, content_type)

        model_id = self._get_model_id(document_type)

        try:
            poller = client.begin_analyze_document(
                model_id=model_id,
                body=content,
                content_type=content_type,
            )
            result = poller.result()

            # Extract fields from result
            fields = []
            if result.documents:
                for doc in result.documents:
                    if doc.fields:
                        for field_name, field_value in doc.fields.items():
                            is_pii, pii_type = self._detect_pii(field_name)
                            fields.append(
                                ExtractedField(
                                    name=field_name,
                                    value=str(field_value.value) if field_value.value else "",
                                    confidence=field_value.confidence or 0.0,
                                    bounding_box=self._extract_bounding_box(field_value),
                                    is_pii=is_pii,
                                    pii_type=pii_type,
                                )
                            )

            # Get raw text
            raw_text = result.content or ""

            # Calculate overall confidence
            overall_confidence = (
                sum(f.confidence for f in fields) / len(fields) if fields else 0.0
            )

            return ExtractionResult(
                document_type=document_type,
                fields=fields,
                raw_text=raw_text,
                page_count=len(result.pages) if result.pages else 1,
                overall_confidence=overall_confidence,
                model_id=model_id,
            )

        except Exception as e:
            logger.error(f"Document Intelligence analysis failed: {e}")
            raise

    async def classify_document(self, content: bytes, content_type: str) -> DocumentType:
        """Classify document type using Azure Document Intelligence."""
        client = self._get_client()

        try:
            # Use layout model to extract text for classification
            poller = client.begin_analyze_document(
                model_id="prebuilt-layout",
                body=content,
                content_type=content_type,
            )
            result = poller.result()

            # Simple keyword-based classification
            text = (result.content or "").lower()

            if "w-2" in text or "wage and tax" in text:
                return DocumentType.W2
            elif "pay stub" in text or "gross pay" in text or "net pay" in text:
                return DocumentType.PAYSTUB
            elif "utility" in text or "electric" in text or "gas bill" in text:
                return DocumentType.UTILITY_BILL
            elif "bank statement" in text or "account summary" in text:
                return DocumentType.BANK_STATEMENT
            elif "driver license" in text or "driver's license" in text:
                return DocumentType.DRIVERS_LICENSE

            return DocumentType.OTHER

        except Exception as e:
            logger.error(f"Document classification failed: {e}")
            return DocumentType.OTHER

    def _detect_pii(self, field_name: str) -> tuple[bool, Optional[PIIType]]:
        """Detect if a field contains PII based on its name."""
        pii_fields = {
            "ssn": PIIType.SSN,
            "social_security": PIIType.SSN,
            "employee_ssn": PIIType.SSN,
            "bank_account": PIIType.BANK_ACCOUNT,
            "account_number": PIIType.BANK_ACCOUNT,
            "routing_number": PIIType.ROUTING_NUMBER,
            "date_of_birth": PIIType.DATE_OF_BIRTH,
            "dob": PIIType.DATE_OF_BIRTH,
            "license_number": PIIType.DRIVERS_LICENSE_NUMBER,
            "address": PIIType.ADDRESS,
            "service_address": PIIType.ADDRESS,
            "phone": PIIType.PHONE,
            "email": PIIType.EMAIL,
        }

        field_lower = field_name.lower()
        for key, pii_type in pii_fields.items():
            if key in field_lower:
                return True, pii_type

        return False, None

    def _extract_bounding_box(self, field_value: Any) -> Optional[dict]:
        """Extract bounding box from field value."""
        if hasattr(field_value, "bounding_regions") and field_value.bounding_regions:
            region = field_value.bounding_regions[0]
            if hasattr(region, "polygon") and region.polygon:
                # Convert polygon to bounding box
                points = region.polygon
                if len(points) >= 4:
                    x_coords = [p.x for p in points]
                    y_coords = [p.y for p in points]
                    return {
                        "x": min(x_coords),
                        "y": min(y_coords),
                        "width": max(x_coords) - min(x_coords),
                        "height": max(y_coords) - min(y_coords),
                        "page": region.page_number or 1,
                    }
        return None


def get_document_intelligence_service() -> DocumentIntelligenceService:
    """Get document intelligence service instance based on configuration."""
    settings = get_settings()
    if settings.use_mock_services:
        return MockDocumentIntelligenceService()
    return AzureDocumentIntelligenceService()
