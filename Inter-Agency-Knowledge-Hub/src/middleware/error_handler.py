"""Error handling middleware for Inter-Agency Knowledge Hub."""

import logging
import traceback
from functools import wraps
from typing import Callable

from flask import Flask, jsonify, request

logger = logging.getLogger("knowledge_hub")


def setup_error_handlers(app: Flask) -> None:
    """Configure error handlers for the Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, 'description') else "Invalid request",
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication required",
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "error": "Forbidden",
            "message": "Access denied",
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": "Resource not found",
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "error": "Unprocessable Entity",
            "message": str(error.description) if hasattr(error, 'description') else "Validation error",
        }), 422

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please try again later.",
        }), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error: {error}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        }), 500


def handle_errors(f: Callable) -> Callable:
    """Decorator for consistent error handling in routes."""
    @wraps(f)
    async def decorated(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({
                "error": "Validation Error",
                "message": str(e),
            }), 400
        except PermissionError as e:
            logger.warning(f"Permission error: {e}")
            return jsonify({
                "error": "Access Denied",
                "message": str(e),
            }), 403
        except FileNotFoundError as e:
            logger.warning(f"Not found: {e}")
            return jsonify({
                "error": "Not Found",
                "message": str(e),
            }), 404
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            }), 500

    return decorated


class APIError(Exception):
    """Custom API error with status code."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
