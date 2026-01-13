"""Extraction agent for field-level data extraction with confidence scoring."""

import logging
from dataclasses import dataclass
from typing import Optional

from src.config import get_settings
from src.models import DocumentType, PIIType
from src.models.extraction import BoundingBox, Extraction
from src.services.document_intelligence import (
    ExtractedField,
    ExtractionResult,
    get_document_intelligence_service,
)

logger = logging.getLogger(__name__)


@dataclass
class FieldMapping:
    """Mapping configuration for a document field."""

    field_name: str
    display_name: str
    is_pii: bool = False
    pii_type: Optional[PIIType] = None
    required: bool = False


# Field mappings by document type (from data-model.md)
FIELD_MAPPINGS = {
    DocumentType.W2: [
        FieldMapping("employer_name", "Employer Name", required=True),
        FieldMapping("employer_ein", "Employer EIN"),
        FieldMapping("employee_ssn", "Employee SSN", is_pii=True, pii_type=PIIType.SSN),
        FieldMapping("wages", "Wages, Tips, etc.", required=True),
        FieldMapping("federal_tax", "Federal Tax Withheld"),
        FieldMapping("tax_year", "Tax Year", required=True),
    ],
    DocumentType.PAYSTUB: [
        FieldMapping("employer_name", "Employer", required=True),
        FieldMapping("employee_name", "Employee Name"),
        FieldMapping("gross_pay", "Gross Pay", required=True),
        FieldMapping("net_pay", "Net Pay"),
        FieldMapping("pay_period_start", "Period Start"),
        FieldMapping("pay_period_end", "Period End"),
        FieldMapping("pay_date", "Pay Date", required=True),
    ],
    DocumentType.UTILITY_BILL: [
        FieldMapping("provider_name", "Provider", required=True),
        FieldMapping("account_number", "Account #", is_pii=True, pii_type=PIIType.BANK_ACCOUNT),
        FieldMapping("service_address", "Service Address", is_pii=True, pii_type=PIIType.ADDRESS),
        FieldMapping("billing_date", "Bill Date", required=True),
        FieldMapping("amount_due", "Amount Due"),
    ],
    DocumentType.BANK_STATEMENT: [
        FieldMapping("institution_name", "Institution", required=True),
        FieldMapping("account_number", "Account #", is_pii=True, pii_type=PIIType.BANK_ACCOUNT),
        FieldMapping("statement_date", "Statement Date", required=True),
        FieldMapping("ending_balance", "Ending Balance"),
    ],
    DocumentType.DRIVERS_LICENSE: [
        FieldMapping("full_name", "Full Name", required=True),
        FieldMapping("date_of_birth", "Date of Birth", is_pii=True, pii_type=PIIType.DATE_OF_BIRTH),
        FieldMapping("license_number", "License Number", is_pii=True, pii_type=PIIType.DRIVERS_LICENSE_NUMBER),
        FieldMapping("address", "Address", is_pii=True, pii_type=PIIType.ADDRESS),
        FieldMapping("expiration_date", "Expiration Date", required=True),
    ],
    DocumentType.BIRTH_CERTIFICATE: [
        FieldMapping("full_name", "Full Name", required=True),
        FieldMapping("date_of_birth", "Date of Birth", is_pii=True, pii_type=PIIType.DATE_OF_BIRTH),
        FieldMapping("place_of_birth", "Place of Birth"),
        FieldMapping("parent_1_name", "Parent 1 Name"),
        FieldMapping("parent_2_name", "Parent 2 Name"),
    ],
    DocumentType.LEASE_AGREEMENT: [
        FieldMapping("landlord_name", "Landlord Name", required=True),
        FieldMapping("tenant_name", "Tenant Name"),
        FieldMapping("property_address", "Property Address", is_pii=True, pii_type=PIIType.ADDRESS),
        FieldMapping("lease_start_date", "Lease Start"),
        FieldMapping("lease_end_date", "Lease End"),
        FieldMapping("monthly_rent", "Monthly Rent"),
    ],
}


