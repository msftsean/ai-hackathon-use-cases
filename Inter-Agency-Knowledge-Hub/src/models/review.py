"""Review models for human-in-the-loop functionality."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .enums import Agency, ReviewStatus


class ReviewFlag(BaseModel):
    """Flag for queries requiring human review."""

    id: UUID = Field(default_factory=uuid4, description="Unique flag ID")
    query: str = Field(..., description="Original search query")
    user_id: str = Field(..., description="User who submitted query")
    user_email: str = Field(default="", description="User email")
    status: ReviewStatus = Field(
        default=ReviewStatus.PENDING,
        description="Review status",
    )
    flag_reason: str = Field(..., description="Reason query was flagged")
    flag_criteria: list[str] = Field(
        default_factory=list,
        description="Criteria that triggered the flag",
    )
    agencies_involved: list[Agency] = Field(
        default_factory=list,
        description="Agencies involved in query",
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="System confidence in results",
    )
    flagged_at: datetime = Field(
        default_factory=datetime.now,
        description="When query was flagged",
    )
    reviewed_at: Optional[datetime] = Field(
        default=None,
        description="When review was completed",
    )
    reviewer_id: Optional[str] = Field(default=None, description="Reviewer user ID")
    reviewer_notes: Optional[str] = Field(default=None, description="Reviewer notes")
    modified_response: Optional[str] = Field(
        default=None,
        description="Modified response if status is MODIFIED",
    )
    original_results: list[dict] = Field(
        default_factory=list,
        description="Original search results",
    )

    @property
    def is_pending(self) -> bool:
        """Check if review is pending."""
        return self.status == ReviewStatus.PENDING

    @property
    def review_duration_minutes(self) -> Optional[int]:
        """Calculate review duration in minutes."""
        if self.reviewed_at and self.flagged_at:
            delta = self.reviewed_at - self.flagged_at
            return int(delta.total_seconds() / 60)
        return None


class ReviewCriteria(BaseModel):
    """Configuration for review flagging criteria."""

    name: str = Field(..., description="Criteria name")
    description: str = Field(default="", description="Criteria description")
    enabled: bool = Field(default=True, description="Whether criteria is active")
    priority: int = Field(default=1, ge=1, le=10, description="Priority level")

    # Criteria conditions
    multi_agency_threshold: int = Field(
        default=3,
        description="Flag if query spans this many agencies",
    )
    sensitive_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords that trigger flagging",
    )
    min_confidence_threshold: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="Flag if confidence below this threshold",
    )
    flagged_topics: list[str] = Field(
        default_factory=list,
        description="Topics that require review",
    )


class ReviewCriteriaConfig(BaseModel):
    """Complete review criteria configuration."""

    version: str = Field(default="1.0", description="Config version")
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp",
    )
    criteria: list[ReviewCriteria] = Field(
        default_factory=list,
        description="List of review criteria",
    )

    @classmethod
    def default_config(cls) -> "ReviewCriteriaConfig":
        """Create default review criteria configuration."""
        return cls(
            criteria=[
                ReviewCriteria(
                    name="multi_agency_conflict",
                    description="Query spans multiple agencies with potentially conflicting policies",
                    multi_agency_threshold=3,
                    priority=1,
                ),
                ReviewCriteria(
                    name="sensitive_keywords",
                    description="Query contains sensitive keywords",
                    sensitive_keywords=[
                        "confidential",
                        "restricted",
                        "security",
                        "breach",
                        "investigation",
                        "legal",
                        "lawsuit",
                        "complaint",
                    ],
                    priority=2,
                ),
                ReviewCriteria(
                    name="low_confidence",
                    description="System has low confidence in results",
                    min_confidence_threshold=0.5,
                    priority=3,
                ),
                ReviewCriteria(
                    name="flagged_topics",
                    description="Query involves pre-flagged topics",
                    flagged_topics=[
                        "personnel records",
                        "disciplinary action",
                        "medical information",
                        "financial data",
                    ],
                    priority=1,
                ),
            ]
        )


class ReviewUpdateRequest(BaseModel):
    """Request to update a review flag."""

    status: ReviewStatus = Field(..., description="New review status")
    reviewer_notes: Optional[str] = Field(default=None, description="Reviewer notes")
    modified_response: Optional[str] = Field(
        default=None,
        description="Modified response (required if status is MODIFIED)",
    )


class ReviewPendingResponse(BaseModel):
    """Response when a query is flagged for review."""

    review_id: str = Field(..., description="Review flag ID")
    message: str = Field(
        default="Your query has been flagged for review",
        description="User message",
    )
    estimated_review_time: str = Field(
        default="24 hours",
        description="Estimated time for review",
    )
    contact_email: str = Field(
        default="support@agency.ny.gov",
        description="Contact for inquiries",
    )
