"""Authentication module for Inter-Agency Knowledge Hub."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from ..config import get_settings
from ..models.user import UserPermissions
from ..models.enums import Agency, DocumentClassification

logger = logging.getLogger("knowledge_hub")


class BaseAuthenticator(ABC):
    """Base class for authentication providers."""

    @abstractmethod
    async def validate_token(self, token: str) -> Optional[dict]:
        """Validate a JWT token and return claims."""
        pass

    @abstractmethod
    async def get_user_groups(self, user_id: str) -> list[str]:
        """Get Entra ID groups for a user."""
        pass

    @abstractmethod
    async def get_user_permissions(self, token: str) -> Optional[UserPermissions]:
        """Get user permissions from token."""
        pass


class EntraAuthenticator(BaseAuthenticator):
    """Microsoft Entra ID (Azure AD) authenticator."""

    def __init__(self):
        """Initialize Entra authenticator."""
        settings = get_settings()
        self.tenant_id = settings.azure_tenant_id
        self.client_id = settings.azure_client_id
        self.client_secret = settings.azure_client_secret

        # In production, initialize MSAL client here
        # self.app = msal.ConfidentialClientApplication(...)
        logger.info("Entra authenticator initialized")

    async def validate_token(self, token: str) -> Optional[dict]:
        """Validate JWT token with Entra ID."""
        try:
            # In production, use MSAL to validate token
            # For now, return mock claims if token is present
            if not token or token == "invalid":
                return None

            # Mock token validation
            return {
                "sub": "user-123",
                "email": "user@agency.ny.gov",
                "name": "Test User",
                "groups": ["DMV_Staff", "AllAgencies_Reviewer"],
                "exp": datetime.now().timestamp() + 3600,
            }
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    async def get_user_groups(self, user_id: str) -> list[str]:
        """Get user's Entra ID group memberships."""
        try:
            # In production, call Microsoft Graph API
            # GET /users/{user_id}/memberOf
            return []
        except Exception as e:
            logger.error(f"Error fetching user groups: {e}")
            return []

    async def get_user_permissions(self, token: str) -> Optional[UserPermissions]:
        """Extract user permissions from token."""
        claims = await self.validate_token(token)
        if not claims:
            return None

        return UserPermissions.from_groups(
            user_id=claims.get("sub", ""),
            email=claims.get("email", ""),
            groups=claims.get("groups", []),
            display_name=claims.get("name", ""),
        )


class MockAuthenticator(BaseAuthenticator):
    """Mock authenticator for offline development."""

    # Predefined mock users
    MOCK_USERS = {
        "admin-token": {
            "user_id": "admin-001",
            "email": "admin@oti.ny.gov",
            "name": "System Admin",
            "groups": ["AllAgencies_Admin", "AllAgencies_Reviewer"],
        },
        "dmv-manager-token": {
            "user_id": "dmv-mgr-001",
            "email": "manager@dmv.ny.gov",
            "name": "DMV Manager",
            "groups": ["DMV_Manager", "DMV_Staff"],
        },
        "dmv-staff-token": {
            "user_id": "dmv-staff-001",
            "email": "staff@dmv.ny.gov",
            "name": "DMV Staff Member",
            "groups": ["DMV_Staff"],
        },
        "dol-staff-token": {
            "user_id": "dol-staff-001",
            "email": "staff@dol.ny.gov",
            "name": "DOL Staff Member",
            "groups": ["DOL_Staff"],
        },
        "multi-agency-token": {
            "user_id": "multi-001",
            "email": "analyst@oti.ny.gov",
            "name": "Cross-Agency Analyst",
            "groups": ["DMV_Staff", "DOL_Staff", "DOH_Staff", "AllAgencies_Reviewer"],
        },
        "public-token": {
            "user_id": "public-001",
            "email": "citizen@example.com",
            "name": "Public User",
            "groups": [],
        },
    }

    def __init__(self):
        """Initialize mock authenticator."""
        logger.info("Using mock authenticator for offline development")

    async def validate_token(self, token: str) -> Optional[dict]:
        """Validate token against mock users."""
        if not token:
            return None

        user = self.MOCK_USERS.get(token)
        if user:
            return {
                "sub": user["user_id"],
                "email": user["email"],
                "name": user["name"],
                "groups": user["groups"],
                "exp": datetime.now().timestamp() + 3600,
            }

        # Allow any token starting with "test-" for flexibility
        if token.startswith("test-"):
            return {
                "sub": f"test-user-{token}",
                "email": "test@test.ny.gov",
                "name": "Test User",
                "groups": ["DMV_Staff"],
                "exp": datetime.now().timestamp() + 3600,
            }

        return None

    async def get_user_groups(self, user_id: str) -> list[str]:
        """Get groups for mock user."""
        for user in self.MOCK_USERS.values():
            if user["user_id"] == user_id:
                return user["groups"]
        return []

    async def get_user_permissions(self, token: str) -> Optional[UserPermissions]:
        """Get permissions for mock user."""
        claims = await self.validate_token(token)
        if not claims:
            return None

        return UserPermissions.from_groups(
            user_id=claims.get("sub", ""),
            email=claims.get("email", ""),
            groups=claims.get("groups", []),
            display_name=claims.get("name", ""),
        )


def get_authenticator() -> BaseAuthenticator:
    """Get the appropriate authenticator based on settings."""
    settings = get_settings()
    if settings.use_mock_services:
        return MockAuthenticator()
    return EntraAuthenticator()
