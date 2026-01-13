"""API routes for Document Eligibility Agent."""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from flask import Blueprint, g, jsonify, request

from src.api.middleware import require_json, validate_uuid
from src.config import get_settings
from src.models import (
    DocumentPriority,
    DocumentSource,
    DocumentStatus,
    DocumentType,
    LogAction,
    ValidationStatus,
)
from src.models.document import Document
from src.models.extraction import Extraction
from src.models.processing_log import ProcessingLog
from src.services import get_audit_service, get_storage_service

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

# In-memory storage for documents (mock mode)
_documents: dict[str, Document] = {}
_extractions: dict[str, list[Extraction]] = {}


def _run_async(coro):
    """Helper to run async functions in Flask."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================================================
# Health Endpoints
# ============================================================================


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "storage": {"status": "up" if settings.use_mock_services else "unknown"},
            "cosmos": {"status": "up" if settings.use_mock_services else "unknown"},
            "redis": {"status": "up" if settings.use_mock_services else "unknown"},
        },
    })


@api_bp.route("/health/ready", methods=["GET"])
def readiness_check():
    """Readiness check endpoint."""
    # Check if all required services are available
    settings = get_settings()
    if settings.use_mock_services:
        return jsonify({"status": "ready"}), 200

    # In production, check actual service connections
    try:
        # Placeholder for real service checks
        return jsonify({"status": "ready"}), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({"status": "not_ready", "error": str(e)}), 503


# ============================================================================
# Document Endpoints
# ============================================================================


@api_bp.route("/documents", methods=["POST"])
def upload_document():
    """Upload a document for processing."""
    settings = get_settings()

    # Check for file in request
    if "file" not in request.files:
        return jsonify({
            "error": "Bad Request",
            "message": "No file provided",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({
            "error": "Bad Request",
            "message": "No filename provided",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    # Get form data
    case_id = request.form.get("case_id")
    if not case_id:
        return jsonify({
            "error": "Bad Request",
            "message": "case_id is required",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    document_type_str = request.form.get("document_type", "other")
    try:
        document_type = DocumentType(document_type_str)
    except ValueError:
        return jsonify({
            "error": "Bad Request",
            "message": f"Invalid document_type: {document_type_str}",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    priority_str = request.form.get("priority", "standard")
    try:
        priority = DocumentPriority(priority_str)
    except ValueError:
        priority = DocumentPriority.STANDARD

    # Read file content
    file_content = file.read()
    file_size = len(file_content)

    # Check file size
    max_size = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        return jsonify({
            "error": "Payload Too Large",
            "message": f"File size exceeds maximum allowed ({settings.max_file_size_mb}MB)",
            "request_id": getattr(g, 'request_id', None),
        }), 413

    # Determine content type
    content_type = file.content_type or "application/octet-stream"

    # Create document
    document = Document(
        case_id=case_id,
        document_type=document_type,
        source=DocumentSource.UPLOAD,
        filename=file.filename,
        file_size_bytes=file_size,
        mime_type=content_type,
        priority=priority,
    )

    # Upload to storage
    storage = get_storage_service()
    try:
        blob_url = _run_async(storage.upload_document(
            case_id=case_id,
            document_id=document.id,
            file_content=file_content,
            filename=file.filename,
            content_type=content_type,
        ))
        document.blob_url = blob_url
        document.content_hash = storage.compute_hash(file_content)
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "Failed to store document",
            "request_id": getattr(g, 'request_id', None),
        }), 500

    # Check for duplicates
    for existing in _documents.values():
        if existing.content_hash == document.content_hash and existing.case_id == case_id:
            document.is_duplicate = True
            document.duplicate_of = existing.id
            break

    # Store document
    _documents[str(document.id)] = document

    # Log upload
    audit = get_audit_service()
    log_entry = ProcessingLog.create_upload_log(
        document_id=document.id,
        actor=request.remote_addr or "unknown",
        filename=file.filename,
        file_size=file_size,
        source=DocumentSource.UPLOAD.value,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )
    _run_async(audit.log(log_entry))

    logger.info(f"Document uploaded: {document.id} ({file.filename})")

    return jsonify(document.to_dict()), 201


@api_bp.route("/documents/<document_id>", methods=["GET"])
@validate_uuid("document_id")
def get_document(document_id: str):
    """Get document details."""
    document = _documents.get(document_id)
    if not document:
        return jsonify({
            "error": "Not Found",
            "message": f"Document {document_id} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    # Get extractions for this document
    extractions = _extractions.get(document_id, [])

    result = document.to_dict()
    result["extractions"] = [e.to_dict() for e in extractions]

    return jsonify(result)


@api_bp.route("/documents/<document_id>", methods=["DELETE"])
@validate_uuid("document_id")
def delete_document(document_id: str):
    """Delete a document."""
    document = _documents.get(document_id)
    if not document:
        return jsonify({
            "error": "Not Found",
            "message": f"Document {document_id} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    # Delete from storage
    if document.blob_url:
        storage = get_storage_service()
        _run_async(storage.delete_document(document.blob_url))

    # Delete from memory
    del _documents[document_id]
    if document_id in _extractions:
        del _extractions[document_id]

    logger.info(f"Document deleted: {document_id}")

    return "", 204


@api_bp.route("/documents/<document_id>/download", methods=["GET"])
@validate_uuid("document_id")
def download_document(document_id: str):
    """Download the original document."""
    document = _documents.get(document_id)
    if not document:
        return jsonify({
            "error": "Not Found",
            "message": f"Document {document_id} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    if not document.blob_url:
        return jsonify({
            "error": "Not Found",
            "message": "Document content not available",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    storage = get_storage_service()
    try:
        content = _run_async(storage.download_document(document.blob_url))
        from flask import Response
        return Response(
            content,
            mimetype=document.mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{document.filename}"'
            },
        )
    except FileNotFoundError:
        return jsonify({
            "error": "Not Found",
            "message": "Document content not found in storage",
            "request_id": getattr(g, 'request_id', None),
        }), 404


@api_bp.route("/documents/<document_id>/approve", methods=["POST"])
@validate_uuid("document_id")
def approve_document(document_id: str):
    """Approve a document."""
    document = _documents.get(document_id)
    if not document:
        return jsonify({
            "error": "Not Found",
            "message": f"Document {document_id} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    # Check if document is in reviewable state
    reviewable_states = [
        DocumentStatus.READY_FOR_REVIEW,
        DocumentStatus.EXTRACTED,
        DocumentStatus.VALIDATING,
    ]
    if document.status not in reviewable_states:
        return jsonify({
            "error": "Conflict",
            "message": f"Document cannot be approved in state: {document.status.value}",
            "request_id": getattr(g, 'request_id', None),
        }), 409

    # Get optional notes
    data = request.get_json(silent=True) or {}
    notes = data.get("notes")

    # Mark as approved
    document.mark_reviewed(
        reviewer_id=request.remote_addr or "unknown",
        approved=True,
        notes=notes,
    )

    # Log approval
    audit = get_audit_service()
    log_entry = ProcessingLog.create_review_log(
        document_id=document.id,
        actor=request.remote_addr or "unknown",
        actor_role="reviewer",
        approved=True,
        notes=notes,
        ip_address=request.remote_addr,
    )
    _run_async(audit.log(log_entry))

    logger.info(f"Document approved: {document_id}")

    return jsonify(document.to_dict())


@api_bp.route("/documents/<document_id>/reject", methods=["POST"])
@validate_uuid("document_id")
@require_json
def reject_document(document_id: str):
    """Reject a document."""
    document = _documents.get(document_id)
    if not document:
        return jsonify({
            "error": "Not Found",
            "message": f"Document {document_id} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    data = request.get_json()
    reason = data.get("reason")
    if not reason:
        return jsonify({
            "error": "Bad Request",
            "message": "reason is required",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    request_resubmission = data.get("request_resubmission", False)

    # Mark as rejected
    document.mark_reviewed(
        reviewer_id=request.remote_addr or "unknown",
        approved=False,
        notes=reason,
    )

    if request_resubmission:
        document.status = DocumentStatus.RESUBMIT_REQUESTED

    # Log rejection
    audit = get_audit_service()
    log_entry = ProcessingLog.create_review_log(
        document_id=document.id,
        actor=request.remote_addr or "unknown",
        actor_role="reviewer",
        approved=False,
        notes=reason,
        ip_address=request.remote_addr,
    )
    _run_async(audit.log(log_entry))

    logger.info(f"Document rejected: {document_id}")

    return jsonify(document.to_dict())


@api_bp.route("/documents/<document_id>/reprocess", methods=["POST"])
@validate_uuid("document_id")
def reprocess_document(document_id: str):
    """Reprocess a document."""
    document = _documents.get(document_id)
    if not document:
        return jsonify({
            "error": "Not Found",
            "message": f"Document {document_id} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    # Reset status to uploaded
    document.status = DocumentStatus.UPLOADED
    document.processed_at = None
    document.overall_confidence = None
    document.validation_status = None

    # Clear existing extractions
    if document_id in _extractions:
        del _extractions[document_id]

    logger.info(f"Document queued for reprocessing: {document_id}")

    return jsonify({"message": "Document queued for reprocessing"}), 202


# ============================================================================
# Queue Endpoints
# ============================================================================


@api_bp.route("/queue", methods=["GET"])
def get_queue():
    """Get the document processing queue."""
    # Query parameters
    status_filter = request.args.get("status")
    doc_type_filter = request.args.get("document_type")
    assigned_to_filter = request.args.get("assigned_to")
    priority_filter = request.args.get("priority")
    sort_by = request.args.get("sort_by", "uploaded_at")
    sort_order = request.args.get("sort_order", "asc")
    page = int(request.args.get("page", 1))
    page_size = min(int(request.args.get("page_size", 20)), 100)

    # Filter documents
    filtered_docs = list(_documents.values())

    if status_filter:
        try:
            status = DocumentStatus(status_filter)
            filtered_docs = [d for d in filtered_docs if d.status == status]
        except ValueError:
            pass

    if doc_type_filter:
        try:
            doc_type = DocumentType(doc_type_filter)
            filtered_docs = [d for d in filtered_docs if d.document_type == doc_type]
        except ValueError:
            pass

    if assigned_to_filter:
        filtered_docs = [d for d in filtered_docs if d.assigned_to == assigned_to_filter]

    if priority_filter:
        try:
            priority = DocumentPriority(priority_filter)
            filtered_docs = [d for d in filtered_docs if d.priority == priority]
        except ValueError:
            pass

    # Sort
    reverse = sort_order == "desc"
    if sort_by == "uploaded_at":
        filtered_docs.sort(key=lambda d: d.uploaded_at, reverse=reverse)
    elif sort_by == "priority":
        priority_order = {
            DocumentPriority.EXPEDITED: 0,
            DocumentPriority.RESUBMISSION: 1,
            DocumentPriority.STANDARD: 2,
            DocumentPriority.LOW: 3,
        }
        filtered_docs.sort(
            key=lambda d: priority_order.get(d.priority, 99), reverse=reverse
        )
    elif sort_by == "confidence":
        filtered_docs.sort(
            key=lambda d: d.overall_confidence or 0, reverse=reverse
        )

    # Paginate
    total = len(filtered_docs)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_docs = filtered_docs[start:end]

    return jsonify({
        "items": [d.to_dict() for d in paginated_docs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": end < total,
    })


@api_bp.route("/queue/stats", methods=["GET"])
def get_queue_stats():
    """Get queue statistics."""
    docs = list(_documents.values())

    # Count by status
    by_status = {}
    for doc in docs:
        status = doc.status.value
        by_status[status] = by_status.get(status, 0) + 1

    # Count by type
    by_type = {}
    for doc in docs:
        doc_type = doc.document_type.value
        by_type[doc_type] = by_type.get(doc_type, 0) + 1

    # Count by priority
    by_priority = {}
    for doc in docs:
        priority = doc.priority.value
        by_priority[priority] = by_priority.get(priority, 0) + 1

    # Calculate auto-approved rate
    approved_count = sum(1 for d in docs if d.status == DocumentStatus.APPROVED)
    total_reviewed = sum(
        1 for d in docs
        if d.status in [DocumentStatus.APPROVED, DocumentStatus.REJECTED]
    )
    auto_approved_rate = (approved_count / total_reviewed) if total_reviewed > 0 else 0.0

    return jsonify({
        "total": len(docs),
        "by_status": by_status,
        "by_type": by_type,
        "by_priority": by_priority,
        "avg_processing_time_ms": 0,  # Placeholder
        "auto_approved_rate": auto_approved_rate,
    })


@api_bp.route("/queue/bulk-approve", methods=["POST"])
@require_json
def bulk_approve():
    """Bulk approve documents."""
    data = request.get_json()
    document_ids = data.get("document_ids", [])

    if not document_ids:
        return jsonify({
            "error": "Bad Request",
            "message": "document_ids is required",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    if len(document_ids) > 50:
        return jsonify({
            "error": "Bad Request",
            "message": "Maximum 50 documents per bulk operation",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    approved = 0
    failed = 0
    errors = []

    audit = get_audit_service()

    for doc_id in document_ids:
        document = _documents.get(doc_id)
        if not document:
            failed += 1
            errors.append({"document_id": doc_id, "error": "Document not found"})
            continue

        reviewable_states = [
            DocumentStatus.READY_FOR_REVIEW,
            DocumentStatus.EXTRACTED,
            DocumentStatus.VALIDATING,
        ]
        if document.status not in reviewable_states:
            failed += 1
            errors.append({
                "document_id": doc_id,
                "error": f"Cannot approve in state: {document.status.value}",
            })
            continue

        document.mark_reviewed(
            reviewer_id=request.remote_addr or "unknown",
            approved=True,
        )

        log_entry = ProcessingLog.create_review_log(
            document_id=document.id,
            actor=request.remote_addr or "unknown",
            actor_role="reviewer",
            approved=True,
            ip_address=request.remote_addr,
        )
        _run_async(audit.log(log_entry))

        approved += 1

    logger.info(f"Bulk approve: {approved} approved, {failed} failed")

    return jsonify({
        "approved": approved,
        "failed": failed,
        "errors": errors,
    })


# ============================================================================
# Extraction Endpoints
# ============================================================================


@api_bp.route("/extractions/<document_id>", methods=["GET"])
@validate_uuid("document_id")
def get_extractions(document_id: str):
    """Get extraction results for a document."""
    document = _documents.get(document_id)
    if not document:
        return jsonify({
            "error": "Not Found",
            "message": f"Document {document_id} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    extractions = _extractions.get(document_id, [])
    include_pii = request.args.get("include_pii", "false").lower() == "true"

    # Build response with potentially masked values
    extraction_results = []
    for ext in extractions:
        result = ext.to_dict()
        if not include_pii and ext.is_pii:
            result["field_value"] = ext.get_display_value(include_pii=False)
        extraction_results.append(result)

    return jsonify({
        "document_id": document_id,
        "document_type": document.document_type.value,
        "overall_confidence": document.overall_confidence,
        "extractions": extraction_results,
    })


@api_bp.route("/extractions/<document_id>/fields/<field_name>", methods=["PATCH"])
@validate_uuid("document_id")
@require_json
def correct_field(document_id: str, field_name: str):
    """Correct an extracted field value."""
    document = _documents.get(document_id)
    if not document:
        return jsonify({
            "error": "Not Found",
            "message": f"Document {document_id} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    extractions = _extractions.get(document_id, [])
    extraction = next((e for e in extractions if e.field_name == field_name), None)
    if not extraction:
        return jsonify({
            "error": "Not Found",
            "message": f"Field {field_name} not found",
            "request_id": getattr(g, 'request_id', None),
        }), 404

    data = request.get_json()
    new_value = data.get("value")
    if new_value is None:
        return jsonify({
            "error": "Bad Request",
            "message": "value is required",
            "request_id": getattr(g, 'request_id', None),
        }), 400

    reason = data.get("reason")
    original_value = extraction.field_value

    # Apply correction
    extraction.correct(new_value, request.remote_addr or "unknown")

    # Log correction
    audit = get_audit_service()
    log_entry = ProcessingLog.create_correction_log(
        document_id=document.id,
        actor=request.remote_addr or "unknown",
        field_name=field_name,
        original_value=original_value,
        new_value=new_value,
        reason=reason,
        ip_address=request.remote_addr,
    )
    _run_async(audit.log(log_entry))

    logger.info(f"Field corrected: {document_id}/{field_name}")

    return jsonify(extraction.to_dict())