class ExtractionAgent:
    """
    Agent responsible for extracting structured data from documents.

    Features:
    - Field-specific extraction using Document Intelligence
    - Confidence score calculation: 0.5*OCR + 0.3*field + 0.2*validation
    - Low-confidence highlighting (threshold: 0.85)
    - PII detection and masking
    """

    def __init__(self):
        """Initialize extraction agent."""
        self._doc_intelligence = get_document_intelligence_service()
        self._settings = get_settings()
        logger.info("ExtractionAgent initialized")

    async def extract_fields(
        self,
        document_id: str,
        content: bytes,
        content_type: str,
        document_type: DocumentType,
    ) -> list[Extraction]:
        """
        Extract fields from a document.

        Returns list of Extraction objects with confidence scores.
        """
        logger.info(f"Extracting fields for document {document_id} ({document_type.value})")

        # Get extraction result from Document Intelligence
        result = await self._doc_intelligence.analyze_document(
            content=content,
            content_type=content_type,
            document_type=document_type,
        )

        # Convert to Extraction models with field mappings
        extractions = self._process_extraction_result(
            document_id=document_id,
            result=result,
            document_type=document_type,
        )

        # Calculate combined confidence scores
        for extraction in extractions:
            extraction.confidence = self._calculate_confidence(
                ocr_confidence=result.overall_confidence,
                field_confidence=extraction.confidence,
                validation_score=1.0,  # Will be updated after validation
            )

        # Flag low-confidence extractions
        low_confidence_count = sum(
            1 for e in extractions
            if e.confidence < self._settings.confidence_threshold
        )

        logger.info(
            f"Extracted {len(extractions)} fields, "
            f"{low_confidence_count} below confidence threshold"
        )

        return extractions

    def _process_extraction_result(
        self,
        document_id: str,
        result: ExtractionResult,
        document_type: DocumentType,
    ) -> list[Extraction]:
        """Process extraction result and apply field mappings."""
        from uuid import UUID

        extractions = []
        field_mappings = FIELD_MAPPINGS.get(document_type, [])

        # Create lookup for extracted fields
        extracted_fields = {f.name.lower(): f for f in result.fields}

        # Process each mapped field
        for mapping in field_mappings:
            field = extracted_fields.get(mapping.field_name.lower())

            if field:
                bounding_box = None
                if field.bounding_box:
                    bounding_box = BoundingBox(**field.bounding_box)

                extraction = Extraction(
                    document_id=UUID(document_id),
                    field_name=mapping.field_name,
                    field_value=field.value,
                    confidence=field.confidence,
                    bounding_box=bounding_box,
                    is_pii=mapping.is_pii or field.is_pii,
                    pii_type=mapping.pii_type or field.pii_type,
                )

                # Generate display value
                if extraction.is_pii:
                    extraction.display_value = extraction._mask_value()

                extractions.append(extraction)

            elif mapping.required:
                # Create placeholder for required missing field
                extraction = Extraction(
                    document_id=UUID(document_id),
                    field_name=mapping.field_name,
                    field_value="",
                    confidence=0.0,
                    is_pii=mapping.is_pii,
                    pii_type=mapping.pii_type,
                )
                extractions.append(extraction)

        # Add any additional extracted fields not in mapping
        for field in result.fields:
            if field.name.lower() not in [m.field_name.lower() for m in field_mappings]:
                bounding_box = None
                if field.bounding_box:
                    bounding_box = BoundingBox(**field.bounding_box)

                extraction = Extraction(
                    document_id=UUID(document_id),
                    field_name=field.name,
                    field_value=field.value,
                    confidence=field.confidence,
                    bounding_box=bounding_box,
                    is_pii=field.is_pii,
                    pii_type=field.pii_type,
                )
                if extraction.is_pii:
                    extraction.display_value = extraction._mask_value()
                extractions.append(extraction)

        return extractions

    def _calculate_confidence(
        self,
        ocr_confidence: float,
        field_confidence: float,
        validation_score: float,
    ) -> float:
        """
        Calculate combined confidence score.

        Formula: 0.5 * OCR_confidence + 0.3 * field_confidence + 0.2 * validation_score

        This weights:
        - OCR quality (50%): Foundation of extraction accuracy
        - Field-level confidence (30%): Model's certainty about specific field
        - Validation score (20%): Additional signal from validation rules
        """
        return (
            0.5 * ocr_confidence +
            0.3 * field_confidence +
            0.2 * validation_score
        )

    def is_low_confidence(self, extraction: Extraction) -> bool:
        """Check if extraction is below confidence threshold."""
        return extraction.confidence < self._settings.confidence_threshold

    def get_low_confidence_fields(self, extractions: list[Extraction]) -> list[Extraction]:
        """Get all extractions below confidence threshold."""
        return [e for e in extractions if self.is_low_confidence(e)]

    def get_field_mapping(self, document_type: DocumentType) -> list[FieldMapping]:
        """Get field mappings for a document type."""
        return FIELD_MAPPINGS.get(document_type, [])

    def get_required_fields(self, document_type: DocumentType) -> list[str]:
        """Get list of required field names for a document type."""
        mappings = FIELD_MAPPINGS.get(document_type, [])
        return [m.field_name for m in mappings if m.required]

    def check_required_fields(
        self, extractions: list[Extraction], document_type: DocumentType
    ) -> tuple[bool, list[str]]:
        """
        Check if all required fields are present and have values.

        Returns (all_present, missing_field_names)
        """
        required = self.get_required_fields(document_type)
        extracted_names = {e.field_name for e in extractions if e.field_value}

        missing = [f for f in required if f not in extracted_names]

        return len(missing) == 0, missing
