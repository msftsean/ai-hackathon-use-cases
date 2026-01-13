"""
API middleware for Constituent Services Agent.

Provides error handling, logging, and request processing middleware.
"""

import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable
from uuid import uuid4

from flask import Flask, g, jsonify, request

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int = 400, error_type: str = "bad_request"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_type="not_found")


class ValidationError(APIError):
    """Request validation error."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400, error_type="validation_error")


class RateLimitError(APIError):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429, error_type="rate_limit_exceeded")


class InternalError(APIError):
    """Internal server error."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500, error_type="internal_error")


def error_response(error: str, message: str, request_id: str, status_code: int = 400) -> tuple:
    """
    Create standardized error response per api.yaml Error schema.

    Args:
        error: Error type identifier
        message: Human-readable error message
        request_id: Unique request identifier
        status_code: HTTP status code

    Returns:
        Tuple of (response_dict, status_code)
    """
    return (
        {
            "error": error,
            "message": message,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
        status_code,
    )


def setup_error_handlers(app: Flask):
    """
    Register error handlers for Flask app.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """Handle custom API errors."""
        request_id = getattr(g, "request_id", str(uuid4()))
        logger.warning(f"API error [{request_id}]: {error.error_type} - {error.message}")
        return jsonify(error_response(
            error.error_type,
            error.message,
            request_id,
            error.status_code,
        )[0]), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors."""
        request_id = getattr(g, "request_id", str(uuid4()))
        return jsonify(error_response(
            "bad_request",
            str(error.description) if hasattr(error, "description") else "Bad request",
            request_id,
            400,
        )[0]), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle not found errors."""
        request_id = getattr(g, "request_id", str(uuid4()))
        return jsonify(error_response(
            "not_found",
            "Resource not found",
            request_id,
            404,
        )[0]), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors."""
        request_id = getattr(g, "request_id", str(uuid4()))
        logger.error(f"Internal error [{request_id}]: {error}")
        return jsonify(error_response(
            "internal_error",
            "An unexpected error occurred",
            request_id,
            500,
        )[0]), 500


def setup_request_middleware(app: Flask):
    """
    Set up request processing middleware.

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request():
        """Process request before handling."""
        g.request_id = str(uuid4())
        g.start_time = time.time()

        # Log request
        logger.info(
            f"Request [{g.request_id}]: {request.method} {request.path}"
        )

    @app.after_request
    def after_request(response):
        """Process response after handling."""
        # Calculate duration
        duration_ms = int((time.time() - g.start_time) * 1000)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = g.request_id

        # Log response
        logger.info(
            f"Response [{g.request_id}]: {response.status_code} ({duration_ms}ms)"
        )

        return response


def async_route(f: Callable) -> Callable:
    """
    Decorator to handle async route functions in Flask.

    Flask doesn't natively support async, so we run async functions
    in an event loop.
    """
    import asyncio

    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()

    return wrapper
