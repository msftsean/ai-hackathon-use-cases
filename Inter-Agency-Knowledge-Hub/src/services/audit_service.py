"""Audit service for Inter-Agency Knowledge Hub."""

import csv
import io
import json
import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..db.database import get_database
from ..models.audit import AccessLog, AuditLogFilter, AuditExportRequest
from ..models.enums import ActionType, Agency

logger = logging.getLogger("knowledge_hub")


class AuditService:
    """Service for logging and querying access audit trail."""

    def __init__(self):
        """Initialize audit service."""
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Ensure database is initialized."""
        if not self._initialized:
            await get_database()
            self._initialized = True

    async def log_access(
        self,
        user_id: str,
        action: ActionType,
        user_email: str = "",
        ip_address: str = "",
        session_id: str = "",
        query: Optional[str] = None,
        document_id: Optional[str] = None,
        agencies: Optional[list[Agency]] = None,
        result_count: Optional[int] = None,
        export_format: Optional[str] = None,
        documents_accessed: Optional[list[str]] = None,
        classification_levels: Optional[list[str]] = None,
    ) -> AccessLog:
        """Log an access event."""
        await self._ensure_initialized()

        log_entry = AccessLog(
            id=uuid4(),
            user_id=user_id,
            user_email=user_email,
            action=action,
            timestamp=datetime.now(),
            ip_address=ip_address,
            session_id=session_id,
            query=query,
            document_id=document_id,
            agencies=agencies or [],
            result_count=result_count,
            export_format=export_format,
            documents_accessed=documents_accessed or [],
            classification_levels=classification_levels or [],
        )

        # Store in database
        db = await get_database()
        row = log_entry.to_db_row()

        await db.execute(
            """
            INSERT INTO audit_logs (
                id, user_id, user_email, action, timestamp, ip_address,
                session_id, query, document_id, agencies, result_count,
                export_format, documents_accessed, classification_levels
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["user_id"],
                row["user_email"],
                row["action"],
                row["timestamp"],
                row["ip_address"],
                row["session_id"],
                row["query"],
                row["document_id"],
                row["agencies"],
                row["result_count"],
                row["export_format"],
                row["documents_accessed"],
                row["classification_levels"],
            ),
        )
        await db.commit()

        logger.info(f"Logged {action.value} action for user {user_id}")
        return log_entry

    async def log_search(
        self,
        user_id: str,
        query: str,
        agencies: list[Agency],
        result_count: int,
        user_email: str = "",
        ip_address: str = "",
        session_id: str = "",
        documents_accessed: Optional[list[str]] = None,
    ) -> AccessLog:
        """Log a search action."""
        return await self.log_access(
            user_id=user_id,
            action=ActionType.SEARCH,
            user_email=user_email,
            ip_address=ip_address,
            session_id=session_id,
            query=query,
            agencies=agencies,
            result_count=result_count,
            documents_accessed=documents_accessed,
        )

    async def log_view(
        self,
        user_id: str,
        document_id: str,
        agency: Agency,
        classification: str,
        user_email: str = "",
        ip_address: str = "",
        session_id: str = "",
    ) -> AccessLog:
        """Log a document view action."""
        return await self.log_access(
            user_id=user_id,
            action=ActionType.VIEW,
            user_email=user_email,
            ip_address=ip_address,
            session_id=session_id,
            document_id=document_id,
            agencies=[agency],
            documents_accessed=[document_id],
            classification_levels=[classification],
        )

    async def log_export(
        self,
        user_id: str,
        export_format: str,
        document_ids: list[str],
        user_email: str = "",
        ip_address: str = "",
        session_id: str = "",
    ) -> AccessLog:
        """Log an export action."""
        return await self.log_access(
            user_id=user_id,
            action=ActionType.EXPORT,
            user_email=user_email,
            ip_address=ip_address,
            session_id=session_id,
            export_format=export_format,
            documents_accessed=document_ids,
            result_count=len(document_ids),
        )

    async def log_cross_reference(
        self,
        user_id: str,
        document_id: str,
        related_document_ids: list[str],
        agencies: list[Agency],
        user_email: str = "",
        ip_address: str = "",
        session_id: str = "",
    ) -> AccessLog:
        """Log a cross-reference view action."""
        return await self.log_access(
            user_id=user_id,
            action=ActionType.CROSS_REFERENCE,
            user_email=user_email,
            ip_address=ip_address,
            session_id=session_id,
            document_id=document_id,
            agencies=agencies,
            documents_accessed=related_document_ids,
            result_count=len(related_document_ids),
        )

    async def get_logs(self, filters: AuditLogFilter) -> tuple[list[AccessLog], int]:
        """Query audit logs with filters."""
        await self._ensure_initialized()
        db = await get_database()

        # Build query
        conditions = []
        params = []

        if filters.user_id:
            conditions.append("user_id = ?")
            params.append(filters.user_id)

        if filters.action:
            conditions.append("action = ?")
            params.append(filters.action.value)

        if filters.date_from:
            conditions.append("timestamp >= ?")
            params.append(filters.date_from.isoformat())

        if filters.date_to:
            conditions.append("timestamp <= ?")
            params.append(filters.date_to.isoformat())

        if filters.agency:
            conditions.append("agencies LIKE ?")
            params.append(f"%{filters.agency.value}%")

        if filters.document_id:
            conditions.append("(document_id = ? OR documents_accessed LIKE ?)")
            params.extend([filters.document_id, f"%{filters.document_id}%"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Get total count
        count_sql = f"SELECT COUNT(*) as count FROM audit_logs WHERE {where_clause}"
        count_result = await db.fetch_one(count_sql, tuple(params))
        total = count_result["count"] if count_result else 0

        # Get paginated results
        query_sql = f"""
            SELECT * FROM audit_logs
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """
        params.extend([filters.limit, filters.offset])
        rows = await db.fetch_all(query_sql, tuple(params))

        logs = [AccessLog.from_db_row(row) for row in rows]
        return logs, total

    async def export_logs(self, request: AuditExportRequest) -> str:
        """Export audit logs in the specified format."""
        logs, _ = await self.get_logs(request.filters)

        if request.format == "csv":
            return self._export_csv(logs, request.include_pii)
        else:
            return self._export_json(logs, request.include_pii)

    def _export_json(self, logs: list[AccessLog], include_pii: bool) -> str:
        """Export logs as JSON."""
        data = []
        for log in logs:
            entry = {
                "id": str(log.id),
                "action": log.action.value,
                "timestamp": log.timestamp.isoformat(),
                "agencies": [a.value for a in log.agencies],
                "query": log.query,
                "document_id": log.document_id,
                "result_count": log.result_count,
            }
            if include_pii:
                entry["user_id"] = log.user_id
                entry["user_email"] = log.user_email
                entry["ip_address"] = log.ip_address
            data.append(entry)

        return json.dumps(data, indent=2)

    def _export_csv(self, logs: list[AccessLog], include_pii: bool) -> str:
        """Export logs as CSV."""
        output = io.StringIO()

        fieldnames = ["id", "action", "timestamp", "agencies", "query", "document_id", "result_count"]
        if include_pii:
            fieldnames.extend(["user_id", "user_email", "ip_address"])

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for log in logs:
            row = {
                "id": str(log.id),
                "action": log.action.value,
                "timestamp": log.timestamp.isoformat(),
                "agencies": ",".join(a.value for a in log.agencies),
                "query": log.query or "",
                "document_id": log.document_id or "",
                "result_count": log.result_count or 0,
            }
            if include_pii:
                row["user_id"] = log.user_id
                row["user_email"] = log.user_email
                row["ip_address"] = log.ip_address
            writer.writerow(row)

        return output.getvalue()

    async def get_user_stats(self, user_id: str) -> dict:
        """Get statistics for a user's activity."""
        await self._ensure_initialized()
        db = await get_database()

        stats = await db.fetch_one(
            """
            SELECT
                COUNT(*) as total_actions,
                SUM(CASE WHEN action = 'search' THEN 1 ELSE 0 END) as searches,
                SUM(CASE WHEN action = 'view' THEN 1 ELSE 0 END) as views,
                SUM(CASE WHEN action = 'export' THEN 1 ELSE 0 END) as exports,
                MIN(timestamp) as first_action,
                MAX(timestamp) as last_action
            FROM audit_logs
            WHERE user_id = ?
            """,
            (user_id,),
        )

        return {
            "user_id": user_id,
            "total_actions": stats["total_actions"] if stats else 0,
            "searches": stats["searches"] if stats else 0,
            "views": stats["views"] if stats else 0,
            "exports": stats["exports"] if stats else 0,
            "first_action": stats["first_action"] if stats else None,
            "last_action": stats["last_action"] if stats else None,
        }
