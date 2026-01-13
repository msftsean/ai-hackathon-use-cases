# Quickstart: Inter-Agency Knowledge Hub

**Feature**: 005-inter-agency-knowledge-hub
**Estimated Setup Time**: 15 minutes

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Azure subscription with:
  - Azure AI Search service
  - Entra ID (Azure AD) tenant
  - Azure AI Project (optional - for Foundry IQ)

## Step 1: Environment Setup

```bash
# Navigate to project directory
cd Inter-Agency-Knowledge-Hub

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Azure Services

Create or edit `.env` file in the project root:

```bash
# Entra ID (Required)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Azure AI Search (Required)
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-admin-key

# Azure AI Project (Optional - for Foundry IQ)
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string

# Azure OpenAI (Optional - for semantic features)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

**Note**: The system works in demo mode without Azure services using mock data.

## Step 3: Setup Knowledge Bases

```bash
# Setup agency indexes with sample data
python setup_knowledge_bases.py

# Or setup with mock data only (no Azure required)
python setup_knowledge_bases.py --mock
```

## Step 4: Verify Installation

```bash
# Run setup tests to verify environment
python -m pytest tests/test_setup.py -v

# Expected output: All tests passing
```

## Step 5: Run the Demo

```bash
# Run interactive demo with mock services
python demo.py --mock

# Or run with Azure services
python demo.py
```

## Step 6: Try the API

```bash
# Start the API server
python src/main.py --api

# In another terminal, test the endpoints:

# Health check (no auth required)
curl http://localhost:5000/api/v1/health

# List agencies
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/v1/agencies

# Search across agencies
curl -X POST http://localhost:5000/api/v1/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "remote work policy"}'

# Get document cross-references
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/v1/documents/{document_id}/cross-references
```

## Quick Examples

### Python API Usage

```python
from src.core.search_engine import SearchEngine
from src.core.permission_filter import PermissionFilter
from src.services.search_service import SearchService

# Initialize services
search_engine = SearchEngine()
permission_filter = PermissionFilter()
search_service = SearchService(search_engine, permission_filter)

# Perform search with user context
results = search_service.search(
    query="employee benefits policy",
    user_groups=["DOL_Staff", "AllAgencies_PolicyAnalyst"],
    agency_filter=["DOL", "OTDA"],
    page=1,
    page_size=20
)

# View results
print(f"Found {results.total_results} documents")
for result in results.results:
    print(f"  [{result.document.agency}] {result.document.title}")
    print(f"    Relevance: {result.relevance_score:.2f}")
    print(f"    URL: {result.document.document_url}")
```

### Get Cross-References

```python
from src.services.cross_reference_service import CrossReferenceService

# Initialize service
xref_service = CrossReferenceService()

# Get related policies
references = xref_service.get_cross_references(
    document_id="doc-uuid-here",
    min_confidence=0.7
)

for ref in references:
    print(f"  [{ref.relationship_type}] {ref.target_document.title}")
    print(f"    Agency: {ref.target_document.agency}")
    print(f"    Confidence: {ref.confidence_score:.2%}")
```

### Audit Log Export

```python
from src.services.audit_service import AuditService
from datetime import date, timedelta

# Initialize service
audit_service = AuditService()

# Export logs for compliance
logs = audit_service.export_logs(
    start_date=date.today() - timedelta(days=30),
    end_date=date.today(),
    format="json"
)

print(f"Exported {len(logs)} access records")
```

## Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test category
python -m pytest tests/test_search.py -v          # Search tests
python -m pytest tests/test_permissions.py -v     # Permission tests
python -m pytest tests/test_audit.py -v           # Audit tests
python -m pytest tests/test_cross_refs.py -v      # Cross-reference tests

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

## Sample Data

Test with provided sample data in `assets/`:

### Agency Configurations (`assets/agency_configs/`)

- `dmv.json` - DMV knowledge base configuration
- `dol.json` - DOL knowledge base configuration
- `otda.json` - OTDA knowledge base configuration
- `doh.json` - DOH knowledge base configuration
- `ogs.json` - OGS knowledge base configuration

### Sample Queries (`assets/sample_queries/`)

- `basic_searches.json` - Simple single-agency queries
- `cross_agency_searches.json` - Multi-agency queries
- `permission_tests.json` - Queries for testing permission filtering

## Troubleshooting

### "Module not found" errors

```bash
# Ensure virtual environment is activated
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Authentication failed" errors

- Verify Entra ID credentials in `.env`
- Check that your Azure AD app has the required API permissions
- Ensure token hasn't expired

### "Search service unavailable" errors

- Verify Azure AI Search endpoint and key in `.env`
- Check that search indexes exist (run `setup_knowledge_bases.py`)
- System continues with mock data if Azure unavailable

### Permission errors

- Verify user groups are correctly populated
- Check document permissions in search index
- Review Entra ID group memberships

## Next Steps

1. Configure your agency's knowledge base
2. Set up Entra ID groups for your organization
3. Index your policy documents
4. Configure human-in-the-loop review criteria
5. Set up audit log export to enterprise systems

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/search | Search across agencies |
| GET | /api/v1/documents/{id} | Get document details |
| GET | /api/v1/documents/{id}/cross-references | Get related policies |
| GET | /api/v1/agencies | List agency sources |
| GET | /api/v1/audit/logs | Get audit logs (admin) |
| POST | /api/v1/audit/logs/export | Export audit logs (admin) |
| GET | /api/v1/reviews | List pending reviews (admin) |
| PUT | /api/v1/reviews/{id} | Update review status (admin) |
| GET | /api/v1/user/permissions | Get current user permissions |
| GET | /api/v1/user/search-history | Get user's search history |
| GET | /api/v1/health | Health check |

## Support

- Run tests to verify setup: `python -m pytest tests/test_setup.py -v`
- Check sample configurations for expected formats
- Review inline code comments and docstrings
