# Research: Document Eligibility Agent

**Feature**: 002-document-eligibility-agent
**Date**: 2026-01-12

## Technology Decisions

### 1. Document Processing Engine

**Decision**: Azure AI Document Intelligence (formerly Form Recognizer)

**Rationale**:
- Native support for W-2, pay stubs, ID documents with pre-built models
- Custom model training available for specialized document types
- High accuracy OCR with confidence scores per field
- Available in Azure Government Cloud (GCC)
- Returns structured JSON with bounding boxes for UI highlighting

**Alternatives Considered**:
- **AWS Textract**: Not available in Azure GCC environment
- **Google Document AI**: Not available in Azure GCC environment
- **Open Source (Tesseract + custom)**: Lower accuracy, more development time
- **Azure Computer Vision OCR**: Less structured output, no pre-built models

### 2. Email Integration

**Decision**: Microsoft Graph API

**Rationale**:
- Native integration with Exchange/Outlook mailboxes
- Supports mailbox monitoring with delta queries
- Handles attachments natively
- Available in GCC High environment
- Existing Entra ID authentication integration

**Alternatives Considered**:
- **IMAP/POP3 polling**: Less efficient, no native attachment handling
- **Power Automate**: Additional licensing, less control
- **Azure Logic Apps**: Additional service complexity

### 3. Document Storage

**Decision**: Azure Blob Storage with lifecycle management

**Rationale**:
- 7-year retention requirement met with lifecycle policies
- Immutable storage for compliance
- Hot/Cool/Archive tiers for cost optimization
- Native encryption at rest
- GCC compliant

**Alternatives Considered**:
- **Azure Files**: Less suitable for large binary files
- **Cosmos DB attachments**: Size limitations, cost inefficient
- **On-premises storage**: Compliance and access complexity

### 4. Processing Queue

**Decision**: Celery with Redis backend

**Rationale**:
- Mature async task queue for Python
- Supports priority queues for expedited documents
- Retry logic for failed processing
- Local development without Azure dependencies
- Worker scaling for batch processing

**Alternatives Considered**:
- **Azure Service Bus**: Additional Azure service, GCC configuration needed
- **Azure Queue Storage**: Less feature-rich, no priority support
- **RQ (Redis Queue)**: Simpler but less mature than Celery

### 5. PII Detection

**Decision**: Azure AI Language with PII detection + Document Intelligence annotations

**Rationale**:
- Pre-trained models for SSN, bank accounts, addresses
- Returns entity locations for redaction
- Integrates with Document Intelligence pipeline
- Confidence scores for each detection

**Alternatives Considered**:
- **Custom regex patterns**: Less accurate, maintenance burden
- **Presidio (Microsoft open source)**: Good but requires self-hosting
- **spaCy NER**: Would need custom training for document PII

### 6. Web Framework

**Decision**: Flask 3.1+ with Celery integration

**Rationale**:
- Consistency with Constituent Services Agent
- Simple, well-documented
- Good Celery integration patterns
- Team familiarity
- GCC deployment proven

**Alternatives Considered**:
- **FastAPI**: Async benefits not critical for this use case
- **Django**: More opinionated, heavier for hackathon

### 7. Extraction Confidence Scoring

**Decision**: Combined confidence = 0.5 * OCR_confidence + 0.3 * field_confidence + 0.2 * validation_score

**Rationale**:
- OCR quality heavily impacts extraction accuracy
- Field-level confidence from Document Intelligence
- Validation rules provide additional signal
- Threshold of 0.85 for auto-approval, below requires review

**Alternatives Considered**:
- **Single Document Intelligence score**: Loses validation context
- **Machine learning ensemble**: Over-engineering for hackathon

## Document Type Support

### MVP Document Types (Day 1-2)

| Document | Pre-built Model | Key Fields |
|----------|-----------------|------------|
| W-2 | `prebuilt-tax.us.w2` | Employer, wages, tax year, withholdings |
| Pay Stub | Custom extraction | Employer, gross pay, net pay, date, period |
| Utility Bill | Custom extraction | Provider, address, amount, date |

### Post-Hackathon Document Types

| Document | Model Approach |
|----------|---------------|
| Bank Statement | Custom model training |
| Driver's License | `prebuilt-idDocument` |
| Birth Certificate | Custom model training |
| Lease Agreement | Custom extraction |

## Validation Rules

### Document Age Validation

| Document Type | Max Age | Rationale |
|---------------|---------|-----------|
| Pay Stub | 60 days | SNAP policy requirement |
| Bank Statement | 30 days | SNAP policy requirement |
| Utility Bill | 60 days | Residency verification |
| W-2 | 2 tax years | Income verification |
| ID Document | Not expired | Must be current |

### Cross-Reference Validation

1. **Name matching**: Extracted name vs. case name (fuzzy match)
2. **Address matching**: Extracted address vs. case address
3. **Date range**: Document period vs. benefits period
4. **Amount reasonableness**: Income vs. historical data

## Security Considerations

### PII Handling

1. **At Rest**: AES-256 encryption via Azure Storage Service Encryption
2. **In Transit**: TLS 1.3 minimum
3. **In Memory**: Clear buffers after processing
4. **Display**: Mask by default, reveal with audit logging
5. **Export**: Auto-redaction for non-privileged exports

### Access Control

| Role | Document Access | PII Access | Admin Functions |
|------|-----------------|------------|-----------------|
| Worker | Assigned queue | Masked | No |
| Reviewer | All documents | Full (logged) | No |
| Supervisor | All documents | Full (logged) | Routing rules |
| Admin | All documents | Full (logged) | All settings |

## Integration Points

### Case Management System

**Pattern**: REST API integration with case ID lookup
**Mock Mode**: In-memory case store for hackathon
**Future**: Integration with agency CMS (OTDA, DOH systems)

### Microsoft Graph

**Scopes Required**:
- `Mail.Read` - Read mailbox
- `Mail.ReadWrite` - Mark processed
- `User.Read` - Current user info

**Authentication**: App-only with certificate (daemon pattern)

## Performance Optimization

### Batch Processing

1. Parallel Document Intelligence calls (max 10 concurrent)
2. Async blob uploads
3. Redis result caching
4. Bulk database writes

### Queue Management

1. Priority queues: expedited > resubmission > standard
2. Dead letter queue for failed processing
3. Retry with exponential backoff
4. Worker auto-scaling based on queue depth

## References

- [Azure Document Intelligence Documentation](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- [Microsoft Graph Mail API](https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview)
- [Azure Blob Storage Lifecycle Management](https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-overview)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html)
