"""Compliance engine for rule-based policy checking."""

import re
import time
from typing import Optional

from ..config import logger, Settings
from ..models.enums import Severity, RuleCategory
from ..models.policy_document import PolicyDocument
from ..models.compliance_rule import ComplianceRule
from ..models.compliance_violation import ComplianceViolation, ViolationSummary
from ..models.compliance_report import ComplianceReport, ReportSummary


class ComplianceEngine:
    """Engine for evaluating documents against compliance rules."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize compliance engine."""
        self.settings = settings or Settings()
        self.rules: dict[str, ComplianceRule] = {}
        self._load_builtin_rules()

    def _load_builtin_rules(self):
        """Load built-in compliance rules."""
        builtin_rules = [
            # Data Protection Rules
            ComplianceRule(
                id="dp_001",
                name="PII Without Protection",
                description="Check for personal identifiable information without protection measures",
                pattern=r"\b(social\s*security|ssn|driver'?s?\s*license|passport\s*number)\b",
                severity=Severity.CRITICAL,
                category=RuleCategory.DATA_PROTECTION,
                recommendation_template="Ensure PII is encrypted and access is restricted. Consider data masking.",
                keywords=["pii", "personal data", "sensitive"],
            ),
            ComplianceRule(
                id="dp_002",
                name="Data Retention Period Missing",
                description="Check if data retention period is specified",
                pattern=r"(?i)data\s*retention|retain(ed|ing)?\s*data|keep\s*data",
                severity=Severity.HIGH,
                category=RuleCategory.DATA_PROTECTION,
                recommendation_template="Specify a clear data retention period and disposal procedures.",
                keywords=["retention", "disposal"],
            ),
            ComplianceRule(
                id="dp_003",
                name="Third Party Data Sharing",
                description="Check for third party data sharing without consent mention",
                pattern=r"(?i)share\s*(data|information)\s*with\s*(third\s*part|vendor|partner)",
                severity=Severity.HIGH,
                category=RuleCategory.DATA_PROTECTION,
                recommendation_template="Ensure consent is obtained before sharing data with third parties.",
                keywords=["third party", "sharing"],
            ),

            # HR Policy Rules
            ComplianceRule(
                id="hr_001",
                name="Discrimination Language",
                description="Check for potentially discriminatory language",
                pattern=r"(?i)\b(regardless\s*of|without\s*regard\s*to)\b.*\b(race|gender|age|religion|disability)\b",
                severity=Severity.LOW,
                category=RuleCategory.HR_POLICY,
                recommendation_template="Good practice found. Ensure comprehensive non-discrimination policy.",
                keywords=["discrimination", "equal opportunity"],
            ),
            ComplianceRule(
                id="hr_002",
                name="Harassment Policy",
                description="Check for harassment policy mentions",
                pattern=r"(?i)\b(harassment|hostile\s*work\s*environment|bullying)\b",
                severity=Severity.MEDIUM,
                category=RuleCategory.HR_POLICY,
                recommendation_template="Ensure harassment policy includes reporting procedures and consequences.",
                keywords=["harassment", "workplace"],
            ),
            ComplianceRule(
                id="hr_003",
                name="Termination Procedure",
                description="Check for termination procedure documentation",
                pattern=r"(?i)\b(termination|dismissal|firing|separation)\s*(procedure|process|policy)\b",
                severity=Severity.MEDIUM,
                category=RuleCategory.HR_POLICY,
                recommendation_template="Document clear termination procedures including notice periods.",
                keywords=["termination", "employment"],
            ),

            # IT Security Rules
            ComplianceRule(
                id="it_001",
                name="Password Policy",
                description="Check for password policy requirements",
                pattern=r"(?i)password\s*(policy|requirement|must|should|length)",
                severity=Severity.HIGH,
                category=RuleCategory.IT_SECURITY,
                recommendation_template="Define minimum password length (12+ chars), complexity, and rotation requirements.",
                keywords=["password", "authentication"],
            ),
            ComplianceRule(
                id="it_002",
                name="Encryption Requirements",
                description="Check for encryption mentions",
                pattern=r"(?i)\b(encrypt(ed|ion)?|aes|rsa|tls|ssl)\b",
                severity=Severity.HIGH,
                category=RuleCategory.IT_SECURITY,
                recommendation_template="Specify encryption standards (AES-256, TLS 1.3) for data at rest and in transit.",
                keywords=["encryption", "security"],
            ),
            ComplianceRule(
                id="it_003",
                name="Access Control",
                description="Check for access control policies",
                pattern=r"(?i)\b(access\s*control|role\s*based|rbac|least\s*privilege)\b",
                severity=Severity.HIGH,
                category=RuleCategory.IT_SECURITY,
                recommendation_template="Implement role-based access control with regular access reviews.",
                keywords=["access", "authorization"],
            ),

            # Legal Compliance Rules
            ComplianceRule(
                id="lc_001",
                name="GDPR Reference",
                description="Check for GDPR compliance mentions",
                pattern=r"(?i)\b(gdpr|general\s*data\s*protection\s*regulation)\b",
                severity=Severity.MEDIUM,
                category=RuleCategory.LEGAL_COMPLIANCE,
                recommendation_template="Ensure GDPR compliance includes data subject rights and lawful bases.",
                keywords=["gdpr", "privacy"],
            ),
            ComplianceRule(
                id="lc_002",
                name="HIPAA Reference",
                description="Check for HIPAA compliance mentions",
                pattern=r"(?i)\b(hipaa|health\s*insurance\s*portability)\b",
                severity=Severity.MEDIUM,
                category=RuleCategory.LEGAL_COMPLIANCE,
                recommendation_template="Ensure HIPAA compliance covers PHI protection and breach notification.",
                keywords=["hipaa", "healthcare"],
            ),

            # Accessibility Rules
            ComplianceRule(
                id="ac_001",
                name="Accessibility Statement",
                description="Check for accessibility policy statements",
                pattern=r"(?i)\b(accessibility|wcag|ada\s*compliance|screen\s*reader)\b",
                severity=Severity.MEDIUM,
                category=RuleCategory.ACCESSIBILITY,
                recommendation_template="Include WCAG 2.1 AA compliance requirements and accommodations process.",
                keywords=["accessibility", "ada"],
            ),
        ]

        for rule in builtin_rules:
            self.rules[rule.id] = rule

        logger.info(f"Loaded {len(self.rules)} built-in compliance rules")

    def add_rule(self, rule: ComplianceRule) -> bool:
        """
        Add a custom rule to the engine.

        Args:
            rule: ComplianceRule to add

        Returns:
            True if added successfully
        """
        # Validate regex pattern
        try:
            re.compile(rule.pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        rule.is_builtin = False
        self.rules[rule.id] = rule
        logger.info(f"Added custom rule: {rule.name}")
        return True

    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a custom rule from the engine.

        Args:
            rule_id: ID of rule to remove

        Returns:
            True if removed

        Raises:
            ValueError: If trying to remove a built-in rule
        """
        rule = self.rules.get(rule_id)
        if not rule:
            return False

        if rule.is_builtin:
            raise ValueError("Cannot remove built-in rules")

        del self.rules[rule_id]
        logger.info(f"Removed rule: {rule_id}")
        return True

    def get_rule(self, rule_id: str) -> Optional[ComplianceRule]:
        """Get a rule by ID."""
        return self.rules.get(rule_id)

    def list_rules(
        self,
        category: Optional[RuleCategory] = None,
        enabled_only: bool = True
    ) -> list[ComplianceRule]:
        """
        List rules with optional filtering.

        Args:
            category: Filter by category
            enabled_only: Only return enabled rules

        Returns:
            List of ComplianceRule objects
        """
        rules = list(self.rules.values())

        if category:
            rules = [r for r in rules if r.category == category]

        if enabled_only:
            rules = [r for r in rules if r.enabled]

        return rules

    def analyze(
        self,
        document: PolicyDocument,
        rule_ids: Optional[list[str]] = None
    ) -> ComplianceReport:
        """
        Analyze a document against compliance rules.

        Args:
            document: PolicyDocument to analyze
            rule_ids: Specific rule IDs to apply (all enabled rules if None)

        Returns:
            ComplianceReport with violations and score
        """
        start_time = time.time()

        # Get rules to apply
        if rule_ids:
            rules = [self.rules[rid] for rid in rule_ids if rid in self.rules]
        else:
            rules = self.list_rules(enabled_only=True)

        violations = []

        # Check each rule
        for rule in rules:
            rule_violations = self._evaluate_rule(document, rule)
            violations.extend(rule_violations)

        # Calculate compliance score
        score = self._calculate_score(violations)

        # Build summary
        violation_summary = ViolationSummary(
            critical=len([v for v in violations if v.severity == Severity.CRITICAL.value]),
            high=len([v for v in violations if v.severity == Severity.HIGH.value]),
            medium=len([v for v in violations if v.severity == Severity.MEDIUM.value]),
            low=len([v for v in violations if v.severity == Severity.LOW.value]),
            total=len(violations),
        )

        processing_time = int((time.time() - start_time) * 1000)

        summary = ReportSummary(
            document_id=document.id,
            document_name=document.filename,
            total_rules_applied=len(rules),
            violations=violation_summary,
            compliance_score=score,
            analysis_time_ms=processing_time,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(violations)

        report = ComplianceReport(
            document_id=document.id,
            document_name=document.filename,
            summary=summary,
            violations=violations,
            recommendations=recommendations,
            processing_time_ms=processing_time,
        )

        logger.info(
            f"Analyzed {document.filename}: score={score:.1f}, "
            f"violations={len(violations)}, time={processing_time}ms"
        )

        return report

    def _evaluate_rule(
        self,
        document: PolicyDocument,
        rule: ComplianceRule
    ) -> list[ComplianceViolation]:
        """Evaluate a single rule against the document."""
        violations = []

        try:
            pattern = re.compile(rule.pattern, re.IGNORECASE | re.MULTILINE)
            matches = pattern.finditer(document.content)

            for match in matches:
                # Get context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(document.content), match.end() + 50)
                context = document.content[start:end]

                # Determine location
                location = self._find_location(document, match.start())

                violations.append(ComplianceViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity.value,
                    category=rule.category.value,
                    matched_text=match.group(),
                    context=context,
                    location=location,
                    start_offset=match.start(),
                    end_offset=match.end(),
                    recommendation=rule.recommendation_template,
                ))

        except re.error as e:
            logger.error(f"Regex error in rule {rule.id}: {e}")

        return violations

    def _find_location(self, document: PolicyDocument, offset: int) -> str:
        """Find the section/location for a given offset."""
        for section in document.sections:
            if section.start_offset <= offset <= section.end_offset:
                if section.page_number:
                    return f"Page {section.page_number}: {section.title}"
                return section.title

        return "Document"

    def _calculate_score(self, violations: list[ComplianceViolation]) -> float:
        """
        Calculate compliance score based on violations.

        Score = 100 - weighted penalties
        Weights: CRITICAL=25, HIGH=15, MEDIUM=5, LOW=1
        Minimum score is 0
        """
        if not violations:
            return 100.0

        penalty = 0
        for violation in violations:
            severity = Severity(violation.severity)
            penalty += severity.weight

        score = max(0, 100 - penalty)
        return round(score, 1)

    def _generate_recommendations(
        self,
        violations: list[ComplianceViolation]
    ) -> list[str]:
        """Generate unique recommendations from violations."""
        recommendations = []
        seen = set()

        # Sort by severity
        severity_order = {
            Severity.CRITICAL.value: 0,
            Severity.HIGH.value: 1,
            Severity.MEDIUM.value: 2,
            Severity.LOW.value: 3,
        }

        sorted_violations = sorted(
            violations,
            key=lambda v: severity_order.get(v.severity, 4)
        )

        for violation in sorted_violations:
            if violation.recommendation not in seen:
                recommendations.append(
                    f"[{violation.severity.upper()}] {violation.recommendation}"
                )
                seen.add(violation.recommendation)

        return recommendations


__all__ = ["ComplianceEngine"]
