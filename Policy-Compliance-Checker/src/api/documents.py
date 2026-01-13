"""Document API endpoints."""

from flask import Blueprint, jsonify, request

from ..config import logger
from ..core.document_parser import DocumentParser
from ..core.compliance_engine import ComplianceEngine
from ..services.document_service import DocumentService
from ..services.report_service import ReportService
from ..models.enums import AnalysisStatus


def create_documents_blueprint(
    parser: DocumentParser,
    engine: ComplianceEngine,
    document_service: DocumentService,
    report_service: ReportService
) -> Blueprint:
    """Create documents API blueprint."""
    bp = Blueprint("documents", __name__, url_prefix="/api/v1/documents")

    @bp.route("", methods=["POST"])
    def upload_document():
        """Upload a document for analysis."""
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "No filename"}), 400

        try:
            content = file.read()
            document = parser.parse_bytes(content, file.filename)
            stored = document_service.store(document)

            return jsonify({
                "id": stored.id,
                "filename": stored.filename,
                "format": stored.format.value,
                "word_count": stored.word_count,
                "page_count": stored.page_count,
                "uploaded_at": stored.uploaded_at.isoformat(),
            }), 201

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return jsonify({"error": "Failed to process document"}), 500

    @bp.route("", methods=["GET"])
    def list_documents():
        """List all uploaded documents."""
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)

        documents, total = document_service.list(limit, offset)

        return jsonify({
            "documents": [
                {
                    "id": d.id,
                    "filename": d.filename,
                    "format": d.format.value,
                    "word_count": d.word_count,
                    "status": d.analysis_status.value,
                    "uploaded_at": d.uploaded_at.isoformat(),
                }
                for d in documents
            ],
            "total": total,
        })

    @bp.route("/<document_id>", methods=["GET"])
    def get_document(document_id):
        """Get a specific document."""
        document = document_service.get(document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        return jsonify({
            "id": document.id,
            "filename": document.filename,
            "format": document.format.value,
            "title": document.title,
            "word_count": document.word_count,
            "page_count": document.page_count,
            "status": document.analysis_status.value,
            "sections": [
                {"title": s.title, "page_number": s.page_number}
                for s in document.sections
            ],
            "uploaded_at": document.uploaded_at.isoformat(),
        })

    @bp.route("/<document_id>", methods=["DELETE"])
    def delete_document(document_id):
        """Delete a document."""
        if document_service.delete(document_id):
            return "", 204
        return jsonify({"error": "Document not found"}), 404

    @bp.route("/<document_id>/analyze", methods=["POST"])
    def analyze_document(document_id):
        """Analyze a document for compliance."""
        document = document_service.get(document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        # Get optional rule IDs from request
        data = request.get_json(silent=True) or {}
        rule_ids = data.get("rule_ids")

        try:
            document_service.update_status(document_id, AnalysisStatus.PROCESSING)

            # Run analysis
            report = engine.analyze(document, rule_ids)

            # Store report
            report_service.store(report)

            document_service.update_status(document_id, AnalysisStatus.COMPLETED)

            return jsonify({
                "report_id": report.id,
                "document_id": report.document_id,
                "compliance_score": report.summary.compliance_score,
                "violations": {
                    "total": report.summary.violations.total,
                    "critical": report.summary.violations.critical,
                    "high": report.summary.violations.high,
                    "medium": report.summary.violations.medium,
                    "low": report.summary.violations.low,
                },
                "recommendations": report.recommendations[:5],
                "processing_time_ms": report.processing_time_ms,
            }), 201

        except Exception as e:
            document_service.update_status(document_id, AnalysisStatus.FAILED)
            logger.error(f"Analysis error: {e}")
            return jsonify({"error": "Analysis failed"}), 500

    return bp


__all__ = ["create_documents_blueprint"]
