"""E2E tests using Playwright for Constituent Services Agent API."""

import pytest
import subprocess
import time
import os
import signal
from playwright.sync_api import sync_playwright, expect

# Server configuration
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api/v1"


@pytest.fixture(scope="module")
def server():
    """Start the Flask server for testing."""
    # Start the server as a subprocess
    env = os.environ.copy()
    env["FLASK_ENV"] = "testing"
    env["USE_MOCK_SERVICES"] = "true"

    process = subprocess.Popen(
        ["python", "-m", "src.main"],
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(3)

    yield process

    # Cleanup
    if os.name == 'nt':  # Windows
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)


@pytest.fixture(scope="module")
def browser_context():
    """Create a Playwright browser context."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()


class TestHealthEndpointsE2E:
    """E2E tests for health endpoints."""

    def test_health_endpoint_returns_ok(self, server, browser_context):
        """Test the health endpoint returns healthy status."""
        page = browser_context.new_page()
        response = page.goto(f"{API_BASE}/health")

        assert response.status == 200

        # Parse JSON response
        data = page.evaluate("() => JSON.parse(document.body.textContent)")
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "version" in data
        assert "timestamp" in data

        page.close()

    def test_readiness_endpoint_returns_ok(self, server, browser_context):
        """Test the readiness endpoint returns ready status."""
        page = browser_context.new_page()
        response = page.goto(f"{API_BASE}/health/ready")

        assert response.status == 200
        page.close()


class TestChatEndpointE2E:
    """E2E tests for chat endpoint."""

    def test_chat_endpoint_responds(self, server, browser_context):
        """Test the chat endpoint returns a response for a valid message."""
        page = browser_context.new_page()

        # Use fetch API to make POST request
        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + API_BASE + """/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: 'What are SNAP benefits?'
                    })
                });
                return {
                    status: response.status,
                    data: await response.json()
                };
            }
        """)

        assert response_data["status"] == 200
        assert "response" in response_data["data"]
        assert "session_id" in response_data["data"]

        page.close()

    def test_chat_endpoint_missing_message_returns_400(self, server, browser_context):
        """Test the chat endpoint returns 400 for missing message."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + API_BASE + """/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                });
                return {
                    status: response.status,
                    data: await response.json()
                };
            }
        """)

        assert response_data["status"] == 400

        page.close()


class TestConversationEndpointsE2E:
    """E2E tests for conversation endpoints."""

    def test_get_nonexistent_conversation_returns_404(self, server, browser_context):
        """Test getting a non-existent conversation returns 404."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + API_BASE + """/conversations/nonexistent-id');
                return {
                    status: response.status
                };
            }
        """)

        assert response_data["status"] == 404

        page.close()


class TestFeedbackEndpointE2E:
    """E2E tests for feedback endpoint."""

    def test_feedback_with_valid_data(self, server, browser_context):
        """Test submitting feedback with valid data returns 201."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + API_BASE + """/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message_id: 'test-message-id',
                        rating: 5,
                        comment: 'Great response!'
                    })
                });
                return {
                    status: response.status,
                    data: await response.json()
                };
            }
        """)

        assert response_data["status"] == 201

        page.close()

    def test_feedback_missing_rating_returns_400(self, server, browser_context):
        """Test submitting feedback without rating returns 400."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + API_BASE + """/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message_id: 'test-message-id'
                    })
                });
                return {
                    status: response.status
                };
            }
        """)

        assert response_data["status"] == 400

        page.close()
