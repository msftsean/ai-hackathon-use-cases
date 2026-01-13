#!/usr/bin/env python3
"""Interactive demonstration script for Policy Compliance Checker."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, ".")

from src.config import Settings, logger
from src.core.document_parser import DocumentParser
from src.core.compliance_engine import ComplianceEngine
from src.models.enums import Severity, RuleCategory
from src.models.compliance_rule import ComplianceRule


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f" {text}")
    print("=" * 60)


def print_section(text: str):
    """Print a section header."""
    print(f"\n{text}")
    print("-" * len(text))


def run_demo():
    """Run the interactive demonstration."""
    print_header("Policy Compliance Checker - Demo")
    print("NY State AI Hackathon")

    # Initialize components
    settings = Settings()
    settings.use_mock_services = True

    parser = DocumentParser(settings)
    engine = ComplianceEngine(settings)

    print("\n[OK] Components initialized")
    print(f"     Loaded {len(engine.rules)} built-in compliance rules")

    # Demo 1: List Rules
    print_section("Demo 1: Available Compliance Rules")

    categories = {}
    for rule in engine.list_rules():
        cat = rule.category.value
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(rule)

    for cat, rules in categories.items():
        print(f"\n  {cat.replace('_', ' ').title()} ({len(rules)} rules)")
        for rule in rules[:2]:
            print(f"    - [{rule.severity.value.upper()}] {rule.name}")
        if len(rules) > 2:
            print(f"    ... and {len(rules) - 2} more")

    # Demo 2: Analyze Sample Document
    print_section("Demo 2: Analyze Sample Document")

    # Create sample policy content
    sample_policy = """
# Employee Data Protection Policy

## Purpose
This policy establishes guidelines for protecting employee personal information
including social security numbers, driver's license information, and other PII.

## Data Handling
All employee data must be encrypted at rest and in transit using AES-256 encryption.
Access to employee records requires role-based access control (RBAC).

## Third Party Sharing
We may share data with third party vendors for payroll processing.
Written consent is required before sharing with partners.

## Password Requirements
Employees must use strong passwords with minimum 12 characters.
Passwords must be rotated every 90 days.

## Data Retention
Employee records are retained for 7 years after termination per legal requirements.

## Harassment Policy
The company maintains a zero-tolerance harassment policy.
All reports of hostile work environment will be investigated.

## Termination Procedure
The termination process includes HR review and exit interview.
"""

    # Parse the sample document
    from src.models.enums import DocumentFormat
    from src.models.policy_document import PolicyDocument, DocumentSection

    document = PolicyDocument(
        filename="employee_data_protection_policy.md",
        format=DocumentFormat.MARKDOWN,
        title="Employee Data Protection Policy",
        content=sample_policy,
        sections=[
            DocumentSection(
                title="Purpose",
                content="This policy establishes guidelines...",
                start_offset=0,
                end_offset=100
            ),
            DocumentSection(
                title="Data Handling",
                content="All employee data must be encrypted...",
                start_offset=100,
                end_offset=300
            ),
        ],
    )

    print(f"\nAnalyzing: {document.filename}")
    print(f"  Words: {document.word_count}")

    # Run analysis
    report = engine.analyze(document)

    print(f"\nCompliance Score: {report.summary.compliance_score:.1f}%")

    score_status = "GOOD" if report.summary.compliance_score >= 80 else "NEEDS WORK"
    print(f"Status: {score_status}")

    print(f"\nViolations Found: {report.summary.violations.total}")
    print(f"  Critical: {report.summary.violations.critical}")
    print(f"  High: {report.summary.violations.high}")
    print(f"  Medium: {report.summary.violations.medium}")
    print(f"  Low: {report.summary.violations.low}")

    # Show some violations
    if report.violations:
        print("\nSample Violations:")
        for v in report.violations[:3]:
            print(f"\n  [{v.severity.upper()}] {v.rule_name}")
            print(f"    Match: \"{v.matched_text[:40]}...\"")
            print(f"    Recommendation: {v.recommendation[:60]}...")

    # Demo 3: Custom Rule
    print_section("Demo 3: Create Custom Rule")

    custom_rule = ComplianceRule(
        name="Employee ID Validation",
        description="Check for employee ID references",
        pattern=r"employee\s*id|emp[_-]?id",
        severity=Severity.LOW,
        category=RuleCategory.CUSTOM,
        recommendation_template="Ensure employee IDs are properly protected.",
        is_builtin=False,
    )

    engine.add_rule(custom_rule)
    print(f"\n[OK] Created custom rule: {custom_rule.name}")
    print(f"     Pattern: {custom_rule.pattern}")
    print(f"     Severity: {custom_rule.severity.value}")

    # Re-analyze with custom rule
    new_report = engine.analyze(document)
    print(f"\n     Rules now: {len(engine.rules)} (including custom)")

    # Demo 4: Supported Formats
    print_section("Demo 4: Supported Document Formats")

    print("\nSupported file types:")
    for ext in parser.get_supported_formats():
        fmt = parser.SUPPORTED_EXTENSIONS[ext]
        print(f"  {ext:12} -> {fmt.value}")

    # Demo 5: Rule Categories
    print_section("Demo 5: Rule Categories Summary")

    print("\nCompliance coverage by category:")
    for cat in RuleCategory:
        rules = engine.list_rules(category=cat)
        print(f"  {cat.value.replace('_', ' ').title():25} {len(rules):3} rules")

    # Summary
    print_header("DEMO COMPLETE")
    print("\nThe Policy Compliance Checker can:")
    print("  1. Parse PDF, DOCX, Markdown, and text documents")
    print("  2. Apply built-in compliance rules across 5 categories")
    print("  3. Create custom rules with regex patterns")
    print("  4. Generate compliance scores (0-100)")
    print("  5. Provide actionable recommendations")
    print("  6. Export reports in JSON and HTML formats")

    print("\nTo analyze your own documents:")
    print("  python src/main.py your_policy.pdf")

    print("\nTo run the API server:")
    print("  python src/main.py --api")
    print("\nAPI will be available at http://localhost:5000/api/v1")


def main():
    """Entry point for demo."""
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
