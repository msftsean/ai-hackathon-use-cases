"""Flask middleware for error handling, logging, and CORS."""

import logging
import time
from functools import wraps
from typing import Callable
from uuid import uuid4

from flask import Flask, g, jsonify, request

logger = logging.getLogger(__name__)


def setup_middleware(app: Flask) -> None:
    """Configure all middleware for the Flask application."""
    setup_request_logging(app)
    setup_error_handlers(app)
    setup_cors(app)


def setup_request_logging(app: Flask) -> None:
    """Set up request logging middleware."""

    @app.before_request
    def before_request():
        """Log incoming request and set up timing."""
        g.request_id = str(uuid4())
        g.start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.path} "
            f"[request_id={g.request_id}]"
        )

    @app.after_request
    def after_request(response):
        """Log completed request with timing."""
        duration_ms = int((time.time() - g.start_time) * 1000)
        logger.info(
            f"Request completed: {request.method} {request.path} "
            f"status={response.status_code} duration={duration_ms}ms "
            f"[request_id={g.request_id}]"
        )
        # Add request ID to response headers
        response.headers["X-Request-ID"] = g.request_id
        return response


def setup_error_handlers(app: Flask) -> None:
    """Set up error handlers for common HTTP errors."""

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, 'description') else "Invalid request",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            "error": "Not Found",
            "message": str(error.description) if hasattr(error, 'description') else "Resource not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    @app.errorhandler(409)
    def conflict(error):
        """Handle 409 Conflict errors."""
        return jsonify({
            "error": "Conflict",
            "message": str(error.description) if hasattr(error, 'description') else "Resource conflict",
            "request_id": getattr(g, 'request_id', None),
        }), 409

    @app.errorhandler(413)
    def payload_too_large(error):
        """Handle 413 Payload Too Large errors."""
        return jsonify({
            "error": "Payload Too Large",
            "message": "File size exceeds maximum allowed (50MB)",
            "request_id": getattr(g, 'request_id', None),
        }), 413

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors."""
        return jsonify({
            "error": "Unprocessable Entity",
            "message": str(error.description) if hasattr(error, 'description') else "Invalid data",
            "request_id": getattr(g, 'request_id', None),
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server errors."""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": getattr(g, 'request_id', None),
        }), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        return jsonify({
            "error": "Service Unavailable",
            "message": "Service temporarily unavailable",
            "request_id": getattr(g, 'request_id', None),
        }), 503


def setup_cors(app: Flask) -> None:
    """Set up CORS headers for development."""
    try:
        from flask_cors import CORS
        CORS(app, resources={
            r"/api/*": {
                "origins": ["http://localhost:5001", "http://127.0.0.1:5001"],
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        })
        logger.info("CORS configured for API routes")
    except ImportError:
        logger.warning("flask-cors not installed, CORS not configured")


def require_json(f: Callable) -> Callable:
    """Decorator to require JSON content type for POST/PUT/PATCH requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ["POST", "PUT", "PATCH"]:
            if not request.is_json and not request.files:
                return jsonify({
                    "error": "Bad Request",
                    "message": "Content-Type must be application/json or multipart/form-data",
                    "request_id": getattr(g, 'request_id', None),
                }), 400
        return f(*args, **kwargs)
    return decorated_function


def validate_uuid(param_name: str) -> Callable:
    """Decorator to validate UUID path parameters."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from uuid import UUID
            uuid_value = kwargs.get(param_name)
            if uuid_value:
                try:
                    # Validate it's a proper UUID
                    UUID(str(uuid_value))
                except (ValueError, TypeError):
                    return jsonify({
                        "error": "Bad Request",
                        "message": f"Invalid UUID format for {param_name}",
                        "request_id": getattr(g, 'request_id', None),
                    }), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator
