"""Document API endpoints for Inter-Agency Knowledge Hub."""

import logging

from flask import Blueprint, jsonify, request, g

from ..models.cross_reference import CrossReferenceRequest
from ..models.enums import Agency, RelationshipType
from ..services.search_service import SearchService
from ..services.cross_reference_service import CrossReferenceService
from ..middleware.auth_middleware import require_auth
from ..middleware.error_handler import handle_errors

logger = logging.getLogger("knowledge_hub")

bp = Blueprint("documents", __name__)

# Service instances
search_service = SearchService()
cross_ref_service = CrossReferenceService()


@bp.route("/api/v1/documents/<document_id>", methods=["GET"])
@require_auth
@handle_errors
async def get_document(document_id: str):
    """Get a specific document with permission checking."""
    doc = await search_service.get_document(
        document_id=document_id,
        permissions=g.permissions,
        ip_address=g.ip_address,
        session_id=g.session_id,
    )

    if not doc:
        return jsonify({"error": "Document not found or access denied"}), 404

    return jsonify({
        "id": doc.get("id"),
        "title": doc.get("title"),
        "content": doc.get("content"),
        "summary": doc.get("summary"),
        "agency": doc.get("agency"),
        "classification": doc.get("classification"),
        "keywords": doc.get("keywords", []),
        "publication_date": doc.get("publication_date"),
        "version": doc.get("version"),
        "document_type": doc.get("document_type"),
        "source_url": doc.get("source_url"),
    })


@bp.route("/api/v1/documents/<document_id>/cross-references", methods=["GET"])
@require_auth
@handle_errors
async def get_cross_references(document_id: str):
    """Get cross-references for a document."""
    # Parse query parameters
    relationship_types = None
    if request.args.get("relationship_types"):
        try:
            relationship_types = [
                RelationshipType(rt)
                for rt in request.args.get("relationship_types").split(",")
            ]
        except ValueError as e:
            return jsonify({"error": f"Invalid relationship type: {e}"}), 400

    agencies = None
    if request.args.get("agencies"):
        try:
            agencies = [Agency(a) for a in request.args.get("agencies").split(",")]
        except ValueError as e:
            return jsonify({"error": f"Invalid agency: {e}"}), 400

    cross_ref_request = CrossReferenceRequest(
        document_id=document_id,
        relationship_types=relationship_types,
        min_confidence=float(request.args.get("min_confidence", 0.7)),
        max_results=int(request.args.get("max_results", 10)),
        include_same_agency=request.args.get("include_same_agency", "true").lower() == "true",
        agencies=agencies,
    )

    response = await cross_ref_service.find_related(
        request=cross_ref_request,
        permissions=g.permissions,
        ip_address=g.ip_address,
        session_id=g.session_id,
    )

    return jsonify({
        "document_id": response.document_id,
        "document_title": response.document_title,
        "source_agency": response.source_agency.value,
        "cross_references": [
            {
                "id": str(ref.id),
                "related_document_id": ref.related_document_id,
                "related_agency": ref.related_agency.value,
                "related_agency_name": ref.related_agency.full_name,
                "relationship_type": ref.relationship_type.value,
                "confidence_score": ref.confidence_score,
                "explanation": ref.explanation,
                "related_title": ref.related_title,
                "related_snippet": ref.related_snippet,
                "is_cross_agency": ref.is_cross_agency,
                "citation": {
                    "formatted": ref.related_citation.citation_format,
                    "url": ref.related_citation.direct_url,
                } if ref.related_citation else None,
            }
            for ref in response.cross_references
        ],
        "total_found": response.total_found,
        "cross_agency_count": response.cross_agency_count,
        "processing_time_ms": response.processing_time_ms,
    })


@bp.route("/api/v1/documents/cross-references/summary", methods=["GET"])
@require_auth
@handle_errors
async def get_cross_reference_summary():
    """Get summary of cross-agency document relationships."""
    summary = await cross_ref_service.get_cross_agency_summary(g.permissions)
    return jsonify(summary)
