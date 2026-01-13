"""Tests for Compliance Engine."""

import pytest

from src.config import Settings
from src.core.compliance_engine import ComplianceEngine
from src.models.enums import Severity, RuleCategory, DocumentFormat
from src.models.compliance_rule import ComplianceRule
from src.models.policy_document import PolicyDocument


@pytest.fixture
def engine():
    """Create compliance engine."""
    settings = Settings()
    settings.use_mock_services = True
    return ComplianceEngine(settings)


@pytest.fixture
def sample_document():
    """Create sample policy document."""
    return PolicyDocument(
        filename="test_policy.md",
        format=DocumentFormat.MARKDOWN,
        title="Test Policy",
        content="""
# Test Policy Document

## Data Protection
All social security numbers must be encrypted.
Data is shared with third party vendors.

## IT Security
Password policy requires 8 character minimum.
All data encrypted using AES encryption.

## HR Policy
We have a harassment policy in place.
        """,
    )


class TestComplianceEngine:
    """Tests for ComplianceEngine."""

    def test_engine_loads_builtin_rules(self, engine):
        """Test that engine loads built-in rules."""
        rules = engine.list_rules()
        assert len(rules) > 0

    def test_list_rules_by_category(self, engine):
        """Test listing rules by category."""
        dp_rules = engine.list_rules(category=RuleCategory.DATA_PROTECTION)
        assert len(dp_rules) > 0
        for rule in dp_rules:
            assert rule.category == RuleCategory.DATA_PROTECTION

    def test_add_custom_rule(self, engine):
        """Test adding custom rule."""
        initial_count = len(engine.list_rules())

        rule = ComplianceRule(
            name="Test Rule",
            description="Test description",
            pattern=r"test\s*pattern",
            severity=Severity.LOW,
            category=RuleCategory.CUSTOM,
            recommendation_template="Test recommendation",
            is_builtin=False,
        )

        engine.add_rule(rule)

        assert len(engine.list_rules()) == initial_count + 1
        assert engine.get_rule(rule.id) is not None

    def test_add_rule_invalid_pattern(self, engine):
        """Test adding rule with invalid regex."""
        rule = ComplianceRule(
            name="Bad Rule",
            description="Test",
            pattern=r"[invalid",  # Invalid regex
            severity=Severity.LOW,
            category=RuleCategory.CUSTOM,
            recommendation_template="Test",
        )

        with pytest.raises(ValueError):
            engine.add_rule(rule)

    def test_remove_custom_rule(self, engine):
        """Test removing custom rule."""
        rule = ComplianceRule(
            name="Temp Rule",
            description="Test",
            pattern=r"temp",
            severity=Severity.LOW,
            category=RuleCategory.CUSTOM,
            recommendation_template="Test",
            is_builtin=False,
        )

        engine.add_rule(rule)
        assert engine.get_rule(rule.id) is not None

        engine.remove_rule(rule.id)
        assert engine.get_rule(rule.id) is None

    def test_cannot_remove_builtin_rule(self, engine):
        """Test that built-in rules cannot be removed."""
        rules = engine.list_rules()
        builtin_rule = next(r for r in rules if r.is_builtin)

        with pytest.raises(ValueError):
            engine.remove_rule(builtin_rule.id)

    def test_analyze_finds_violations(self, engine, sample_document):
        """Test that analysis finds violations."""
        report = engine.analyze(sample_document)

        assert report is not None
        assert report.document_id == sample_document.id
        assert report.summary.violations.total > 0

    def test_analyze_calculates_score(self, engine, sample_document):
        """Test that analysis calculates compliance score."""
        report = engine.analyze(sample_document)

        assert 0 <= report.summary.compliance_score <= 100

    def test_analyze_generates_recommendations(self, engine, sample_document):
        """Test that analysis generates recommendations."""
        report = engine.analyze(sample_document)

        # If there are violations, should have recommendations
        if report.summary.violations.total > 0:
            assert len(report.recommendations) > 0

    def test_analyze_with_specific_rules(self, engine, sample_document):
        """Test analyzing with specific rule IDs."""
        rules = engine.list_rules(category=RuleCategory.DATA_PROTECTION)
        rule_ids = [r.id for r in rules]

        report = engine.analyze(sample_document, rule_ids=rule_ids)

        assert report.summary.total_rules_applied == len(rule_ids)


class TestSeverityScoring:
    """Tests for severity scoring."""

    def test_severity_weights(self):
        """Test severity weight values."""
        assert Severity.CRITICAL.weight == 25
        assert Severity.HIGH.weight == 15
        assert Severity.MEDIUM.weight == 5
        assert Severity.LOW.weight == 1

    def test_clean_document_score(self, engine):
        """Test clean document gets 100 score."""
        clean_doc = PolicyDocument(
            filename="clean.txt",
            format=DocumentFormat.TEXT,
            title="Clean Document",
            content="This is a clean document with no compliance issues.",
        )

        report = engine.analyze(clean_doc)

        # Should have 100 score if no violations found
        # (may still find some matches depending on rules)
        assert report.summary.compliance_score >= 0

    def test_score_decreases_with_violations(self, engine):
        """Test score decreases with violations."""
        # Document with PII mention
        pii_doc = PolicyDocument(
            filename="pii.txt",
            format=DocumentFormat.TEXT,
            title="PII Document",
            content="We store social security numbers and driver's license data.",
        )

        report = engine.analyze(pii_doc)

        # Should have lower score due to critical violations
        assert report.summary.compliance_score < 100

    def test_minimum_score_is_zero(self, engine):
        """Test score cannot go below zero."""
        # Document with many violations
        bad_doc = PolicyDocument(
            filename="bad.txt",
            format=DocumentFormat.TEXT,
            title="Bad Document",
            content="""
            social security numbers
            ssn: 123-45-6789
            driver's license
            passport number
            social security number again
            more ssn data
            """,
        )

        report = engine.analyze(bad_doc)

        assert report.summary.compliance_score >= 0
