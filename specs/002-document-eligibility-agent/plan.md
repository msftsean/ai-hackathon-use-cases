# Implementation Plan: Document Eligibility Agent

**Branch**: `002-document-eligibility-agent` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-document-eligibility-agent/spec.md`

## Summary

Build an AI-powered document processing agent that automatically extracts, validates, and routes eligibility documents (W-2s, pay stubs, utility bills, identity documents) using Azure Document Intelligence. The system performs OCR, structured data extraction with confidence scoring, and preliminary validation while maintaining human oversight for final determinations. Must comply with NY LOADinG Act transparency requirements and maintain 7-year document retention.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- Azure AI Document Intelligence SDK (azure-ai-documentintelligence>=1.0.0)
- Azure AI Projects SDK (azure-ai-projects>=1.0.0)
- Azure Blob Storage SDK (azure-storage-blob>=12.0.0)
- Microsoft Graph SDK (msgraph-sdk>=1.0.0) for email monitoring
- Flask 3.1+ (web interface)
- Celery + Redis (async document processing queue)

**Storage**:
- Azure Blob Storage (document storage with 7-year retention)
- Azure Cosmos DB (document metadata, extraction results, audit logs)
- Redis (processing queue, session cache)

**Testing**:
- pytest with pytest-asyncio
- Azure AI Evaluation SDK
- Sample document test fixtures

**Target Platform**: Azure Government Cloud (GCC), Windows 365 VMs
**Project Type**: Single Python application with web frontend

**Performance Goals**:
- Document intake to ready-for-review: < 2 minutes
- Data extraction accuracy: > 95%
- Batch processing: 100+ documents
- Support 50 concurrent workers

**Constraints**:
- All data within Azure GCC boundary
- PII encryption at rest and in transit
- Human review required for all final determinations
- 7-year document retention for audit
- WCAG 2.1 AA accessibility compliance
- LOADinG Act audit trail required

**Scale/Scope**:
- 7 document types (MVP: 3 types)
- 10+ extraction fields per document
- Daily volume: 1000+ documents
- 50 eligibility workers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Test-First Development | PASS | Unit tests for extraction, validation; integration tests for Document Intelligence |
| Library-First Architecture | PASS | Agent built as standalone library with CLI for batch processing |
| Integration Testing | PASS | Contract tests for Document Intelligence, Graph API, Blob Storage |
| Observability | PASS | Structured logging to Application Insights, LOADinG Act audit trail |
| Simplicity | PASS | Start with 3 document types (W-2, pay stub, utility bill), expand post-hackathon |

## Project Structure

### Documentation (this feature)

```text
specs/002-document-eligibility-agent/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.yaml         # OpenAPI specification
└── tasks.md             # Phase 2 output (from /speckit.tasks)
```

### Source Code (repository root)

```text
Document-Eligibility-Agent/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── document_processor.py    # Main document processing orchestration
│   │   ├── extraction_agent.py      # Data extraction with Document Intelligence
│   │   └── validation_agent.py      # Document validation rules
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py              # Document model with status tracking
│   │   ├── extraction.py            # Extraction results model
│   │   └── processing_log.py        # Audit log model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_intelligence.py # Azure Document Intelligence wrapper
│   │   ├── storage_service.py       # Azure Blob Storage operations
│   │   ├── email_service.py         # Microsoft Graph email monitoring
│   │   └── audit_service.py         # LOADinG Act compliance logging
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Flask API routes
│   │   └── middleware.py            # Auth, logging middleware
│   └── config/
│       ├── __init__.py
│       └── settings.py              # Configuration management
├── tests/
│   ├── unit/
│   │   ├── test_extraction.py
│   │   ├── test_validation.py
│   │   └── test_document.py
│   ├── integration/
│   │   ├── test_document_intelligence.py
│   │   └── test_api.py
│   └── evaluation/
│       ├── test_cases.jsonl
│       ├── red_team_cases.jsonl
│       └── run_evals.py
├── static/                          # Web interface
│   ├── index.html
│   ├── queue.js
│   └── styles.css
├── sample_documents/                # Test fixtures
│   ├── w2_sample.pdf
│   ├── paystub_sample.pdf
│   └── utility_bill_sample.pdf
├── requirements.txt
├── demo.py
└── README.md
```

**Structure Decision**: Single Python application with clear separation between document processing agent, services for external integrations (Document Intelligence, Graph, Blob Storage), and API layer. The agent/ directory contains document processing and validation logic, services/ handles Azure service integrations.

## Complexity Tracking

> No constitution violations identified. MVP scope appropriately constrained to 3 document types and core extraction/validation functionality.

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Single service architecture | Hackathon timeline, simpler deployment | Microservices (rejected: overhead for 2-day sprint) |
| Flask for API | Team familiarity, GCC-compatible, consistent with CSA | FastAPI (rejected: consistency with other agents) |
| Celery for async processing | Mature, Redis-backed, handles document queue | Azure Functions (rejected: local dev complexity) |
| Cosmos DB for metadata | Azure GCC compliant, flexible schema for extraction results | SQL (rejected: schema flexibility needed) |
