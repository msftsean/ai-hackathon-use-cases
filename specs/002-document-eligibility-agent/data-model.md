# Data Model: Document Eligibility Agent

**Feature**: 002-document-eligibility-agent
**Date**: 2026-01-12

## Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│      Document       │       │    ValidationRule   │
├─────────────────────┤       ├─────────────────────┤
│ id: UUID            │       │ id: UUID            │
│ case_id: str        │       │ document_type: enum │
│ document_type: enum │       │ rule_type: enum     │
│ status: enum        │       │ parameters: json    │
│ source: enum        │       │ error_message: str  │
│ filename: str       │       │ active: bool        │
│ blob_url: str       │       └─────────────────────┘
│ content_hash: str   │
│ uploaded_at: dt     │
│ processed_at: dt    │
│ assigned_to: str    │
│ priority: enum      │
└──────────┬──────────┘
           │
           │ 1:N
           ▼
┌─────────────────────┐
│     Extraction      │
├─────────────────────┤
│ id: UUID            │
│ document_id: UUID   │──────────────┐
│ field_name: str     │              │
│ field_value: str    │              │
│ confidence: float   │              │ N:1
│ bounding_box: json  │              │
│ is_pii: bool        │              │
│ validated: bool     │              │
│ validation_status   │              │
└──────────┬──────────┘              │
           │                         │
           │ N:1                     │
           ▼                         ▼
┌─────────────────────┐   ┌─────────────────────┐
│   ProcessingLog     │   │   ExtractionModel   │
├─────────────────────┤   ├─────────────────────┤
│ id: UUID            │   │ id: UUID            │
│ document_id: UUID   │   │ name: str           │
│ action: enum        │   │ model_id: str       │
│ actor: str          │   │ document_types: []  │
│ details: json       │   │ version: str        │
│ timestamp: dt       │   │ accuracy: float     │
│ ip_address: str     │   └─────────────────────┘
│ user_agent: str     │
└─────────────────────┘
```

## Entities

### Document

Represents a submitted document with metadata, processing status, and assignment tracking.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| case_id | string | Yes | Reference to eligibility case |
| document_type | enum | Yes | Type of document (w2, paystub, utility_bill, etc.) |
| status | enum | Yes | Processing status |
| source | enum | Yes | How document was received |
| filename | string | Yes | Original filename |
| blob_url | string | Yes | Azure Blob Storage URL |
| content_hash | string | Yes | SHA-256 hash for deduplication |
| file_size_bytes | integer | Yes | File size in bytes |
| mime_type | string | Yes | MIME type (application/pdf, image/jpeg, etc.) |
| page_count | integer | No | Number of pages |
| uploaded_at | datetime | Yes | When document was received |
| processed_at | datetime | No | When extraction completed |
| assigned_to | string | No | Worker ID for review |
| assigned_at | datetime | No | When assigned |
| reviewed_at | datetime | No | When review completed |
| reviewed_by | string | No | Reviewer ID |
| priority | enum | Yes | Processing priority |
| is_duplicate | boolean | No | Flagged as duplicate |
| duplicate_of | UUID | No | Reference to original document |
| overall_confidence | float | No | Combined confidence score |
| validation_status | enum | No | Overall validation result |
| notes | string | No | Worker notes |

**Validation Rules**:
- case_id must exist in case management system (or mock store)
- document_type must be one of supported types
- blob_url must be valid Azure Blob URL
- content_hash used for duplicate detection
- file_size_bytes max 50MB

**State Transitions**:
```
[UPLOADED] → [PROCESSING] → [EXTRACTED] → [VALIDATING] → [READY_FOR_REVIEW]
                  ↓              ↓              ↓                 ↓
              [FAILED]      [FAILED]       [FAILED]         [APPROVED]
                                                                 ↓
                                                           [REJECTED]
                                                                 ↓
                                                           [RESUBMIT_REQUESTED]
