"""Service module with factory pattern for mock/real service switching."""

from typing import TYPE_CHECKING

from src.config import get_settings

if TYPE_CHECKING:
    from .audit_service import AuditService
    from .storage_service import StorageService


def get_storage_service() -> "StorageService":
    """Get storage service instance based on configuration."""
    from .storage_service import MockStorageService, AzureStorageService

    settings = get_settings()
    if settings.use_mock_services:
        return MockStorageService()
    return AzureStorageService()


def get_audit_service() -> "AuditService":
    """Get audit service instance based on configuration."""
    from .audit_service import MockAuditService, CosmosAuditService

    settings = get_settings()
    if settings.use_mock_services:
        return MockAuditService()
    return CosmosAuditService()


__all__ = [
    "get_storage_service",
    "get_audit_service",
]
