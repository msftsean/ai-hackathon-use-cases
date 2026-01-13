"""Review API endpoints for Inter-Agency Knowledge Hub."""

import logging

from flask import Blueprint, jsonify, request, g

from ..models.review import ReviewUpdateRequest, ReviewStatus
from ..services.review_service import ReviewService
from ..middleware.auth_middleware import require_reviewer, require_auth
from ..middleware.error_handler import handle_errors

logger = logging.getLogger("knowledge_hub")

bp = Blueprint("reviews", __name__)

review_service = ReviewService()


@bp.route("/api/v1/reviews", methods=["GET"])
@require_reviewer
@handle_errors
async def list_pending_reviews():
    """List pending reviews (reviewer/admin only)."""
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    flags, total = await review_service.get_pending_reviews(limit, offset)

    return jsonify({
        "reviews": [
            {
                "id": str(flag.id),
                "query": flag.query,
                "user_id": flag.user_id,
                "user_email": flag.user_email,
                "status": flag.status.value,
                "flag_reason": flag.flag_reason,
                "flag_criteria": flag.flag_criteria,
                "agencies_involved": [a.value for a in flag.agencies_involved],
                "confidence_score": flag.confidence_score,
                "flagged_at": flag.flagged_at.isoformat(),
                "original_results_count": len(flag.original_results),
            }
            for flag in flags
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    })


@bp.route("/api/v1/reviews/<flag_id>", methods=["GET"])
@require_reviewer
@handle_errors
async def get_review(flag_id: str):
    """Get a specific review flag."""
    flag = await review_service.get_review(flag_id)

    if not flag:
        return jsonify({"error": "Review not found"}), 404

    return jsonify({
        "id": str(flag.id),
        "query": flag.query,
        "user_id": flag.user_id,
        "user_email": flag.user_email,
        "status": flag.status.value,
        "flag_reason": flag.flag_reason,
        "flag_criteria": flag.flag_criteria,
        "agencies_involved": [a.value for a in flag.agencies_involved],
        "confidence_score": flag.confidence_score,
        "flagged_at": flag.flagged_at.isoformat(),
        "reviewed_at": flag.reviewed_at.isoformat() if flag.reviewed_at else None,
        "reviewer_id": flag.reviewer_id,
        "reviewer_notes": flag.reviewer_notes,
        "modified_response": flag.modified_response,
        "original_results": flag.original_results,
    })


@bp.route("/api/v1/reviews/<flag_id>", methods=["PUT"])
@require_reviewer
@handle_errors
async def update_review(flag_id: str):
    """Update a review flag (approve/modify/reject)."""
    data = request.get_json()

    if not data or "status" not in data:
        return jsonify({"error": "Status is required"}), 400

    try:
        status = ReviewStatus(data["status"])
    except ValueError:
        return jsonify({"error": "Invalid status value"}), 400

    # Validate modified status requires modified_response
    if status == ReviewStatus.MODIFIED and not data.get("modified_response"):
        return jsonify({"error": "modified_response required for MODIFIED status"}), 400

    update = ReviewUpdateRequest(
        status=status,
        reviewer_notes=data.get("reviewer_notes"),
        modified_response=data.get("modified_response"),
    )

    flag = await review_service.update_review(
        flag_id=flag_id,
        update=update,
        reviewer_id=g.user_id,
    )

    if not flag:
        return jsonify({"error": "Review not found"}), 404

    return jsonify({
        "id": str(flag.id),
        "status": flag.status.value,
        "reviewed_at": flag.reviewed_at.isoformat() if flag.reviewed_at else None,
        "reviewer_id": flag.reviewer_id,
        "message": f"Review {flag_id} updated to {status.value}",
    })


@bp.route("/api/v1/reviews/stats", methods=["GET"])
@require_reviewer
@handle_errors
async def review_stats():
    """Get review statistics."""
    stats = await review_service.get_review_stats()
    return jsonify(stats)


@bp.route("/api/v1/reviews/status/<flag_id>", methods=["GET"])
@require_auth
@handle_errors
async def check_review_status(flag_id: str):
    """Check the status of a review (for the user who submitted it)."""
    flag = await review_service.get_review(flag_id)

    if not flag:
        return jsonify({"error": "Review not found"}), 404

    # Only allow the user who submitted or reviewers/admins to check
    if flag.user_id != g.user_id and not g.permissions.is_reviewer and not g.permissions.is_admin:
        return jsonify({"error": "Access denied"}), 403

    response = {
        "id": str(flag.id),
        "status": flag.status.value,
        "flagged_at": flag.flagged_at.isoformat(),
    }

    # Include additional info if review is complete
    if flag.status != ReviewStatus.PENDING:
        response["reviewed_at"] = flag.reviewed_at.isoformat() if flag.reviewed_at else None

        if flag.status == ReviewStatus.APPROVED:
            response["message"] = "Your query has been approved. Results are now available."
        elif flag.status == ReviewStatus.MODIFIED:
            response["message"] = "Your query results have been modified by a reviewer."
            response["modified_response"] = flag.modified_response
        elif flag.status == ReviewStatus.REJECTED:
            response["message"] = "Your query has been rejected."
            response["reviewer_notes"] = flag.reviewer_notes

    return jsonify(response)
