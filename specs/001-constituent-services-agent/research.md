# Research: Constituent Services Agent

**Feature**: 001-constituent-services-agent
**Date**: 2026-01-12

## Research Topics

### 1. Azure AI Foundry with Foundry IQ for Government RAG

**Decision**: Use Azure AI Projects SDK with Foundry IQ file_search tool for agentic RAG

**Rationale**:
- Foundry IQ provides built-in citation tracking required for LOADinG Act compliance
- Multi-hop reasoning across documents without custom pipeline
- Azure Government Cloud (GCC) compatible
- Automatic chunk management and relevance scoring

**Alternatives Considered**:
- Custom Azure AI Search + LangChain pipeline: More control but requires significant setup time
- Semantic Kernel RAG pattern: Good but lacks built-in citation extraction
- Direct OpenAI Assistants API: Not available in GCC

**Implementation Notes**:
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=connection_string
)
agent = client.agents.create_agent(
    model="gpt-4o",
    tools=[{"type": "file_search"}]  # Foundry IQ
)
```

---

### 2. Multi-Language Support Architecture

**Decision**: Azure Translator API with detect-translate-process-translate pattern

**Rationale**:
- Azure Translator supports all 8 required languages (EN, ES, ZH, AR, RU, KO, HT, BN)
- GCC-compliant service available
- Auto-detection eliminates need for user language selection
- Response translation maintains technical accuracy

**Alternatives Considered**:
- GPT-4 native translation: Quality concerns for government terminology
- Google Translate: Not GCC-compliant
- Custom translation models: Too complex for hackathon timeline

**Implementation Pattern**:
1. Detect incoming language
2. Translate to English if not English
3. Process query through agent
4. Translate response back to detected language
5. Keep agency names/technical terms in English with translation notes

---

### 3. LOADinG Act Audit Trail Requirements

**Decision**: Structured logging to Azure Cosmos DB with immutable records

**Rationale**:
- LOADinG Act requires documenting AI decision processes
- Cosmos DB provides flexible schema for evolving requirements
- Immutable records with TTL for data retention compliance
- Query capability for audit requests

**Required Fields per Interaction**:
| Field | Description |
|-------|-------------|
| interaction_id | Unique identifier |
| timestamp | UTC timestamp |
| query | Original user query (anonymized) |
| response | Agent response text |
| sources_used | List of document citations |
| confidence_score | Agent confidence (0-1) |
| model_version | GPT model version used |
| language | Detected/used language |
| escalated | Boolean if escalated to human |

**Retention Policy**:
- Full records: 30 days
- Anonymized records: 90 days
- Aggregated statistics: Indefinite

---

### 4. Web Chat Interface for Accessibility (WCAG 2.1 AA)

**Decision**: Simple HTML/CSS/JavaScript with ARIA labels and keyboard navigation

**Rationale**:
- WCAG 2.1 AA is a hard requirement
- Simple implementation reduces accessibility bugs
- No complex framework dependencies
- Easy to test with screen readers

**Key Accessibility Features**:
- Semantic HTML structure
- ARIA live regions for dynamic content
- Full keyboard navigation
- Sufficient color contrast (4.5:1 minimum)
- Focus indicators visible
- Skip links for navigation
- Alt text for any images

**Testing Tools**:
- axe DevTools
- WAVE
- Manual screen reader testing (NVDA, JAWS)

---

### 5. Mock Services for Offline Development

**Decision**: Implement mock classes for all Azure services

**Rationale**:
- Hackathon participants may not have Azure credentials
- Enables local development and testing
- Demonstrates functionality without live services
- Faster development iteration

**Mock Services Required**:
| Service | Mock Class |
|---------|------------|
| Foundry IQ | MockFoundryIQKnowledgeBase |
| Translator | MockMultilingualAgent |
| Cosmos DB | MockAuditService (in-memory dict) |

**Pattern**: Factory function with environment variable toggle
```python
def get_knowledge_base(use_mock=False):
    if use_mock or os.getenv("USE_MOCK_SERVICES"):
        return MockFoundryIQKnowledgeBase()
    return FoundryIQKnowledgeBase(connection_string)
```

---

### 6. Confidence Scoring and Escalation

**Decision**: Combine model confidence with citation count for composite score

**Rationale**:
- Model-only confidence can be unreliable
- Citation count indicates source grounding
- Clear threshold for human escalation

**Scoring Formula**:
```
confidence = 0.6 * model_confidence + 0.4 * min(citation_count / 3, 1.0)
```

**Escalation Thresholds**:
| Confidence | Action |
|------------|--------|
| > 0.8 | Direct response |
| 0.5 - 0.8 | Response with disclaimer |
| < 0.5 | Offer human escalation |
| Benefits eligibility | Always offer escalation (per spec) |

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.11+ |
| AI Framework | Semantic Kernel | 1.45+ |
| RAG | Azure AI Foundry (Foundry IQ) | Latest |
| Translation | Azure Translator | Latest |
| Storage | Azure Cosmos DB | Latest |
| Search Index | Azure AI Search | 11.5+ |
| Web Framework | Flask | 3.1+ |
| Testing | pytest + Azure AI Evaluation | Latest |
| Red Teaming | promptfoo | 0.100+ |

## Open Questions Resolved

1. **Q: How to handle PII in conversations?**
   A: Don't store - process in memory only, log anonymized summaries

2. **Q: What happens when Azure services are unavailable?**
   A: Graceful degradation with offline FAQ + clear error messaging

3. **Q: How to update knowledge base content?**
   A: Weekly batch ingestion from SharePoint with manual trigger option

4. **Q: How to handle multi-turn conversations?**
   A: Foundry IQ threads maintain context; session ID tracks conversation
