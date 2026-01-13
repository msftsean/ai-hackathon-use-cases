"""Review service for human-in-the-loop functionality."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from ..config import get_settings
from ..db.database import get_database
from ..models.review import (
    ReviewFlag,
    ReviewCriteria,
    ReviewCriteriaConfig,
    ReviewUpdateRequest,
    ReviewStatus,
    ReviewPendingResponse,
)
from ..models.search import SearchQuery, SearchResponse
from ..models.user import UserPermissions
from ..models.enums import Agency

logger = logging.getLogger("knowledge_hub")


class ReviewService:
    """Service for flagging and reviewing complex queries."""

    def __init__(self):
        """Initialize review service."""
        settings = get_settings()
        self.criteria_path = settings.review_criteria_path
        self._criteria_config: Optional[ReviewCriteriaConfig] = None
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Ensure service is initialized."""
        if not self._initialized:
            await get_database()
            self._load_criteria()
            self._initialized = True

    def _load_criteria(self) -> None:
        """Load review criteria from configuration file."""
        criteria_path = Path(self.criteria_path)
        if criteria_path.exists():
            try:
                with open(criteria_path) as f:
                    data = json.load(f)
                self._criteria_config = ReviewCriteriaConfig(**data)
                logger.info(f"Loaded {len(self._criteria_config.criteria)} review criteria")
            except Exception as e:
                logger.error(f"Error loading review criteria: {e}")
                self._criteria_config = ReviewCriteriaConfig.default_config()
        else:
            logger.info("Using default review criteria")
            self._criteria_config = ReviewCriteriaConfig.default_config()

    def should_flag_query(
        self,
        query: SearchQuery,
        response: SearchResponse,
        permissions: UserPermissions,
    ) -> tuple[bool, list[str]]:
        """Check if a query should be flagged for review."""
        if not self._criteria_config:
            self._load_criteria()

        triggered_criteria = []

        for criteria in self._criteria_config.criteria:
            if not criteria.enabled:
                continue

            # Check multi-agency threshold
            if query.agencies and len(query.agencies) >= criteria.multi_agency_threshold:
                triggered_criteria.append(f"multi_agency: {len(query.agencies)} agencies")

            # Check sensitive keywords
            query_lower = query.query.lower()
            for keyword in criteria.sensitive_keywords:
                if keyword.lower() in query_lower:
                    triggered_criteria.append(f"sensitive_keyword: {keyword}")
                    break

            # Check low confidence (based on result scores)
            if response.results:
                avg_confidence = sum(r.relevance_score for r in response.results) / len(response.results)
                if avg_confidence < criteria.min_confidence_threshold:
                    triggered_criteria.append(f"low_confidence: {avg_confidence:.2f}")

            # Check flagged topics
            for topic in criteria.flagged_topics:
                if topic.lower() in query_lower:
                    triggered_criteria.append(f"flagged_topic: {topic}")
                    break

        should_flag = len(triggered_criteria) > 0
        return should_flag, triggered_criteria

    async def flag_query(
        self,
        query: SearchQuery,
        response: SearchResponse,
        permissions: UserPermissions,
        triggered_criteria: list[str],
    ) -> ReviewFlag:
        """Create a review flag for a query."""
        await self._ensure_initialized()

        flag = ReviewFlag(
            id=uuid4(),
            query=query.query,
            user_id=permissions.user_id,
            user_email=permissions.email,
            status=ReviewStatus.PENDING,
            flag_reason="; ".join(triggered_criteria),
            flag_criteria=triggered_criteria,
            agencies_involved=query.agencies or list(Agency),
            confidence_score=sum(r.relevance_score for r in response.results) / len(response.results) if response.results else 0.0,
            original_results=[
                {
                    "document_id": r.document_id,
                    "title": r.title,
                    "agency": r.agency.value,
                    "score": r.relevance_score,
                }
                for r in response.results
            ],
        )

        # Store in database
        db = await get_database()
        await db.execute(
            """
            INSERT INTO review_flags (
                id, query, user_id, user_email, status, flag_reason,
                flag_criteria, agencies_involved, confidence_score,
                flagged_at, original_results
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(flag.id),
                flag.query,
                flag.user_id,
                flag.user_email,
                flag.status.value,
                flag.flag_reason,
                json.dumps(flag.flag_criteria),
                ",".join(a.value for a in flag.agencies_involved),
                flag.confidence_score,
                flag.flagged_at.isoformat(),
                json.dumps(flag.original_results),
            ),
        )
        await db.commit()

        logger.info(f"Flagged query '{query.query}' for review: {flag.id}")
        return flag

    async def get_pending_reviews(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ReviewFlag], int]:
        """Get pending reviews for administrators."""
        await self._ensure_initialized()
        db = await get_database()

        # Get total count
        count_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM review_flags WHERE status = 'pending'"
        )
        total = count_result["count"] if count_result else 0

        # Get pending reviews
        rows = await db.fetch_all(
            """
            SELECT * FROM review_flags
            WHERE status = 'pending'
            ORDER BY flagged_at ASC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        flags = [self._row_to_flag(row) for row in rows]
        return flags, total

    async def get_review(self, flag_id: str) -> Optional[ReviewFlag]:
        """Get a specific review flag."""
        await self._ensure_initialized()
        db = await get_database()

        row = await db.fetch_one(
            "SELECT * FROM review_flags WHERE id = ?",
            (flag_id,),
        )

        return self._row_to_flag(row) if row else None

    async def update_review(
        self,
        flag_id: str,
        update: ReviewUpdateRequest,
        reviewer_id: str,
    ) -> Optional[ReviewFlag]:
        """Update a review flag status."""
        await self._ensure_initialized()
        db = await get_database()

        # Verify flag exists
        existing = await self.get_review(flag_id)
        if not existing:
            return None

        # Update flag
        await db.execute(
            """
            UPDATE review_flags
            SET status = ?, reviewer_id = ?, reviewer_notes = ?,
                modified_response = ?, reviewed_at = ?
            WHERE id = ?
            """,
            (
                update.status.value,
                reviewer_id,
                update.reviewer_notes,
                update.modified_response,
                datetime.now().isoformat(),
                flag_id,
            ),
        )
        await db.commit()

        logger.info(f"Review {flag_id} updated to {update.status.value} by {reviewer_id}")
        return await self.get_review(flag_id)

    async def get_review_stats(self) -> dict:
        """Get review statistics."""
        await self._ensure_initialized()
        db = await get_database()

        stats = await db.fetch_one(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'modified' THEN 1 ELSE 0 END) as modified,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM review_flags
            """
        )

        return {
            "total": stats["total"] if stats else 0,
            "pending": stats["pending"] if stats else 0,
            "approved": stats["approved"] if stats else 0,
            "modified": stats["modified"] if stats else 0,
            "rejected": stats["rejected"] if stats else 0,
        }

    def _row_to_flag(self, row: dict) -> ReviewFlag:
        """Convert database row to ReviewFlag."""
        return ReviewFlag(
            id=row["id"],
            query=row["query"],
            user_id=row["user_id"],
            user_email=row.get("user_email", ""),
            status=ReviewStatus(row["status"]),
            flag_reason=row["flag_reason"],
            flag_criteria=json.loads(row.get("flag_criteria", "[]")),
            agencies_involved=[Agency(a) for a in row.get("agencies_involved", "").split(",") if a],
            confidence_score=row.get("confidence_score", 0.0),
            flagged_at=datetime.fromisoformat(row["flagged_at"]),
            reviewed_at=datetime.fromisoformat(row["reviewed_at"]) if row.get("reviewed_at") else None,
            reviewer_id=row.get("reviewer_id"),
            reviewer_notes=row.get("reviewer_notes"),
            modified_response=row.get("modified_response"),
            original_results=json.loads(row.get("original_results", "[]")),
        )

    def get_pending_response(self, flag: ReviewFlag) -> ReviewPendingResponse:
        """Generate a response for a flagged query."""
        return ReviewPendingResponse(
            review_id=str(flag.id),
            message="Your query has been flagged for review due to: " + flag.flag_reason,
            estimated_review_time="24 hours",
            contact_email="knowledge-hub-support@oti.ny.gov",
        )
