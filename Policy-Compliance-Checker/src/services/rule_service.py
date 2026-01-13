"""Rule service for managing compliance rules."""

import re
from typing import Optional

from ..config import logger
from ..models.enums import RuleCategory
from ..models.compliance_rule import (
    ComplianceRule,
    RuleCreateRequest,
    RuleUpdateRequest,
)
from ..core.compliance_engine import ComplianceEngine


class RuleService:
    """Service for managing compliance rules."""

    def __init__(self, engine: ComplianceEngine):
        """Initialize rule service."""
        self.engine = engine

    def create(self, request: RuleCreateRequest) -> ComplianceRule:
        """
        Create a custom compliance rule.

        Args:
            request: Rule creation request

        Returns:
            Created ComplianceRule

        Raises:
            ValueError: If pattern is invalid
        """
        # Validate regex pattern
        self._validate_pattern(request.pattern)

        rule = ComplianceRule(
            name=request.name,
            description=request.description,
            pattern=request.pattern,
            severity=request.severity,
            category=request.category,
            recommendation_template=request.recommendation_template,
            keywords=request.keywords,
            is_builtin=False,
        )

        self.engine.add_rule(rule)
        logger.info(f"Created custom rule: {rule.id}")

        return rule

    def get(self, rule_id: str) -> Optional[ComplianceRule]:
        """Get a rule by ID."""
        return self.engine.get_rule(rule_id)

    def list(
        self,
        category: Optional[RuleCategory] = None,
        include_disabled: bool = False
    ) -> list[ComplianceRule]:
        """
        List rules with optional filtering.

        Args:
            category: Filter by category
            include_disabled: Include disabled rules

        Returns:
            List of ComplianceRule objects
        """
        return self.engine.list_rules(
            category=category,
            enabled_only=not include_disabled
        )

    def update(
        self,
        rule_id: str,
        request: RuleUpdateRequest
    ) -> Optional[ComplianceRule]:
        """
        Update a rule.

        Args:
            rule_id: Rule ID to update
            request: Update request

        Returns:
            Updated rule if found

        Raises:
            ValueError: If trying to update builtin rule or invalid pattern
        """
        rule = self.engine.get_rule(rule_id)
        if not rule:
            return None

        if rule.is_builtin and request.pattern:
            raise ValueError("Cannot modify pattern of built-in rules")

        # Validate new pattern if provided
        if request.pattern:
            self._validate_pattern(request.pattern)
            rule.pattern = request.pattern

        if request.name:
            rule.name = request.name
        if request.description:
            rule.description = request.description
        if request.severity:
            rule.severity = request.severity
        if request.recommendation_template:
            rule.recommendation_template = request.recommendation_template
        if request.keywords is not None:
            rule.keywords = request.keywords
        if request.enabled is not None:
            rule.enabled = request.enabled

        logger.info(f"Updated rule: {rule_id}")
        return rule

    def delete(self, rule_id: str) -> bool:
        """
        Delete a custom rule.

        Args:
            rule_id: Rule ID to delete

        Returns:
            True if deleted

        Raises:
            ValueError: If trying to delete builtin rule
        """
        return self.engine.remove_rule(rule_id)

    def _validate_pattern(self, pattern: str) -> None:
        """Validate regex pattern."""
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

    def get_categories(self) -> list[dict]:
        """Get all rule categories with counts."""
        categories = []
        for cat in RuleCategory:
            rules = self.list(category=cat)
            categories.append({
                "name": cat.value,
                "display_name": cat.value.replace("_", " ").title(),
                "rule_count": len(rules),
            })
        return categories


__all__ = ["RuleService"]
