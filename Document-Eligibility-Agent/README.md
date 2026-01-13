# Document Eligibility Agent

AI-powered document processing system for NY State social services. Automatically processes eligibility documents (W-2s, pay stubs, utility bills) using Azure Document Intelligence and Semantic Kernel.

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

- **Document OCR**: Extract text from scanned documents using Azure Document Intelligence
- **Intelligent Classification**: Automatically identify document types
- **Data Extraction**: Extract key fields (income, employer, dates)
- **PII Detection**: Automatic detection and masking of sensitive data
- **Confidence Scoring**: Quality metrics for extracted data
- **Eligibility Assessment**: Rule-based benefit calculations

## Supported Document Types

| Document | Fields Extracted |
|----------|-----------------|
| W-2 Forms | Wages, employer, tax year |
| Pay Stubs | Gross pay, pay period, employer |
| Utility Bills | Provider, address, amount due |
| Bank Statements | Institution, balance, transactions |
| Driver's Licenses | Name, DOB, expiration |
| Birth Certificates | Name, DOB, parents |
| Lease Agreements | Landlord, address, rent amount |

## Project Structure

```
Document-Eligibility-Agent/
├── src/
│   ├── agent/           # Processing agents
│   ├── api/             # Flask routes
│   ├── config/          # Settings
│   ├── models/          # Document models
│   ├── services/        # OCR, email, storage services
│   └── plugins/         # Semantic Kernel plugins
├── sample_documents/    # Test documents
├── static/              # Web interface assets
├── tests/               # Test suite (86 tests)
├── demo.py              # Interactive demo
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

# Azure Document Intelligence (Required for OCR)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-doc-intel.cognitiveservices.azure.com
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key
```

**Where to find these values:**
1. **Azure OpenAI**: Azure Portal → Your OpenAI resource → Keys and Endpoint
2. **Document Intelligence**: Azure Portal → Your Document Intelligence resource → Keys and Endpoint
3. **Deployment Name**: Azure AI Studio → Deployments (e.g., `gpt-4o`)

## Eligibility Programs

- **SNAP**: Supplemental Nutrition Assistance Program
- **Medicaid**: Healthcare coverage
- **Housing Assistance**: Rental subsidies
- **HEAP**: Home Energy Assistance Program

## Tech Stack

- **Azure Document Intelligence**: OCR and document parsing
- **Microsoft Graph**: Email processing
- **Semantic Kernel**: AI orchestration
- **Azure OpenAI**: Intelligent extraction
- **Flask**: Web API framework
- **Pydantic**: Data validation

## Hackathon Team

NY State AI Hackathon - January 2026
