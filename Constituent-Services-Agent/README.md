# Constituent Services Agent

AI-powered conversational agent for NY State constituent services. Provides accurate, citation-backed answers about government services with multi-language support.

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

### 3. Run Web Interface

```bash
python -m src.main
```

Open http://localhost:5000 in your browser.

## Features

- **Basic Q&A**: Ask questions about NY State services in plain language
- **Citation Support**: All responses include source citations
- **Confidence Scoring**: Shows confidence level for responses
- **Escalation**: Offers human agent escalation when confidence is low
- **WCAG 2.1 AA**: Accessible web interface

## Demo Scenarios

Try these queries:

1. "How do I apply for SNAP benefits?"
2. "How do I renew my driver's license?"
3. "How do I file for unemployment?"
4. "Am I eligible for Medicaid?"

## Project Structure

```
Constituent-Services-Agent/
├── src/
│   ├── agent/           # AI agent components
│   ├── api/             # Flask routes
│   ├── config/          # Settings
│   ├── models/          # Data models
│   └── services/        # External integrations
├── static/              # Web interface
├── sample_data/         # Mock agency data
├── tests/               # Test suite
├── demo.py              # Demo script
└── requirements.txt
```

## Configuration

For Azure services, create a `.env` file based on `.env.example`:

```env
USE_MOCK_SERVICES=false

# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Foundry (Optional)
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string
```

**Where to find these values:**
1. Go to [Azure Portal](https://portal.azure.com) → Your Azure OpenAI resource
2. **Keys and Endpoint** → Copy Endpoint and Key
3. **Model deployments** → Note your deployment name (e.g., `gpt-4o`)

## Agency Coverage

- **DMV**: Driver licenses, vehicle registration, REAL ID
- **DOL**: Unemployment insurance, paid family leave
- **OTDA**: SNAP, HEAP, Medicaid

## Hackathon Team

NY State AI Hackathon - January 2026
