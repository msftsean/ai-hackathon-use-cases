"""Flask application factory and entry point."""

import logging
import os
from pathlib import Path

from flask import Flask, send_from_directory

from src.api import api_bp
from src.api.middleware import setup_middleware
from src.config import get_settings


def create_app() -> Flask:
    """Create and configure the Flask application."""
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Create Flask app
    app = Flask(
        __name__,
        static_folder=None,  # We'll configure static files manually
    )
    app.secret_key = settings.flask_secret_key

    # Configure max content length (50MB)
    app.config["MAX_CONTENT_LENGTH"] = settings.max_file_size_mb * 1024 * 1024

    # Setup middleware
    setup_middleware(app)

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # Serve static files from static/ directory
    static_dir = Path(__file__).parent.parent / "static"

    @app.route("/")
    def index():
        """Serve the main dashboard page."""
        return send_from_directory(static_dir, "index.html")

    @app.route("/<path:filename>")
    def static_files(filename):
        """Serve static files."""
        return send_from_directory(static_dir, filename)

    logger.info(
        f"Document Eligibility Agent initialized "
        f"(mock_mode={settings.use_mock_services})"
    )

    return app


def main():
    """Run the Flask application."""
    settings = get_settings()
    app = create_app()
    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=settings.flask_debug,
    )


if __name__ == "__main__":
    main()
