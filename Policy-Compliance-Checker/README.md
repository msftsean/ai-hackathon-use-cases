# Policy Compliance Checker

AI-powered automated review of policy documents against compliance rules for NY State agencies. Analyzes documents for regulation compliance and generates detailed reports with recommendations.

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

- **Document Parsing**: Support for PDF, DOCX, Markdown, and plain text
- **Rule-Based Checking**: Pattern matching with configurable compliance rules
- **AI-Powered Analysis**: Deep content analysis using Azure OpenAI
- **Severity Classification**: Critical, High, Medium, Low categorization
- **Compliance Scoring**: 0-100 score with detailed breakdown
- **Recommendations**: Actionable guidance for each violation
- **Version Comparison**: Track policy changes over time

## Supported Document Types

| Format | Extension | Parser |
|--------|-----------|--------|
| PDF | .pdf | pypdf |
| Word | .docx | python-docx |
| Markdown | .md | Built-in |
| Plain Text | .txt | Built-in |

## Project Structure

```
Policy-Compliance-Checker/
├── src/
│   ├── api/             # Flask routes
│   ├── config/          # Settings
│   ├── models/          # Compliance models
│   ├── services/        # Rule engine, parsing
│   └── plugins/         # Semantic Kernel plugins
├── assets/              # Sample documents
├── tests/               # Test suite (14 tests)
├── demo.py              # Interactive demo
└── requirements.txt
```

## Compliance Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Data Privacy | PII handling rules | Encryption, retention |
| Accessibility | WCAG compliance | Alt text, contrast |
| Security | Security standards | Authentication, logging |
| Documentation | Policy requirements | Version control, approval |

## Configuration

For Azure services, create a `.env` file based on `.env.example`:

```env
USE_MOCK_SERVICES=false

# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Where to find these values:**
1. Go to [Azure Portal](https://portal.azure.com) → Your Azure OpenAI resource
2. **Keys and Endpoint** → Copy Endpoint and Key
3. **Model deployments** → Note your deployment name (e.g., `gpt-4o`)

## Sample Output

```json
{
  "document": "policy-draft.md",
  "compliance_score": 72,
  "violations": [
    {
      "rule": "DATA_RETENTION",
      "severity": "high",
      "location": "Section 3.2",
      "recommendation": "Add data retention period specification"
    }
  ]
}
```

## Tech Stack

- **Azure OpenAI**: AI-powered analysis
- **Semantic Kernel**: AI orchestration
- **pypdf**: PDF parsing
- **python-docx**: Word document parsing
- **Flask**: Web API framework
- **Pydantic**: Data validation

## Hackathon Team

NY State AI Hackathon - January 2026
