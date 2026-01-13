"""Health check endpoint for Inter-Agency Knowledge Hub."""

from datetime import datetime

from flask import Blueprint, jsonify

from ..config import get_settings

bp = Blueprint("health", __name__)


@bp.route("/api/v1/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    settings = get_settings()

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "service": "inter-agency-knowledge-hub",
        "environment": {
            "mock_services": settings.use_mock_services,
            "debug": settings.debug,
        },
    })


@bp.route("/api/v1/health/ready", methods=["GET"])
def readiness_check():
    """Readiness probe for Kubernetes."""
    # In production, check database and search service connectivity
    return jsonify({
        "ready": True,
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": "ok",
            "search_service": "ok",
            "auth_service": "ok",
        },
    })


@bp.route("/api/v1/health/live", methods=["GET"])
def liveness_check():
    """Liveness probe for Kubernetes."""
    return jsonify({
        "alive": True,
        "timestamp": datetime.now().isoformat(),
    })
