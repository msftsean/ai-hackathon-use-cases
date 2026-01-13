"""E2E tests using Playwright for Document Eligibility Agent API."""

import pytest
import subprocess
import time
import os
import signal
from playwright.sync_api import sync_playwright

# Server configuration
BASE_URL = "http://127.0.0.1:5001"


@pytest.fixture(scope="module")
def server():
    """Start the Flask server for testing."""
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
        response = page.goto(f"{BASE_URL}/health")

        assert response.status == 200

        data = page.evaluate("() => JSON.parse(document.body.textContent)")
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

        page.close()

    def test_readiness_endpoint_returns_ok(self, server, browser_context):
        """Test the readiness endpoint returns ready status."""
        page = browser_context.new_page()
        response = page.goto(f"{BASE_URL}/health/ready")

        assert response.status == 200
        page.close()


class TestDocumentEndpointsE2E:
    """E2E tests for document endpoints."""

    def test_get_nonexistent_document_returns_404(self, server, browser_context):
        """Test getting a non-existent document returns 404."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + BASE_URL + """/documents/550e8400-e29b-41d4-a716-446655440000');
                return {
                    status: response.status
                };
            }
        """)

        assert response_data["status"] == 404

        page.close()

    def test_upload_document_no_file_returns_400(self, server, browser_context):
        """Test uploading without file returns 400."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + BASE_URL + """/documents', {
                    method: 'POST',
                    body: new FormData()
                });
                return {
                    status: response.status
                };
            }
        """)

        assert response_data["status"] == 400

        page.close()


class TestQueueEndpointsE2E:
    """E2E tests for queue endpoints."""

    def test_get_queue_returns_list(self, server, browser_context):
        """Test getting queue returns list structure."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + BASE_URL + """/queue');
                return {
                    status: response.status,
                    data: await response.json()
                };
            }
        """)

        assert response_data["status"] == 200
        assert "items" in response_data["data"]
        assert "total" in response_data["data"]
        assert "page" in response_data["data"]

        page.close()

    def test_get_queue_stats(self, server, browser_context):
        """Test getting queue stats."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + BASE_URL + """/queue/stats');
                return {
                    status: response.status,
                    data: await response.json()
                };
            }
        """)

        assert response_data["status"] == 200
        assert "total" in response_data["data"]
        assert "by_status" in response_data["data"]
        assert "by_type" in response_data["data"]

        page.close()

    def test_bulk_approve_missing_ids_returns_400(self, server, browser_context):
        """Test bulk approve without document IDs returns 400."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + BASE_URL + """/queue/bulk-approve', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                });
                return {
                    status: response.status
                };
            }
        """)

        assert response_data["status"] == 400

        page.close()


class TestExtractionEndpointsE2E:
    """E2E tests for extraction endpoints."""

    def test_get_extractions_nonexistent_returns_404(self, server, browser_context):
        """Test getting extractions for non-existent document returns 404."""
        page = browser_context.new_page()

        response_data = page.evaluate("""
            async () => {
                const response = await fetch('""" + BASE_URL + """/extractions/550e8400-e29b-41d4-a716-446655440000');
                return {
                    status: response.status
                };
            }
        """)

        assert response_data["status"] == 404

        page.close()
