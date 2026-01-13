"""
InteractionLog and UserFeedback models for Constituent Services Agent.

These models support LOADinG Act compliance audit trail and
constituent feedback collection.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class InteractionLog(BaseModel):
    """
    Audit record for LOADinG Act compliance.

    Records immutable audit data for each agent interaction,
    including query/response hashes and token usage.
    """

    id: UUID = Field(default_factory=uuid4, description="Log entry unique identifier")
    message_id: UUID = Field(description="Foreign key to Message")
    query_hash: str = Field(description="SHA-256 hash of user query")
    response_hash: str = Field(description="SHA-256 hash of response")
    model_version: str = Field(description="GPT model identifier")
    latency_ms: int = Field(ge=0, description="End-to-end processing time in ms")
    token_count_input: int = Field(ge=0, description="Input tokens consumed")
    token_count_output: int = Field(ge=0, description="Output tokens generated")
    sources_count: int = Field(ge=0, description="Number of citations")
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Computed confidence score"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Log creation time (UTC)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "message_id": "550e8400-e29b-41d4-a716-446655440000",
                "query_hash": "a3f5d8e9c2b1a4f7e6d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5",
                "response_hash": "b4e6f9a0c3d2b5e8f7a6c9d0b3e4f5a2c1d0e9f8a7b6c5d4",
                "model_version": "gpt-4-turbo-2024-04-09",
                "latency_ms": 2350,
                "token_count_input": 450,
                "token_count_output": 280,
                "sources_count": 3,
                "confidence_score": 0.85,
                "created_at": "2026-01-12T10:30:15Z",
            }
        }
    }


class UserFeedback(BaseModel):
    """
    Optional constituent feedback on responses.

    Collects satisfaction ratings and optional comments
    for continuous improvement.
    """

    id: UUID = Field(default_factory=uuid4, description="Feedback unique identifier")
    message_id: UUID = Field(description="Foreign key to Message")
    rating: int = Field(ge=1, le=5, description="1-5 star rating")
    helpful: Optional[bool] = Field(
        default=None,
        description="Was the response helpful?"
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional text feedback"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Feedback time (UTC)"
    )

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Ensure rating is 1-5."""
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
                "message_id": "550e8400-e29b-41d4-a716-446655440000",
                "rating": 4,
                "helpful": True,
                "comment": "Very clear explanation of the application process.",
                "created_at": "2026-01-12T10:35:00Z",
            }
        }
    }
