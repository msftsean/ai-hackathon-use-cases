"""Search service for Inter-Agency Knowledge Hub."""

import logging
from typing import Optional

from ..config import get_settings
from ..core.search_engine import get_search_engine, BaseSearchEngine
from ..core.permission_filter import PermissionFilter
from ..core.citation_builder import CitationBuilder
from ..models.search import SearchQuery, SearchResponse, SearchResult
from ..models.user import UserPermissions
from ..models.enums import Agency
from .audit_service import AuditService

logger = logging.getLogger("knowledge_hub")


class SearchService:
    """Orchestration service for search operations."""

    def __init__(
        self,
        search_engine: Optional[BaseSearchEngine] = None,
        audit_service: Optional[AuditService] = None,
    ):
        """Initialize search service."""
        self.search_engine = search_engine or get_search_engine()
        self.permission_filter = PermissionFilter()
        self.citation_builder = CitationBuilder()
        self.audit_service = audit_service or AuditService()

    async def search(
        self,
        query: SearchQuery,
        permissions: UserPermissions,
        ip_address: str = "",
        session_id: str = "",
    ) -> SearchResponse:
        """Execute a search with permission filtering and audit logging."""
        # Check and cache permissions
        cached_perms = self.permission_filter.get_cached_permissions(permissions.user_id)
        if not cached_perms:
            self.permission_filter.cache_permissions(permissions.user_id, permissions)

        # Restrict agencies to those the user can access
        accessible_agencies = self.permission_filter.get_accessible_agencies(permissions)
        if query.agencies:
            # Filter requested agencies to only accessible ones
            query.agencies = [a for a in query.agencies if a in accessible_agencies]
            if not query.agencies:
                # No accessible agencies requested
                logger.warning(f"User {permissions.user_id} requested inaccessible agencies")
                return SearchResponse(
                    query=query.query,
                    results=[],
                    total_results=0,
                    page=query.page,
                    page_size=query.page_size,
                    total_pages=0,
                    agencies_searched=[],
                    suggestions=["You don't have access to the requested agencies"],
                )
        else:
            # Search all accessible agencies
            query.agencies = accessible_agencies

        # Build security filter
        security_filter = self.permission_filter.build_security_filter(permissions)

        # Execute search
        response = await self.search_engine.search(query, security_filter)

        # Post-filter results for additional security
        filtered_results = []
        for result in response.results:
            # Get full document to check permissions
            doc = await self.search_engine.get_document(result.document_id)
            if doc:
                can_access = self.permission_filter.check_document_access(
                    permissions=permissions,
                    agency=Agency(doc.get("agency", "dmv")),
                    classification=doc.get("classification", "public"),
                    allowed_groups=doc.get("allowed_groups", []),
                )
                if can_access:
                    filtered_results.append(result)
            else:
                # Document not found in search engine, include result anyway
                filtered_results.append(result)

        response.results = filtered_results
        response.total_results = len(filtered_results)

        # Log the search
        await self.audit_service.log_search(
            user_id=permissions.user_id,
            query=query.query,
            agencies=response.agencies_searched,
            result_count=response.total_results,
            user_email=permissions.email,
            ip_address=ip_address,
            session_id=session_id,
            documents_accessed=[r.document_id for r in response.results],
        )

        return response

    async def get_document(
        self,
        document_id: str,
        permissions: UserPermissions,
        ip_address: str = "",
        session_id: str = "",
    ) -> Optional[dict]:
        """Get a document with permission checking."""
        doc = await self.search_engine.get_document(document_id)
        if not doc:
            return None

        # Check access
        from ..models.enums import DocumentClassification
        try:
            agency = Agency(doc.get("agency", "dmv"))
            classification = DocumentClassification(doc.get("classification", "public"))
        except ValueError:
            logger.error(f"Invalid agency/classification for document {document_id}")
            return None

        can_access = self.permission_filter.check_document_access(
            permissions=permissions,
            agency=agency,
            classification=classification,
            allowed_groups=doc.get("allowed_groups", []),
        )

        if not can_access:
            logger.warning(
                f"User {permissions.user_id} denied access to document {document_id}"
            )
            return None

        # Log view
        await self.audit_service.log_view(
            user_id=permissions.user_id,
            document_id=document_id,
            agency=agency,
            classification=classification.value,
            user_email=permissions.email,
            ip_address=ip_address,
            session_id=session_id,
        )

        # Redact sensitive fields based on permission level
        return self.permission_filter.redact_sensitive_fields(doc, permissions)

    async def get_search_suggestions(self, partial_query: str) -> list[str]:
        """Get search suggestions for autocomplete."""
        # Simple keyword suggestions based on common terms
        common_terms = [
            "remote work",
            "telework policy",
            "eligibility requirements",
            "procurement procedures",
            "health regulations",
            "driver license",
            "unemployment benefits",
            "disability assistance",
        ]

        partial_lower = partial_query.lower()
        suggestions = [term for term in common_terms if partial_lower in term.lower()]
        return suggestions[:5]

    async def get_popular_searches(self, limit: int = 10) -> list[dict]:
        """Get popular recent searches."""
        # In production, aggregate from search history
        return [
            {"query": "remote work policy", "count": 150},
            {"query": "eligibility requirements", "count": 120},
            {"query": "procurement", "count": 95},
            {"query": "driver license renewal", "count": 80},
            {"query": "unemployment insurance", "count": 75},
        ][:limit]
