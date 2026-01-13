# Data Model: DotNet Virtual Citizen Assistant

**Feature**: 006-dotnet-virtual-citizen-assistant
**Date**: 2026-01-12

## Entity Overview

```
┌─────────────────────┐     sends      ┌─────────────────────────┐
│       User          │───────────────▶│      ChatMessage        │
└─────────────────────┘                └─────────────────────────┘
                                                │
                                                │ belongs to
                                                ▼
┌─────────────────────┐     contains   ┌─────────────────────────┐
│    ChatSession      │◀───────────────│      ChatMessage        │
└─────────────────────┘                └─────────────────────────┘
         │                                      │
         │ generates                            │ cites
         ▼                                      ▼
┌─────────────────────┐                ┌─────────────────────────┐
│   ChatResponse      │───────────────▶│    DocumentSource       │
└─────────────────────┘    includes    └─────────────────────────┘
                                                │
┌─────────────────────┐     matches            │ references
│    SearchQuery      │────────────────────────┘
└─────────────────────┘
         │
         │ returns
         ▼
┌─────────────────────┐     contains   ┌─────────────────────────┐
│   SearchResponse    │───────────────▶│     SearchResult        │
└─────────────────────┘                └─────────────────────────┘
                                                │
                                                │ wraps
                                                ▼
┌─────────────────────┐     belongs to ┌─────────────────────────┐
│  ServiceCategory    │◀───────────────│       Document          │
└─────────────────────┘                └─────────────────────────┘
```

## Enumerations

### MessageRole

| Value | Description |
|-------|-------------|
| `User` | Message from the citizen |
| `Assistant` | Response from the AI assistant |
| `System` | System instructions (internal) |

### SearchMode

| Value | Description |
|-------|-------------|
| `Keyword` | Traditional keyword-based search |
| `Semantic` | AI-powered semantic/vector search |
| `Hybrid` | Combined keyword and semantic search |

### DocumentStatus

| Value | Description |
|-------|-------------|
| `Active` | Document is current and searchable |
| `Archived` | Document is outdated but preserved |
| `Draft` | Document is not yet published |

## Core Entities

### ChatMessage

A single message in a conversation.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `Id` | string | Yes | GUID format | Unique message identifier |
| `SessionId` | string | Yes | GUID format | Parent session reference |
| `Role` | MessageRole | Yes | Valid enum | Who sent the message |
| `Content` | string | Yes | 1-10000 chars | Message text content |
| `Timestamp` | DateTimeOffset | Auto | - | When message was sent |
| `Sources` | List<DocumentSource> | No | - | Cited documents (assistant only) |

**Validation Rules**:
- `Content` must not be empty or whitespace
- `Sources` only populated for assistant messages

### ChatSession

A conversation session containing message history.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `SessionId` | string | Yes | Unique session identifier |
| `CreatedAt` | DateTimeOffset | Auto | Session start time |
| `LastActivityAt` | DateTimeOffset | Auto | Most recent message time |
| `Messages` | List<ChatMessage> | Yes | Ordered message history |
| `Metadata` | Dictionary<string, object> | No | Additional session data |

**Validation Rules**:
- Session expires after 30 minutes of inactivity
- Maximum 100 messages per session

### ChatResponse

Response from the AI assistant.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Content` | string | Yes | AI-generated response text |
| `Sources` | List<DocumentSource> | No | Documents cited in response |
| `Confidence` | float | No | Confidence score (0.0-1.0) |
| `ProcessingTimeMs` | int | Auto | Response generation time |

### DocumentSource

A citation reference to a source document.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `DocumentId` | string | Yes | Reference to Document |
| `Title` | string | Yes | Document title for display |
| `Url` | string | Yes | Link to full document |
| `Relevance` | float | No | Relevance to the query (0.0-1.0) |

### Document

A searchable service document in Azure AI Search.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `Id` | string | Yes | Unique, non-empty | Document identifier (key) |
| `Title` | string | Yes | 1-500 chars | Document title |
| `Content` | string | Yes | 1-50000 chars | Full document text |
| `Summary` | string | No | Max 1000 chars | Brief description |
| `Category` | string | Yes | Non-empty | Service category |
| `SubCategory` | string | No | - | More specific categorization |
| `Tags` | List<string> | No | - | Searchable keywords |
| `Url` | string | No | Valid URL | External source link |
| `LastUpdated` | DateTimeOffset | Auto | - | Last modification time |
| `Status` | DocumentStatus | Yes | Valid enum | Publication status |
| `ContentVector` | List<float> | No | 1536 dimensions | Embedding for semantic search |

**Index Configuration**:
- `Id`: Key field
- `Title`, `Content`, `Summary`, `Tags`: Searchable
- `Category`, `SubCategory`: Filterable, Facetable
- `LastUpdated`: Sortable, Filterable
- `ContentVector`: Vector field for semantic search

### SearchQuery

A user's search request.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `Query` | string | Yes | 1-500 chars | Search query text |
| `Mode` | SearchMode | No | Valid enum | Search mode (default: Semantic) |
| `Category` | string | No | - | Filter by category |
| `Top` | int | No | 1-50, default 10 | Number of results |
| `Skip` | int | No | >= 0, default 0 | Pagination offset |
| `HighlightFields` | List<string> | No | - | Fields to highlight |

### SearchResponse

Results from a search operation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Query` | string | Yes | Original query text |
| `Results` | List<SearchResult> | Yes | Matching documents |
| `TotalCount` | long | Yes | Total matching documents |
| `Facets` | Dictionary<string, List<FacetValue>> | No | Category facets |
| `SearchTimeMs` | int | Auto | Search execution time |

