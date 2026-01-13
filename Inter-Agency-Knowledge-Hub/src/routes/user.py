"""User API endpoints for Inter-Agency Knowledge Hub."""

import logging

from flask import Blueprint, jsonify, request, g

from ..db.database import get_database
from ..middleware.auth_middleware import require_auth
from ..middleware.error_handler import handle_errors

logger = logging.getLogger("knowledge_hub")

bp = Blueprint("user", __name__)


@bp.route("/api/v1/user/permissions", methods=["GET"])
@require_auth
@handle_errors
async def get_user_permissions():
    """Get current user's permissions."""
    perms = g.permissions

    return jsonify({
        "user_id": perms.user_id,
        "email": perms.email,
        "display_name": perms.display_name,
        "groups": perms.groups,
        "agencies": [a.value for a in perms.agencies],
        "agency_names": {a.value: a.full_name for a in perms.agencies},
        "max_classification": perms.max_classification.value,
        "is_admin": perms.is_admin,
        "is_reviewer": perms.is_reviewer,
        "cached_at": perms.cached_at.isoformat(),
    })


@bp.route("/api/v1/user/profile", methods=["GET"])
@require_auth
@handle_errors
async def get_user_profile():
    """Get current user's profile and activity summary."""
    perms = g.permissions

    # Get user activity stats
    from ..services.audit_service import AuditService
    audit_service = AuditService()
    stats = await audit_service.get_user_stats(perms.user_id)

    return jsonify({
        "user_id": perms.user_id,
        "email": perms.email,
        "display_name": perms.display_name,
        "agencies": [
            {"id": a.value, "name": a.full_name}
            for a in perms.agencies
        ],
        "roles": {
            "is_admin": perms.is_admin,
            "is_reviewer": perms.is_reviewer,
        },
        "activity": {
            "total_actions": stats.get("total_actions", 0),
            "searches": stats.get("searches", 0),
            "views": stats.get("views", 0),
            "exports": stats.get("exports", 0),
            "first_action": stats.get("first_action"),
            "last_action": stats.get("last_action"),
        },
    })


@bp.route("/api/v1/user/search-history", methods=["GET"])
@require_auth
@handle_errors
async def get_search_history():
    """Get current user's search history."""
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))

    db = await get_database()

    # Get total count
    count_result = await db.fetch_one(
        "SELECT COUNT(*) as count FROM search_history WHERE user_id = ?",
        (g.user_id,),
    )
    total = count_result["count"] if count_result else 0

    # Get search history
    rows = await db.fetch_all(
        """
        SELECT * FROM search_history
        WHERE user_id = ?
        ORDER BY searched_at DESC
        LIMIT ? OFFSET ?
        """,
        (g.user_id, limit, offset),
    )

    return jsonify({
        "history": [
            {
                "id": row["id"],
                "query": row["query"],
                "result_count": row["result_count"],
                "agencies_searched": row.get("agencies_searched", "").split(",") if row.get("agencies_searched") else [],
                "searched_at": row["searched_at"],
            }
            for row in rows
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    })


@bp.route("/api/v1/user/search-history/<query_id>", methods=["DELETE"])
@require_auth
@handle_errors
async def delete_search_history_item(query_id: str):
    """Delete a search history item."""
    db = await get_database()

    # Verify ownership
    existing = await db.fetch_one(
        "SELECT * FROM search_history WHERE id = ? AND user_id = ?",
        (query_id, g.user_id),
    )

    if not existing:
        return jsonify({"error": "Search history item not found"}), 404

    await db.execute(
        "DELETE FROM search_history WHERE id = ? AND user_id = ?",
        (query_id, g.user_id),
    )
    await db.commit()

    return "", 204


@bp.route("/api/v1/user/search-history", methods=["DELETE"])
@require_auth
@handle_errors
async def clear_search_history():
    """Clear all search history for current user."""
    db = await get_database()

    await db.execute(
        "DELETE FROM search_history WHERE user_id = ?",
        (g.user_id,),
    )
    await db.commit()

    return jsonify({"message": "Search history cleared"})
