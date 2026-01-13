# Tasks: Constituent Services Agent

**Input**: Design documents from `/specs/001-constituent-services-agent/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/api.yaml ✓, quickstart.md ✓

**Tests**: Tests are included based on the Evaluation Framework in spec.md (Azure AI Evaluation SDK, promptfoo red teaming).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- **Source**: `src/` (agent/, models/, services/, api/, config/)
- **Tests**: `tests/` (unit/, integration/, evaluation/)
- **Static**: `static/` (web interface)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Python environment setup

- [ ] T001 Create project directory structure per plan.md in Constituent-Services-Agent/
- [ ] T002 Initialize Python 3.11+ project with pyproject.toml and requirements.txt
- [ ] T003 [P] Create src/__init__.py with package initialization
- [ ] T004 [P] Create src/config/__init__.py and src/config/settings.py with environment configuration
- [ ] T005 [P] Create .env.example with all required environment variables from quickstart.md
- [ ] T006 [P] Configure ruff for linting and black for formatting in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Data Models (shared by all stories)

- [ ] T007 [P] Create MessageRole enum in src/models/__init__.py
- [ ] T008 [P] Create ConversationStatus enum in src/models/__init__.py
- [ ] T009 [P] Create Agency enum in src/models/__init__.py
- [ ] T010 [P] Create SupportedLanguage enum in src/models/__init__.py
- [ ] T011 [P] Create DocumentType enum in src/models/__init__.py
- [ ] T012 Create Conversation model in src/models/conversation.py with fields: id, session_id, language, created_at, updated_at, status, escalated, escalation_reason
- [ ] T013 [P] Create Message model in src/models/conversation.py with fields: id, conversation_id, role, content, original_content, timestamp, confidence, processing_time_ms
- [ ] T014 Create KnowledgeSource model in src/models/knowledge_source.py with fields: id, agency, title, content, summary, url, document_type, last_updated, indexing_status, chunk_count
- [ ] T015 [P] Create Citation model in src/models/knowledge_source.py with fields: id, message_id, source_id, quote, relevance_score, start_offset, end_offset

### Core Services (required by all stories)

- [ ] T016 Create base service factory pattern in src/services/__init__.py with USE_MOCK_SERVICES toggle
- [ ] T017 Implement MockFoundryIQKnowledgeBase class in src/agent/foundry_iq_client.py for offline development
- [ ] T018 Implement FoundryIQKnowledgeBase class in src/agent/foundry_iq_client.py with Azure AI Projects SDK
- [ ] T019 Implement knowledge_service.py in src/services/knowledge_service.py with agency content loading from sample_data/

### API Foundation

- [ ] T020 Create Flask app factory in src/main.py with CORS and middleware setup
- [ ] T021 Create API error handling middleware in src/api/middleware.py with Error schema from contracts/api.yaml
- [ ] T022 [P] Implement health check endpoint GET /health in src/api/routes.py per contracts/api.yaml
- [ ] T023 [P] Implement readiness check endpoint GET /health/ready in src/api/routes.py per contracts/api.yaml

### Sample Data

- [ ] T024 [P] Load DMV sample data in sample_data/nys_agencies/dmv.json
- [ ] T025 [P] Load DOL sample data in sample_data/nys_agencies/dol.json
- [ ] T026 [P] Load OTDA sample data in sample_data/nys_agencies/otda.json

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Service Inquiry (Priority: P1) 🎯 MVP

**Goal**: Enable constituents to ask questions about government services in plain language and receive accurate, citation-backed answers within 5 seconds

**Independent Test**: Ask "How do I apply for SNAP benefits?" and verify response includes eligibility requirements, application steps, and citation to OTDA documentation

### Tests for User Story 1

- [ ] T027 [P] [US1] Create unit test for ConstituentAgent in tests/unit/test_agent.py
- [ ] T028 [P] [US1] Create integration test for POST /chat endpoint in tests/integration/test_api.py
- [ ] T029 [P] [US1] Create evaluation test cases in tests/evaluation/test_cases.jsonl (8 Q&A scenarios from spec.md)

### Implementation for User Story 1

- [ ] T030 [US1] Implement ConstituentAgent class in src/agent/constituent_agent.py with query method and confidence scoring
- [ ] T031 [US1] Implement confidence scoring formula in src/agent/constituent_agent.py: 0.6 * model_confidence + 0.4 * min(citation_count / 3, 1.0)
- [ ] T032 [US1] Implement POST /chat endpoint in src/api/routes.py per ChatRequest/ChatResponse schemas from contracts/api.yaml
- [ ] T033 [US1] Implement GET /conversations/{session_id} endpoint in src/api/routes.py for conversation history
- [ ] T034 [US1] Implement DELETE /conversations/{session_id} endpoint in src/api/routes.py for session cleanup

### Web Interface for User Story 1

- [ ] T035 [P] [US1] Create index.html in static/index.html with WCAG 2.1 AA compliant chat layout
- [ ] T036 [P] [US1] Create chat.js in static/chat.js with session management and API integration
- [ ] T037 [P] [US1] Create styles.css in static/styles.css with 4.5:1 contrast ratio and focus indicators

### Demo Script for User Story 1

- [ ] T038 [US1] Create demo.py with mock mode demonstration of basic Q&A

**Checkpoint**: User Story 1 complete - Basic Q&A with citations works independently

---

## Phase 4: User Story 2 - Multi-Language Support (Priority: P2)

**Goal**: Enable non-English speaking residents to interact with the agent in their preferred language (8 supported languages)

**Independent Test**: Submit inquiry in Spanish "¿Cómo puedo solicitar beneficios de SNAP?" and verify response is in Spanish with accurate translation

### Tests for User Story 2

- [ ] T039 [P] [US2] Create unit test for translation_service in tests/unit/test_translation.py
- [ ] T040 [P] [US2] Create unit test for MultilingualAgent in tests/unit/test_agent.py

### Implementation for User Story 2

- [ ] T041 [P] [US2] Implement MockMultilingualAgent class in src/agent/multilingual_agent.py for offline development
- [ ] T042 [US2] Implement translation_service.py in src/services/translation_service.py with Azure Translator API
- [ ] T043 [US2] Implement language detection in src/agent/multilingual_agent.py with detect-translate-process-translate pattern
- [ ] T044 [US2] Update ConstituentAgent in src/agent/constituent_agent.py to wrap with MultilingualAgent
- [ ] T045 [US2] Update POST /chat endpoint in src/api/routes.py to return language and original_response fields

### Web Interface for User Story 2

- [ ] T046 [US2] Update chat.js in static/chat.js to display detected language and original response option

**Checkpoint**: User Story 2 complete - Multi-language support works independently

---

## Phase 5: User Story 3 - Benefits Eligibility Pre-Screening (Priority: P3)

**Goal**: Help residents understand if they might be eligible for benefits before starting an application with clear disclaimers

**Independent Test**: Ask "Am I eligible for Medicaid?" and verify agent asks income/household questions and provides preliminary guidance with disclaimer

### Tests for User Story 3

- [ ] T047 [P] [US3] Create unit test for eligibility screening logic in tests/unit/test_agent.py

### Implementation for User Story 3

- [ ] T048 [US3] Add eligibility screening prompts to ConstituentAgent system instructions in src/agent/constituent_agent.py
- [ ] T049 [US3] Implement eligibility question flow in src/agent/constituent_agent.py for SNAP, Medicaid, HEAP
- [ ] T050 [US3] Add disclaimer generation for benefits eligibility responses in src/agent/constituent_agent.py
- [ ] T051 [US3] Update ChatResponse to include disclaimer field handling in src/api/routes.py

**Checkpoint**: User Story 3 complete - Eligibility pre-screening works independently

---

## Phase 6: User Story 4 - Service Location Finder (Priority: P4)

**Goal**: Help residents find nearest office locations for in-person services with accessibility information

**Independent Test**: Ask "Where can I renew my driver's license near Albany?" and verify DMV locations returned with addresses and hours

### Tests for User Story 4

- [ ] T052 [P] [US4] Create unit test for location finder in tests/unit/test_knowledge.py

### Implementation for User Story 4

- [ ] T053 [P] [US4] Add location data to sample_data/nys_agencies/ JSON files with addresses, hours, accessibility info
- [ ] T054 [US4] Implement location search capability in src/services/knowledge_service.py
- [ ] T055 [US4] Update ConstituentAgent in src/agent/constituent_agent.py to handle location queries
- [ ] T056 [US4] Add suggested_actions to ChatResponse for location links in src/api/routes.py

**Checkpoint**: User Story 4 complete - Location finder works independently

---

## Phase 7: User Story 5 - Escalation to Human Agent (Priority: P5)

**Goal**: Enable smooth handoff to human agents when AI cannot adequately address an inquiry, preserving conversation context

**Independent Test**: Ask about a specific case number and verify agent offers human escalation with context transfer

### Tests for User Story 5

- [ ] T057 [P] [US5] Create unit test for escalation logic in tests/unit/test_agent.py
- [ ] T058 [P] [US5] Create integration test for POST /conversations/{session_id}/escalate in tests/integration/test_api.py

### Implementation for User Story 5

- [ ] T059 [US5] Implement escalation detection in src/agent/constituent_agent.py based on confidence threshold < 0.5
- [ ] T060 [US5] Implement POST /conversations/{session_id}/escalate endpoint in src/api/routes.py per contracts/api.yaml
- [ ] T061 [US5] Update ConstituentAgent to offer escalation proactively when confidence is low in src/agent/constituent_agent.py
- [ ] T062 [US5] Add suggested_actions with type "escalate" to ChatResponse in src/api/routes.py

### Web Interface for User Story 5

- [ ] T063 [US5] Update chat.js in static/chat.js to display escalation option and handle escalation flow

**Checkpoint**: User Story 5 complete - Human escalation works independently

---

## Phase 8: LOADinG Act Compliance & Audit Logging

**Purpose**: Implement audit trail for NY LOADinG Act transparency requirements

- [ ] T064 Create InteractionLog model in src/models/interaction_log.py with fields: id, message_id, query_hash, response_hash, model_version, latency_ms, token_count_input, token_count_output, sources_count, confidence_score, created_at
- [ ] T065 [P] Create UserFeedback model in src/models/interaction_log.py with fields: id, message_id, rating, helpful, comment, created_at
- [ ] T066 Implement MockAuditService in src/services/audit_service.py for offline development
- [ ] T067 Implement audit_service.py in src/services/audit_service.py with Cosmos DB integration
- [ ] T068 Update ConstituentAgent in src/agent/constituent_agent.py to log all interactions via audit_service
- [ ] T069 Implement POST /feedback endpoint in src/api/routes.py per FeedbackRequest schema from contracts/api.yaml

---

## Phase 9: Evaluation Framework & Red Teaming

**Purpose**: Implement quality and safety evaluation per spec.md evaluation framework

- [ ] T070 [P] Create red team test cases in tests/evaluation/red_team_cases.jsonl (8 adversarial scenarios from spec.md)
- [ ] T071 [P] Create promptfoo configuration in tests/evaluation/promptfoo.yaml for red teaming
- [ ] T072 Implement run_evals.py in tests/evaluation/run_evals.py with GroundednessEvaluator, RelevanceEvaluator, CoherenceEvaluator, FluencyEvaluator, ContentSafetyEvaluator
- [ ] T073 Add safety guardrails to ConstituentAgent in src/agent/constituent_agent.py for jailbreak/PII extraction prevention

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, accessibility validation, and demo preparation

- [ ] T074 [P] Create README.md in Constituent-Services-Agent/README.md with setup and usage instructions
- [ ] T075 Validate WCAG 2.1 AA compliance in static/ files using axe DevTools
- [ ] T076 [P] Add ARIA live regions for dynamic chat content in static/index.html
- [ ] T077 Add keyboard navigation support in static/chat.js
- [ ] T078 Performance optimization: ensure < 5 second response time in src/agent/constituent_agent.py
- [ ] T079 Run quickstart.md validation end-to-end
- [ ] T080 Create demo presentation flow script in demo.py for hackathon showcase

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **LOADinG Act (Phase 8)**: Can start after Phase 2, independent of user stories
- **Evaluation (Phase 9)**: Depends on at least User Story 1 completion
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Basic Q&A) | Phase 2 only | Foundational complete |
| US2 (Multi-Language) | Phase 2 only | Foundational complete |
| US3 (Eligibility) | Phase 2, benefits from US1 | Foundational complete |
| US4 (Location) | Phase 2, benefits from US1 | Foundational complete |
| US5 (Escalation) | Phase 2, benefits from US1 | Foundational complete |

### Within Each User Story

1. Tests written and verified to FAIL before implementation
2. Models/data before services
3. Services before agent updates
4. Agent updates before API endpoints
5. API endpoints before web interface updates
6. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005, T006 can run in parallel

**Phase 2 (Foundational)**:
- T007-T011 (enums) can run in parallel
- T013, T015 can run in parallel after T012, T014
- T022, T023 (health endpoints) can run in parallel
- T024, T025, T026 (sample data) can run in parallel

**Phase 3+ (User Stories)**:
- Once Phase 2 completes, all user stories can start in parallel (if team capacity allows)
- All tests within a story marked [P] can run in parallel
- Web interface tasks marked [P] can run in parallel with implementation

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "T027 [P] [US1] Create unit test for ConstituentAgent"
Task: "T028 [P] [US1] Create integration test for POST /chat"
Task: "T029 [P] [US1] Create evaluation test cases"

# Launch all web interface tasks together:
Task: "T035 [P] [US1] Create index.html"
Task: "T036 [P] [US1] Create chat.js"
Task: "T037 [P] [US1] Create styles.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Day 1 Hackathon Target

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Basic Q&A with citations)
4. **STOP and VALIDATE**: Test with "How do I apply for SNAP benefits?"
5. Demo basic Q&A with citations in English

### Day 2 Expansion

1. Add User Story 2 (Multi-Language) → Test with Spanish query → Demo
2. Add Phase 8 (LOADinG Act) if time permits
3. Add Phase 9 (Evaluation) for demo quality validation

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. User Story 1 → Test independently → Demo (MVP!)
3. User Story 2 → Test independently → Demo (Multi-language!)
4. User Story 3 → Test independently → Demo (Eligibility!)
5. Each story adds value without breaking previous stories

### Hackathon Team Strategy (2-3 developers)

With multiple developers:

1. Team completes Setup + Foundational together (2-3 hours)
2. Once Foundational is done:
   - Developer A: User Story 1 (Basic Q&A) - **MVP Priority**
   - Developer B: User Story 2 (Multi-Language)
   - Developer C: Phase 8 (Audit Logging) + Phase 9 (Evaluation)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Mock services (USE_MOCK_SERVICES=true) enable offline development
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