### SearchResult

A single search result with relevance information.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Document` | Document | Yes | Matched document |
| `Score` | double | Yes | Relevance score |
| `Highlights` | Dictionary<string, List<string>> | No | Highlighted snippets |
| `Captions` | List<string> | No | Semantic captions |

### ServiceCategory

A grouping of documents by service type.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Name` | string | Yes | Category identifier |
| `DisplayName` | string | Yes | Human-readable name |
| `Description` | string | No | Category description |
| `Icon` | string | No | Font Awesome icon class |
| `DocumentCount` | int | Yes | Number of documents |
| `SubCategories` | List<string> | No | Child categories |

### FacetValue

A facet bucket for aggregation results.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Value` | string | Yes | Facet value |
| `Count` | long | Yes | Number of matches |

## Upload Entities

### UploadDocument

Document format for batch upload to Azure AI Search.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier |
| `title` | string | Yes | Document title |
| `content` | string | Yes | Full content |
| `summary` | string | No | Brief summary |
| `category` | string | Yes | Service category |
| `subCategory` | string | No | Sub-category |
| `tags` | List<string> | No | Keywords |
| `url` | string | No | Source URL |
| `lastUpdated` | string | No | ISO 8601 date |

### UploadResult

Result of a batch upload operation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `TotalDocuments` | int | Yes | Documents processed |
| `SuccessCount` | int | Yes | Successfully indexed |
| `FailedCount` | int | Yes | Failed to index |
| `Errors` | List<UploadError> | No | Error details |
| `DurationMs` | long | Yes | Total upload time |

### UploadError

Error details for failed document upload.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `DocumentId` | string | Yes | Failed document ID |
| `ErrorMessage` | string | Yes | Error description |
| `StatusCode` | int | No | HTTP status code |

## State Transitions

### Chat Session Lifecycle

```
Created → Active → Expired
              ↓
          Archived (optional)
```

### Document Lifecycle

```
Draft → Active → Archived
          ↓
        Updated (re-indexed)
```

## Indexes and Queries

### Primary Queries

1. **Semantic search**: `query` → AI-ranked documents with captions
2. **Keyword search**: `query` → TF-IDF ranked documents
3. **Category filter**: `category` → documents in category
4. **Document by ID**: `id` → single document
5. **Recent documents**: `lastUpdated > date` → sorted by date
6. **Category facets**: aggregate document counts by category

### Search Index Schema

```json
{
  "name": "citizen-services",
  "fields": [
    { "name": "id", "type": "Edm.String", "key": true },
    { "name": "title", "type": "Edm.String", "searchable": true },
    { "name": "content", "type": "Edm.String", "searchable": true },
    { "name": "summary", "type": "Edm.String", "searchable": true },
    { "name": "category", "type": "Edm.String", "filterable": true, "facetable": true },
    { "name": "subCategory", "type": "Edm.String", "filterable": true, "facetable": true },
    { "name": "tags", "type": "Collection(Edm.String)", "searchable": true },
    { "name": "url", "type": "Edm.String" },
    { "name": "lastUpdated", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true },
    { "name": "contentVector", "type": "Collection(Edm.Single)", "dimensions": 1536, "vectorSearchProfile": "default" }
  ],
  "semanticConfiguration": {
    "name": "citizen-services-semantic",
    "prioritizedFields": {
      "titleField": { "fieldName": "title" },
      "contentFields": [{ "fieldName": "content" }],
      "keywordsFields": [{ "fieldName": "tags" }]
    }
  }
}
```
