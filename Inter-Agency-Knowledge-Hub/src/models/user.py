"""User models for Inter-Agency Knowledge Hub."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import Agency, DocumentClassification


class UserPermissions(BaseModel):
    """User permissions derived from Entra ID groups."""

    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    display_name: str = Field(default="", description="User display name")
    groups: list[str] = Field(default_factory=list, description="Entra ID group memberships")
    agencies: list[Agency] = Field(
        default_factory=list,
        description="Agencies the user has access to",
    )
    max_classification: DocumentClassification = Field(
        default=DocumentClassification.PUBLIC,
        description="Maximum document classification level accessible",
    )
    is_admin: bool = Field(default=False, description="Whether user is an admin")
    is_reviewer: bool = Field(default=False, description="Whether user can review flagged queries")
    cached_at: datetime = Field(
        default_factory=datetime.now,
        description="When permissions were cached",
    )

    @classmethod
    def from_groups(cls, user_id: str, email: str, groups: list[str], display_name: str = "") -> "UserPermissions":
        """Create UserPermissions from Entra ID groups."""
        agencies = []
        max_classification = DocumentClassification.PUBLIC
        is_admin = False
        is_reviewer = False

        # Parse group memberships
        for group in groups:
            group_lower = group.lower()

            # Check for all-agency access
            if "allagencies" in group_lower:
                agencies = list(Agency)
                if "admin" in group_lower:
                    is_admin = True
                    max_classification = DocumentClassification.CONFIDENTIAL
                elif "manager" in group_lower:
                    max_classification = DocumentClassification.RESTRICTED
                elif "staff" in group_lower:
                    max_classification = DocumentClassification.INTERNAL
                continue

            # Check for specific agency access
            for agency in Agency:
                if agency.value in group_lower:
                    if agency not in agencies:
                        agencies.append(agency)

                    if "admin" in group_lower:
                        is_admin = True
                        max_classification = DocumentClassification.CONFIDENTIAL
                    elif "manager" in group_lower:
                        if max_classification.access_level < DocumentClassification.RESTRICTED.access_level:
                            max_classification = DocumentClassification.RESTRICTED
                    elif "staff" in group_lower:
                        if max_classification.access_level < DocumentClassification.INTERNAL.access_level:
                            max_classification = DocumentClassification.INTERNAL

            # Check for reviewer role
            if "reviewer" in group_lower or "compliance" in group_lower:
                is_reviewer = True

        return cls(
            user_id=user_id,
            email=email,
            display_name=display_name,
            groups=groups,
            agencies=agencies,
            max_classification=max_classification,
            is_admin=is_admin,
            is_reviewer=is_reviewer,
        )

    def can_access_document(self, agency: Agency, classification: DocumentClassification) -> bool:
        """Check if user can access a document."""
        # Check agency access
        if agency not in self.agencies and not self.is_admin:
            return False

        # Check classification level
        return classification.access_level <= self.max_classification.access_level

    def build_security_filter(self) -> str:
        """Build Azure AI Search OData filter for user's permissions."""
        if self.is_admin:
            # Admins see everything
            return ""

        filters = []

        # Filter by agency
        if self.agencies:
            agency_values = [f"'{a.value}'" for a in self.agencies]
            filters.append(f"agency in ({', '.join(agency_values)})")

        # Filter by classification
        allowed_classifications = [
            c.value for c in DocumentClassification
            if c.access_level <= self.max_classification.access_level
        ]
        class_values = [f"'{c}'" for c in allowed_classifications]
        filters.append(f"classification in ({', '.join(class_values)})")

        # Filter by group membership
        if self.groups:
            group_filters = " or ".join(
                f"allowed_groups/any(g: g eq '{group}')" for group in self.groups
            )
            filters.append(f"({group_filters} or classification eq 'public')")

        return " and ".join(filters) if filters else ""


class UserSession(BaseModel):
    """User session information."""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    ip_address: str = Field(default="", description="Client IP address")
    user_agent: str = Field(default="", description="Client user agent")
    started_at: datetime = Field(
        default_factory=datetime.now,
        description="Session start time",
    )
    last_activity: datetime = Field(
        default_factory=datetime.now,
        description="Last activity timestamp",
    )
    permissions: Optional[UserPermissions] = Field(
        default=None,
        description="Cached user permissions",
    )
