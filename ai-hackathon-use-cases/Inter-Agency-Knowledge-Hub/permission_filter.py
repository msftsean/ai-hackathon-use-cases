"""Entra ID integration for document-level security"""
from azure.identity import DefaultAzureCredential
from typing import Optional
import os


class EntraPermissionFilter:
    """Permission filtering based on Entra ID group membership"""

    # Mapping of Entra ID groups to agency access
    GROUP_AGENCY_MAPPING = {
        "NYS-DMV-Staff": ["DMV"],
        "NYS-DOL-Staff": ["DOL"],
        "NYS-OTDA-Staff": ["OTDA"],
        "NYS-DOH-Staff": ["DOH"],
        "NYS-OGS-Staff": ["OGS"],
        "NYS-All-Agencies": ["DMV", "DOL", "OTDA", "DOH", "OGS"],
        "NYS-Social-Services": ["OTDA", "DOH"],
        "NYS-Admin-Services": ["DMV", "OGS"]
    }

    def __init__(self, tenant_id: str, client_id: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.credential = DefaultAzureCredential()

    def get_user_permissions(self, user_token: str) -> list[str]:
        """
        Get list of agencies user can access based on Entra ID groups

        Args:
            user_token: User's access token from Entra ID

        Returns:
            List of agency codes user can access
        """
        # In production, this would decode the token and check group claims
        # For now, return a placeholder that would be replaced with actual implementation
        from msgraph import GraphServiceClient

        graph_client = GraphServiceClient(self.credential)

        # Get user's group memberships
        groups = graph_client.me.member_of.get()

        permitted_agencies = set()
        for group in groups.value:
            group_name = group.display_name
            if group_name in self.GROUP_AGENCY_MAPPING:
                permitted_agencies.update(self.GROUP_AGENCY_MAPPING[group_name])

        return list(permitted_agencies)

    def filter_documents(
        self,
        documents: list[dict],
        user_permissions: list[str]
    ) -> list[dict]:
        """
        Filter documents based on user permissions

        Args:
            documents: List of documents with 'agency' field
            user_permissions: List of agencies user can access

        Returns:
            Filtered list of documents
        """
        return [
            doc for doc in documents
            if doc.get("agency") in user_permissions
        ]


class MockEntraPermissionFilter:
    """Mock implementation for offline development"""

    GROUP_AGENCY_MAPPING = {
        "NYS-DMV-Staff": ["DMV"],
        "NYS-DOL-Staff": ["DOL"],
        "NYS-OTDA-Staff": ["OTDA"],
        "NYS-DOH-Staff": ["DOH"],
        "NYS-OGS-Staff": ["OGS"],
        "NYS-All-Agencies": ["DMV", "DOL", "OTDA", "DOH", "OGS"],
        "NYS-Social-Services": ["OTDA", "DOH"],
        "NYS-Admin-Services": ["DMV", "OGS"]
    }

    # Mock users for testing
    MOCK_USERS = {
        "alice@nys.gov": ["NYS-All-Agencies"],
        "bob@dmv.ny.gov": ["NYS-DMV-Staff"],
        "carol@dol.ny.gov": ["NYS-DOL-Staff"],
        "dave@social.ny.gov": ["NYS-Social-Services"],
        "eve@admin.ny.gov": ["NYS-Admin-Services"]
    }

    def __init__(self, tenant_id: str = None, client_id: str = None):
        pass

    def get_user_permissions(self, user_email: str) -> list[str]:
        """
        Mock permission lookup for testing

        Args:
            user_email: User's email address

        Returns:
            List of agency codes user can access
        """
        groups = self.MOCK_USERS.get(user_email, [])

        permitted_agencies = set()
        for group in groups:
            if group in self.GROUP_AGENCY_MAPPING:
                permitted_agencies.update(self.GROUP_AGENCY_MAPPING[group])

        return list(permitted_agencies)

    def filter_documents(
        self,
        documents: list[dict],
        user_permissions: list[str]
    ) -> list[dict]:
        """Filter documents based on user permissions"""
        return [
            doc for doc in documents
            if doc.get("agency") in user_permissions
        ]


def get_permission_filter(use_mock: bool = False) -> EntraPermissionFilter:
    """Factory function to get appropriate permission filter"""
    if use_mock or os.getenv("USE_MOCK_SERVICES", "false").lower() == "true":
        return MockEntraPermissionFilter()

    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")

    if not tenant_id or not client_id:
        print("Warning: Azure credentials not found, using mock permission filter")
        return MockEntraPermissionFilter()

    return EntraPermissionFilter(tenant_id, client_id)
