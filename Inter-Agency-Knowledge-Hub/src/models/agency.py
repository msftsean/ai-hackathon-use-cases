"""Agency models for Inter-Agency Knowledge Hub."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import Agency


class AgencySource(BaseModel):
    """Information about an agency as a knowledge source."""

    agency: Agency = Field(..., description="Agency identifier")
    name: str = Field(..., description="Full agency name")
    description: str = Field(default="", description="Agency description")
    index_name: str = Field(..., description="Azure AI Search index name")
    document_count: int = Field(default=0, description="Number of indexed documents")
    last_sync: Optional[datetime] = Field(
        default=None,
        description="Last synchronization timestamp",
    )
    base_url: str = Field(default="", description="Agency website base URL")
    contact_email: str = Field(default="", description="Agency contact email")
    enabled: bool = Field(default=True, description="Whether agency is enabled")

    @classmethod
    def from_agency(cls, agency: Agency) -> "AgencySource":
        """Create AgencySource from Agency enum."""
        base_urls = {
            Agency.DMV: "https://dmv.ny.gov",
            Agency.DOL: "https://dol.ny.gov",
            Agency.OTDA: "https://otda.ny.gov",
            Agency.DOH: "https://health.ny.gov",
            Agency.OGS: "https://ogs.ny.gov",
        }

        descriptions = {
            Agency.DMV: "Vehicle registration, driver licensing, and road safety policies",
            Agency.DOL: "Employment, unemployment insurance, and workplace safety policies",
            Agency.OTDA: "Public assistance, disability benefits, and social services policies",
            Agency.DOH: "Public health, healthcare facilities, and medical policies",
            Agency.OGS: "Procurement, facilities management, and administrative policies",
        }

        return cls(
            agency=agency,
            name=agency.full_name,
            description=descriptions.get(agency, ""),
            index_name=agency.index_name,
            base_url=base_urls.get(agency, ""),
        )


class AgencyConfig(BaseModel):
    """Configuration for an agency in the knowledge hub."""

    agency: Agency = Field(..., description="Agency identifier")
    enabled: bool = Field(default=True, description="Whether agency is enabled")
    index_settings: dict = Field(
        default_factory=dict,
        description="Azure AI Search index configuration",
    )
    permission_groups: list[str] = Field(
        default_factory=list,
        description="Entra ID groups for this agency",
    )
    admin_groups: list[str] = Field(
        default_factory=list,
        description="Admin groups for this agency",
    )
    sync_schedule: str = Field(
        default="0 0 * * *",
        description="Cron schedule for document sync",
    )
