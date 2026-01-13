# Inter-Agency Knowledge Hub

Cross-agency document search with permission-aware responses using Foundry IQ.

## What it does
- Unified search across multiple NYS agency document repositories
- Permission-aware responses (only shows documents user can access)
- Citation tracking for compliance
- Cross-reference related policies across agencies

## Tech Stack
- Microsoft Foundry with Foundry IQ
- Azure AI Search with security filters
- Semantic Kernel for orchestration
- Entra ID for permission enforcement

## Quick Start
1. `pip install -r requirements.txt`
2. `python setup_knowledge_bases.py`
3. `python demo.py`

## Supported Agencies
- **DMV** - Department of Motor Vehicles
- **DOL** - Department of Labor
- **OTDA** - Office of Temporary and Disability Assistance
- **DOH** - Department of Health
- **OGS** - Office of General Services

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │    │   Knowledge Hub  │    │  Agency Sources │
│                 │    │                  │    │                 │
│ • Search Input  │───►│ • Foundry IQ     │───►│ • DMV Docs      │
│ • User Context  │    │ • Permission     │    │ • DOL Policies  │
│ • Entra ID      │    │   Filtering      │    │ • OTDA Guides   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Response       │
                       │                  │
                       │ • Relevant Docs  │
                       │ • Citations      │
                       │ • Cross-Refs     │
                       └──────────────────┘
```

## Features

### Permission-Aware Search
- Integrates with Entra ID for user authentication
- Applies document-level security filters
- Only returns documents the user is authorized to view

### Citation Tracking
- Every response includes source citations
- Links to original documents
- Supports LOADinG Act compliance requirements

### Cross-Agency References
- Identifies related policies across agencies
- Highlights dependencies and conflicts
- Suggests relevant resources from other agencies

## Configuration

Set the following environment variables:

```bash
# Azure AI Project
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string

# Entra ID
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id

# Azure AI Search
AZURE_SEARCH_ENDPOINT=your-search-endpoint
AZURE_SEARCH_KEY=your-search-key
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run demo with mock services
python demo.py --mock

# Run with Azure services
python demo.py
```

## Responsible AI Considerations

- **Human-in-the-loop**: Complex cross-agency queries are flagged for review
- **Audit Trail**: All searches and document access are logged
- **Bias Testing**: Regular evaluation of search result quality across agencies
- **Transparency**: Clear indication of document sources and access permissions
