"""Test configuration and fixtures for Inter-Agency Knowledge Hub."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Configure test environment."""
    # Use mock services by default in tests
    monkeypatch.setenv("USE_MOCK_SERVICES", "true")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
