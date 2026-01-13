"""
API routes for Constituent Services Agent.

Implements REST endpoints per contracts/api.yaml specification.
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from flask import Blueprint, jsonify, request

from src.api.middleware import NotFoundError, ValidationError, async_route
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Create blueprint for API routes
api = Blueprint("api", __name__, url_prefix="/api/v1")

# In-memory conversation storage (replace with Cosmos DB in production)
_conversations: dict = {}


# ============================================================================
# Health Endpoints (T022, T023)
# ============================================================================


@api.route("/health", methods=["GET"])
def health_check():
    """
    GET /health - Service health check.

    Returns service health status and dependency information.
    """
    settings = get_settings()

    # Check dependencies (simplified for MVP)
    dependencies = {
        "knowledge_base": {
            "status": "up",
            "latency_ms": 10,
        },
    }

    if not settings.use_mock_services:
        # Would check actual Azure services here
        pass

    status = "healthy"
    for dep in dependencies.values():
        if dep["status"] == "down":
            status = "unhealthy"
            break
        elif dep["status"] == "degraded":
            status = "degraded"

    return jsonify({
        "status": status,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "dependencies": dependencies,
    })


@api.route("/health/ready", methods=["GET"])
def readiness_check():
    """
    GET /health/ready - Service readiness check.

    Returns 200 if service is ready to handle requests, 503 otherwise.
    """
    # For MVP, always ready if health check passes
    settings = get_settings()

    if settings.use_mock_services:
        # Mock mode is always ready
        return "", 200

    # Would check actual service readiness here
    return "", 200


# ============================================================================
# Chat Endpoints (T032)
# ============================================================================


@api.route("/chat", methods=["POST"])
@async_route
async def send_message():
    """
    POST /chat - Send a message to the agent.

    Request body (ChatRequest):
        - message: str (required) - User message text
        - session_id: str (optional) - Session identifier
        - language: str (optional) - Override language detection

    Returns ChatResponse with agent response and citations.
    """
    from src.services import get_knowledge_base

    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")

    message = data.get("message")
    if not message:
        raise ValidationError("message field is required")

    if len(message) > 10000:
        raise ValidationError("message must be 10000 characters or less")

    session_id = data.get("session_id") or str(uuid4())
    requested_language = data.get("language")

    # Get or create conversation
    if session_id not in _conversations:
        _conversations[session_id] = {
            "session_id": session_id,
            "status": "active",
            "language": requested_language or "en",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "messages": [],
        }

    conversation = _conversations[session_id]

    # Add user message
    user_message_id = str(uuid4())
    conversation["messages"].append({
        "id": user_message_id,
        "role": "user",
        "content": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })

    # Query knowledge base
    knowledge_base = get_knowledge_base()
    start_time = datetime.utcnow()

    response = await knowledge_base.query(
        question=message,
        conversation_history=conversation["messages"][:-1],  # Exclude current message
        max_citations=get_settings().max_citations,
    )

    processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    # Build citations for response
    citations = []
    for cite in response.citations:
        citations.append({
            "source_id": cite.source_id,
            "title": cite.title,
            "agency": cite.agency,
            "url": cite.url,
            "quote": cite.quote,
            "relevance": cite.relevance_score,
        })

    # Compute confidence using formula from spec
    # confidence = 0.6 * model_confidence + 0.4 * min(citation_count / 3, 1.0)
    citation_factor = min(len(citations) / 3, 1.0)
    computed_confidence = 0.6 * response.confidence + 0.4 * citation_factor

    # Add assistant message
    assistant_message_id = str(uuid4())
    conversation["messages"].append({
        "id": assistant_message_id,
        "role": "assistant",
        "content": response.answer,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "confidence": computed_confidence,
        "citations": citations,
    })
    conversation["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Build suggested actions
    suggested_actions = []
    if computed_confidence < get_settings().confidence_threshold:
        suggested_actions.append({
            "type": "escalate",
            "label": "Talk to a human agent",
            "value": f"/conversations/{session_id}/escalate",
        })

    # Build response
    result = {
        "session_id": session_id,
        "message_id": assistant_message_id,
        "response": response.answer,
        "language": conversation["language"],
        "confidence": round(computed_confidence, 3),
        "citations": citations,
        "suggested_actions": suggested_actions,
    }

    # Add disclaimer for low confidence or eligibility responses
    if computed_confidence < 0.6:
        result["disclaimer"] = (
            "This information is provided for general guidance only. "
            "Please verify with official sources or contact the relevant agency directly."
        )

    return jsonify(result)


# ============================================================================
# Conversation Endpoints (T033, T034)
# ============================================================================


@api.route("/conversations/<session_id>", methods=["GET"])
def get_conversation(session_id: str):
    """
    GET /conversations/{session_id} - Get conversation history.

    Returns full conversation including all messages.
    """
    if session_id not in _conversations:
        raise NotFoundError(f"Conversation {session_id} not found")

    return jsonify(_conversations[session_id])


@api.route("/conversations/<session_id>", methods=["DELETE"])
def end_conversation(session_id: str):
    """
    DELETE /conversations/{session_id} - End conversation.

    Marks conversation as completed and clears session.
    """
    if session_id not in _conversations:
        raise NotFoundError(f"Conversation {session_id} not found")

    conversation = _conversations[session_id]
    conversation["status"] = "completed"
    conversation["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return "", 204


# ============================================================================
# Escalation Endpoint (T060)
# ============================================================================


@api.route("/conversations/<session_id>/escalate", methods=["POST"])
def escalate_conversation(session_id: str):
    """
    POST /conversations/{session_id}/escalate - Escalate to human agent.

    Request body:
        - reason: str (optional) - Reason for escalation

    Returns escalation details including queue position.
    """
    if session_id not in _conversations:
        raise NotFoundError(f"Conversation {session_id} not found")

    data = request.get_json() or {}
    reason = data.get("reason", "User requested human assistance")

    conversation = _conversations[session_id]
    conversation["status"] = "escalated"
    conversation["escalated"] = True
    conversation["escalation_reason"] = reason
    conversation["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Mock escalation response
    return jsonify({
        "escalation_id": str(uuid4()),
        "estimated_wait_time": 5,  # minutes
        "queue_position": 3,
    })


# ============================================================================
# Feedback Endpoint (T069)
# ============================================================================


@api.route("/feedback", methods=["POST"])
def submit_feedback():
    """
    POST /feedback - Submit user feedback.

    Request body (FeedbackRequest):
        - message_id: str (required) - UUID of the message
        - rating: int (required) - 1-5 star rating
        - helpful: bool (optional) - Was response helpful?
        - comment: str (optional) - Text feedback

    Returns 201 on success.
    """
    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")

    message_id = data.get("message_id")
    if not message_id:
        raise ValidationError("message_id is required")

    rating = data.get("rating")
    if rating is None:
        raise ValidationError("rating is required")
    if not isinstance(rating, int) or not 1 <= rating <= 5:
        raise ValidationError("rating must be an integer between 1 and 5")

    comment = data.get("comment")
    if comment and len(comment) > 1000:
        raise ValidationError("comment must be 1000 characters or less")

    # In production, would save to database
    logger.info(f"Feedback received for message {message_id}: rating={rating}")

    return "", 201
