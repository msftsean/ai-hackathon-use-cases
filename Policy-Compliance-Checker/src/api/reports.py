"""Reports API endpoints."""

from flask import Blueprint, jsonify, request, Response

from ..config import logger
from ..services.report_service import ReportService


def create_reports_blueprint(report_service: ReportService) -> Blueprint:
    """Create reports API blueprint."""
    bp = Blueprint("reports", __name__, url_prefix="/api/v1/reports")

    @bp.route("/<report_id>", methods=["GET"])
    def get_report(report_id):
        """Get a compliance report."""
        report = report_service.get(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404

        return jsonify({
            "id": report.id,
            "document_id": report.document_id,
            "document_name": report.document_name,
            "summary": {
                "compliance_score": report.summary.compliance_score,
                "total_rules_applied": report.summary.total_rules_applied,
                "violations": {
                    "total": report.summary.violations.total,
                    "critical": report.summary.violations.critical,
                    "high": report.summary.violations.high,
                    "medium": report.summary.violations.medium,
                    "low": report.summary.violations.low,
                },
                "analysis_time_ms": report.summary.analysis_time_ms,
            },
            "violations": [
                {
                    "id": v.id,
                    "rule_name": v.rule_name,
                    "severity": v.severity,
                    "category": v.category,
                    "matched_text": v.matched_text,
                    "location": v.location,
                    "recommendation": v.recommendation,
                }
                for v in report.violations
            ],
            "recommendations": report.recommendations,
            "ai_insights": report.ai_insights,
            "generated_at": report.generated_at.isoformat(),
        })

    @bp.route("/<report_id>/export", methods=["GET"])
    def export_report(report_id):
        """Export a compliance report."""
        report = report_service.get(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404

        export_format = request.args.get("format", "json").lower()

        if export_format == "html":
            html = report_service.export_html(report)
            return Response(
                html,
                mimetype="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename=report_{report_id}.html"
                }
            )
        else:
            json_str = report_service.export_json(report)
            return Response(
                json_str,
                mimetype="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=report_{report_id}.json"
                }
            )

    @bp.route("", methods=["GET"])
    def list_reports():
        """List all reports."""
        limit = request.args.get("limit", 100, type=int)
        reports = report_service.list(limit)

        return jsonify({
            "reports": [
                {
                    "id": r.id,
                    "document_id": r.document_id,
                    "document_name": r.document_name,
                    "compliance_score": r.summary.compliance_score,
                    "violation_count": r.summary.violations.total,
                    "generated_at": r.generated_at.isoformat(),
                }
                for r in reports
            ],
            "total": len(reports),
        })

    return bp


__all__ = ["create_reports_blueprint"]
