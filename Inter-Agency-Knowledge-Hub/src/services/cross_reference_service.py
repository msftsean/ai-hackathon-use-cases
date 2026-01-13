"""Cross-reference service for Inter-Agency Knowledge Hub."""

import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..config import get_settings
from ..core.search_engine import get_search_engine, BaseSearchEngine
from ..core.permission_filter import PermissionFilter
from ..core.citation_builder import CitationBuilder
from ..models.cross_reference import (
    CrossReference,
    CrossReferenceRequest,
    CrossReferenceResponse,
)
from ..models.enums import Agency, RelationshipType, DocumentClassification
from ..models.user import UserPermissions
from .audit_service import AuditService

logger = logging.getLogger("knowledge_hub")


class CrossReferenceService:
    """Service for finding and managing cross-agency document references."""

    def __init__(
        self,
        search_engine: Optional[BaseSearchEngine] = None,
        audit_service: Optional[AuditService] = None,
    ):
        """Initialize cross-reference service."""
        settings = get_settings()
        self.search_engine = search_engine or get_search_engine()
        self.permission_filter = PermissionFilter()
        self.citation_builder = CitationBuilder()
        self.audit_service = audit_service or AuditService()
        self.min_confidence = settings.cross_ref_min_confidence
        self.max_results = settings.cross_ref_max_results

    async def find_related(
        self,
        request: CrossReferenceRequest,
        permissions: UserPermissions,
        ip_address: str = "",
        session_id: str = "",
    ) -> CrossReferenceResponse:
        """Find documents related to the given document."""
        # Get source document
        source_doc = await self.search_engine.get_document(request.document_id)
        if not source_doc:
            return CrossReferenceResponse(
                document_id=request.document_id,
                source_agency=Agency.DMV,  # Default
                cross_references=[],
                total_found=0,
            )

        source_agency = Agency(source_doc.get("agency", "dmv"))
        source_title = source_doc.get("title", "")

        # Extract keywords from source document
        keywords = source_doc.get("keywords", [])
        content = source_doc.get("content", "")

        # Find related documents using keyword search
        from ..models.search import SearchQuery
        search_query = SearchQuery(
            query=" ".join(keywords[:5]) if keywords else source_title,
            page=1,
            page_size=request.max_results * 2,  # Get extra to filter
        )

        # Filter by requested agencies if specified
        if request.agencies:
            search_query.agencies = request.agencies
        elif not request.include_same_agency:
            # Exclude source agency
            search_query.agencies = [a for a in Agency if a != source_agency]

        # Build security filter
        security_filter = self.permission_filter.build_security_filter(permissions)

        # Execute search
        response = await self.search_engine.search(search_query, security_filter)

        # Build cross-references from results
        cross_refs = []
        for result in response.results:
            # Skip source document
            if result.document_id == request.document_id:
                continue

            # Skip same agency if not requested
            if not request.include_same_agency and result.agency == source_agency:
                continue

            # Calculate confidence based on relevance score
            confidence = result.relevance_score
            if confidence < request.min_confidence:
                continue

            # Classify relationship type
            relationship = self._classify_relationship(
                source_doc, result, confidence
            )

            # Filter by relationship type if specified
            if request.relationship_types and relationship not in request.relationship_types:
                continue

            # Get related document for citation
            related_doc = await self.search_engine.get_document(result.document_id)
            related_citation = None
            if related_doc:
                related_citation = self.citation_builder.build_citation_from_search_hit(related_doc)

            cross_ref = CrossReference(
                id=uuid4(),
                source_document_id=request.document_id,
                source_agency=source_agency,
                related_document_id=result.document_id,
                related_agency=result.agency,
                relationship_type=relationship,
                confidence_score=confidence,
                similarity_score=result.relevance_score,
                explanation=self._generate_explanation(relationship, result),
                related_title=result.title,
                related_snippet=result.snippet,
                related_citation=related_citation,
            )
            cross_refs.append(cross_ref)

            if len(cross_refs) >= request.max_results:
                break

        # Log cross-reference action
        await self.audit_service.log_cross_reference(
            user_id=permissions.user_id,
            document_id=request.document_id,
            related_document_ids=[ref.related_document_id for ref in cross_refs],
            agencies=list({ref.related_agency for ref in cross_refs}),
            user_email=permissions.email,
            ip_address=ip_address,
            session_id=session_id,
        )

        return CrossReferenceResponse(
            document_id=request.document_id,
            document_title=source_title,
            source_agency=source_agency,
            cross_references=cross_refs,
            total_found=len(cross_refs),
        )

    def _classify_relationship(
        self,
        source_doc: dict,
        result,
        confidence: float,
    ) -> RelationshipType:
        """Classify the type of relationship between documents."""
        source_keywords = set(source_doc.get("keywords", []))
        result_keywords = set(result.citation.title.lower().split())

        # Check for keyword overlap
        keyword_overlap = len(source_keywords & result_keywords)

        # Check for same document type
        source_type = source_doc.get("document_type", "")
        result_type = result.document_type

        # Check for version relationship
        source_title = source_doc.get("title", "").lower()
        result_title = result.title.lower()

        # Supersedes: similar titles, different versions
        if source_title.replace("v2", "").replace("v1", "") == result_title.replace("v2", "").replace("v1", ""):
            return RelationshipType.SUPERSEDES

        # Similar topic: high keyword overlap
        if keyword_overlap >= 3 or confidence > 0.8:
            return RelationshipType.SIMILAR_TOPIC

        # Dependency: referenced in content
        if result.document_id in source_doc.get("content", ""):
            return RelationshipType.DEPENDENCY

        # Default to related
        return RelationshipType.RELATED

    def _generate_explanation(
        self,
        relationship: RelationshipType,
        result,
    ) -> str:
        """Generate explanation for the relationship."""
        explanations = {
            RelationshipType.SIMILAR_TOPIC: f"Covers similar topics related to {result.title}",
            RelationshipType.DEPENDENCY: f"Referenced by or references {result.title}",
            RelationshipType.SUPERSEDES: f"May be an updated version of {result.title}",
            RelationshipType.CONFLICT: f"May have conflicting information with {result.title}",
            RelationshipType.RELATED: f"Related policy from {result.agency.full_name}",
        }
        return explanations.get(relationship, "Related document")

    async def get_cross_agency_summary(
        self,
        permissions: UserPermissions,
    ) -> dict:
        """Get a summary of cross-agency document relationships."""
        # In production, this would aggregate from a relationship index
        return {
            "total_relationships": 150,
            "by_relationship_type": {
                RelationshipType.SIMILAR_TOPIC.value: 80,
                RelationshipType.DEPENDENCY.value: 30,
                RelationshipType.SUPERSEDES.value: 15,
                RelationshipType.RELATED.value: 25,
            },
            "by_agency_pair": [
                {"agencies": ["dmv", "dol"], "count": 25},
                {"agencies": ["dol", "otda"], "count": 20},
                {"agencies": ["doh", "ogs"], "count": 15},
            ],
        }
