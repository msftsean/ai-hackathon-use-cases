"""Main Flask application entry point for Emergency Response Agent."""

import os
from pathlib import Path

from flask import Flask, send_from_directory

from .config import Settings, logger
from .api.routes import create_api_blueprint
from .orchestration.emergency_coordinator import EmergencyResponseCoordinator


def create_app(settings: Settings = None) -> Flask:
    """
    Create and configure Flask application.

    Args:
        settings: Optional Settings instance

    Returns:
        Configured Flask application
    """
    settings = settings or Settings()

    app = Flask(__name__, static_folder=None)
    app.config["JSON_SORT_KEYS"] = False

    # Initialize coordinator
    coordinator = EmergencyResponseCoordinator(settings)

    # Register API blueprint
    api_blueprint = create_api_blueprint(coordinator)
    app.register_blueprint(api_blueprint)

    # Static file serving for dashboard
    static_dir = Path(__file__).parent.parent / "static"

    @app.route("/")
    def index():
        """Serve the dashboard."""
        if static_dir.exists() and (static_dir / "index.html").exists():
            return send_from_directory(static_dir, "index.html")
        return """
        <html>
        <head><title>Emergency Response Agent</title></head>
        <body>
            <h1>Emergency Response Planning Agent</h1>
            <p>API is running. Use <a href="/api/v1/health">/api/v1/health</a> to check status.</p>
            <h2>API Endpoints:</h2>
            <ul>
                <li>POST /api/v1/scenarios - Create scenario</li>
                <li>GET /api/v1/scenarios - List scenarios</li>
                <li>POST /api/v1/scenarios/{id}/plan - Generate plan</li>
                <li>GET /api/v1/weather/current?lat=&lon= - Get weather</li>
                <li>GET /api/v1/evacuation/routes?zone= - Get evacuation routes</li>
                <li>GET /api/v1/historical/search?q= - Search incidents</li>
            </ul>
        </body>
        </html>
        """

    @app.route("/static/<path:filename>")
    def serve_static(filename):
        """Serve static files."""
        return send_from_directory(static_dir, filename)

    return app


def main():
    """Run the Flask application."""
    settings = Settings()
    app = create_app(settings)

    port = settings.flask_port
    logger.info(f"Starting Emergency Response Agent on port {port}")
    logger.info(f"Mock services: {'enabled' if settings.use_mock_services else 'disabled'}")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
