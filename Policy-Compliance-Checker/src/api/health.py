"""Health check API endpoint."""

from flask import Blueprint, jsonify

from ..config import Settings


def create_health_blueprint(settings: Settings) -> Blueprint:
    """Create health API blueprint."""
    bp = Blueprint("health", __name__, url_prefix="/api/v1")

    @bp.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "Policy Compliance Checker",
            "version": "0.1.0",
            "azure_openai_available": settings.has_azure_openai,
            "mock_mode": settings.use_mock_services,
        })

    return bp


__all__ = ["create_health_blueprint"]
