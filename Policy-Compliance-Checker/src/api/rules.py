"""Rules API endpoints."""

from flask import Blueprint, jsonify, request

from ..config import logger
from ..services.rule_service import RuleService
from ..models.compliance_rule import RuleCreateRequest, RuleUpdateRequest
from ..models.enums import RuleCategory, Severity


def create_rules_blueprint(rule_service: RuleService) -> Blueprint:
    """Create rules API blueprint."""
    bp = Blueprint("rules", __name__, url_prefix="/api/v1/rules")

    @bp.route("", methods=["GET"])
    def list_rules():
        """List all compliance rules."""
        category = request.args.get("category")
        include_disabled = request.args.get("include_disabled", "false").lower() == "true"

        cat = RuleCategory(category) if category else None
        rules = rule_service.list(category=cat, include_disabled=include_disabled)

        return jsonify({
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "severity": r.severity.value,
                    "category": r.category.value,
                    "is_builtin": r.is_builtin,
                    "enabled": r.enabled,
                }
                for r in rules
            ],
            "total": len(rules),
        })

    @bp.route("/<rule_id>", methods=["GET"])
    def get_rule(rule_id):
        """Get a specific rule."""
        rule = rule_service.get(rule_id)
        if not rule:
            return jsonify({"error": "Rule not found"}), 404

        return jsonify({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "pattern": rule.pattern,
            "severity": rule.severity.value,
            "category": rule.category.value,
            "recommendation_template": rule.recommendation_template,
            "keywords": rule.keywords,
            "is_builtin": rule.is_builtin,
            "enabled": rule.enabled,
            "created_at": rule.created_at.isoformat(),
        })

    @bp.route("", methods=["POST"])
    def create_rule():
        """Create a custom compliance rule."""
        data = request.get_json()

        try:
            rule_request = RuleCreateRequest(
                name=data.get("name"),
                description=data.get("description"),
                pattern=data.get("pattern"),
                severity=Severity(data.get("severity")),
                category=RuleCategory(data.get("category", "custom")),
                recommendation_template=data.get("recommendation_template"),
                keywords=data.get("keywords", []),
            )

            rule = rule_service.create(rule_request)

            return jsonify({
                "id": rule.id,
                "name": rule.name,
                "message": "Custom rule created successfully",
            }), 201

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Rule creation error: {e}")
            return jsonify({"error": "Failed to create rule"}), 500

    @bp.route("/<rule_id>", methods=["PUT"])
    def update_rule(rule_id):
        """Update a compliance rule."""
        data = request.get_json()

        try:
            update_request = RuleUpdateRequest(
                name=data.get("name"),
                description=data.get("description"),
                pattern=data.get("pattern"),
                severity=Severity(data["severity"]) if "severity" in data else None,
                recommendation_template=data.get("recommendation_template"),
                keywords=data.get("keywords"),
                enabled=data.get("enabled"),
            )

            rule = rule_service.update(rule_id, update_request)
            if not rule:
                return jsonify({"error": "Rule not found"}), 404

            return jsonify({
                "id": rule.id,
                "name": rule.name,
                "message": "Rule updated successfully",
            })

        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @bp.route("/<rule_id>", methods=["DELETE"])
    def delete_rule(rule_id):
        """Delete a custom rule."""
        try:
            if rule_service.delete(rule_id):
                return "", 204
            return jsonify({"error": "Rule not found"}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @bp.route("/categories", methods=["GET"])
    def list_categories():
        """List rule categories with counts."""
        categories = rule_service.get_categories()
        return jsonify({"categories": categories})

    return bp


__all__ = ["create_rules_blueprint"]
