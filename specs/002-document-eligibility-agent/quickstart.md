# Quick Start: Document Eligibility Agent

Get the document processing agent running in 5 minutes for the NY State AI Hackathon.

## Prerequisites

- Python 3.11+
- Git
- Redis (for processing queue)
- (Optional) Azure subscription with AI services

## Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/msftsean/ai-hackathon-use-cases
cd ai-hackathon-use-cases
git checkout nys-hackathon-jan-2026
cd Document-Eligibility-Agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Redis (for queue)

```bash
# Windows (using Docker)
docker run -d -p 6379:6379 redis:alpine

# Mac
brew install redis
redis-server

# Or skip Redis for mock mode
```

### 5. Run with Mock Services (No Azure Required)

```bash
# Set mock mode
set USE_MOCK_SERVICES=true  # Windows
export USE_MOCK_SERVICES=true  # Mac/Linux

# Run demo
python demo.py
```

### 6. Run Web Interface

```bash
python -m src.main
```

Open http://localhost:5001 in your browser.

## Configuration (Optional)

For Azure services, create a `.env` file:

```env
# Azure Document Intelligence
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com
AZURE_DOC_INTELLIGENCE_KEY=your-key

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER=documents

# Azure Cosmos DB
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com
COSMOS_KEY=your-key
COSMOS_DATABASE=doc-eligibility

# Microsoft Graph (for email)
GRAPH_CLIENT_ID=your-client-id
GRAPH_CLIENT_SECRET=your-secret
GRAPH_TENANT_ID=your-tenant-id
INTAKE_MAILBOX=intake@agency.ny.gov

# Redis
REDIS_URL=redis://localhost:6379/0

# Feature flags
USE_MOCK_SERVICES=false
```

## Testing

```bash
# Run unit tests
python -m pytest tests/unit -v

# Run integration tests (requires Azure)
python -m pytest tests/integration -v

# Run AI evaluations
python tests/evaluation/run_evals.py
```

## Demo Scenarios

### Document Upload
```bash
# Upload a W-2 document
curl -X POST http://localhost:5001/api/v1/documents \
  -F "file=@sample_documents/w2_sample.pdf" \
  -F "case_id=CASE-12345" \
  -F "document_type=w2"
```

### Check Extraction Results
```bash
# Get extraction for document
curl http://localhost:5001/api/v1/extractions/{document_id}
```

### View Queue
```bash
# Get processing queue
curl http://localhost:5001/api/v1/queue?status=ready_for_review
```

## Web Interface Demo Flow

1. **Upload Document**: Click "Upload" and select a sample PDF
2. **View Processing**: Watch status change from "Processing" to "Extracted"
3. **Review Extractions**: See extracted fields with confidence scores
4. **Check Validation**: Review any validation warnings
5. **Approve/Reject**: Complete the review workflow

## Project Structure

```
Document-Eligibility-Agent/
├── src/
│   ├── agent/           # Document processing logic
│   ├── models/          # Data models
│   ├── services/        # Azure service integrations
│   ├── api/             # Flask routes
│   └── config/          # Settings
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
├── static/              # Web interface
├── sample_documents/    # Test fixtures
├── requirements.txt
└── demo.py
```

## Extending for Hackathon

### Add New Document Type

1. Add type to `DocumentType` enum in `src/models/__init__.py`
2. Create field mapping in `src/agent/extraction_agent.py`
3. Add validation rules in `src/agent/validation_agent.py`
4. Add sample document to `sample_documents/`
5. Update mock extractions in `src/services/document_intelligence.py`

### Add Validation Rule

1. Add rule to `ValidationRule` in database/config
2. Implement rule logic in `src/agent/validation_agent.py`
3. Test with sample document

### Customize Queue UI

Edit files in `static/`:
- `index.html` - Layout and structure
- `queue.js` - Queue interaction logic
- `styles.css` - Appearance

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Redis connection fails
```bash
# Check Redis is running
redis-cli ping  # Should return PONG
```

### Document Intelligence errors
```bash
# Verify credentials
az cognitiveservices account keys list --name your-account --resource-group your-rg
```

### Mock mode not working
```bash
# Ensure environment variable is set
echo $USE_MOCK_SERVICES  # Should be "true"
```

## Sample Documents

Test fixtures are provided in `sample_documents/`:
- `w2_sample.pdf` - W-2 tax form
- `paystub_sample.pdf` - Pay stub
- `utility_bill_sample.pdf` - Utility bill

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Pick tasks matching your team's skills
3. Build, test, and demo!

## Resources

- [Feature Spec](./spec.md) - Full requirements
- [Data Model](./data-model.md) - Entity definitions
- [API Contract](./contracts/api.yaml) - OpenAPI specification
- [Research](./research.md) - Technology decisions
