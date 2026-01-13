"""Unit tests for ValidationAgent."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.agent.validation_agent import ValidationAgent, ValidationResult
from src.models import DocumentType, RuleType, Severity, ValidationStatus
from src.models.extraction import Extraction
from src.models.validation_rule import ValidationRule


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_to_dict(self):
        """Test ValidationResult to_dict conversion."""
        result = ValidationResult(
            rule_name="Test Rule",
            status=ValidationStatus.PASSED,
            message="Test message",
            field_name="test_field",
            severity=Severity.ERROR,
        )

        d = result.to_dict()
        assert d["rule_name"] == "Test Rule"
        assert d["status"] == "passed"
        assert d["message"] == "Test message"
        assert d["field_name"] == "test_field"
        assert d["severity"] == "error"


class TestValidationAgent:
    """Tests for ValidationAgent class."""

    @pytest.fixture
    def agent(self):
        """Create ValidationAgent instance."""
        return ValidationAgent()

    @pytest.fixture
    def sample_extractions(self):
        """Create sample extraction data."""
        doc_id = uuid4()
        return [
            Extraction(
                document_id=doc_id,
                field_name="employer_name",
                field_value="ACME Corp",
                confidence=0.95,
            ),
            Extraction(
                document_id=doc_id,
                field_name="wages",
                field_value="$50,000.00",
                confidence=0.92,
            ),
            Extraction(
                document_id=doc_id,
                field_name="pay_date",
                field_value=datetime.utcnow().strftime("%m/%d/%Y"),
                confidence=0.88,
            ),
        ]

    @pytest.mark.asyncio
    async def test_validate_document_returns_status_and_results(self, agent, sample_extractions):
        """Test that validate_document returns status and results list."""
        status, results = await agent.validate_document(
            document_type=DocumentType.PAYSTUB,
            extractions=sample_extractions,
        )

        assert isinstance(status, ValidationStatus)
        assert isinstance(results, list)
        assert all(isinstance(r, ValidationResult) for r in results)

    @pytest.mark.asyncio
    async def test_validate_document_with_case_data(self, agent, sample_extractions):
        """Test validation with case data for cross-referencing."""
        sample_extractions.append(
            Extraction(
                document_id=sample_extractions[0].document_id,
                field_name="employee_name",
                field_value="John Doe",
                confidence=0.90,
            )
        )

        case_data = {
            "applicant_name": "John Doe",
            "address": "123 Main St",
        }

        status, results = await agent.validate_document(
            document_type=DocumentType.PAYSTUB,
            extractions=sample_extractions,
            case_data=case_data,
        )

        assert isinstance(status, ValidationStatus)
        # Cross-reference validation should be included
        cross_ref_results = [r for r in results if "Match" in r.rule_name]
        assert len(cross_ref_results) > 0

    @pytest.mark.asyncio
    async def test_validate_document_old_date_fails(self, agent):
        """Test that old documents fail age validation."""
        doc_id = uuid4()
        old_date = (datetime.utcnow() - timedelta(days=100)).strftime("%m/%d/%Y")
        extractions = [
            Extraction(
                document_id=doc_id,
                field_name="pay_date",
                field_value=old_date,
                confidence=0.95,
            ),
        ]

        status, results = await agent.validate_document(
            document_type=DocumentType.PAYSTUB,
            extractions=extractions,
        )

        # Should have failed age validation
        age_results = [r for r in results if "Age" in r.rule_name]
        failed_age = [r for r in age_results if r.status == ValidationStatus.FAILED]
        assert len(failed_age) > 0

    def test_validate_required_field_missing(self, agent):
        """Test required field validation when field is missing."""
        rule = ValidationRule(
            name="Test Required",
            document_type=DocumentType.W2,
            rule_type=RuleType.REQUIRED_FIELD,
            field_name="employer_name",
            error_message="Employer name required",
            created_by="test",
        )

        extractions = []  # No extractions

        result = agent._validate_required_field(rule, extractions)

        assert result.status == ValidationStatus.FAILED
        assert result.field_name == "employer_name"

    def test_validate_required_field_present(self, agent):
        """Test required field validation when field is present."""
        rule = ValidationRule(
            name="Test Required",
            document_type=DocumentType.W2,
            rule_type=RuleType.REQUIRED_FIELD,
            field_name="employer_name",
            error_message="Employer name required",
            created_by="test",
        )

        extractions = [
            Extraction(
                document_id=uuid4(),
                field_name="employer_name",
                field_value="ACME Corp",
                confidence=0.95,
            )
        ]

        result = agent._validate_required_field(rule, extractions)

        assert result.status == ValidationStatus.PASSED

    def test_validate_format_valid(self, agent):
        """Test format validation with valid pattern."""
        rule = ValidationRule(
            name="SSN Format",
            document_type=DocumentType.W2,
            rule_type=RuleType.FORMAT,
            field_name="employee_ssn",
            parameters={"pattern": r"^\d{3}-\d{2}-\d{4}$"},
            error_message="Invalid SSN format",
            created_by="test",
        )

        extractions = [
            Extraction(
                document_id=uuid4(),
                field_name="employee_ssn",
                field_value="123-45-6789",
                confidence=0.95,
            )
        ]

        result = agent._validate_format(rule, extractions)

        assert result.status == ValidationStatus.PASSED

    def test_validate_format_invalid(self, agent):
        """Test format validation with invalid pattern."""
        rule = ValidationRule(
            name="SSN Format",
            document_type=DocumentType.W2,
            rule_type=RuleType.FORMAT,
            field_name="employee_ssn",
            parameters={"pattern": r"^\d{3}-\d{2}-\d{4}$"},
            error_message="Invalid SSN format",
            created_by="test",
        )

        extractions = [
            Extraction(
                document_id=uuid4(),
                field_name="employee_ssn",
                field_value="12345",  # Invalid format
                confidence=0.95,
            )
        ]

        result = agent._validate_format(rule, extractions)

        assert result.status == ValidationStatus.FAILED

    def test_validate_range_valid(self, agent):
        """Test range validation with valid value."""
        rule = ValidationRule(
            name="Wages Non-Negative",
            document_type=DocumentType.W2,
            rule_type=RuleType.RANGE,
            field_name="wages",
            parameters={"min": 0},
            error_message="Wages cannot be negative",
            created_by="test",
        )

        extractions = [
            Extraction(
                document_id=uuid4(),
                field_name="wages",
                field_value="$50,000",
                confidence=0.95,
            )
        ]

        result = agent._validate_range(rule, extractions)

        assert result.status == ValidationStatus.PASSED

    def test_validate_range_below_min(self, agent):
        """Test range validation with value below minimum."""
        rule = ValidationRule(
            name="Wages Non-Negative",
            document_type=DocumentType.W2,
            rule_type=RuleType.RANGE,
            field_name="wages",
            parameters={"min": 0},
            error_message="Wages cannot be negative",
            created_by="test",
        )

        extractions = [
            Extraction(
                document_id=uuid4(),
                field_name="wages",
                field_value="-100",
                confidence=0.95,
            )
        ]

        result = agent._validate_range(rule, extractions)

        assert result.status == ValidationStatus.FAILED

    def test_validate_range_above_max(self, agent):
        """Test range validation with value above maximum."""
        rule = ValidationRule(
            name="Max Test",
            document_type=DocumentType.W2,
            rule_type=RuleType.RANGE,
            field_name="amount",
            parameters={"max": 1000},
            error_message="Amount too high",
            created_by="test",
        )

        extractions = [
            Extraction(
                document_id=uuid4(),
                field_name="amount",
                field_value="2000",
                confidence=0.95,
            )
        ]

        result = agent._validate_range(rule, extractions)

        assert result.status == ValidationStatus.FAILED

    def test_fuzzy_match_exact(self, agent):
        """Test fuzzy matching with exact match."""
        assert agent._fuzzy_match("John Doe", "John Doe") is True

    def test_fuzzy_match_case_insensitive(self, agent):
        """Test fuzzy matching is case insensitive."""
        assert agent._fuzzy_match("JOHN DOE", "john doe") is True

    def test_fuzzy_match_contains(self, agent):
        """Test fuzzy matching with containment."""
        assert agent._fuzzy_match("John Doe", "John Doe Jr") is True

    def test_fuzzy_match_word_overlap(self, agent):
        """Test fuzzy matching with word overlap."""
        assert agent._fuzzy_match("John Robert Doe", "Robert Doe") is True

    def test_fuzzy_match_no_match(self, agent):
        """Test fuzzy matching with no match."""
        assert agent._fuzzy_match("John Doe", "Jane Smith") is False

    def test_parse_date_us_format(self, agent):
        """Test date parsing with US format."""
        result = agent._parse_date("12/25/2024")
        assert result is not None
        assert result.month == 12
        assert result.day == 25
        assert result.year == 2024

    def test_parse_date_iso_format(self, agent):
        """Test date parsing with ISO format."""
        result = agent._parse_date("2024-12-25")
        assert result is not None
        assert result.year == 2024

    def test_parse_date_year_only(self, agent):
        """Test date parsing with year only (W-2 tax year)."""
        result = agent._parse_date("2024")
        assert result is not None
        assert result.year == 2024

    def test_parse_date_invalid(self, agent):
        """Test date parsing with invalid format."""
        result = agent._parse_date("not a date")
        assert result is None

    def test_determine_overall_status_all_passed(self, agent):
        """Test overall status when all passed."""
        results = [
            ValidationResult("Rule1", ValidationStatus.PASSED, severity=Severity.ERROR),
            ValidationResult("Rule2", ValidationStatus.PASSED, severity=Severity.ERROR),
        ]

        status = agent._determine_overall_status(results)

        assert status == ValidationStatus.PASSED

    def test_determine_overall_status_has_error(self, agent):
        """Test overall status when there's an error."""
        results = [
            ValidationResult("Rule1", ValidationStatus.PASSED, severity=Severity.ERROR),
            ValidationResult("Rule2", ValidationStatus.FAILED, severity=Severity.ERROR),
        ]

        status = agent._determine_overall_status(results)

        assert status == ValidationStatus.FAILED

    def test_determine_overall_status_has_warning(self, agent):
        """Test overall status when there's a warning but no error."""
        results = [
            ValidationResult("Rule1", ValidationStatus.PASSED, severity=Severity.ERROR),
            ValidationResult("Rule2", ValidationStatus.WARNING, severity=Severity.WARNING),
        ]

        status = agent._determine_overall_status(results)

        assert status == ValidationStatus.WARNING