```

---

### Extraction

Represents an extracted data field from a document with confidence and validation status.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| document_id | UUID | Yes | Foreign key to Document |
| field_name | string | Yes | Name of extracted field |
| field_value | string | Yes | Extracted value |
| display_value | string | No | Formatted/masked value for display |
| confidence | float | Yes | Extraction confidence (0.0-1.0) |
| bounding_box | json | No | Location in document {x, y, width, height, page} |
| is_pii | boolean | Yes | Whether field contains PII |
| pii_type | enum | No | Type of PII (ssn, bank_account, dob, etc.) |
| validated | boolean | Yes | Whether validation was run |
| validation_status | enum | No | Validation result |
| validation_message | string | No | Validation error/warning message |
| manually_corrected | boolean | No | Whether worker corrected value |
| original_value | string | No | Value before correction |
| corrected_by | string | No | Worker who made correction |
| corrected_at | datetime | No | When correction was made |

**Validation Rules**:
- confidence must be between 0.0 and 1.0
- bounding_box required if from OCR extraction
- display_value auto-generated with PII masking

---

### ProcessingLog

Audit trail for LOADinG Act compliance. Records all processing steps and user actions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| document_id | UUID | Yes | Foreign key to Document |
| action | enum | Yes | Action performed |
| actor | string | Yes | User ID or "system" |
| actor_role | string | No | Role of actor at time of action |
| details | json | Yes | Action-specific details |
| timestamp | datetime | Yes | When action occurred |
| ip_address | string | No | Client IP address |
| user_agent | string | No | Client user agent |
| session_id | string | No | User session ID |
| duration_ms | integer | No | Processing duration |

**Validation Rules**:
- All fields required (no nulls except optional)
- Records are immutable (no updates)
- TTL: 7 years (compliance requirement)

**Action Types**:
- `UPLOADED` - Document received
- `PROCESSING_STARTED` - Extraction began
- `PROCESSING_COMPLETED` - Extraction finished
- `PROCESSING_FAILED` - Extraction error
- `VALIDATION_STARTED` - Validation began
- `VALIDATION_COMPLETED` - Validation finished
- `ASSIGNED` - Assigned to worker
- `VIEWED` - Document viewed
- `PII_ACCESSED` - PII revealed
- `FIELD_CORRECTED` - Extraction corrected
- `APPROVED` - Document approved
- `REJECTED` - Document rejected
- `RESUBMIT_REQUESTED` - Resubmission requested
- `EXPORTED` - Document exported

---

### ValidationRule

Configurable validation rules for document processing.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| name | string | Yes | Rule name |
| document_type | enum | Yes | Applicable document type |
| rule_type | enum | Yes | Type of validation |
| field_name | string | No | Field to validate (if field-level) |
| parameters | json | Yes | Rule parameters |
| error_message | string | Yes | Message shown on failure |
| severity | enum | Yes | error, warning, info |
| active | boolean | Yes | Whether rule is enabled |
| created_by | string | Yes | Who created the rule |
| created_at | datetime | Yes | When created |
| updated_at | datetime | No | Last update |

**Rule Types**:
- `AGE` - Document age limit
- `REQUIRED_FIELD` - Field must be present
- `FORMAT` - Value format validation
- `RANGE` - Numeric range check
- `CROSS_REFERENCE` - Check against case data
- `CUSTOM` - Custom logic

---

### ExtractionModel

Tracks Document Intelligence models used for extraction.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| name | string | Yes | Model display name |
| model_id | string | Yes | Azure model identifier |
| document_types | array | Yes | Supported document types |
| version | string | Yes | Model version |
| accuracy | float | No | Measured accuracy |
| is_prebuilt | boolean | Yes | Whether pre-built or custom |
| training_date | datetime | No | When custom model trained |
| active | boolean | Yes | Whether currently used |

---

## Enums

### DocumentType
```python
class DocumentType(str, Enum):
    W2 = "w2"
    PAYSTUB = "paystub"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    DRIVERS_LICENSE = "drivers_license"
    BIRTH_CERTIFICATE = "birth_certificate"
    LEASE_AGREEMENT = "lease_agreement"
    OTHER = "other"
