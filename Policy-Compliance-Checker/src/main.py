"""Main entry point for Policy Compliance Checker."""

import argparse
import sys
from pathlib import Path

from flask import Flask

from .config import Settings, logger
from .core.document_parser import DocumentParser
from .core.compliance_engine import ComplianceEngine
from .services.document_service import DocumentService
from .services.rule_service import RuleService
from .services.report_service import ReportService
from .api.documents import create_documents_blueprint
from .api.rules import create_rules_blueprint
from .api.reports import create_reports_blueprint
from .api.health import create_health_blueprint


def create_app(settings: Settings = None) -> Flask:
    """
    Create and configure Flask application.

    Args:
        settings: Optional Settings instance

    Returns:
        Configured Flask application
    """
    settings = settings or Settings()

    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["MAX_CONTENT_LENGTH"] = settings.max_file_size_bytes

    # Initialize services
    parser = DocumentParser(settings)
    engine = ComplianceEngine(settings)
    document_service = DocumentService()
    rule_service = RuleService(engine)
    report_service = ReportService()

    # Register blueprints
    app.register_blueprint(create_health_blueprint(settings))
    app.register_blueprint(create_documents_blueprint(
        parser, engine, document_service, report_service
    ))
    app.register_blueprint(create_rules_blueprint(rule_service))
    app.register_blueprint(create_reports_blueprint(report_service))

    @app.route("/")
    def index():
        """Root endpoint."""
        return """
        <html>
        <head><title>Policy Compliance Checker</title></head>
        <body>
            <h1>Policy Compliance Checker</h1>
            <p>API is running. Use <a href="/api/v1/health">/api/v1/health</a> to check status.</p>
            <h2>API Endpoints:</h2>
            <ul>
                <li>POST /api/v1/documents - Upload document</li>
                <li>GET /api/v1/documents - List documents</li>
                <li>POST /api/v1/documents/{id}/analyze - Analyze document</li>
                <li>GET /api/v1/reports/{id} - Get report</li>
                <li>GET /api/v1/rules - List rules</li>
                <li>POST /api/v1/rules - Create custom rule</li>
            </ul>
        </body>
        </html>
        """

    return app


def analyze_file(file_path: str, settings: Settings = None) -> None:
    """
    Analyze a single file from command line.

    Args:
        file_path: Path to document file
        settings: Optional Settings instance
    """
    settings = settings or Settings()

    parser = DocumentParser(settings)
    engine = ComplianceEngine(settings)

    print(f"\nPolicy Compliance Checker")
    print("=" * 50)

    # Parse document
    print(f"\nAnalyzing: {file_path}")
    try:
        document = parser.parse_file(file_path)
        print(f"  Format: {document.format.value}")
        print(f"  Words: {document.word_count:,}")
        print(f"  Sections: {len(document.sections)}")
    except Exception as e:
        print(f"Error parsing document: {e}")
        return

    # Run analysis
    print("\nRunning compliance check...")
    report = engine.analyze(document)

    # Display results
    print(f"\n{'=' * 50}")
    print("COMPLIANCE REPORT")
    print(f"{'=' * 50}")

    print(f"\nCompliance Score: {report.summary.compliance_score:.1f}%")

    score = report.summary.compliance_score
    if score >= 80:
        status = "GOOD"
    elif score >= 50:
        status = "NEEDS IMPROVEMENT"
    else:
        status = "POOR"
    print(f"Status: {status}")

    print(f"\nViolations Found: {report.summary.violations.total}")
    print(f"  Critical: {report.summary.violations.critical}")
    print(f"  High: {report.summary.violations.high}")
    print(f"  Medium: {report.summary.violations.medium}")
    print(f"  Low: {report.summary.violations.low}")

    if report.violations:
        print(f"\n{'=' * 50}")
        print("VIOLATION DETAILS")
        print(f"{'=' * 50}")

        for v in report.violations[:10]:  # Show first 10
            print(f"\n[{v.severity.upper()}] {v.rule_name}")
            print(f"  Location: {v.location}")
            print(f"  Match: \"{v.matched_text}\"")
            print(f"  Recommendation: {v.recommendation}")

        if len(report.violations) > 10:
            print(f"\n... and {len(report.violations) - 10} more violations")

    if report.recommendations:
        print(f"\n{'=' * 50}")
        print("RECOMMENDATIONS")
        print(f"{'=' * 50}")

        for rec in report.recommendations[:5]:
            print(f"\n  - {rec}")

    print(f"\n{'=' * 50}")
    print(f"Analysis completed in {report.processing_time_ms}ms")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Policy Compliance Checker")
    parser.add_argument(
        "file",
        nargs="?",
        help="Document file to analyze"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run as API server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="API server port (default: 5000)"
    )

    args = parser.parse_args()
    settings = Settings()

    if args.api:
        # Run API server
        app = create_app(settings)
        logger.info(f"Starting Policy Compliance Checker API on port {args.port}")
        app.run(host="0.0.0.0", port=args.port, debug=False)
    elif args.file:
        # Analyze single file
        analyze_file(args.file, settings)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python -m src.main document.pdf       # Analyze a document")
        print("  python -m src.main --api              # Run API server")


if __name__ == "__main__":
    main()
