"""Database module for Inter-Agency Knowledge Hub."""

import logging
from pathlib import Path
from typing import Optional

import aiosqlite

from ..config import get_settings

logger = logging.getLogger("knowledge_hub")


class Database:
    """SQLite database for audit logs and local storage."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database."""
        settings = get_settings()
        self.db_path = db_path or settings.database_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Connect to the database."""
        # Ensure directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._create_tables()
        logger.info(f"Connected to database at {self.db_path}")

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        if not self._connection:
            return

        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                user_email TEXT,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT,
                session_id TEXT,
                query TEXT,
                document_id TEXT,
                agencies TEXT,
                result_count INTEGER,
                export_format TEXT,
                documents_accessed TEXT,
                classification_levels TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id);
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);

            CREATE TABLE IF NOT EXISTS review_flags (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                user_id TEXT NOT NULL,
                user_email TEXT,
                status TEXT NOT NULL,
                flag_reason TEXT NOT NULL,
                flag_criteria TEXT,
                agencies_involved TEXT,
                confidence_score REAL,
                flagged_at TEXT NOT NULL,
                reviewed_at TEXT,
                reviewer_id TEXT,
                reviewer_notes TEXT,
                modified_response TEXT,
                original_results TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_review_status ON review_flags(status);
            CREATE INDEX IF NOT EXISTS idx_review_flagged_at ON review_flags(flagged_at);

            CREATE TABLE IF NOT EXISTS search_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                query TEXT NOT NULL,
                result_count INTEGER,
                agencies_searched TEXT,
                searched_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_search_user_id ON search_history(user_id);
            CREATE INDEX IF NOT EXISTS idx_search_searched_at ON search_history(searched_at);
        """)
        await self._connection.commit()
        logger.debug("Database tables created/verified")

    async def execute(self, sql: str, params: tuple = ()) -> aiosqlite.Cursor:
        """Execute a SQL statement."""
        if not self._connection:
            await self.connect()
        return await self._connection.execute(sql, params)

    async def execute_many(self, sql: str, params_list: list[tuple]) -> None:
        """Execute a SQL statement with multiple parameter sets."""
        if not self._connection:
            await self.connect()
        await self._connection.executemany(sql, params_list)
        await self._connection.commit()

    async def fetch_one(self, sql: str, params: tuple = ()) -> Optional[dict]:
        """Fetch a single row."""
        cursor = await self.execute(sql, params)
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        """Fetch all rows."""
        cursor = await self.execute(sql, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def commit(self) -> None:
        """Commit current transaction."""
        if self._connection:
            await self._connection.commit()


# Global database instance
_db: Optional[Database] = None


async def get_database() -> Database:
    """Get the database instance."""
    global _db
    if _db is None:
        _db = Database()
        await _db.connect()
    return _db


async def close_database() -> None:
    """Close the database connection."""
    global _db
    if _db:
        await _db.close()
        _db = None
