"""Validation agent for document validation rules."""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional

from src.config import get_settings
from src.models import DocumentType, RuleType, Severity, ValidationStatus
from src.models.extraction import Extraction
from src.models.validation_rule import ValidationRule, get_rules_for_document_type

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of a validation check."""

    def __init__(
        self,
        rule_name: str,
        status: ValidationStatus,
        message: Optional[str] = None,
        field_name: Optional[str] = None,
        severity: Severity = Severity.ERROR,
    ):
        self.rule_name = rule_name
        self.status = status
        self.message = message
        self.field_name = field_name
        self.severity = severity

    def to_dict(self) -> dict:
        return {
            "rule_name": self.rule_name,
            "status": self.status.value,
            "message": self.message,
            "field_name": self.field_name,
            "severity": self.severity.value,
        }


class ValidationAgent:
    """
    Agent responsible for validating documents and extractions.

    Validation types:
    - Document age validation (60 days for income, 30 days for bank, etc.)
    - Document completeness (all required fields present)
    - Quality/alteration detection
    - Cross-reference validation (name matching, address matching)
    - Format validation (SSN format, EIN format, etc.)
    - Range validation (amounts non-negative, etc.)
    """

    # Maximum document age by type (in days)
    MAX_AGE_DAYS = {
        DocumentType.PAYSTUB: 60,
        DocumentType.BANK_STATEMENT: 30,
        DocumentType.UTILITY_BILL: 60,
        DocumentType.W2: 730,  # 2 years
        DocumentType.DRIVERS_LICENSE: 0,  # Must not be expired
    }

    def __init__(self):
        """Initialize validation agent."""
        self._settings = get_settings()
        logger.info("ValidationAgent initialized")

    async def validate_document(
        self,
        document_type: DocumentType,
        extractions: list[Extraction],
        case_data: Optional[dict] = None,
    ) -> tuple[ValidationStatus, list[ValidationResult]]:
        """
        Run all validation rules on a document.

        Returns (overall_status, list of validation results)
        """
        logger.info(f"Validating document of type: {document_type.value}")

        results = []

        # Get applicable rules
        rules = get_rules_for_document_type(document_type)

        # Run each rule
        for rule in rules:
            try:
                result = await self._run_rule(rule, extractions, case_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Rule {rule.name} failed: {e}")
                results.append(ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.SKIPPED,
                    message=f"Rule execution failed: {e}",
                    severity=rule.severity,
                ))

        # Run built-in validations
        results.extend(self._validate_document_age(document_type, extractions))
        results.extend(self._validate_completeness(document_type, extractions))

        # Cross-reference validation if case data provided
        if case_data:
            results.extend(self._validate_cross_references(extractions, case_data))

        # Determine overall status
        overall_status = self._determine_overall_status(results)

        # Update extraction validation status
        self._update_extraction_status(extractions, results)

        logger.info(
            f"Validation complete: {overall_status.value}, "
            f"{len([r for r in results if r.status == ValidationStatus.PASSED])} passed, "
            f"{len([r for r in results if r.status == ValidationStatus.FAILED])} failed"
        )

        return overall_status, results

    async def _run_rule(
        self,
        rule: ValidationRule,
        extractions: list[Extraction],
        case_data: Optional[dict],
    ) -> ValidationResult:
        """Run a single validation rule."""
        if rule.rule_type == RuleType.AGE:
            return self._validate_age_rule(rule, extractions)
        elif rule.rule_type == RuleType.REQUIRED_FIELD:
            return self._validate_required_field(rule, extractions)
        elif rule.rule_type == RuleType.FORMAT:
            return self._validate_format(rule, extractions)
        elif rule.rule_type == RuleType.RANGE:
            return self._validate_range(rule, extractions)
        elif rule.rule_type == RuleType.CROSS_REFERENCE:
            return self._validate_cross_reference(rule, extractions, case_data)
        else:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.SKIPPED,
                message=f"Rule type {rule.rule_type.value} not implemented",
                severity=rule.severity,
            )

    def _validate_age_rule(
        self, rule: ValidationRule, extractions: list[Extraction]
    ) -> ValidationResult:
        """Validate document age using date fields."""
        # Look for date fields
        date_fields = ["pay_date", "billing_date", "statement_date", "tax_year"]
        date_value = None

        for field_name in date_fields:
            extraction = next((e for e in extractions if e.field_name == field_name), None)
            if extraction and extraction.field_value:
                date_value = extraction.field_value
                break

        if not date_value:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.WARNING,
                message="Could not find date field for age validation",
                severity=Severity.WARNING,
            )

        # Parse date
        parsed_date = self._parse_date(date_value)
        if not parsed_date:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.WARNING,
                message=f"Could not parse date: {date_value}",
                severity=Severity.WARNING,
            )

        # Check age
        max_age_days = rule.parameters.get("max_age_days", 60)
        max_age_years = rule.parameters.get("max_age_years")

        if max_age_years:
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_years * 365)
        else:
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

        if parsed_date < cutoff_date:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.FAILED,
                message=rule.error_message,
                severity=rule.severity,
            )

        return ValidationResult(
            rule_name=rule.name,
            status=ValidationStatus.PASSED,
            severity=rule.severity,
        )

    def _validate_required_field(
        self, rule: ValidationRule, extractions: list[Extraction]
    ) -> ValidationResult:
        """Validate that a required field is present."""
        field_name = rule.field_name
        extraction = next((e for e in extractions if e.field_name == field_name), None)

        if not extraction or not extraction.field_value:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.FAILED,
                message=rule.error_message,
                field_name=field_name,
                severity=rule.severity,
            )

        return ValidationResult(
            rule_name=rule.name,
            status=ValidationStatus.PASSED,
            field_name=field_name,
            severity=rule.severity,
        )

    def _validate_format(
        self, rule: ValidationRule, extractions: list[Extraction]
    ) -> ValidationResult:
        """Validate field format using regex pattern."""
        field_name = rule.field_name
        extraction = next((e for e in extractions if e.field_name == field_name), None)

        if not extraction or not extraction.field_value:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.SKIPPED,
                message=f"Field {field_name} not found",
                field_name=field_name,
                severity=rule.severity,
            )

        pattern = rule.parameters.get("pattern")
        if not pattern:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.SKIPPED,
                message="No pattern specified",
                field_name=field_name,
                severity=rule.severity,
            )

        if re.match(pattern, extraction.field_value):
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.PASSED,
                field_name=field_name,
                severity=rule.severity,
            )

        return ValidationResult(
            rule_name=rule.name,
            status=ValidationStatus.FAILED,
            message=rule.error_message,
            field_name=field_name,
            severity=rule.severity,
        )

    def _validate_range(
        self, rule: ValidationRule, extractions: list[Extraction]
    ) -> ValidationResult:
        """Validate numeric field is within range."""
        field_name = rule.field_name
        extraction = next((e for e in extractions if e.field_name == field_name), None)

        if not extraction or not extraction.field_value:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.SKIPPED,
                message=f"Field {field_name} not found",
                field_name=field_name,
                severity=rule.severity,
            )

        try:
            # Parse numeric value (remove currency symbols, commas)
            value_str = extraction.field_value.replace("$", "").replace(",", "")
            value = float(value_str)

            min_val = rule.parameters.get("min")
            max_val = rule.parameters.get("max")

            if min_val is not None and value < min_val:
                return ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.FAILED,
                    message=rule.error_message,
                    field_name=field_name,
                    severity=rule.severity,
                )

            if max_val is not None and value > max_val:
                return ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.FAILED,
                    message=rule.error_message,
                    field_name=field_name,
                    severity=rule.severity,
                )

            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.PASSED,
                field_name=field_name,
                severity=rule.severity,
            )

        except (ValueError, TypeError):
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.WARNING,
                message=f"Could not parse numeric value: {extraction.field_value}",
                field_name=field_name,
                severity=Severity.WARNING,
            )

    def _validate_cross_reference(
        self,
        rule: ValidationRule,
        extractions: list[Extraction],
        case_data: Optional[dict],
    ) -> ValidationResult:
        """Validate field against case data."""
        if not case_data:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.SKIPPED,
                message="No case data available for cross-reference",
                severity=rule.severity,
            )

        field_name = rule.field_name
        extraction = next((e for e in extractions if e.field_name == field_name), None)

        if not extraction:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.SKIPPED,
                message=f"Field {field_name} not found",
                field_name=field_name,
                severity=rule.severity,
            )

        # Get expected value from case data
        expected = case_data.get(field_name)
        if not expected:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.SKIPPED,
                message=f"No case data for {field_name}",
                field_name=field_name,
                severity=rule.severity,
            )

        # Fuzzy match for names/addresses
        if self._fuzzy_match(extraction.field_value, expected):
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.PASSED,
                field_name=field_name,
                severity=rule.severity,
            )

        return ValidationResult(
            rule_name=rule.name,
            status=ValidationStatus.WARNING,
            message=f"Value '{extraction.field_value}' does not match case data '{expected}'",
            field_name=field_name,
            severity=Severity.WARNING,
        )

    def _validate_document_age(
        self, document_type: DocumentType, extractions: list[Extraction]
    ) -> list[ValidationResult]:
        """Built-in document age validation."""
        results = []
        max_age = self.MAX_AGE_DAYS.get(document_type)

        if max_age is None:
            return results

        # Find date field
        date_fields = ["pay_date", "billing_date", "statement_date", "expiration_date"]
        date_extraction = None

        for field_name in date_fields:
            extraction = next((e for e in extractions if e.field_name == field_name), None)
            if extraction and extraction.field_value:
                date_extraction = extraction
                break

        if not date_extraction:
            return results

        parsed_date = self._parse_date(date_extraction.field_value)
        if not parsed_date:
            return results

        # Special handling for expiration dates (must be in future)
        if date_extraction.field_name == "expiration_date":
            if parsed_date < datetime.utcnow():
                results.append(ValidationResult(
                    rule_name="Document Expiration",
                    status=ValidationStatus.FAILED,
                    message="Document has expired",
                    field_name=date_extraction.field_name,
                    severity=Severity.ERROR,
                ))
            else:
                results.append(ValidationResult(
                    rule_name="Document Expiration",
                    status=ValidationStatus.PASSED,
                    field_name=date_extraction.field_name,
                ))
        else:
            # Check age for other date types
            cutoff = datetime.utcnow() - timedelta(days=max_age)
            if parsed_date < cutoff:
                results.append(ValidationResult(
                    rule_name="Document Age",
                    status=ValidationStatus.FAILED,
                    message=f"Document is older than {max_age} days",
                    field_name=date_extraction.field_name,
                    severity=Severity.ERROR,
                ))
            else:
                results.append(ValidationResult(
                    rule_name="Document Age",
                    status=ValidationStatus.PASSED,
                    field_name=date_extraction.field_name,
                ))

        return results

    def _validate_completeness(
        self, document_type: DocumentType, extractions: list[Extraction]
    ) -> list[ValidationResult]:
        """Check that all required fields are present."""
        from src.agent.extraction_agent import FIELD_MAPPINGS

        results = []
        mappings = FIELD_MAPPINGS.get(document_type, [])

        for mapping in mappings:
            if not mapping.required:
                continue

            extraction = next(
                (e for e in extractions if e.field_name == mapping.field_name), None
            )

            if not extraction or not extraction.field_value:
                results.append(ValidationResult(
                    rule_name="Required Field",
                    status=ValidationStatus.FAILED,
                    message=f"Required field '{mapping.display_name}' is missing",
                    field_name=mapping.field_name,
                    severity=Severity.ERROR,
                ))

        return results

    def _validate_cross_references(
        self, extractions: list[Extraction], case_data: dict
    ) -> list[ValidationResult]:
        """Cross-reference extracted data against case data."""
        results = []

        # Name matching
        name_fields = ["employee_name", "full_name", "tenant_name"]
        case_name = case_data.get("applicant_name")

        if case_name:
            for field_name in name_fields:
                extraction = next((e for e in extractions if e.field_name == field_name), None)
                if extraction and extraction.field_value:
                    if self._fuzzy_match(extraction.field_value, case_name):
                        results.append(ValidationResult(
                            rule_name="Name Match",
                            status=ValidationStatus.PASSED,
                            field_name=field_name,
                        ))
                    else:
                        results.append(ValidationResult(
                            rule_name="Name Match",
                            status=ValidationStatus.WARNING,
                            message=f"Name '{extraction.field_value}' may not match case name '{case_name}'",
                            field_name=field_name,
                            severity=Severity.WARNING,
                        ))
                    break

        # Address matching
        address_fields = ["service_address", "address", "property_address"]
        case_address = case_data.get("address")

        if case_address:
            for field_name in address_fields:
                extraction = next((e for e in extractions if e.field_name == field_name), None)
                if extraction and extraction.field_value:
                    if self._fuzzy_match(extraction.field_value, case_address):
                        results.append(ValidationResult(
                            rule_name="Address Match",
                            status=ValidationStatus.PASSED,
                            field_name=field_name,
                        ))
                    else:
                        results.append(ValidationResult(
                            rule_name="Address Match",
                            status=ValidationStatus.WARNING,
                            message="Address may not match case address",
                            field_name=field_name,
                            severity=Severity.WARNING,
                        ))
                    break

        return results

    def _determine_overall_status(self, results: list[ValidationResult]) -> ValidationStatus:
        """Determine overall validation status from results."""
        has_errors = any(
            r.status == ValidationStatus.FAILED and r.severity == Severity.ERROR
            for r in results
        )
        has_warnings = any(
            r.status in [ValidationStatus.FAILED, ValidationStatus.WARNING]
            and r.severity == Severity.WARNING
            for r in results
        )

        if has_errors:
            return ValidationStatus.FAILED
        elif has_warnings:
            return ValidationStatus.WARNING
        elif all(r.status in [ValidationStatus.PASSED, ValidationStatus.SKIPPED] for r in results):
            return ValidationStatus.PASSED
        else:
            return ValidationStatus.PENDING

    def _update_extraction_status(
        self, extractions: list[Extraction], results: list[ValidationResult]
    ) -> None:
        """Update extraction validation status from results."""
        # Group results by field name
        results_by_field = {}
        for result in results:
            if result.field_name:
                if result.field_name not in results_by_field:
                    results_by_field[result.field_name] = []
                results_by_field[result.field_name].append(result)

        # Update each extraction
        for extraction in extractions:
            field_results = results_by_field.get(extraction.field_name, [])

            if not field_results:
                extraction.validated = True
                extraction.validation_status = ValidationStatus.PASSED
            else:
                extraction.validated = True
                # Use worst status
                if any(r.status == ValidationStatus.FAILED for r in field_results):
                    extraction.validation_status = ValidationStatus.FAILED
                    extraction.validation_message = next(
                        (r.message for r in field_results if r.message), None
                    )
                elif any(r.status == ValidationStatus.WARNING for r in field_results):
                    extraction.validation_status = ValidationStatus.WARNING
                    extraction.validation_message = next(
                        (r.message for r in field_results if r.message), None
                    )
                else:
                    extraction.validation_status = ValidationStatus.PASSED

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats."""
        formats = [
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%Y",  # Just year (for W-2 tax year)
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None

    def _fuzzy_match(self, value1: str, value2: str, threshold: float = 0.8) -> bool:
        """Simple fuzzy string matching."""
        # Normalize strings
        v1 = value1.lower().strip()
        v2 = value2.lower().strip()

        # Exact match
        if v1 == v2:
            return True

        # Check if one contains the other
        if v1 in v2 or v2 in v1:
            return True

        # Simple word overlap check
        words1 = set(v1.split())
        words2 = set(v2.split())

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2)
        similarity = overlap / max(len(words1), len(words2))

        return similarity >= threshold
