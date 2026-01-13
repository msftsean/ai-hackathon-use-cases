# Quickstart: Policy Compliance Checker

**Feature**: 004-policy-compliance-checker
**Estimated Setup Time**: 10 minutes

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Azure OpenAI API key (optional - fallback mode available)

## Step 1: Environment Setup

```bash
# Navigate to project directory
cd Policy-Compliance-Checker

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

## Step 2: Configure API Keys (Optional)

Create or edit `.env` file in the project root:

```bash
# Azure OpenAI Configuration (Optional - for AI-powered analysis)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Document Intelligence (Optional - for complex PDF layouts)
AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-service.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=your-form-recognizer-key
```

**Note**: The system works without API keys using pattern-based analysis only.

## Step 3: Verify Installation

```bash
# Run setup tests to verify environment
python -m pytest tests/test_setup.py -v

# Expected output: All tests passing
```

## Step 4: Run the Demo

```bash
# Run interactive demo
python demo.py

# Or analyze a specific document
python src/main.py assets/test_documents/employee_code_of_conduct.md
```

## Step 5: Try the API

```bash
# Start the API server
python src/main.py --api

# In another terminal, test the endpoints:

# Health check
curl http://localhost:5000/api/v1/health

# Upload a document
curl -X POST http://localhost:5000/api/v1/documents \
  -F "file=@assets/test_documents/employee_code_of_conduct.md"

# Analyze document (replace {document_id} with actual ID from upload)
curl -X POST http://localhost:5000/api/v1/documents/{document_id}/analyze

# Get compliance report
curl http://localhost:5000/api/v1/reports/{report_id}
```

## Quick Examples

### Python API Usage

```python
from src.core.document_parser import DocumentParser
from src.core.compliance_engine import ComplianceEngine

# Parse document
parser = DocumentParser()
document = parser.parse_file("policy.pdf")

# Run compliance check
engine = ComplianceEngine()
report = engine.analyze(document)

# View results
print(f"Compliance Score: {report.compliance_score}")
print(f"Violations Found: {len(report.violations)}")
for violation in report.violations:
    print(f"  [{violation.rule.severity}] {violation.rule.name}")
    print(f"    Location: {violation.matched_text[:50]}...")
    print(f"    Recommendation: {violation.recommendation}")
```

### Create Custom Rule

```python
from src.core.compliance_engine import ComplianceEngine
from src.models.compliance_rule import ComplianceRule, Severity, RuleCategory

# Create custom rule
rule = ComplianceRule(
    name="Data Retention Period",
    description="Ensure data retention period is specified",
    pattern=r"data.*retention.*\d+\s*(days|months|years)",
    severity=Severity.HIGH,
    category=RuleCategory.DATA_PROTECTION,
    recommendation_template="Specify a clear data retention period in the policy."
)

# Add to engine
engine = ComplianceEngine()
engine.add_rule(rule)

# Analyze with custom rule
report = engine.analyze(document)
```

## Running Tests

```bash
# Run all tests (59 tests)
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test category
python -m pytest tests/test_core_components.py -v     # Unit tests
python -m pytest tests/test_integration.py -v         # Integration tests
python -m pytest tests/test_plugins.py -v             # Plugin tests

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

## Sample Documents

Test with provided sample documents in `assets/test_documents/`:

- `employee_code_of_conduct.md` - Employee policy with HR compliance
- `data_privacy_protection_policy.md` - Data protection policy
- `remote_work_policy_it_department.md` - IT department remote work policy

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

### "API key not found" warning
- System continues with pattern-based analysis only
- Add API keys to `.env` for AI-powered insights

### Document parsing errors
- Verify file format is supported (PDF, DOCX, MD, TXT)
- Check file is not corrupted
- Ensure file size is under 10MB

## Next Steps

1. Try analyzing your own policy documents
2. Create custom compliance rules for your organization
3. Explore rule templates in `assets/rule_templates/`
4. Build a web dashboard using the API
5. Integrate with your document management system

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/documents | Upload document |
| GET | /api/v1/documents | List documents |
| POST | /api/v1/documents/{id}/analyze | Analyze document |
| GET | /api/v1/reports/{id} | Get compliance report |
| GET | /api/v1/rules | List compliance rules |
| POST | /api/v1/rules | Create custom rule |
| GET | /api/v1/templates | List rule templates |
| POST | /api/v1/compare | Compare two documents |
| GET | /api/v1/health | Health check |

## Support

- Run tests to verify setup: `python -m pytest tests/test_setup.py -v`
- Check sample documents for expected formats
- Review inline code comments and docstrings
