# newyork Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-12

## Active Technologies

- Python 3.11+ (001-constituent-services-agent, 002-document-eligibility-agent, 003-emergency-response-agent, 004-policy-compliance-checker, 005-inter-agency-knowledge-hub)
- .NET 9.0 / C# 13 (006-dotnet-virtual-citizen-assistant)
- Semantic Kernel 1.37+ Python (003-emergency-response-agent, 004-policy-compliance-checker, 005-inter-agency-knowledge-hub)
- Semantic Kernel 1.65.0 .NET (006-dotnet-virtual-citizen-assistant)
- Pydantic 2.x (002-document-eligibility-agent, 003-emergency-response-agent, 004-policy-compliance-checker, 005-inter-agency-knowledge-hub)
- Flask 3.x (002-document-eligibility-agent, 003-emergency-response-agent, 004-policy-compliance-checker, 005-inter-agency-knowledge-hub)
- ASP.NET Core MVC (006-dotnet-virtual-citizen-assistant)
- pypdf 6.1.1+ (004-policy-compliance-checker)
- python-docx (004-policy-compliance-checker)
- Azure AI Search SDK (005-inter-agency-knowledge-hub, 006-dotnet-virtual-citizen-assistant)
- Azure OpenAI (006-dotnet-virtual-citizen-assistant)
- MSAL / Azure Identity (005-inter-agency-knowledge-hub, 006-dotnet-virtual-citizen-assistant)
- xUnit / FluentAssertions / Moq (006-dotnet-virtual-citizen-assistant)
- Bootstrap 5.3.0 (006-dotnet-virtual-citizen-assistant)

## Project Structure

```text
Constituent-Services-Agent/       # 001 - Chatbot for constituent services (Python)
Document-Eligibility-Agent/       # 002 - Document OCR and validation (Python)
Emergency-Response-Agent/         # 003 - Emergency response planning (Python)
Policy-Compliance-Checker/        # 004 - Policy document compliance checking (Python)
Inter-Agency-Knowledge-Hub/       # 005 - Cross-agency document search (Python)
DotNet-Virtual-Citizen-Assistant/ # 006 - NYC citizen services RAG chatbot (.NET)
specs/                            # Feature specifications
```

## Commands

```bash
# Python projects (001-005)
pytest tests/ -v
ruff check .
python -m src.main

# .NET project (006)
dotnet build
dotnet test
dotnet run --project VirtualCitizenAgent
```

## Code Style

Python 3.11+: Follow standard conventions
- Use async/await for I/O operations
- Pydantic models for data validation
- Mock services for offline development

.NET 9.0 / C# 13: Follow standard conventions
- Use async/await for I/O operations
- Nullable reference types enabled
- Dependency injection via IServiceCollection
- Semantic Kernel plugins with KernelFunction attributes

## Recent Changes

- 006-dotnet-virtual-citizen-assistant: Added .NET 9, Semantic Kernel 1.65, RAG pipeline, Azure AI Search, Bootstrap UI
- 005-inter-agency-knowledge-hub: Added Azure AI Search, Entra ID auth, cross-agency search, audit logging
- 004-policy-compliance-checker: Added Semantic Kernel, pypdf, python-docx, compliance rule engine
- 003-emergency-response-agent: Added Semantic Kernel, Weather API integration
- 002-document-eligibility-agent: Added Azure Document Intelligence, PII detection
- 001-constituent-services-agent: Initial setup

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
