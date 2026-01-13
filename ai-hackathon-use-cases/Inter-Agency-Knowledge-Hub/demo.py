"""Demo script for Inter-Agency Knowledge Hub"""
import argparse
import os
from knowledge_hub import InterAgencyKnowledgeHub, MockInterAgencyKnowledgeHub
from permission_filter import get_permission_filter


def run_demo(use_mock: bool = True):
    """Run interactive demo of the Inter-Agency Knowledge Hub"""

    print("=" * 60)
    print("NY State Inter-Agency Knowledge Hub Demo")
    print("=" * 60)
    print()

    # Initialize components
    if use_mock:
        print("Running with MOCK services (no Azure connection required)")
        hub = MockInterAgencyKnowledgeHub()
        permission_filter = get_permission_filter(use_mock=True)
    else:
        connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        if not connection_string:
            print("Error: AZURE_AI_PROJECT_CONNECTION_STRING not set")
            print("Use --mock flag to run with mock services")
            return
        hub = InterAgencyKnowledgeHub(connection_string)
        permission_filter = get_permission_filter(use_mock=False)

    # Demo users with different permission levels
    demo_users = [
        ("alice@nys.gov", "Full Access User"),
        ("bob@dmv.ny.gov", "DMV Staff"),
        ("carol@dol.ny.gov", "DOL Staff"),
        ("dave@social.ny.gov", "Social Services Staff"),
    ]

    # Demo queries
    demo_queries = [
        "How do I renew my driver's license?",
        "What are the unemployment benefits requirements?",
        "How do I apply for SNAP benefits?",
        "Tell me about workers compensation"
    ]

    print("Demo Users:")
    for email, role in demo_users:
        permissions = permission_filter.get_user_permissions(email)
        print(f"  {email} ({role}): Can access {permissions}")
    print()

    # Interactive mode
    print("Interactive Demo")
    print("-" * 40)
    print("Enter a user email to simulate (or 'alice@nys.gov' for full access)")
    print("Then enter your search query")
    print("Type 'quit' to exit")
    print()

    while True:
        user_email = input("User email: ").strip()
        if user_email.lower() == 'quit':
            break

        if not user_email:
            user_email = "alice@nys.gov"
            print(f"Using default user: {user_email}")

        permissions = permission_filter.get_user_permissions(user_email)
        print(f"User permissions: {permissions}")

        if not permissions:
            print("User has no agency permissions. Try a different user.")
            continue

        query = input("Search query: ").strip()
        if query.lower() == 'quit':
            break

        if not query:
            query = "How do I apply for benefits?"
            print(f"Using default query: {query}")

        print()
        print("Searching...")
        print("-" * 40)

        result = hub.search(
            query=query,
            user_permissions=permissions
        )

        print(f"Query: {result['query']}")
        print(f"Searched agencies: {result['permitted_agencies']}")
        print()
        print("Answer:")
        print(result['answer'])
        print()

        if result['citations']:
            print("Citations:")
            for citation in result['citations']:
                print(f"  - [{citation['agency']}] {citation['file_id']}")
        print()

        if result['cross_references']:
            print("Cross-References:")
            for ref in result['cross_references']:
                print(f"  - {ref['note']}: {ref['agencies']}")
        print()
        print("-" * 40)
        print()


def run_sample_queries(use_mock: bool = True):
    """Run sample queries for quick demonstration"""

    print("=" * 60)
    print("Sample Queries Demo")
    print("=" * 60)
    print()

    if use_mock:
        hub = MockInterAgencyKnowledgeHub()
    else:
        connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        hub = InterAgencyKnowledgeHub(connection_string)

    # Full access user
    permissions = ["DMV", "DOL", "OTDA", "DOH", "OGS"]

    queries = [
        "How do I renew my driver's license?",
        "What are the unemployment filing requirements?",
        "How do I apply for SNAP?",
        "Where can I get birth certificate?"
    ]

    for query in queries:
        print(f"Query: {query}")
        print("-" * 40)

        result = hub.search(query=query, user_permissions=permissions)
        print(result['answer'][:500])
        print()
        print("=" * 60)
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inter-Agency Knowledge Hub Demo")
    parser.add_argument("--mock", action="store_true", default=True,
                        help="Use mock services (default: True)")
    parser.add_argument("--azure", action="store_true",
                        help="Use Azure services (requires credentials)")
    parser.add_argument("--samples", action="store_true",
                        help="Run sample queries instead of interactive mode")

    args = parser.parse_args()

    use_mock = not args.azure

    if args.samples:
        run_sample_queries(use_mock)
    else:
        run_demo(use_mock)
