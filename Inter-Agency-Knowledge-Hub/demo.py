#!/usr/bin/env python3
"""Interactive demonstration of Inter-Agency Knowledge Hub.

This demo showcases:
1. Cross-agency document search
2. Permission-aware result filtering
3. Citation tracking for LOADinG Act compliance
4. Cross-reference identification
5. Human-in-the-loop review flagging
"""

import asyncio
import sys
from datetime import datetime


async def demo_search_service():
    """Demonstrate the search service capabilities."""
    from src.services.search_service import SearchService
    from src.models.search import SearchQuery
    from src.models.user import UserPermissions
    from src.models.enums import Agency

    print("\n" + "=" * 60)
    print("  DEMO: Cross-Agency Search Service")
    print("=" * 60)

    search_service = SearchService()

    # Create mock users with different permission levels
    users = {
        "admin": UserPermissions.from_groups(
            user_id="admin-001",
            email="admin@oti.ny.gov",
            groups=["AllAgencies_Admin"],
            display_name="System Admin",
        ),
        "dmv_staff": UserPermissions.from_groups(
            user_id="dmv-001",
            email="staff@dmv.ny.gov",
            groups=["DMV_Staff"],
            display_name="DMV Staff",
        ),
        "public": UserPermissions.from_groups(
            user_id="public-001",
            email="citizen@example.com",
            groups=[],
            display_name="Public User",
        ),
    }

    # Demo 1: Admin search across all agencies
    print("\n--- Demo 1: Admin Search (All Agencies) ---")
    print("Query: 'remote work policy'")
    print(f"User: {users['admin'].display_name} ({users['admin'].email})")

    query = SearchQuery(query="remote work policy", page_size=5)
    response = await search_service.search(query, users["admin"])

    print(f"\nResults: {response.total_results} documents found")
    print(f"Agencies searched: {[a.value for a in response.agencies_searched]}")
    print(f"Processing time: {response.processing_time_ms}ms")

    for i, result in enumerate(response.results[:3], 1):
        print(f"\n  {i}. {result.title}")
        print(f"     Agency: {result.agency.full_name}")
        print(f"     Score: {result.relevance_score:.2f}")
        print(f"     Citation: {result.citation.citation_format[:80]}...")

    # Demo 2: DMV staff search (limited by permissions)
    print("\n--- Demo 2: DMV Staff Search (Permission-Limited) ---")
    print("Query: 'remote work policy'")
    print(f"User: {users['dmv_staff'].display_name} ({users['dmv_staff'].email})")

    response = await search_service.search(query, users["dmv_staff"])

    print(f"\nResults: {response.total_results} documents found")
    print(f"Agencies accessible: {[a.value for a in users['dmv_staff'].agencies]}")

    # Demo 3: Public user search (public documents only)
    print("\n--- Demo 3: Public User Search (Public Only) ---")
    print("Query: 'eligibility requirements'")
    print(f"User: {users['public'].display_name}")

    query = SearchQuery(query="eligibility requirements")
    response = await search_service.search(query, users["public"])

    print(f"\nResults: {response.total_results} documents found")
    for result in response.results[:2]:
        print(f"  - {result.title} ({result.agency.value})")


async def demo_cross_references():
    """Demonstrate cross-reference service."""
    from src.services.cross_reference_service import CrossReferenceService
    from src.models.cross_reference import CrossReferenceRequest
    from src.models.user import UserPermissions

    print("\n" + "=" * 60)
    print("  DEMO: Cross-Agency Reference Detection")
    print("=" * 60)

    cross_ref_service = CrossReferenceService()

    admin = UserPermissions.from_groups(
        user_id="admin-001",
        email="admin@oti.ny.gov",
        groups=["AllAgencies_Admin"],
    )

    # Find cross-references for DMV remote work policy
    print("\n--- Finding Related Policies for DMV Remote Work Policy ---")

    request = CrossReferenceRequest(
        document_id="dmv-001",
        min_confidence=0.5,
        max_results=5,
    )

    response = await cross_ref_service.find_related(request, admin)

    print(f"\nSource: {response.document_title}")
    print(f"Agency: {response.source_agency.full_name}")
    print(f"Cross-references found: {response.total_found}")
    print(f"Cross-agency references: {response.cross_agency_count}")

    for ref in response.cross_references[:3]:
        print(f"\n  Related: {ref.related_title}")
        print(f"  Agency: {ref.related_agency.full_name}")
        print(f"  Relationship: {ref.relationship_type.value}")
        print(f"  Confidence: {ref.confidence_score:.2f}")
        print(f"  Explanation: {ref.explanation}")


