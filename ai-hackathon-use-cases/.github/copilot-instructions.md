## Project Context
- NY State government hackathon application
- Must follow accessibility guidelines (WCAG 2.1 AA)
- Use Azure AI services (GCC-compliant where possible)
- No external data storage outside Azure
- Human-in-the-loop required for citizen-affecting decisions

## Conventions
- All strings must be internationalized (i18n-ready)
- Error handling: structured logging to Application Insights
- API calls: use managed identity, no hardcoded credentials
- Document all AI decision points for LOADinG Act compliance

## Tech Stack
- Azure AI Foundry (formerly Azure AI Studio)
- Microsoft Foundry with Foundry IQ for RAG
- Semantic Kernel 1.45+
- Python 3.11+ or .NET 9

## Security Requirements
- All API keys must be stored in Azure Key Vault or environment variables
- Use DefaultAzureCredential for authentication
- Implement proper input validation and sanitization
- Log all AI decisions for audit trail

## Responsible AI Guidelines
- Always provide source citations for AI-generated responses
- Implement confidence thresholds for automated decisions
- Route low-confidence responses to human review
- Test for bias across demographic groups
- Document limitations and edge cases

## Code Quality Standards
- Write unit tests for all new functionality
- Use type hints in Python code
- Follow PEP 8 style guidelines for Python
- Follow .NET coding conventions for C# code
- Include docstrings for public functions and classes
