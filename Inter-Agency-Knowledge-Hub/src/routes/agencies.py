"""Agency API endpoints for Inter-Agency Knowledge Hub."""

import logging

from flask import Blueprint, jsonify, g

from ..models.agency import AgencySource
from ..models.enums import Agency
from ..core.permission_filter import PermissionFilter
from ..middleware.auth_middleware import require_auth
from ..middleware.error_handler import handle_errors

logger = logging.getLogger("knowledge_hub")

bp = Blueprint("agencies", __name__)

permission_filter = PermissionFilter()


@bp.route("/api/v1/agencies", methods=["GET"])
@require_auth
@handle_errors
async def list_agencies():
    """List all agencies the user has access to."""
    # Get accessible agencies for this user
    accessible = permission_filter.get_accessible_agencies(g.permissions)

    agencies = []
    for agency in Agency:
        source = AgencySource.from_agency(agency)
        agencies.append({
            "id": agency.value,
            "name": agency.full_name,
            "description": source.description,
            "accessible": agency in accessible,
            "base_url": source.base_url,
        })

    return jsonify({
        "agencies": agencies,
        "accessible_count": len(accessible),
        "total_count": len(Agency),
    })


@bp.route("/api/v1/agencies/<agency_id>", methods=["GET"])
@require_auth
@handle_errors
async def get_agency(agency_id: str):
    """Get details for a specific agency."""
    try:
        agency = Agency(agency_id)
    except ValueError:
        return jsonify({"error": "Invalid agency ID"}), 404

    # Check if user has access
    accessible = permission_filter.get_accessible_agencies(g.permissions)
    if agency not in accessible and not g.permissions.is_admin:
        return jsonify({"error": "Access denied to this agency"}), 403

    source = AgencySource.from_agency(agency)

    return jsonify({
        "id": agency.value,
        "name": agency.full_name,
        "description": source.description,
        "index_name": source.index_name,
        "document_count": source.document_count,
        "base_url": source.base_url,
        "last_sync": source.last_sync.isoformat() if source.last_sync else None,
        "enabled": source.enabled,
    })