async def demo_review_flagging():
    """Demonstrate human-in-the-loop review flagging."""
    from src.services.review_service import ReviewService
    from src.services.search_service import SearchService
    from src.models.search import SearchQuery, SearchResponse, SearchResult
    from src.models.user import UserPermissions
    from src.models.enums import Agency

    print("\n" + "=" * 60)
    print("  DEMO: Human-in-the-Loop Review Flagging")
    print("=" * 60)

    review_service = ReviewService()
    review_service._load_criteria()

    user = UserPermissions.from_groups(
        user_id="user-001",
        email="user@agency.ny.gov",
        groups=["DMV_Staff", "DOL_Staff", "DOH_Staff"],
    )

    # Demo query that triggers review
    print("\n--- Testing Review Criteria ---")

    # Query 1: Multi-agency query
    query1 = SearchQuery(
        query="confidential personnel records",
        agencies=[Agency.DMV, Agency.DOL, Agency.DOH, Agency.OTDA],
    )

    # Create mock response
    mock_response = SearchResponse(
        query=query1.query,
        results=[],
        agencies_searched=query1.agencies,
    )

    should_flag, criteria = review_service.should_flag_query(query1, mock_response, user)
    print(f"\nQuery: '{query1.query}'")
    print(f"Agencies: {[a.value for a in query1.agencies]}")
    print(f"Flagged: {should_flag}")
    if criteria:
        print(f"Triggered criteria: {criteria}")

    # Query 2: Sensitive keywords
    query2 = SearchQuery(query="security breach investigation")

    should_flag, criteria = review_service.should_flag_query(query2, mock_response, user)
    print(f"\nQuery: '{query2.query}'")
    print(f"Flagged: {should_flag}")
    if criteria:
        print(f"Triggered criteria: {criteria}")

    # Query 3: Normal query (should not be flagged)
    query3 = SearchQuery(query="remote work guidelines")

    should_flag, criteria = review_service.should_flag_query(query3, mock_response, user)
    print(f"\nQuery: '{query3.query}'")
    print(f"Flagged: {should_flag}")


async def demo_permission_filter():
    """Demonstrate permission filtering."""
    from src.core.permission_filter import PermissionFilter
    from src.models.user import UserPermissions
    from src.models.enums import Agency, DocumentClassification

    print("\n" + "=" * 60)
    print("  DEMO: Permission-Based Filtering")
    print("=" * 60)

    filter = PermissionFilter()

    # Different user types
    users = {
        "Admin": UserPermissions.from_groups(
            "admin", "admin@ny.gov", ["AllAgencies_Admin"]
        ),
        "DMV Manager": UserPermissions.from_groups(
            "mgr", "mgr@dmv.ny.gov", ["DMV_Manager"]
        ),
        "DMV Staff": UserPermissions.from_groups(
            "staff", "staff@dmv.ny.gov", ["DMV_Staff"]
        ),
        "Public": UserPermissions.from_groups(
            "public", "citizen@email.com", []
        ),
    }

    print("\n--- User Permission Levels ---")
    for name, perms in users.items():
        print(f"\n{name}:")
        print(f"  Agencies: {[a.value for a in perms.agencies] or ['None (public only)']}")
        print(f"  Max Classification: {perms.max_classification.value}")
        print(f"  Admin: {perms.is_admin}")

    # Test document access
    print("\n--- Document Access Matrix ---")

    test_cases = [
        (Agency.DMV, DocumentClassification.PUBLIC, ["DMV_Staff"]),
        (Agency.DMV, DocumentClassification.INTERNAL, ["DMV_Staff"]),
        (Agency.DMV, DocumentClassification.RESTRICTED, ["DMV_Manager"]),
        (Agency.DMV, DocumentClassification.CONFIDENTIAL, ["DMV_Admin"]),
        (Agency.DOL, DocumentClassification.INTERNAL, ["DOL_Staff"]),
    ]

    print(f"\n{'Document':<40} {'Admin':<8} {'DMV Mgr':<8} {'DMV Staff':<10} {'Public':<8}")
    print("-" * 80)

    for agency, classification, groups in test_cases:
        doc_desc = f"{agency.value.upper()} - {classification.value}"

        access = []
        for name, perms in users.items():
            can_access = filter.check_document_access(perms, agency, classification, groups)
            access.append("Yes" if can_access else "No")

        print(f"{doc_desc:<40} {access[0]:<8} {access[1]:<8} {access[2]:<10} {access[3]:<8}")


async def demo_citation_builder():
    """Demonstrate citation building."""
    from src.core.citation_builder import CitationBuilder
    from src.models.enums import Agency

    print("\n" + "=" * 60)
    print("  DEMO: Citation Building (LOADinG Act Compliance)")
    print("=" * 60)

    builder = CitationBuilder()

    # Build a citation
    citation = builder.build_citation(
        document_id="dmv-policy-001",
        title="Remote Work Policy for DMV Employees",
        agency=Agency.DMV,
        publication_date=datetime(2024, 1, 15),
        version="2.0",
    )

    print("\n--- Citation Formats ---")

    print("\nChicago Style:")
    print(f"  {builder.format_citation(citation, 'chicago')}")

    print("\nAPA Style:")
    print(f"  {builder.format_citation(citation, 'apa')}")

    print("\nMLA Style:")
    print(f"  {builder.format_citation(citation, 'mla')}")

    print("\nPlain Text:")
    print(f"  {builder.format_citation(citation, 'plain')}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  INTER-AGENCY KNOWLEDGE HUB - INTERACTIVE DEMO")
    print("  Cross-Agency Document Search System")
    print("=" * 60)
    print("\nThis demo showcases the key features of the Knowledge Hub:")
    print("  1. Cross-agency search with relevance ranking")
    print("  2. Permission-aware result filtering")
    print("  3. LOADinG Act citation compliance")
    print("  4. Cross-reference detection")
    print("  5. Human-in-the-loop review flagging")

    try:
        await demo_search_service()
        await demo_cross_references()
        await demo_review_flagging()
        await demo_permission_filter()
        await demo_citation_builder()

        print("\n" + "=" * 60)
        print("  DEMO COMPLETE")
        print("=" * 60)
        print("\nTo start the API server, run:")
        print("  python -m src.main")
        print("\nAvailable mock authentication tokens:")
        print("  - admin-token: Full admin access")
        print("  - dmv-staff-token: DMV staff access")
        print("  - multi-agency-token: Multi-agency access")
        print()

    except Exception as e:
        print(f"\nError running demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
