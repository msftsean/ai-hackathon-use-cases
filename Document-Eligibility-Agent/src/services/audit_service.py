"""Audit service for LOADinG Act compliance logging."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.config import get_settings
from src.models import LogAction
from src.models.processing_log import ProcessingLog

logger = logging.getLogger(__name__)


class AuditService(ABC):
    """Abstract base class for audit logging service."""

    @abstractmethod
    async def log(self, entry: ProcessingLog) -> None:
        """Log a processing event."""
        pass

    @abstractmethod
    async def get_logs_for_document(
        self, document_id: UUID, limit: int = 100
    ) -> list[ProcessingLog]:
        """Get all audit logs for a document."""
        pass

    @abstractmethod
    async def get_logs_by_action(
        self,
        action: LogAction,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[ProcessingLog]:
        """Get audit logs filtered by action type."""
        pass

    @abstractmethod
    async def get_logs_by_actor(
        self,
        actor: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[ProcessingLog]:
        """Get audit logs for a specific actor."""
        pass


class MockAuditService(AuditService):
    """Mock audit service for development/testing."""

    def __init__(self):
        """Initialize mock audit service with in-memory store."""
        self._logs: list[ProcessingLog] = []
        logger.info("MockAuditService initialized")

    async def log(self, entry: ProcessingLog) -> None:
        """Log a processing event to mock storage."""
        self._logs.append(entry)
        logger.info(
            f"Audit log: {entry.action.value} for document {entry.document_id} "
            f"by {entry.actor}"
        )

    async def get_logs_for_document(
        self, document_id: UUID, limit: int = 100
    ) -> list[ProcessingLog]:
        """Get all audit logs for a document from mock storage."""
        logs = [log for log in self._logs if log.document_id == document_id]
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]

    async def get_logs_by_action(
        self,
        action: LogAction,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[ProcessingLog]:
        """Get audit logs filtered by action type from mock storage."""
        logs = [log for log in self._logs if log.action == action]

        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]

        return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]

    async def get_logs_by_actor(
        self,
        actor: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[ProcessingLog]:
        """Get audit logs for a specific actor from mock storage."""
        logs = [log for log in self._logs if log.actor == actor]

        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]

        return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_all_logs(self) -> list[ProcessingLog]:
        """Get all logs (for testing)."""
        return sorted(self._logs, key=lambda x: x.timestamp, reverse=True)

    def clear(self) -> None:
        """Clear all logs (for testing)."""
        self._logs.clear()


class CosmosAuditService(AuditService):
    """Cosmos DB audit service for production."""

    def __init__(self):
        """Initialize Cosmos DB audit client."""
        settings = get_settings()
        self._endpoint = settings.cosmos_endpoint
        self._key = settings.cosmos_key
        self._database_name = settings.cosmos_database
        self._container_name = "processing_logs"
        self._client = None
        self._container = None
        logger.info("CosmosAuditService initialized")

    def _get_container(self):
        """Get or create Cosmos DB container client."""
        if self._container is None:
            try:
                from azure.cosmos import CosmosClient, PartitionKey

                self._client = CosmosClient(self._endpoint, self._key)
                database = self._client.get_database_client(self._database_name)

                # Create container if it doesn't exist
                self._container = database.create_container_if_not_exists(
                    id=self._container_name,
                    partition_key=PartitionKey(path="/document_id"),
                    # 7-year TTL for compliance (in seconds)
                    default_ttl=7 * 365 * 24 * 60 * 60,
                )
            except ImportError:
                raise RuntimeError(
                    "azure-cosmos package not installed. "
                    "Run: pip install azure-cosmos"
                )
        return self._container

    async def log(self, entry: ProcessingLog) -> None:
        """Log a processing event to Cosmos DB."""
        container = self._get_container()

        # Convert to dict with string UUIDs for Cosmos
        log_dict = entry.to_dict()
        log_dict["id"] = str(entry.id)
        log_dict["document_id"] = str(entry.document_id)

        # Partition key is the date (YYYY-MM-DD) for efficient querying
        log_dict["partition_key"] = entry.timestamp.strftime("%Y-%m-%d")

        container.create_item(body=log_dict)
        logger.info(
            f"Audit log saved to Cosmos: {entry.action.value} for "
            f"document {entry.document_id}"
        )

    async def get_logs_for_document(
        self, document_id: UUID, limit: int = 100
    ) -> list[ProcessingLog]:
        """Get all audit logs for a document from Cosmos DB."""
        container = self._get_container()

        query = (
            "SELECT * FROM c WHERE c.document_id = @document_id "
            "ORDER BY c.timestamp DESC OFFSET 0 LIMIT @limit"
        )
        parameters = [
            {"name": "@document_id", "value": str(document_id)},
            {"name": "@limit", "value": limit},
        ]

        items = container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )

        return [ProcessingLog(**item) for item in items]

    async def get_logs_by_action(
        self,
        action: LogAction,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[ProcessingLog]:
        """Get audit logs filtered by action type from Cosmos DB."""
        container = self._get_container()

        query = "SELECT * FROM c WHERE c.action = @action"
        parameters = [{"name": "@action", "value": action.value}]

        if start_date:
            query += " AND c.timestamp >= @start_date"
            parameters.append(
                {"name": "@start_date", "value": start_date.isoformat()}
            )
        if end_date:
            query += " AND c.timestamp <= @end_date"
            parameters.append({"name": "@end_date", "value": end_date.isoformat()})

        query += " ORDER BY c.timestamp DESC OFFSET 0 LIMIT @limit"
        parameters.append({"name": "@limit", "value": limit})

        items = container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )

        return [ProcessingLog(**item) for item in items]

    async def get_logs_by_actor(
        self,
        actor: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[ProcessingLog]:
        """Get audit logs for a specific actor from Cosmos DB."""
        container = self._get_container()

        query = "SELECT * FROM c WHERE c.actor = @actor"
        parameters = [{"name": "@actor", "value": actor}]

        if start_date:
            query += " AND c.timestamp >= @start_date"
            parameters.append(
                {"name": "@start_date", "value": start_date.isoformat()}
            )
        if end_date:
            query += " AND c.timestamp <= @end_date"
            parameters.append({"name": "@end_date", "value": end_date.isoformat()})

        query += " ORDER BY c.timestamp DESC OFFSET 0 LIMIT @limit"
        parameters.append({"name": "@limit", "value": limit})

        items = container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )

        return [ProcessingLog(**item) for item in items]
