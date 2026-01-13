# Inter-Agency Knowledge Hub

Cross-agency document search system with permission-aware results for NY State government. Provides unified search across multiple agency knowledge bases with role-based access control.

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Demo (Mock Mode)

No Azure services required:

```bash
python demo.py
```

### 3. Run Tests

```bash
python -m pytest tests/ -v
```

## Features

- **Unified Search**: Query across 5+ agency knowledge bases
- **Permission-Aware Results**: Role-based filtering via Entra ID
- **Citation Tracking**: Source attribution for LOADinG Act compliance
- **Cross-Agency References**: Link related policies across agencies
- **Human-in-the-Loop**: Escalation for complex queries
- **7-Year Audit Logs**: Complete search and access history

## Supported Agencies

| Agency | Domain | Documents |
|--------|--------|-----------|
| DMV | Transportation | Licensing, registration |
| DOL | Labor | Employment, wages |
| OTDA | Social Services | Benefits, assistance |
| DOH | Health | Public health, regulations |
| OGS | General Services | Procurement, facilities |

## Project Structure

```
Inter-Agency-Knowledge-Hub/
├── src/
│   ├── api/             # Flask routes
│   ├── config/          # Settings
│   ├── models/          # Search models
│   ├── services/        # Search, auth services
│   └── plugins/         # Semantic Kernel plugins
├── assets/              # Sample documents
├── data/                # Index data
├── tests/               # Test suite (38 tests)
├── demo.py              # Interactive demo
└── requirements.txt
```

## Search Architecture

```
┌─────────────────────────────────────────┐
│            Search Request               │
│    (Query + User Context + Filters)     │
└───────────────────┬─────────────────────┘
                    │
         ┌──────────▼──────────┐
         │   Permission Check   │
         │   (Entra ID Groups)  │
         └──────────┬──────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌───────┐     ┌───────┐       ┌───────┐
│  DMV  │     │  DOL  │  ...  │  DOH  │
│ Index │     │ Index │       │ Index │
└───────┘     └───────┘       └───────┘
```

## Configuration

For Azure services, create a `.env` file based on `.env.example`:

```env
USE_MOCK_SERVICES=false
AZURE_AI_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_AI_SEARCH_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your-key
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

## Search Modes

| Mode | Description | Best For |
|------|-------------|----------|
| Semantic | Vector similarity search | Natural language queries |
| Keyword | Traditional text matching | Exact phrases |
| Hybrid | Combined semantic + keyword | General use |

## Compliance Features

- **LOADinG Act**: Citation tracking for all AI responses
- **RAISE Act**: Transparent AI assistance disclosure
- **Audit Trail**: Complete 7-year query and access logs
- **Data Privacy**: PII masking in search results

## Tech Stack

- **Azure AI Search**: Vector and hybrid search
- **Foundry IQ**: Intelligent retrieval
- **Entra ID**: Authentication and authorization
- **Semantic Kernel**: AI orchestration
- **Flask**: Web API framework
- **Pydantic**: Data models

## Hackathon Team

NY State AI Hackathon - January 2026
