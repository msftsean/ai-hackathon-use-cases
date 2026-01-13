"""Pytest configuration for E2E tests."""

import pytest


def pytest_configure(config):
    """Configure pytest markers for E2E tests."""
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")


def pytest_collection_modifyitems(config, items):
    """Skip E2E tests if --run-e2e flag is not provided."""
    if config.getoption("--run-e2e", default=False):
        return

    skip_e2e = pytest.mark.skip(reason="need --run-e2e option to run")
    for item in items:
        if "e2e" in item.keywords or "e2e" in str(item.fspath):
            item.add_marker(skip_e2e)


def pytest_addoption(parser):
    """Add command line options for E2E tests."""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="run e2e tests",
    )
