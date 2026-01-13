# Research: Inter-Agency Knowledge Hub

**Feature**: 005-inter-agency-knowledge-hub
**Date**: 2026-01-12

## Research Tasks Completed

### 1. Azure AI Search Integration

**Decision**: Azure AI Search SDK (azure-search-documents 11.4.0+) with security filters

**Rationale**:
- Native security trimming support via document-level ACLs
- Built-in semantic ranking for relevance scoring
- Supports multiple indexes for agency separation
- Python SDK well-documented and actively maintained

**Alternatives Considered**:
- Elasticsearch: Requires manual security implementation
- Azure Cognitive Search (legacy): Deprecated in favor of AI Search
- Custom vector search: More complex, less mature for this use case

### 2. Entra ID Authentication

**Decision**: Microsoft Identity (MSAL) with Azure SDK DefaultAzureCredential

**Rationale**:
- Standard Microsoft authentication across NYS agencies
- Supports service principal for server-to-server
- Group membership for permission mapping
- Works seamlessly with Azure AI Search security filters

**Pattern**:
```python
from azure.identity import DefaultAzureCredential
from msal import ConfidentialClientApplication

class EntraAuthenticator:
    def __init__(self, tenant_id: str, client_id: str):
        self.credential = DefaultAzureCredential()
        self.app = ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}"
        )

    def get_user_groups(self, token: str) -> list[str]:
        # Extract group memberships for permission filtering
        pass

    def get_search_filter(self, user_groups: list[str]) -> str:
        # Build Azure AI Search security filter
        return f"permissions/any(p: search.in(p, '{','.join(user_groups)}'))"
```

### 3. Permission Model Design

**Decision**: Group-based permissions with document-level security metadata

**Rationale**:
- Maps directly to Entra ID group memberships
- Supports cross-agency roles (e.g., "AllAgencies_PolicyAnalyst")
- Document indexing includes permissions field
- Filter applied at search time, not post-processing

**Permission Hierarchy**:
```
Agency-Level Groups:
- DMV_Staff, DMV_Manager, DMV_Admin
- DOL_Staff, DOL_Manager, DOL_Admin
- OTDA_Staff, OTDA_Manager, OTDA_Admin
- DOH_Staff, DOH_Manager, DOH_Admin
- OGS_Staff, OGS_Manager, OGS_Admin

Cross-Agency Groups:
- AllAgencies_PolicyAnalyst
- AllAgencies_ComplianceOfficer
- AllAgencies_Executive
- Public (no authentication required for public docs)
```

### 4. Citation Standard

**Decision**: Custom citation format based on government document standards

**Rationale**:
- Meets LOADinG Act requirements
- Includes all required metadata fields
- Machine-readable for export
- Human-readable for display

**Citation Format**:
```python
class DocumentCitation:
    document_id: str          # Unique identifier
    title: str                # Document title
    agency: str               # Source agency (DMV, DOL, etc.)
    publication_date: date    # Original publication
    last_modified: datetime   # Last modification
    document_url: str         # Direct link to source
    version: str              # Document version if applicable
    classification: str       # Public, Internal, Restricted
```

### 5. Cross-Reference Algorithm

**Decision**: Semantic similarity with Azure AI Search vector search + keyword matching

**Rationale**:
- Semantic search captures conceptual relationships
- Keyword matching catches exact policy references
- Configurable threshold for relationship strength
- Can identify potential conflicts via sentiment analysis

**Algorithm**:
```python
def find_cross_references(document_id: str, min_similarity: float = 0.7) -> list[CrossReference]:
    # Get document embedding
    source_doc = get_document(document_id)

    # Vector search for semantically similar documents
    similar_docs = search_index.search(
        vector_queries=[VectorizedQuery(
            vector=source_doc.embedding,
            k_nearest_neighbors=10,
            fields="content_vector"
        )],
        filter=f"document_id ne '{document_id}'"  # Exclude self
    )

    # Classify relationship type
    references = []
    for doc in similar_docs:
        if doc.score >= min_similarity:
            relationship = classify_relationship(source_doc, doc)
            references.append(CrossReference(
                source_id=document_id,
                target_id=doc.document_id,
                relationship_type=relationship,
                confidence=doc.score
            ))

    return references
```

### 6. Human-in-the-Loop Criteria

**Decision**: Rule-based flagging with configurable thresholds

**Rationale**:
- Predictable, auditable flagging criteria
- Administrators can adjust sensitivity
- Supports multiple trigger conditions
- Integrates with existing workflow systems

**Flagging Rules**:
```python
class ReviewCriteria:
    # Flag if query spans more than N agencies with conflicting results
    multi_agency_conflict_threshold: int = 3

    # Flag if query contains sensitive keywords
    sensitive_keywords: list[str] = ["legal", "termination", "lawsuit", "confidential"]

    # Flag if confidence score below threshold
    low_confidence_threshold: float = 0.5

    # Flag if query topic is marked for review
    flagged_topics: list[str] = ["budget", "personnel", "security"]
```

### 7. Web Framework

**Decision**: Flask 3.x with async support (consistent with other hackathon projects)

**Rationale**:
- Consistent with projects 002, 003, 004
- Lightweight, minimal boilerplate
- Easy Blueprint pattern for modular API routes
- Supports async for concurrent search operations

### 8. AI Orchestration

**Decision**: Semantic Kernel 1.37.0 with Foundry IQ integration

**Rationale**:
- Consistent with projects 003, 004
- Native plugin architecture for search plugins
- Supports Azure OpenAI for intelligent summarization
- Foundry IQ integration for document understanding

### 9. Audit Logging

**Decision**: SQLite for local audit logs with async writes, exportable to enterprise systems

**Rationale**:
- Local persistence ensures no audit gaps during network issues
- Async writes don't block search operations
- Standard SQL for easy querying and export
- Can sync to enterprise logging systems

**Audit Schema**:
```python
class AccessLog:
    log_id: str               # UUID
    user_id: str              # Entra ID user principal
    user_groups: list[str]    # Groups at time of access
    query_text: str           # Search query
    document_ids: list[str]   # Documents accessed
    action: str               # "search", "view", "export"
    timestamp: datetime       # UTC timestamp
    ip_address: str           # Client IP
    session_id: str           # Session correlation
```

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle multi-tenant search? | Single index per agency with cross-index queries |
| How to enforce permissions at scale? | Azure AI Search security filters at query time |
| How to track citations? | Standardized citation model in search results |
| How to identify related policies? | Vector similarity + keyword matching |
| How to handle flagged queries? | Database queue with admin notification |

## Dependencies Confirmed

```text
semantic-kernel>=1.37.0
azure-search-documents>=11.4.0
azure-identity>=1.15.0
msal>=1.25.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
flask[async]>=3.0.0
python-dotenv>=1.0.0
pytest>=8.4.2
aiohttp>=3.9.0
aiosqlite>=0.19.0
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Azure AI Search rate limits | Caching, pagination limits |
| Entra ID service unavailability | Cached group memberships (short TTL) |
| Cross-agency permission conflicts | Clear permission hierarchy, admin override |
| Audit log data loss | Local SQLite with sync to enterprise |
| Stale cross-references | Periodic re-indexing job |
