"""ExtractionModel model for tracking Document Intelligence models."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from . import DocumentType


class ExtractionModel(BaseModel):
    """
    Tracks Document Intelligence models used for extraction.
    Maps document types to appropriate Azure AI models.
    """

    # Primary key
    id: UUID = Field(default_factory=uuid4, description="Unique model identifier")

    # Model identification
    name: str = Field(..., description="Model display name")
    model_id: str = Field(..., description="Azure model identifier")

    # Capabilities
    document_types: list[DocumentType] = Field(
        default_factory=list, description="Supported document types"
    )

    # Version tracking
    version: str = Field(..., description="Model version")

    # Performance metrics
    accuracy: Optional[float] = Field(
        default=None, description="Measured accuracy (0.0-1.0)"
    )

    # Model type
    is_prebuilt: bool = Field(
        default=True, description="Whether pre-built or custom trained"
    )
    training_date: Optional[datetime] = Field(
        default=None, description="When custom model was trained"
    )

    # Status
    active: bool = Field(default=True, description="Whether currently used")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return self.model_dump(mode="json")


# Pre-built Azure Document Intelligence models
PREBUILT_MODELS = [
    ExtractionModel(
        name="W-2 Tax Form",
        model_id="prebuilt-tax.us.w2",
        document_types=[DocumentType.W2],
        version="2023-07-31",
        accuracy=0.95,
        is_prebuilt=True,
    ),
    ExtractionModel(
        name="US Driver License",
        model_id="prebuilt-idDocument",
        document_types=[DocumentType.DRIVERS_LICENSE],
        version="2023-07-31",
        accuracy=0.92,
        is_prebuilt=True,
    ),
    ExtractionModel(
        name="General Document",
        model_id="prebuilt-document",
        document_types=[
            DocumentType.PAYSTUB,
            DocumentType.UTILITY_BILL,
            DocumentType.BANK_STATEMENT,
            DocumentType.LEASE_AGREEMENT,
            DocumentType.BIRTH_CERTIFICATE,
            DocumentType.OTHER,
        ],
        version="2023-07-31",
        accuracy=0.88,
        is_prebuilt=True,
    ),
    ExtractionModel(
        name="Layout Analysis",
        model_id="prebuilt-layout",
        document_types=[DocumentType.OTHER],
        version="2023-07-31",
        accuracy=0.90,
        is_prebuilt=True,
    ),
]


def get_model_for_document_type(doc_type: DocumentType) -> ExtractionModel:
    """
    Get the appropriate extraction model for a document type.

    Returns the most specific model available (W-2 model for W-2s,
    ID model for licenses, general document model for others).
    """
    for model in PREBUILT_MODELS:
        if doc_type in model.document_types and model.active:
            return model

    # Fallback to general document model
    return next(
        (m for m in PREBUILT_MODELS if m.model_id == "prebuilt-document"),
        PREBUILT_MODELS[-1],
    )


def get_all_active_models() -> list[ExtractionModel]:
    """Get all active extraction models."""
    return [m for m in PREBUILT_MODELS if m.active]