```

### DocumentStatus
```python
class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VALIDATING = "validating"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESUBMIT_REQUESTED = "resubmit_requested"
    FAILED = "failed"
```

### DocumentSource
```python
class DocumentSource(str, Enum):
    EMAIL = "email"
    UPLOAD = "upload"
    FAX = "fax"
    SCAN = "scan"
```

### DocumentPriority
```python
class DocumentPriority(str, Enum):
    EXPEDITED = "expedited"
    RESUBMISSION = "resubmission"
    STANDARD = "standard"
    LOW = "low"
```

### ValidationStatus
```python
class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    PENDING = "pending"
```

### PIIType
```python
class PIIType(str, Enum):
    SSN = "ssn"
    BANK_ACCOUNT = "bank_account"
    ROUTING_NUMBER = "routing_number"
    DATE_OF_BIRTH = "date_of_birth"
    DRIVERS_LICENSE_NUMBER = "drivers_license_number"
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
```

### LogAction
```python
class LogAction(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING_STARTED = "processing_started"
    PROCESSING_COMPLETED = "processing_completed"
    PROCESSING_FAILED = "processing_failed"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    ASSIGNED = "assigned"
    VIEWED = "viewed"
    PII_ACCESSED = "pii_accessed"
    FIELD_CORRECTED = "field_corrected"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESUBMIT_REQUESTED = "resubmit_requested"
    EXPORTED = "exported"
```

---

## Storage Mapping

| Entity | Storage | Partition Key | TTL |
|--------|---------|---------------|-----|
| Document | Cosmos DB | case_id | 7 years |
| Extraction | Cosmos DB | document_id | 7 years |
| ProcessingLog | Cosmos DB | date (YYYY-MM-DD) | 7 years |
| ValidationRule | Cosmos DB | document_type | None |
| ExtractionModel | Cosmos DB | N/A (small table) | None |
| Document Files | Blob Storage | case_id/document_id | 7 years |

---

## Indexes

### Cosmos DB Indexes
- Document: case_id, status, assigned_to, uploaded_at, document_type
- Extraction: document_id, field_name, is_pii
- ProcessingLog: document_id, timestamp, action, actor

### Blob Storage Organization
```
documents/
├── {case_id}/
│   ├── {document_id}/
│   │   ├── original.pdf
│   │   ├── thumbnail.jpg
│   │   └── metadata.json
```

---

## Field Mappings by Document Type

### W-2
| Field Name | Display Name | PII | Validation |
|------------|--------------|-----|------------|
| employer_name | Employer Name | No | Required |
| employer_ein | Employer EIN | No | Format check |
| employee_ssn | Employee SSN | Yes | Format, masked |
| wages | Wages, Tips, etc. | No | Numeric |
| federal_tax | Federal Tax Withheld | No | Numeric |
| tax_year | Tax Year | No | Within 2 years |

### Pay Stub
| Field Name | Display Name | PII | Validation |
|------------|--------------|-----|------------|
| employer_name | Employer | No | Required |
| employee_name | Employee Name | No | Cross-ref case |
| gross_pay | Gross Pay | No | Numeric |
| net_pay | Net Pay | No | Numeric |
| pay_period_start | Period Start | No | Date format |
| pay_period_end | Period End | No | Date format |
| pay_date | Pay Date | No | Within 60 days |

### Utility Bill
| Field Name | Display Name | PII | Validation |
|------------|--------------|-----|------------|
| provider_name | Provider | No | Required |
| account_number | Account # | Yes | Masked |
| service_address | Service Address | Yes | Cross-ref case |
| billing_date | Bill Date | No | Within 60 days |
| amount_due | Amount Due | No | Numeric |
