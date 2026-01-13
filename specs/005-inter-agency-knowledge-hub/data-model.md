# Data Model: Inter-Agency Knowledge Hub

**Feature**: 005-inter-agency-knowledge-hub
**Date**: 2026-01-12

## Entity Overview

```
┌─────────────────────┐     submits     ┌─────────────────────────┐
│       User          │────────────────▶│      SearchQuery        │
└─────────────────────┘                 └─────────────────────────┘
         │                                        │
         │ authenticates via                      │ returns
         ▼                                        ▼
┌─────────────────────┐                ┌─────────────────────────┐
│    EntraIDToken     │                │     SearchResult        │
└─────────────────────┘                └─────────────────────────┘
         │                                        │
         │ contains                               │ includes
         ▼                                        ▼
┌─────────────────────┐                ┌─────────────────────────┐
│   UserPermissions   │                │   DocumentCitation      │
└─────────────────────┘                └─────────────────────────┘
                                                  │
┌─────────────────────┐     indexes              │ references
│    AgencySource     │──────────────────────────┘
└─────────────────────┘
         │
         │ contains
         ▼
┌─────────────────────┐     relates to  ┌─────────────────────────┐
│  IndexedDocument    │────────────────▶│    CrossReference       │
└─────────────────────┘                 └─────────────────────────┘
         │
         │ logged in
         ▼
┌─────────────────────┐     triggers    ┌─────────────────────────┐
│     AccessLog       │                 │     ReviewFlag          │
└─────────────────────┘                 └─────────────────────────┘
```

## Enumerations

### Agency

| Value | Description |
|-------|-------------|
| `DMV` | Department of Motor Vehicles |
| `DOL` | Department of Labor |
| `OTDA` | Office of Temporary and Disability Assistance |
| `DOH` | Department of Health |
| `OGS` | Office of General Services |

### DocumentClassification

| Value | Description |
|-------|-------------|
| `PUBLIC` | Available to all users without authentication |
| `INTERNAL` | Available to authenticated agency employees |
| `RESTRICTED` | Available only to specific permission groups |
| `CONFIDENTIAL` | Requires explicit access grant |

### RelationshipType

| Value | Description |
|-------|-------------|
| `SIMILAR_TOPIC` | Documents cover similar subject matter |
| `DEPENDENCY` | Document A depends on/references Document B |
| `SUPERSEDES` | Document A replaces Document B |
| `CONFLICT` | Potential policy conflict detected |
| `RELATED` | General relationship, unclassified |

### ReviewStatus

| Value | Description |
|-------|-------------|
| `PENDING` | Flagged, awaiting administrator review |
| `APPROVED` | Administrator approved the response |
| `MODIFIED` | Administrator modified the response |
| `REJECTED` | Administrator rejected the query/response |

### ActionType

| Value | Description |
|-------|-------------|
| `SEARCH` | User performed a search query |
| `VIEW` | User viewed a document |
| `EXPORT` | User exported document or citation |
| `CROSS_REFERENCE` | User accessed cross-reference results |

## Core Entities

### SearchQuery

A user's search request to the knowledge hub.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `query_id` | string | Yes | UUID format | Unique identifier |
| `query_text` | string | Yes | 1-500 chars | Search query text |
| `user_id` | string | Yes | Non-empty | Entra ID user principal |
| `user_groups` | list[string] | Yes | - | User's permission groups |
| `agency_filter` | list[Agency] | No | Valid enums | Filter to specific agencies |
| `date_range_start` | date | No | - | Filter by publication date |
| `date_range_end` | date | No | - | Filter by publication date |
| `classification_filter` | list[DocumentClassification] | No | Valid enums | Filter by classification |
| `page` | int | No | >= 1 | Pagination page number |
| `page_size` | int | No | 1-100, default 20 | Results per page |
| `submitted_at` | datetime | Auto | - | Query submission timestamp |

**Validation Rules**:
- `query_text` must have at least 1 non-whitespace character
- `date_range_end` must be >= `date_range_start` if both provided
- `page_size` defaults to 20, max 100

### SearchResult

A single result from a search query.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `result_id` | string | Yes | Unique identifier |
| `query_id` | string | Yes | Reference to SearchQuery |
| `document` | DocumentCitation | Yes | Citation for matched document |
| `relevance_score` | float | Yes | 0.0-1.0 relevance score |
| `snippet` | string | Yes | Highlighted text excerpt |
| `cross_references` | list[CrossReference] | No | Related documents |
| `position` | int | Yes | Position in result set |

### DocumentCitation

Standardized citation information for a document.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `document_id` | string | Yes | UUID format | Unique identifier |
| `title` | string | Yes | Non-empty | Document title |
| `agency` | Agency | Yes | Valid enum | Source agency |
| `publication_date` | date | Yes | - | Original publication date |
| `last_modified` | datetime | Yes | - | Last modification timestamp |
| `document_url` | string | Yes | Valid URL | Direct link to source |
| `version` | string | No | - | Document version |
| `classification` | DocumentClassification | Yes | Valid enum | Access classification |
| `author` | string | No | - | Document author |
| `department` | string | No | - | Department within agency |

