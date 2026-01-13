"""Main entry point for Inter-Agency Knowledge Hub."""

import asyncio
import logging
from pathlib import Path

from flask import Flask
from flask_cors import CORS

from .config import get_settings
from .middleware.error_handler import setup_error_handlers
from .routes import health, search, documents, agencies, audit, reviews, user
from .db.database import get_database, close_database

logger = logging.getLogger("knowledge_hub")


def create_app() -> Flask:
    """Create and configure the Flask application."""
    settings = get_settings()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["JSON_SORT_KEYS"] = False

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Session-ID"],
        }
    })

    # Setup error handlers
    setup_error_handlers(app)

    # Register blueprints
    app.register_blueprint(health.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(agencies.bp)
    app.register_blueprint(audit.bp)
    app.register_blueprint(reviews.bp)
    app.register_blueprint(user.bp)

    # Initialize database on first request
    @app.before_request
    async def init_db():
        await get_database()

    # Cleanup on shutdown
    @app.teardown_appcontext
    async def cleanup(exception=None):
        await close_database()

    logger.info(f"Inter-Agency Knowledge Hub initialized (mock_services={settings.use_mock_services})")

    return app


def main():
    """Run the application."""
    settings = get_settings()

    # Ensure data directory exists
    data_dir = Path(settings.database_path).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    app = create_app()

    print("\n" + "=" * 60)
    print("  Inter-Agency Knowledge Hub")
    print("  Cross-Agency Document Search System")
    print("=" * 60)
    print(f"\n  Server: http://{settings.flask_host}:{settings.flask_port}")
    print(f"  API Docs: http://{settings.flask_host}:{settings.flask_port}/api/v1/health")
    print(f"  Mock Services: {settings.use_mock_services}")
    print("\n  Available Agencies:")
    from .models.enums import Agency
    for agency in Agency:
        print(f"    - {agency.value}: {agency.full_name}")
    print("\n  Mock Authentication Tokens:")
    print("    - admin-token: Full admin access")
    print("    - dmv-manager-token: DMV manager access")
    print("    - dmv-staff-token: DMV staff access")
    print("    - dol-staff-token: DOL staff access")
    print("    - multi-agency-token: Multi-agency analyst")
    print("    - public-token: Public user (limited)")
    print("\n" + "=" * 60 + "\n")

    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=settings.debug,
    )


if __name__ == "__main__":
    main()
