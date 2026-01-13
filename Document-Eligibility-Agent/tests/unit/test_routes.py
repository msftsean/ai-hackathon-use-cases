"""Unit tests for API routes."""

import pytest
from flask import Flask
from uuid import uuid4
from io import BytesIO

from src.api.routes import api_bp
from src.api.middleware import setup_error_handlers


@pytest.fixture
def app():
    """Create Flask test app."""
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.config["TESTING"] = True
    setup_error_handlers(app)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client):
        """Test GET /health returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "dependencies" in data

    def test_readiness_check(self, client):
        """Test GET /health/ready returns 200."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ready"


class TestDocumentUploadEndpoint:
    """Tests for document upload endpoint."""

    def test_upload_no_file(self, client):
        """Test POST /documents without file returns 400."""
        response = client.post("/documents")

        assert response.status_code == 400
        data = response.get_json()
        assert "No file provided" in data["message"]

    def test_upload_no_filename(self, client):
        """Test POST /documents with empty filename returns 400."""
        response = client.post(
            "/documents",
            data={
                "file": (BytesIO(b"content"), ""),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_upload_no_case_id(self, client):
        """Test POST /documents without case_id returns 400."""
        response = client.post(
            "/documents",
            data={
                "file": (BytesIO(b"content"), "test.pdf"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "case_id is required" in data["message"]

    def test_upload_invalid_document_type(self, client):
        """Test POST /documents with invalid document_type returns 400."""
        response = client.post(
            "/documents",
            data={
                "file": (BytesIO(b"content"), "test.pdf"),
                "case_id": "CASE-001",
                "document_type": "invalid_type",
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_upload_success(self, client):
        """Test POST /documents with valid data returns 201."""
        response = client.post(
            "/documents",
            data={
                "file": (BytesIO(b"%PDF-1.4 test content"), "test.pdf"),
                "case_id": "CASE-001",
                "document_type": "w2",
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["case_id"] == "CASE-001"
        assert data["document_type"] == "w2"
        assert "id" in data


class TestDocumentGetEndpoint:
    """Tests for document retrieval endpoints."""

    def test_get_document_not_found(self, client):
        """Test GET /documents/{id} returns 404 for missing document."""
        doc_id = str(uuid4())
        response = client.get(f"/documents/{doc_id}")

        assert response.status_code == 404

    def test_get_document_invalid_uuid(self, client):
        """Test GET /documents/{id} with invalid UUID returns 400."""
        response = client.get("/documents/not-a-uuid")

        assert response.status_code == 400


class TestDocumentDeleteEndpoint:
    """Tests for document delete endpoint."""

    def test_delete_document_not_found(self, client):
        """Test DELETE /documents/{id} returns 404 for missing document."""
        doc_id = str(uuid4())
        response = client.delete(f"/documents/{doc_id}")

        assert response.status_code == 404

    def test_delete_document_invalid_uuid(self, client):
        """Test DELETE /documents/{id} with invalid UUID returns 400."""
        response = client.delete("/documents/not-a-uuid")

        assert response.status_code == 400


class TestDocumentApprovalEndpoints:
    """Tests for document approval/rejection endpoints."""

    def test_approve_document_not_found(self, client):
        """Test POST /documents/{id}/approve returns 404 for missing document."""
        doc_id = str(uuid4())
        response = client.post(f"/documents/{doc_id}/approve")

        assert response.status_code == 404

    def test_reject_document_not_found(self, client):
        """Test POST /documents/{id}/reject returns 404 for missing document."""
        doc_id = str(uuid4())
        response = client.post(
            f"/documents/{doc_id}/reject",
            json={"reason": "Invalid document"},
        )

        assert response.status_code == 404

    def test_reject_document_missing_reason(self, client):
        """Test POST /documents/{id}/reject without reason returns 400."""
        # First upload a document
        upload_response = client.post(
            "/documents",
            data={
                "file": (BytesIO(b"%PDF-1.4 test content"), "test.pdf"),
                "case_id": "CASE-001",
                "document_type": "w2",
            },
            content_type="multipart/form-data",
        )
        doc_id = upload_response.get_json()["id"]

        # Try to reject without reason
        response = client.post(
            f"/documents/{doc_id}/reject",
            json={},
        )

        assert response.status_code == 400


class TestQueueEndpoints:
    """Tests for queue management endpoints."""

    def test_get_queue_empty(self, client):
        """Test GET /queue returns empty list initially."""
        response = client.get("/queue")

        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_get_queue_stats(self, client):
        """Test GET /queue/stats returns statistics."""
        response = client.get("/queue/stats")

        assert response.status_code == 200
        data = response.get_json()
        assert "total" in data
        assert "by_status" in data
        assert "by_type" in data
        assert "by_priority" in data

    def test_bulk_approve_missing_ids(self, client):
        """Test POST /queue/bulk-approve without document_ids returns 400."""
        response = client.post(
            "/queue/bulk-approve",
            json={},
        )

        assert response.status_code == 400

    def test_bulk_approve_too_many(self, client):
        """Test POST /queue/bulk-approve with too many IDs returns 400."""
        response = client.post(
            "/queue/bulk-approve",
            json={"document_ids": [str(uuid4()) for _ in range(51)]},
        )

        assert response.status_code == 400


class TestExtractionEndpoints:
    """Tests for extraction endpoints."""

    def test_get_extractions_not_found(self, client):
        """Test GET /extractions/{id} returns 404 for missing document."""
        doc_id = str(uuid4())
        response = client.get(f"/extractions/{doc_id}")

        assert response.status_code == 404

    def test_correct_field_not_found(self, client):
        """Test PATCH /extractions/{id}/fields/{name} returns 404 for missing document."""
        doc_id = str(uuid4())
        response = client.patch(
            f"/extractions/{doc_id}/fields/employer_name",
            json={"value": "New Corp"},
        )

        assert response.status_code == 404


class TestDocumentDownloadEndpoint:
    """Tests for document download endpoint."""

    def test_download_document_not_found(self, client):
        """Test GET /documents/{id}/download returns 404 for missing document."""
        doc_id = str(uuid4())
        response = client.get(f"/documents/{doc_id}/download")

        assert response.status_code == 404


class TestDocumentReprocessEndpoint:
    """Tests for document reprocess endpoint."""

    def test_reprocess_document_not_found(self, client):
        """Test POST /documents/{id}/reprocess returns 404 for missing document."""
        doc_id = str(uuid4())
        response = client.post(f"/documents/{doc_id}/reprocess")

        assert response.status_code == 404
