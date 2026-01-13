"""Search API endpoints for Inter-Agency Knowledge Hub."""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from flask import Blueprint, jsonify, request, g

from ..models.search import SearchQuery
from ..models.enums import Agency
from ..services.search_service import SearchService
from ..services.review_service import ReviewService
from ..middleware.auth_middleware import require_auth
from ..middleware.error_handler import handle_errors

logger = logging.getLogger("knowledge_hub")

bp = Blueprint("search", __name__)

# Service instances
search_service = SearchService()
review_service = ReviewService()


@bp.route("/api/v1/search", methods=["POST"])
@require_auth
@handle_errors
async def search():
    """Execute a search across agency knowledge bases."""
    data = request.get_json()

    if not data or not data.get("query"):
        return jsonify({"error": "Query is required"}), 400

    # Parse agencies if provided
    agencies = None
    if "agencies" in data:
        try:
            agencies = [Agency(a) for a in data["agencies"]]
        except ValueError as e:
            return jsonify({"error": f"Invalid agency: {e}"}), 400

    # Parse date filters
    date_from = None
    date_to = None
    if data.get("date_from"):
        try:
            date_from = datetime.fromisoformat(data["date_from"])
        except ValueError:
            return jsonify({"error": "Invalid date_from format"}), 400
    if data.get("date_to"):
        try:
            date_to = datetime.fromisoformat(data["date_to"])
        except ValueError:
            return jsonify({"error": "Invalid date_to format"}), 400

    # Build search query
    query = SearchQuery(
        query=data["query"],
        agencies=agencies,
        page=data.get("page", 1),
        page_size=min(data.get("page_size", 10), 100),
        include_snippets=data.get("include_snippets", True),
        date_from=date_from,
        date_to=date_to,
        document_types=data.get("document_types"),
    )

    # Execute search
    response = await search_service.search(
        query=query,
        permissions=g.permissions,
        ip_address=g.ip_address,
        session_id=g.session_id,
    )

    # Check if query should be flagged for review
    should_flag, criteria = review_service.should_flag_query(
        query=query,
        response=response,
        permissions=g.permissions,
    )

    if should_flag:
        flag = await review_service.flag_query(
            query=query,
            response=response,
            permissions=g.permissions,
            triggered_criteria=criteria,
        )
        response.requires_review = True
        response.review_id = str(flag.id)

        # Return 202 Accepted with pending response
        pending_response = review_service.get_pending_response(flag)
        return jsonify({
            "status": "pending_review",
            "review_id": pending_response.review_id,
            "message": pending_response.message,
            "estimated_review_time": pending_response.estimated_review_time,
            "contact_email": pending_response.contact_email,
            # Still include partial results for non-sensitive queries
            "partial_results": {
                "total_results": response.total_results,
                "agencies_searched": [a.value for a in response.agencies_searched],
            } if not any("confidential" in c.lower() for c in criteria) else None,
        }), 202

    # Return search results
    return jsonify({
        "query_id": str(response.query_id),
        "query": response.query,
        "results": [
            {
                "document_id": r.document_id,
                "title": r.title,
                "agency": r.agency.value,
                "agency_name": r.agency.full_name,
                "relevance_score": r.relevance_score,
                "snippet": r.snippet,
                "publication_date": r.publication_date.isoformat(),
                "document_type": r.document_type,
                "citation": {
                    "formatted": r.citation.citation_format,
                    "url": r.citation.direct_url,
                },
            }
            for r in response.results
        ],
        "total_results": response.total_results,
        "page": response.page,
        "page_size": response.page_size,
        "total_pages": response.total_pages,
        "agencies_searched": [a.value for a in response.agencies_searched],
        "processing_time_ms": response.processing_time_ms,
        "suggestions": response.suggestions,
    })


@bp.route("/api/v1/search/suggestions", methods=["GET"])
@require_auth
@handle_errors
async def search_suggestions():
    """Get search suggestions for autocomplete."""
    partial_query = request.args.get("q", "")

    if len(partial_query) < 2:
        return jsonify({"suggestions": []})

    suggestions = await search_service.get_search_suggestions(partial_query)
    return jsonify({"suggestions": suggestions})


@bp.route("/api/v1/search/popular", methods=["GET"])
@require_auth
@handle_errors
async def popular_searches():
    """Get popular recent searches."""
    limit = request.args.get("limit", 10, type=int)
    popular = await search_service.get_popular_searches(limit)
    return jsonify({"popular_searches": popular})
