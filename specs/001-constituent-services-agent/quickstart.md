# Quick Start: Constituent Services Agent

Get the agent running in 5 minutes for the NY State AI Hackathon.

## Prerequisites

- Python 3.11+
- Git
- (Optional) Azure subscription with AI services

## Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/msftsean/ai-hackathon-use-cases
cd ai-hackathon-use-cases
git checkout nys-hackathon-jan-2026
cd Constituent-Services-Agent
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

### 4. Run with Mock Services (No Azure Required)

```bash
# Set mock mode
set USE_MOCK_SERVICES=true  # Windows
export USE_MOCK_SERVICES=true  # Mac/Linux

# Run demo
python demo.py
```

### 5. Run Web Interface

```bash
python -m src.main
```

Open http://localhost:5000 in your browser.

## Configuration (Optional)

For Azure services, create a `.env` file:

```env
# Azure AI Project
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your-key

# Azure Translator
AZURE_TRANSLATOR_KEY=your-key
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com

# Azure Cosmos DB
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com
COSMOS_KEY=your-key
COSMOS_DATABASE=constituent-agent

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

### Basic Query
```
User: How do I apply for SNAP benefits?
Agent: [Provides application steps with citations to OTDA documentation]
```

### Multi-Language
```
User: ¿Cómo puedo renovar mi licencia de conducir?
Agent: [Responds in Spanish with DMV information]
```

### Low Confidence
```
User: What is the status of my unemployment claim?
Agent: [Offers escalation to human agent since case-specific queries require authentication]
```

## Project Structure

```
Constituent-Services-Agent/
├── src/
│   ├── agent/           # Core AI components
│   ├── models/          # Data models
│   ├── services/        # External integrations
│   ├── api/             # Flask routes
│   └── config/          # Settings
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
├── static/              # Web interface
├── requirements.txt
└── demo.py
```

## Extending for Hackathon

### Add New Agency Content

1. Add JSON file to `sample_data/nys_agencies/`
2. Register in `src/services/knowledge_service.py`
3. Update mock responses in `src/agent/foundry_iq_client.py`

### Add New Language

1. Add language code to `SupportedLanguage` enum
2. Add mock translations in `MockMultilingualAgent`
3. Test with sample queries

### Customize Chat Interface

Edit files in `static/`:
- `index.html` - Layout and structure
- `chat.js` - Interaction logic
- `styles.css` - Appearance

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Azure connection fails
```bash
# Verify credentials
az login
az account show
```

### Mock mode not working
```bash
# Ensure environment variable is set
echo $USE_MOCK_SERVICES  # Should be "true"
```

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Pick tasks matching your team's skills
3. Build, test, and demo!

## Resources

- [Feature Spec](./spec.md) - Full requirements
- [Data Model](./data-model.md) - Entity definitions
- [API Contract](./contracts/api.yaml) - OpenAPI specification
- [Research](./research.md) - Technology decisions
