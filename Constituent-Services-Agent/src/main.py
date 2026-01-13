"""
Main entry point for Constituent Services Agent.

Flask application factory with CORS and middleware setup.
"""

import logging
import os
import sys

from flask import Flask
from flask_cors import CORS

from src.config.settings import get_settings


def create_app() -> Flask:
    """
    Create and configure Flask application.

    Returns:
        Configured Flask application instance
    """
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Create Flask app
    app = Flask(
        __name__,
        static_folder="../static",
        static_url_path="/",
    )

    # Configure app
    app.config["DEBUG"] = settings.debug

    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # Register middleware
    from src.api.middleware import setup_error_handlers, setup_request_middleware
    setup_error_handlers(app)
    setup_request_middleware(app)

    # Register API routes
    from src.api.routes import api
    app.register_blueprint(api)

    # Root route serves static index.html
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    # Log startup info
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Mock mode: {settings.use_mock_services}")
    logger.info(f"Debug mode: {settings.debug}")

    return app


def main():
    """Run the application."""
    settings = get_settings()
    app = create_app()

    print(f"\n{'='*60}")
    print(f"  {settings.app_name} v{settings.app_version}")
    print(f"{'='*60}")
    print(f"  Mode: {'MOCK (offline)' if settings.use_mock_services else 'AZURE (live)'}")
    print(f"  Server: http://{settings.host}:{settings.port}")
    print(f"  API Docs: http://{settings.host}:{settings.port}/api/v1/health")
    print(f"{'='*60}\n")

    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
    )


if __name__ == "__main__":
    main()
