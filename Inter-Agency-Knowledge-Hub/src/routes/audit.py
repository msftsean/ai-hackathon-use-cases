"""Audit API endpoints for Inter-Agency Knowledge Hub."""

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request, g, Response

from ..models.audit import AuditLogFilter, AuditExportRequest
from ..models.enums import ActionType, Agency
from ..services.audit_service import AuditService
from ..middleware.auth_middleware import require_admin
from ..middleware.error_handler import handle_errors

logger = logging.getLogger("knowledge_hub")

bp = Blueprint("audit", __name__)

audit_service = AuditService()


@bp.route("/api/v1/audit/logs", methods=["GET"])
@require_admin
@handle_errors
async def list_audit_logs():
    """List audit logs (admin only)."""
    # Parse query parameters
    filters = AuditLogFilter(
        user_id=request.args.get("user_id"),
        action=ActionType(request.args.get("action")) if request.args.get("action") else None,
        date_from=datetime.fromisoformat(request.args.get("date_from")) if request.args.get("date_from") else None,
        date_to=datetime.fromisoformat(request.args.get("date_to")) if request.args.get("date_to") else None,
        agency=Agency(request.args.get("agency")) if request.args.get("agency") else None,
        document_id=request.args.get("document_id"),
        limit=int(request.args.get("limit", 100)),
        offset=int(request.args.get("offset", 0)),
    )

    logs, total = await audit_service.get_logs(filters)

    return jsonify({
        "logs": [
            {
                "id": str(log.id),
                "user_id": log.user_id,
                "user_email": log.user_email,
                "action": log.action.value,
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
                "query": log.query,
                "document_id": log.document_id,
                "agencies": [a.value for a in log.agencies],
                "result_count": log.result_count,
            }
            for log in logs
        ],
        "total": total,
        "limit": filters.limit,
        "offset": filters.offset,
    })


@bp.route("/api/v1/audit/logs/export", methods=["POST"])
@require_admin
@handle_errors
async def export_audit_logs():
    """Export audit logs (admin only)."""
    data = request.get_json() or {}

    # Build export request
    filters = AuditLogFilter(
        user_id=data.get("user_id"),
        action=ActionType(data.get("action")) if data.get("action") else None,
        date_from=datetime.fromisoformat(data.get("date_from")) if data.get("date_from") else None,
        date_to=datetime.fromisoformat(data.get("date_to")) if data.get("date_to") else None,
        agency=Agency(data.get("agency")) if data.get("agency") else None,
        limit=int(data.get("limit", 10000)),
        offset=0,
    )

    export_request = AuditExportRequest(
        format=data.get("format", "json"),
        filters=filters,
        include_pii=data.get("include_pii", False),
    )

    # Generate export
    content = await audit_service.export_logs(export_request)

    # Set content type based on format
    if export_request.format == "csv":
        content_type = "text/csv"
        filename = f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        content_type = "application/json"
        filename = f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return Response(
        content,
        mimetype=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )


@bp.route("/api/v1/audit/stats", methods=["GET"])
@require_admin
@handle_errors
async def audit_stats():
    """Get audit statistics (admin only)."""
    # Get stats for a specific user or overall
    user_id = request.args.get("user_id")

    if user_id:
        stats = await audit_service.get_user_stats(user_id)
    else:
        # Get overall stats
        from ..db.database import get_database
        db = await get_database()

        result = await db.fetch_one("""
            SELECT
                COUNT(*) as total_actions,
                COUNT(DISTINCT user_id) as unique_users,
                SUM(CASE WHEN action = 'search' THEN 1 ELSE 0 END) as total_searches,
                SUM(CASE WHEN action = 'view' THEN 1 ELSE 0 END) as total_views,
                SUM(CASE WHEN action = 'export' THEN 1 ELSE 0 END) as total_exports
            FROM audit_logs
        """)

        stats = {
            "total_actions": result["total_actions"] if result else 0,
            "unique_users": result["unique_users"] if result else 0,
            "total_searches": result["total_searches"] if result else 0,
            "total_views": result["total_views"] if result else 0,
            "total_exports": result["total_exports"] if result else 0,
        }

    return jsonify(stats)
