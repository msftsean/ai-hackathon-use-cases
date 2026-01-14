"""Azure Blob Storage service for document storage."""

import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from src.config import get_settings

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """Abstract base class for storage service."""

    @abstractmethod
    async def upload_document(
        self,
        case_id: str,
        document_id: UUID,
        file_content: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        """Upload a document and return the blob URL."""
        pass

    @abstractmethod
    async def download_document(self, blob_url: str) -> bytes:
        """Download a document from storage."""
        pass

    @abstractmethod
    async def delete_document(self, blob_url: str) -> bool:
        """Delete a document from storage."""
        pass

    @abstractmethod
    async def get_document_url(
        self, case_id: str, document_id: UUID, filename: str
    ) -> str:
        """Get the URL for a document."""
        pass

    @staticmethod
    def compute_hash(content: bytes) -> str:
        """Compute SHA-256 hash of content for deduplication."""
        return hashlib.sha256(content).hexdigest()


class MockStorageService(StorageService):
    """Mock storage service for development/testing."""

    def __init__(self):
        """Initialize mock storage with in-memory store."""
        self._storage: dict[str, bytes] = {}
        self._metadata: dict[str, dict] = {}
        logger.info("MockStorageService initialized")

    async def upload_document(
        self,
        case_id: str,
        document_id: UUID,
        file_content: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        """Upload a document to mock storage."""
        blob_path = f"documents/{case_id}/{document_id}/{filename}"
        self._storage[blob_path] = file_content
        self._metadata[blob_path] = {
            "case_id": case_id,
            "document_id": str(document_id),
            "filename": filename,
            "content_type": content_type,
            "size": len(file_content),
            "uploaded_at": datetime.utcnow().isoformat(),
            "content_hash": self.compute_hash(file_content),
        }
        logger.info(f"Mock uploaded document: {blob_path}")
        return f"mock://storage/{blob_path}"

    async def download_document(self, blob_url: str) -> bytes:
        """Download a document from mock storage."""
        # Extract path from mock URL
        blob_path = blob_url.replace("mock://storage/", "")
        if blob_path in self._storage:
            logger.info(f"Mock downloaded document: {blob_path}")
            return self._storage[blob_path]
        raise FileNotFoundError(f"Document not found: {blob_path}")

    async def delete_document(self, blob_url: str) -> bool:
        """Delete a document from mock storage."""
        blob_path = blob_url.replace("mock://storage/", "")
        if blob_path in self._storage:
            del self._storage[blob_path]
            del self._metadata[blob_path]
            logger.info(f"Mock deleted document: {blob_path}")
            return True
        return False

    async def get_document_url(
        self, case_id: str, document_id: UUID, filename: str
    ) -> str:
        """Get the URL for a document in mock storage."""
        return f"mock://storage/documents/{case_id}/{document_id}/{filename}"

    def get_all_documents(self) -> list[dict]:
        """Get all documents in mock storage (for testing)."""
        return list(self._metadata.values())


class AzureStorageService(StorageService):
    """Azure Blob Storage service implementation."""

    def __init__(self):
        """Initialize Azure storage client."""
        settings = get_settings()
        self._connection_string = settings.azure_storage_connection_string
        self._container_name = settings.azure_storage_container
        self._client = None
        logger.info("AzureStorageService initialized")

    def _get_client(self):
        """Get or create blob service client."""
        if self._client is None:
            try:
                from azure.storage.blob import BlobServiceClient

                self._client = BlobServiceClient.from_connection_string(
                    self._connection_string
                )
            except ImportError:
                raise RuntimeError(
                    "azure-storage-blob package not installed. "
                    "Run: pip install azure-storage-blob"
                )
        return self._client

    async def upload_document(
        self,
        case_id: str,
        document_id: UUID,
        file_content: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        """Upload a document to Azure Blob Storage."""
        from azure.storage.blob import ContentSettings

        client = self._get_client()
        container_client = client.get_container_client(self._container_name)

        blob_path = f"documents/{case_id}/{document_id}/{filename}"
        blob_client = container_client.get_blob_client(blob_path)

        blob_client.upload_blob(
            file_content,
            content_settings=ContentSettings(content_type=content_type),
            overwrite=True,
            metadata={
                "case_id": case_id,
                "document_id": str(document_id),
                "content_hash": self.compute_hash(file_content),
            },
        )

        logger.info(f"Uploaded document to Azure: {blob_path}")
        return blob_client.url

    async def download_document(self, blob_url: str) -> bytes:
        """Download a document from Azure Blob Storage."""
        client = self._get_client()

        # Parse blob URL to get container and blob name
        from urllib.parse import urlparse

        parsed = urlparse(blob_url)
        path_parts = parsed.path.lstrip("/").split("/", 1)
        if len(path_parts) < 2:
            raise ValueError(f"Invalid blob URL: {blob_url}")

        container_name, blob_name = path_parts
        container_client = client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        download = blob_client.download_blob()
        content = download.readall()
        logger.info(f"Downloaded document from Azure: {blob_name}")
        return content

    async def delete_document(self, blob_url: str) -> bool:
        """Delete a document from Azure Blob Storage."""
        client = self._get_client()

        from urllib.parse import urlparse

        parsed = urlparse(blob_url)
        path_parts = parsed.path.lstrip("/").split("/", 1)
        if len(path_parts) < 2:
            return False

        container_name, blob_name = path_parts
        container_client = client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        try:
            blob_client.delete_blob()
            logger.info(f"Deleted document from Azure: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    async def get_document_url(
        self, case_id: str, document_id: UUID, filename: str
    ) -> str:
        """Get the URL for a document in Azure Blob Storage."""
        client = self._get_client()
        container_client = client.get_container_client(self._container_name)
        blob_path = f"documents/{case_id}/{document_id}/{filename}"
        blob_client = container_client.get_blob_client(blob_path)
        return blob_client.url
