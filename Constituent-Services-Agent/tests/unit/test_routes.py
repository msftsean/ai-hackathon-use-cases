"""Unit tests for API routes."""

import pytest
from flask import Flask
from src.api.routes import api
from src.api.middleware import setup_error_handlers
from src.config.settings import get_settings


@pytest.fixture
def app():
    """Create Flask test app."""
    app = Flask(__name__)
    app.register_blueprint(api)
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
        """Test GET /api/v1/health returns healthy status."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "version" in data
        assert "timestamp" in data
        assert "dependencies" in data

    def test_readiness_check(self, client):
        """Test GET /api/v1/health/ready returns 200."""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200


class TestConversationEndpoints:
    """Tests for conversation endpoints."""

    def test_get_conversation_not_found(self, client):
        """Test GET /api/v1/conversations/{id} returns 404 for missing session."""
        response = client.get("/api/v1/conversations/nonexistent-id")

        assert response.status_code == 404

    def test_delete_conversation_not_found(self, client):
        """Test DELETE /api/v1/conversations/{id} returns 404 for missing session."""
        response = client.delete("/api/v1/conversations/nonexistent-id")

        assert response.status_code == 404


class TestChatEndpoint:
    """Tests for chat endpoint."""

    def test_chat_missing_body(self, client):
        """Test POST /api/v1/chat without body returns 400."""
        response = client.post("/api/v1/chat", 
                               data="null",
                               content_type="application/json")

        assert response.status_code == 400

    def test_chat_missing_message(self, client):
        """Test POST /api/v1/chat without message returns 400."""
        response = client.post("/api/v1/chat", json={})

        assert response.status_code == 400

    def test_chat_message_too_long(self, client):
        """Test POST /api/v1/chat with too long message returns 400."""
        response = client.post("/api/v1/chat", json={
            "message": "x" * 10001
        })

        assert response.status_code == 400


class TestEscalationEndpoint:
    """Tests for escalation endpoint."""

    def test_escalate_not_found(self, client):
        """Test POST /api/v1/conversations/{id}/escalate returns 404 for missing session."""
        response = client.post("/api/v1/conversations/nonexistent-id/escalate")

        assert response.status_code == 404


class TestFeedbackEndpoint:
    """Tests for feedback endpoint."""

    def test_feedback_missing_body(self, client):
        """Test POST /api/v1/feedback without body returns 400."""
        response = client.post("/api/v1/feedback",
                               data="null",
                               content_type="application/json")

        assert response.status_code == 400

    def test_feedback_missing_message_id(self, client):
        """Test POST /api/v1/feedback without message_id returns 400."""
        response = client.post("/api/v1/feedback", json={
            "rating": 5
        })

        assert response.status_code == 400

    def test_feedback_missing_rating(self, client):
        """Test POST /api/v1/feedback without rating returns 400."""
        response = client.post("/api/v1/feedback", json={
            "message_id": "some-id"
        })

        assert response.status_code == 400

    def test_feedback_invalid_rating(self, client):
        """Test POST /api/v1/feedback with invalid rating returns 400."""
        response = client.post("/api/v1/feedback", json={
            "message_id": "some-id",
            "rating": 6
        })

        assert response.status_code == 400

    def test_feedback_comment_too_long(self, client):
        """Test POST /api/v1/feedback with too long comment returns 400."""
        response = client.post("/api/v1/feedback", json={
            "message_id": "some-id",
            "rating": 5,
            "comment": "x" * 1001
        })

        assert response.status_code == 400

    def test_feedback_valid(self, client):
        """Test POST /api/v1/feedback with valid data returns 201."""
        response = client.post("/api/v1/feedback", json={
            "message_id": "some-id",
            "rating": 5,
            "comment": "Great help!"
        })

        assert response.status_code == 201
