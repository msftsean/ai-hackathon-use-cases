"""Unit tests for AuditService."""

import pytest
from datetime import datetime, timedelta

from src.services.audit_service import AuditService
from src.models.audit import AuditLogFilter
from src.models.enums import ActionType, Agency


@pytest.fixture
async def audit_service():
    """Create audit service with test database."""
    service = AuditService()
    # Use in-memory database for tests
    from src.db.database import Database
    service._db = Database(":memory:")
    await service._ensure_initialized()
    return service


class TestAuditService:
    """Tests for AuditService."""

    @pytest.mark.asyncio
    async def test_log_search_action(self, audit_service):
        """Test logging a search action."""
        log = await audit_service.log_search(
            user_id="user-001",
            query="remote work policy",
            agencies=[Agency.DMV, Agency.DOL],
            result_count=10,
            user_email="user@test.com",
            ip_address="192.168.1.1",
        )

        assert log is not None
        assert log.user_id == "user-001"
        assert log.action == ActionType.SEARCH
        assert log.query == "remote work policy"
        assert log.result_count == 10
        assert Agency.DMV in log.agencies

    @pytest.mark.asyncio
    async def test_log_view_action(self, audit_service):
        """Test logging a view action."""
        log = await audit_service.log_view(
            user_id="user-001",
            document_id="doc-001",
            agency=Agency.DMV,
            classification="internal",
        )

        assert log is not None
        assert log.action == ActionType.VIEW
        assert log.document_id == "doc-001"
        assert "doc-001" in log.documents_accessed

    @pytest.mark.asyncio
    async def test_log_export_action(self, audit_service):
        """Test logging an export action."""
        log = await audit_service.log_export(
            user_id="user-001",
            export_format="csv",
            document_ids=["doc-001", "doc-002", "doc-003"],
        )

        assert log is not None
        assert log.action == ActionType.EXPORT
        assert log.export_format == "csv"
        assert log.result_count == 3

    @pytest.mark.asyncio
    async def test_query_logs_by_user(self, audit_service):
        """Test querying logs by user."""
        # Create some logs
        await audit_service.log_search(
            user_id="user-001",
            query="test query",
            agencies=[Agency.DMV],
            result_count=5,
        )

        filters = AuditLogFilter(user_id="user-001")
        logs, total = await audit_service.get_logs(filters)

        assert total >= 1
        assert all(log.user_id == "user-001" for log in logs)

    @pytest.mark.asyncio
    async def test_query_logs_by_action(self, audit_service):
        """Test querying logs by action type."""
        await audit_service.log_view(
            user_id="user-001",
            document_id="doc-001",
            agency=Agency.DMV,
            classification="public",
        )

        filters = AuditLogFilter(action=ActionType.VIEW)
        logs, total = await audit_service.get_logs(filters)

        assert all(log.action == ActionType.VIEW for log in logs)

    @pytest.mark.asyncio
    async def test_export_json(self, audit_service):
        """Test JSON export."""
        await audit_service.log_search(
            user_id="user-001",
            query="test",
            agencies=[Agency.DMV],
            result_count=1,
        )

        from src.models.audit import AuditExportRequest
        export_request = AuditExportRequest(format="json")
        content = await audit_service.export_logs(export_request)

        assert content is not None
        import json
        data = json.loads(content)
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_export_csv(self, audit_service):
        """Test CSV export."""
        await audit_service.log_search(
            user_id="user-001",
            query="test",
            agencies=[Agency.DMV],
            result_count=1,
        )

        from src.models.audit import AuditExportRequest
        export_request = AuditExportRequest(format="csv")
        content = await audit_service.export_logs(export_request)

        assert content is not None
        assert "id,action,timestamp" in content

    @pytest.mark.asyncio
    async def test_get_user_stats(self, audit_service):
        """Test getting user statistics."""
        # Create multiple logs
        await audit_service.log_search(
            user_id="stats-user",
            query="query1",
            agencies=[Agency.DMV],
            result_count=5,
        )
        await audit_service.log_search(
            user_id="stats-user",
            query="query2",
            agencies=[Agency.DOL],
            result_count=3,
        )

        stats = await audit_service.get_user_stats("stats-user")

        assert stats["user_id"] == "stats-user"
        assert stats["total_actions"] >= 2
        assert stats["searches"] >= 2