**Validation Rules**:
- `document_url` must be a valid HTTP/HTTPS URL
- `last_modified` must be >= `publication_date`

### IndexedDocument

A document indexed in the Azure AI Search knowledge base.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | Unique identifier |
| `citation` | DocumentCitation | Yes | Citation metadata |
| `content` | string | Yes | Full document text |
| `content_vector` | list[float] | Yes | Embedding for semantic search |
| `permissions` | list[string] | Yes | Groups with access |
| `keywords` | list[string] | No | Extracted keywords |
| `indexed_at` | datetime | Auto | Indexing timestamp |

### AgencySource

Configuration for an agency's knowledge base.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agency_id` | string | Yes | Unique identifier |
| `agency` | Agency | Yes | Agency enum value |
| `display_name` | string | Yes | Human-readable name |
| `search_index_name` | string | Yes | Azure AI Search index name |
| `document_count` | int | No | Estimated document count |
| `last_sync` | datetime | No | Last synchronization |
| `default_permissions` | list[string] | Yes | Base permission groups |
| `is_active` | bool | Yes | Whether source is searchable |

### AccessLog

Audit record for document and search access.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `log_id` | string | Yes | Unique identifier (UUID) |
| `user_id` | string | Yes | Entra ID user principal |
| `user_groups` | list[string] | Yes | Groups at time of access |
| `action` | ActionType | Yes | Type of action |
| `query_text` | string | No | Search query if applicable |
| `document_ids` | list[string] | No | Documents accessed |
| `timestamp` | datetime | Auto | UTC timestamp |
| `ip_address` | string | No | Client IP address |
| `session_id` | string | No | Session correlation ID |
| `response_time_ms` | int | No | Response time in ms |
| `result_count` | int | No | Number of results returned |

**Retention**: 7 years per LOADinG Act compliance

### CrossReference

A relationship between two documents.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reference_id` | string | Yes | Unique identifier |
| `source_document_id` | string | Yes | Source document |
| `target_document_id` | string | Yes | Related document |
| `relationship_type` | RelationshipType | Yes | Type of relationship |
| `confidence_score` | float | Yes | 0.0-1.0 confidence |
| `detected_at` | datetime | Auto | Detection timestamp |
| `verified_by` | string | No | Admin who verified |
| `notes` | string | No | Additional context |

**Validation Rules**:
- `source_document_id` must not equal `target_document_id`
- `confidence_score` must be between 0.0 and 1.0

### ReviewFlag

Marker for queries requiring human review.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `flag_id` | string | Yes | Unique identifier |
| `query_id` | string | Yes | Reference to SearchQuery |
| `criteria_matched` | list[string] | Yes | Review criteria triggered |
| `status` | ReviewStatus | Yes | Current review status |
| `flagged_at` | datetime | Auto | Flag creation timestamp |
| `reviewed_by` | string | No | Admin reviewer |
| `reviewed_at` | datetime | No | Review timestamp |
| `admin_notes` | string | No | Administrator notes |
| `modified_response` | string | No | Modified response if applicable |

### UserPermissions

Cached user permission information.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Entra ID user principal |
| `display_name` | string | Yes | User display name |
| `email` | string | Yes | User email |
| `groups` | list[string] | Yes | Permission group memberships |
| `agencies` | list[Agency] | Yes | Agencies user can access |
| `is_admin` | bool | Yes | Has admin privileges |
| `cached_at` | datetime | Auto | Cache timestamp |
| `expires_at` | datetime | Yes | Cache expiration |

**Validation Rules**:
- `expires_at` must be > `cached_at`
- Default cache TTL: 15 minutes

## State Transitions

### Search Query Lifecycle

```
Submitted → Validated → Permissions Applied → Searched → Results Returned
                                                  ↓
                                            (if flagged)
                                                  ↓
                                          Flagged for Review → Reviewed → Released/Rejected
```

### Review Flag Lifecycle

```
PENDING → APPROVED (response sent)
        → MODIFIED (modified response sent)
        → REJECTED (error returned to user)
```

## Indexes and Queries

### Primary Queries

1. **Search documents**: `query_text` + `user_groups` → filtered results
2. **Get document by ID**: `document_id` (exact match)
3. **Get cross-references**: `document_id` → related documents
4. **Get access logs by user**: `user_id` + date range
5. **Get pending reviews**: `status = PENDING`
6. **List agency sources**: `is_active = true`

### Secondary Indexes

- `SearchQuery.user_id` for user query history
- `AccessLog.timestamp` for audit queries
- `AccessLog.user_id` for user access history
- `CrossReference.source_document_id` for lookups
- `ReviewFlag.status` for pending reviews queue
- `IndexedDocument.permissions` for security filtering
