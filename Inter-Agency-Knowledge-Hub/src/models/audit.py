"""Audit models for Inter-Agency Knowledge Hub."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .enums import ActionType, Agency


class AccessLog(BaseModel):
    """Access log entry for audit trail."""

    id: UUID = Field(default_factory=uuid4, description="Unique log entry ID")
    user_id: str = Field(..., description="User identifier")
    user_email: str = Field(default="", description="User email")
    action: ActionType = Field(..., description="Type of action performed")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When action occurred",
    )
    ip_address: str = Field(default="", description="Client IP address")
    session_id: str = Field(default="", description="Session identifier")

    # Action-specific fields
    query: Optional[str] = Field(default=None, description="Search query if action is SEARCH")
    document_id: Optional[str] = Field(
        default=None,
        description="Document ID if action is VIEW or CROSS_REFERENCE",
    )
    agencies: list[Agency] = Field(
        default_factory=list,
        description="Agencies involved in the action",
    )
    result_count: Optional[int] = Field(
        default=None,
        description="Number of results if action is SEARCH",
    )
    export_format: Optional[str] = Field(
        default=None,
        description="Export format if action is EXPORT",
    )

    # Compliance metadata
    documents_accessed: list[str] = Field(
        default_factory=list,
        description="List of document IDs accessed",
    )
    classification_levels: list[str] = Field(
        default_factory=list,
        description="Classification levels of accessed documents",
    )

    def to_db_row(self) -> dict:
        """Convert to database row format."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "user_email": self.user_email,
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "session_id": self.session_id,
            "query": self.query,
            "document_id": self.document_id,
            "agencies": ",".join(a.value for a in self.agencies),
            "result_count": self.result_count,
            "export_format": self.export_format,
            "documents_accessed": ",".join(self.documents_accessed),
            "classification_levels": ",".join(self.classification_levels),
        }

    @classmethod
    def from_db_row(cls, row: dict) -> "AccessLog":
        """Create AccessLog from database row."""
        return cls(
            id=UUID(row["id"]),
            user_id=row["user_id"],
            user_email=row.get("user_email", ""),
            action=ActionType(row["action"]),
            timestamp=datetime.fromisoformat(row["timestamp"]),
            ip_address=row.get("ip_address", ""),
            session_id=row.get("session_id", ""),
            query=row.get("query"),
            document_id=row.get("document_id"),
            agencies=[Agency(a) for a in row.get("agencies", "").split(",") if a],
            result_count=row.get("result_count"),
            export_format=row.get("export_format"),
            documents_accessed=row.get("documents_accessed", "").split(",") if row.get("documents_accessed") else [],
            classification_levels=row.get("classification_levels", "").split(",") if row.get("classification_levels") else [],
        )


class AuditLogFilter(BaseModel):
    """Filter criteria for querying audit logs."""

    user_id: Optional[str] = Field(default=None, description="Filter by user ID")
    action: Optional[ActionType] = Field(default=None, description="Filter by action type")
    date_from: Optional[datetime] = Field(default=None, description="Filter by start date")
    date_to: Optional[datetime] = Field(default=None, description="Filter by end date")
    agency: Optional[Agency] = Field(default=None, description="Filter by agency")
    document_id: Optional[str] = Field(default=None, description="Filter by document ID")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Result offset")


class AuditExportRequest(BaseModel):
    """Request for exporting audit logs."""

    format: str = Field(default="json", description="Export format (json or csv)")
    filters: AuditLogFilter = Field(
        default_factory=AuditLogFilter,
        description="Filters to apply",
    )
    include_pii: bool = Field(
        default=False,
        description="Include personally identifiable information",
    )
