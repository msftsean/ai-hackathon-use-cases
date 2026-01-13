# Research: Emergency Response Planning Agent

**Feature**: 003-emergency-response-agent
**Date**: 2026-01-12

## Research Tasks Completed

### 1. Multi-Agent Orchestration Framework

**Decision**: Microsoft Semantic Kernel 1.37+

**Rationale**:
- Native Python async/await support
- Built-in kernel functions for AI-powered planning
- Extensible plugin architecture for specialized agents
- Strong Azure OpenAI integration
- Active maintenance and community support

**Alternatives Considered**:
- LangChain: More complex, heavier dependency footprint
- Custom orchestration: Would require significant development time
- AutoGen: Less mature, more focused on conversational agents

### 2. Data Validation Framework

**Decision**: Pydantic 2.x with field validators

**Rationale**:
- Native async support in v2
- Automatic JSON serialization/deserialization
- Field validators for domain-specific rules (positive radius, non-negative population)
- Excellent IDE support and type hints
- Integration with FastAPI/Flask for API validation

**Alternatives Considered**:
- Dataclasses: Lacks built-in validation
- attrs: Less ecosystem support
- marshmallow: More verbose, less Pythonic

### 3. Weather API Integration

**Decision**: OpenWeatherMap API with fallback mock data

**Rationale**:
- Free tier (1000 calls/day) sufficient for development/demo
- Current conditions, forecasts, and alerts endpoints
- Well-documented REST API
- Graceful degradation pattern with mock data when unavailable

**Alternatives Considered**:
- National Weather Service API: US-only, more complex authentication
- Weather.gov: Less structured response format
- Azure Maps Weather: Requires Azure subscription

### 4. Web Framework

**Decision**: Flask 3.x with async support

**Rationale**:
- Lightweight, minimal boilerplate
- Blueprint pattern for modular API routes
- Easy static file serving for web dashboard
- Familiar to most Python developers
- Async view support via flask[async]

**Alternatives Considered**:
- FastAPI: Better for pure API, overkill for demo
- Django: Too heavy for single-purpose agent
- Quart: Less mature ecosystem

### 5. Historical Data Storage

**Decision**: Azure AI Search (production) / In-memory (MVP)

**Rationale**:
- Full-text search on incident descriptions, lessons learned
- Faceted filtering by type, severity, date
- Vector search capability for semantic similarity (future)
- Scales with historical data growth

**Alternatives Considered**:
- Elasticsearch: Requires separate infrastructure
- SQLite with FTS5: Limited scalability
- Cosmos DB: Overkill for search-primary use case

### 6. Resource Calculation Algorithm

**Decision**: Population-based scaling with emergency type multipliers

**Rationale**:
- Aligns with FEMA resource typing guidelines
- Simple formula: `base_personnel = max(50, population // 1000)`
- Type-specific multipliers: Hurricane 2.0x, Fire 1.8x, Public Health 1.5x
- Produces reasonable estimates for demonstration

**Algorithm**:
```python
resource_multipliers = {
    EmergencyType.HURRICANE: 2.0,
    EmergencyType.PUBLIC_HEALTH: 1.5,
    EmergencyType.FIRE: 1.8,
    EmergencyType.INFRASTRUCTURE_FAILURE: 1.2,
    EmergencyType.EARTHQUAKE: 1.5
}

base_personnel = max(50, population // 1000)
final_personnel = int(base_personnel * multiplier)
vehicles = final_personnel // 5
medical_units = population // 5000
shelters = population // 1000
```

### 7. Agency Assignment Logic

**Decision**: Emergency type to lead agency mapping with supporting agencies list

**Rationale**:
- Reflects real-world incident command system (ICS)
- Type-specific lead agencies (FDNY for fire, DOH for health, OEM for disasters)
- Supporting agencies pulled from common pool plus type-specific additions

**Mapping**:
```python
lead_agencies = {
    EmergencyType.FIRE: "Fire Department",
    EmergencyType.PUBLIC_HEALTH: "Department of Health",
    EmergencyType.HURRICANE: "Office of Emergency Management",
    EmergencyType.INFRASTRUCTURE_FAILURE: "Department of Transportation",
    EmergencyType.SECURITY_INCIDENT: "Police Department",
    EmergencyType.FLOOD: "Office of Emergency Management",
    EmergencyType.WINTER_STORM: "Office of Emergency Management",
    EmergencyType.EARTHQUAKE: "Office of Emergency Management"
}
```

### 8. Evacuation Route Planning

**Decision**: Pre-defined NYC routes with capacity calculations

**Rationale**:
- Major evacuation routes are well-documented (FDR, West Side Highway, BQE, LIE)
- Capacity-based calculations for people per hour
- Bottleneck identification for traffic management
- Mock traffic data for demo, extensible for real API integration

**Key Routes**:
- FDR Drive: 4000 vehicles/hour capacity
- West Side Highway: 3500 vehicles/hour
- BQE: 5000 vehicles/hour
- LIE: 6000 vehicles/hour

### 9. Timeline Generation

**Decision**: Five-milestone standard timeline

**Rationale**:
- Aligns with ICS phases: immediate, short-term, medium-term, long-term, recovery
- Time offsets based on emergency type and severity
- Provides clear structure for response coordination

**Milestones**:
1. Initial Response Deployed (T+0)
2. Command Post Established (T+30 min)
3. Full Resource Deployment (T+3 hours)
4. Situation Assessment Complete (T+5 hours)
5. Response Transition to Recovery (T+duration)

### 10. Testing Strategy

**Decision**: pytest with pytest-asyncio, 80+ tests across 5 categories

**Rationale**:
- Async test support essential for orchestration testing
- Category breakdown ensures coverage:
  - Setup tests (infrastructure validation)
  - Model tests (Pydantic validation)
  - Service tests (weather, traffic, search)
  - Coordinator tests (orchestration logic)
  - Integration tests (end-to-end workflows)

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle API failures? | Graceful degradation to mock data within 2 seconds |
| What emergency types to support? | 7 types: hurricane, fire, flood, winter_storm, public_health, earthquake, infrastructure_failure |
| How to calculate resources? | Population-based with type multipliers, aligned with FEMA guidelines |
| What timeline structure? | 5 milestones following ICS phases |
| How to store historical data? | Azure AI Search (production), in-memory (MVP) |

## Dependencies Confirmed

```text
semantic-kernel>=1.37.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
aiohttp>=3.9.0
flask[async]>=3.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Weather API rate limits | Mock data fallback, caching |
| Complex multi-agent coordination | Start with single coordinator, add agents incrementally |
| Resource calculation accuracy | Document assumptions, allow configuration |
| External service availability | All services have mock implementations |
