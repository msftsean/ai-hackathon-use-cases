"""Permission filtering for Inter-Agency Knowledge Hub."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from ..config import get_settings
from ..models.user import UserPermissions
from ..models.enums import Agency, DocumentClassification

logger = logging.getLogger("knowledge_hub")


class PermissionFilter:
    """Filter search results based on user permissions."""

    def __init__(self):
        """Initialize permission filter."""
        settings = get_settings()
        self.cache_ttl_minutes = settings.permission_cache_ttl_minutes
        self._cache: dict[str, tuple[UserPermissions, datetime]] = {}

    def cache_permissions(self, user_id: str, permissions: UserPermissions) -> None:
        """Cache user permissions."""
        self._cache[user_id] = (permissions, datetime.now())
        logger.debug(f"Cached permissions for user {user_id}")

    def get_cached_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get cached permissions if still valid."""
        if user_id not in self._cache:
            return None

        permissions, cached_at = self._cache[user_id]
        if datetime.now() - cached_at > timedelta(minutes=self.cache_ttl_minutes):
            del self._cache[user_id]
            logger.debug(f"Cache expired for user {user_id}")
            return None

        return permissions

    def invalidate_cache(self, user_id: str) -> None:
        """Invalidate cached permissions for a user."""
        if user_id in self._cache:
            del self._cache[user_id]
            logger.debug(f"Invalidated cache for user {user_id}")

    def build_security_filter(self, permissions: UserPermissions) -> str:
        """Build Azure AI Search OData filter for user's permissions.

        This implements security trimming at the search level to ensure
        users only see documents they're authorized to access.
        """
        if permissions.is_admin:
            # Admins see everything
            logger.debug(f"Admin user {permissions.user_id} - no filter applied")
            return ""

        filters = []

        # Filter by agency access
        if permissions.agencies:
            agency_values = [f"'{a.value}'" for a in permissions.agencies]
            filters.append(f"agency in ({', '.join(agency_values)})")
        else:
            # No agency access - only public documents
            filters.append("classification eq 'public'")

        # Filter by classification level
        allowed_classifications = self._get_allowed_classifications(permissions)
        if allowed_classifications:
            class_values = [f"'{c}'" for c in allowed_classifications]
            filters.append(f"classification in ({', '.join(class_values)})")

        # Filter by group membership for restricted documents
        if permissions.groups:
            group_filters = []
            for group in permissions.groups:
                group_filters.append(f"allowed_groups/any(g: g eq '{group}')")

            # User can see document if:
            # 1. Document is public, OR
            # 2. User is in one of the allowed groups
            filters.append(
                f"(classification eq 'public' or {' or '.join(group_filters)})"
            )

        filter_string = " and ".join(filters) if filters else ""
        logger.debug(f"Built filter for user {permissions.user_id}: {filter_string}")
        return filter_string

    def _get_allowed_classifications(
        self, permissions: UserPermissions
    ) -> list[str]:
        """Get list of classification levels the user can access."""
        allowed = []
        for classification in DocumentClassification:
            if classification.access_level <= permissions.max_classification.access_level:
                allowed.append(classification.value)
        return allowed

    def filter_results(
        self,
        results: list[dict],
        permissions: UserPermissions,
    ) -> list[dict]:
        """Post-filter search results based on permissions.

        This provides a second layer of security after search-time filtering.
        """
        if permissions.is_admin:
            return results

        filtered = []
        for result in results:
            agency_str = result.get("agency", "")
            classification_str = result.get("classification", "public")

            try:
                agency = Agency(agency_str)
                classification = DocumentClassification(classification_str)
            except ValueError:
                # Skip documents with invalid agency/classification
                logger.warning(f"Invalid agency/classification in result: {result.get('id')}")
                continue

            # Check agency access
            if agency not in permissions.agencies and not permissions.is_admin:
                continue

            # Check classification level
            if classification.access_level > permissions.max_classification.access_level:
                continue

            # Check group membership for non-public documents
            if classification != DocumentClassification.PUBLIC:
                allowed_groups = result.get("allowed_groups", [])
                if not any(g in permissions.groups for g in allowed_groups):
                    continue

            filtered.append(result)

        logger.debug(
            f"Filtered {len(results)} results to {len(filtered)} for user {permissions.user_id}"
        )
        return filtered

    def check_document_access(
        self,
        permissions: UserPermissions,
        agency: Agency,
        classification: DocumentClassification,
        allowed_groups: list[str],
    ) -> bool:
        """Check if user can access a specific document."""
        # Admins can access everything
        if permissions.is_admin:
            return True

        # Public documents are accessible to everyone
        if classification == DocumentClassification.PUBLIC:
            return True

        # Check agency access for non-public documents
        if agency not in permissions.agencies:
            return False

        # Check classification level
        if classification.access_level > permissions.max_classification.access_level:
            return False

        # Check group membership
        return any(g in permissions.groups for g in allowed_groups)

    def get_accessible_agencies(self, permissions: UserPermissions) -> list[Agency]:
        """Get list of agencies the user can access."""
        if permissions.is_admin:
            return list(Agency)
        return permissions.agencies

    def redact_sensitive_fields(
        self,
        result: dict,
        permissions: UserPermissions,
    ) -> dict:
        """Redact sensitive fields based on user's permission level."""
        if permissions.is_admin:
            return result

        redacted = result.copy()

        # Redact internal fields for lower permission levels
        if permissions.max_classification.access_level < DocumentClassification.INTERNAL.access_level:
            redacted.pop("internal_notes", None)
            redacted.pop("author_email", None)

        # Redact restricted fields
        if permissions.max_classification.access_level < DocumentClassification.RESTRICTED.access_level:
            redacted.pop("review_history", None)
            redacted.pop("approval_chain", None)

        return redacted
