# Data Model: Constituent Services Agent

**Feature**: 001-constituent-services-agent
**Date**: 2026-01-12

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│  Conversation   │       │ KnowledgeSource │
├─────────────────┤       ├─────────────────┤
│ id: UUID        │       │ id: UUID        │
│ session_id: str │       │ agency: str     │
│ language: str   │       │ title: str      │
│ created_at: dt  │       │ content: str    │
│ updated_at: dt  │       │ url: str        │
│ status: enum    │       │ last_updated: dt│
│ escalated: bool │       │ document_type   │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │ 1:N                     │ N:M
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│    Message      │       │    Citation     │
├─────────────────┤       ├─────────────────┤
│ id: UUID        │       │ id: UUID        │
│ conversation_id │───────│ message_id      │
│ role: enum      │       │ source_id       │
│ content: str    │       │ quote: str      │
│ timestamp: dt   │       │ relevance: float│
│ confidence: float       └─────────────────┘
└─────────────────┘
         │
         │ 1:1
         ▼
┌─────────────────┐
│ InteractionLog  │
├─────────────────┤
│ id: UUID        │
│ message_id      │
│ query_hash: str │
│ response_hash   │
│ model_version   │
│ latency_ms: int │
│ created_at: dt  │
└─────────────────┘
```

## Entities

### Conversation

Represents a chat session between a constituent and the agent.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| session_id | string | Yes | Browser session identifier |
| language | string | Yes | Detected/selected language code (ISO 639-1) |
| created_at | datetime | Yes | Session start time (UTC) |
| updated_at | datetime | Yes | Last activity time (UTC) |
| status | enum | Yes | active, completed, escalated, expired |
| escalated | boolean | No | True if escalated to human agent |
| escalation_reason | string | No | Reason for escalation |

**Validation Rules**:
- session_id must be unique per active conversation
- language must be one of: en, es, zh, ar, ru, ko, ht, bn
- status transitions: active → completed | escalated | expired
- Conversations expire after 30 minutes of inactivity

**State Transitions**:
```
[NEW] → active → completed
           ↓
      → escalated → completed
           ↓
      → expired
```

---

### Message

Individual message within a conversation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| conversation_id | UUID | Yes | Foreign key to Conversation |
| role | enum | Yes | user, assistant, system |
| content | string | Yes | Message text |
| original_content | string | No | Original text before translation |
| timestamp | datetime | Yes | Message time (UTC) |
| confidence | float | No | Agent confidence score (0.0-1.0) |
| processing_time_ms | integer | No | Time to generate response |

**Validation Rules**:
- content max length: 10,000 characters
- role must be one of: user, assistant, system
- confidence only present for assistant messages
- original_content only present if translation occurred

---

### KnowledgeSource

Indexed document from agency knowledge base.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| agency | string | Yes | Agency code (DMV, DOL, OTDA, DOH, OGS) |
| title | string | Yes | Document title |
| content | string | Yes | Full document content |
| summary | string | No | AI-generated summary |
| url | string | Yes | Source URL for citation |
| document_type | enum | Yes | faq, policy, form, guide, webpage |
| last_updated | datetime | Yes | Last content update |
| indexing_status | enum | Yes | pending, indexed, failed |
| chunk_count | integer | No | Number of indexed chunks |

**Validation Rules**:
- agency must be one of: DMV, DOL, OTDA, DOH, OGS
- url must be valid HTTPS URL on ny.gov domain
- document_type categorizes content for retrieval tuning
- last_updated must be within 90 days for active sources

---

### Citation

Links agent responses to source documents.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| message_id | UUID | Yes | Foreign key to Message |
| source_id | UUID | Yes | Foreign key to KnowledgeSource |
| quote | string | Yes | Relevant quote from source |
| relevance_score | float | Yes | Relevance to query (0.0-1.0) |
| start_offset | integer | No | Character offset in source |
| end_offset | integer | No | End character offset |

**Validation Rules**:
- quote max length: 500 characters
- relevance_score must be between 0.0 and 1.0
- Each message should have 1-5 citations

---

### InteractionLog

Audit record for LOADinG Act compliance.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| message_id | UUID | Yes | Foreign key to Message |
| query_hash | string | Yes | SHA-256 hash of user query |
| response_hash | string | Yes | SHA-256 hash of response |
| model_version | string | Yes | GPT model identifier |
| latency_ms | integer | Yes | End-to-end processing time |
| token_count_input | integer | Yes | Input tokens consumed |
| token_count_output | integer | Yes | Output tokens generated |
| sources_count | integer | Yes | Number of citations |
| confidence_score | float | Yes | Computed confidence |
| created_at | datetime | Yes | Log creation time (UTC) |

**Validation Rules**:
- All fields required (no nulls)
- Records are immutable (no updates)
- TTL: 90 days for full records

---

### UserFeedback

Optional constituent feedback on responses.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| message_id | UUID | Yes | Foreign key to Message |
| rating | integer | Yes | 1-5 star rating |
| helpful | boolean | No | Was the response helpful? |
| comment | string | No | Optional text feedback |
| created_at | datetime | Yes | Feedback time (UTC) |

**Validation Rules**:
- rating must be 1-5
- comment max length: 1000 characters
- One feedback per message

---

## Enums

### ConversationStatus
```python
class ConversationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    EXPIRED = "expired"
```

### MessageRole
```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
```

### DocumentType
```python
class DocumentType(str, Enum):
    FAQ = "faq"
    POLICY = "policy"
    FORM = "form"
    GUIDE = "guide"
    WEBPAGE = "webpage"
```

### Agency
```python
class Agency(str, Enum):
    DMV = "DMV"
    DOL = "DOL"
    OTDA = "OTDA"
    DOH = "DOH"
    OGS = "OGS"
```

### SupportedLanguage
```python
class SupportedLanguage(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    CHINESE = "zh"
    ARABIC = "ar"
    RUSSIAN = "ru"
    KOREAN = "ko"
    HAITIAN_CREOLE = "ht"
    BENGALI = "bn"
```

---

## Storage Mapping

| Entity | Storage | Partition Key | TTL |
|--------|---------|---------------|-----|
| Conversation | Cosmos DB | session_id | 30 days |
| Message | Cosmos DB | conversation_id | 30 days |
| KnowledgeSource | Azure AI Search | agency | None |
| Citation | Cosmos DB | message_id | 30 days |
| InteractionLog | Cosmos DB | date (YYYY-MM-DD) | 90 days |
| UserFeedback | Cosmos DB | message_id | 90 days |

---

## Indexes

### Azure AI Search (KnowledgeSource)
- Full-text index on: title, content, summary
- Filterable: agency, document_type, last_updated
- Semantic ranking enabled
- Vector embeddings for content

### Cosmos DB Indexes
- Conversation: session_id, status, created_at
- Message: conversation_id, timestamp
- InteractionLog: created_at, model_version
