"""Report service for generating compliance reports."""

import json
from typing import Optional

from ..config import logger
from ..models.compliance_report import ComplianceReport


class ReportService:
    """Service for report storage and export."""

    def __init__(self):
        """Initialize report service."""
        self.reports: dict[str, ComplianceReport] = {}

    def store(self, report: ComplianceReport) -> ComplianceReport:
        """
        Store a compliance report.

        Args:
            report: ComplianceReport to store

        Returns:
            Stored report
        """
        self.reports[report.id] = report
        logger.info(f"Stored report: {report.id}")
        return report

    def get(self, report_id: str) -> Optional[ComplianceReport]:
        """Get a report by ID."""
        return self.reports.get(report_id)

    def get_by_document(self, document_id: str) -> Optional[ComplianceReport]:
        """Get the most recent report for a document."""
        doc_reports = [
            r for r in self.reports.values()
            if r.document_id == document_id
        ]
        if doc_reports:
            return max(doc_reports, key=lambda r: r.generated_at)
        return None

    def list(self, limit: int = 100) -> list[ComplianceReport]:
        """List all reports."""
        reports = list(self.reports.values())
        reports.sort(key=lambda r: r.generated_at, reverse=True)
        return reports[:limit]

    def export_json(self, report: ComplianceReport) -> str:
        """
        Export report as JSON.

        Args:
            report: ComplianceReport to export

        Returns:
            JSON string
        """
        return report.model_dump_json(indent=2)

    def export_html(self, report: ComplianceReport) -> str:
        """
        Export report as HTML.

        Args:
            report: ComplianceReport to export

        Returns:
            HTML string
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compliance Report - {report.document_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .score {{ font-size: 2em; font-weight: bold; }}
        .score.high {{ color: #27ae60; }}
        .score.medium {{ color: #f39c12; }}
        .score.low {{ color: #e74c3c; }}
        .violation {{ border-left: 4px solid #e74c3c; padding: 10px; margin: 10px 0; background: #fff; }}
        .violation.critical {{ border-color: #8e44ad; }}
        .violation.high {{ border-color: #e74c3c; }}
        .violation.medium {{ border-color: #f39c12; }}
        .violation.low {{ border-color: #3498db; }}
        .severity {{ display: inline-block; padding: 2px 8px; border-radius: 3px; color: white; font-size: 0.8em; }}
        .severity.critical {{ background: #8e44ad; }}
        .severity.high {{ background: #e74c3c; }}
        .severity.medium {{ background: #f39c12; }}
        .severity.low {{ background: #3498db; }}
        .recommendations {{ background: #e8f4f8; padding: 15px; border-radius: 5px; }}
        .recommendation {{ margin: 10px 0; padding-left: 20px; }}
        code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>Compliance Report</h1>
    <p><strong>Document:</strong> {report.document_name}</p>
    <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="summary">
        <h2>Summary</h2>
        <p class="score {'high' if report.summary.compliance_score >= 80 else 'medium' if report.summary.compliance_score >= 50 else 'low'}">
            Compliance Score: {report.summary.compliance_score:.1f}%
        </p>
        <p>Rules Applied: {report.summary.total_rules_applied}</p>
        <p>Violations Found: {report.summary.violations.total}</p>
        <ul>
            <li>Critical: {report.summary.violations.critical}</li>
            <li>High: {report.summary.violations.high}</li>
            <li>Medium: {report.summary.violations.medium}</li>
            <li>Low: {report.summary.violations.low}</li>
        </ul>
    </div>

    <h2>Violations</h2>
"""
        if report.violations:
            for v in report.violations:
                html += f"""
    <div class="violation {v.severity}">
        <p><span class="severity {v.severity}">{v.severity.upper()}</span> <strong>{v.rule_name}</strong></p>
        <p>Location: {v.location}</p>
        <p>Match: <code>{v.matched_text}</code></p>
        <p>Context: ...{v.context}...</p>
        <p><em>Recommendation: {v.recommendation}</em></p>
    </div>
"""
        else:
            html += "<p>No violations found.</p>"

        html += """
    <div class="recommendations">
        <h2>Recommendations</h2>
"""
        if report.recommendations:
            for rec in report.recommendations:
                html += f'        <div class="recommendation">{rec}</div>\n'
        else:
            html += "<p>No recommendations.</p>"

        html += """
    </div>

    <footer style="margin-top: 30px; color: #666; font-size: 0.9em;">
        <p>Generated by Policy Compliance Checker - NY State AI Hackathon</p>
    </footer>
</body>
</html>"""

        return html


__all__ = ["ReportService"]
