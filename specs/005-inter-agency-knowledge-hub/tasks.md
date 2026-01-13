# Tasks: Inter-Agency Knowledge Hub

**Input**: Design documents from `/specs/005-inter-agency-knowledge-hub/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Tests are included as this is a security-critical system requiring validation of permission filtering and audit compliance.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `Inter-Agency-Knowledge-Hub/src/`, `Inter-Agency-Knowledge-Hub/tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per plan.md in Inter-Agency-Knowledge-Hub/
- [ ] T002 Initialize Python 3.11+ project with pyproject.toml and requirements.txt
- [ ] T003 [P] Configure pytest and ruff for testing and linting
- [ ] T004 [P] Create .env.example with all required environment variables from quickstart.md
- [ ] T005 [P] Create src/__init__.py and package structure (core/, services/, plugins/, config/)
- [ ] T006 [P] Create tests/__init__.py and test directory structure (unit/, integration/, contract/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration & Settings

- [ ] T007 Implement Settings class with pydantic-settings in src/config/settings.py
- [ ] T008 [P] Implement mock service toggle and fallback configuration in src/config/settings.py

### Core Enumerations & Base Models

- [ ] T009 [P] Create Agency enum (DMV, DOL, OTDA, DOH, OGS) in src/models/enums.py
- [ ] T010 [P] Create DocumentClassification enum (PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL) in src/models/enums.py
- [ ] T011 [P] Create RelationshipType enum (SIMILAR_TOPIC, DEPENDENCY, SUPERSEDES, CONFLICT, RELATED) in src/models/enums.py
- [ ] T012 [P] Create ReviewStatus enum (PENDING, APPROVED, MODIFIED, REJECTED) in src/models/enums.py
- [ ] T013 [P] Create ActionType enum (SEARCH, VIEW, EXPORT, CROSS_REFERENCE) in src/models/enums.py

### Shared Models

- [ ] T014 Create DocumentCitation Pydantic model in src/models/document.py
- [ ] T015 [P] Create AgencySource Pydantic model in src/models/agency.py
- [ ] T016 [P] Create UserPermissions Pydantic model in src/models/user.py

### Azure AI Search Integration

- [ ] T017 Implement SearchEngine base class with Azure AI Search SDK in src/core/search_engine.py
- [ ] T018 Implement MockSearchEngine fallback for offline development in src/core/search_engine.py
- [ ] T019 [P] Create index configuration for agency document schemas in src/core/search_engine.py

### Authentication & Authorization

- [ ] T020 Implement EntraAuthenticator with MSAL in src/core/auth.py
- [ ] T021 Implement MockAuthenticator for offline development in src/core/auth.py
- [ ] T022 Implement JWT token validation middleware in src/middleware/auth_middleware.py
- [ ] T023 Implement get_user_groups() method for Entra ID group extraction in src/core/auth.py

### Flask API Foundation

- [ ] T024 Create Flask application factory in src/main.py
- [ ] T025 [P] Implement health check endpoint GET /api/v1/health in src/routes/health.py
- [ ] T026 [P] Implement error handling middleware in src/middleware/error_handler.py
- [ ] T027 Configure CORS and request/response logging in src/main.py

### Database & Audit Infrastructure

- [ ] T028 Setup SQLite database connection with aiosqlite in src/db/database.py
- [ ] T029 Create audit_logs table schema in src/db/schema.py
- [ ] T030 Implement async write operations for audit logs in src/db/database.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Search Across Agencies (Priority: P1) 🎯 MVP

**Goal**: Enable unified search across 5 NYS agency knowledge bases with relevance-ranked results

**Independent Test**: Enter a search query (e.g., "remote work policy"), receive relevant documents from multiple agencies with source citations.

### Tests for User Story 1

- [ ] T031 [P] [US1] Contract test for POST /api/v1/search in tests/contract/test_search.py
- [ ] T032 [P] [US1] Integration test for cross-agency search in tests/integration/test_search.py
- [ ] T033 [P] [US1] Unit test for SearchEngine.search() method in tests/unit/test_search_engine.py

### Implementation for User Story 1

- [ ] T034 [P] [US1] Create SearchQuery Pydantic model in src/models/search.py
- [ ] T035 [P] [US1] Create SearchResult Pydantic model in src/models/search.py
- [ ] T036 [P] [US1] Create SearchResponse Pydantic model in src/models/search.py
- [ ] T037 [US1] Implement SearchEngine.search() with Azure AI Search cross-index query in src/core/search_engine.py
- [ ] T038 [US1] Implement relevance scoring and ranking algorithm in src/core/search_engine.py
- [ ] T039 [US1] Implement pagination (page, page_size, total_results) in search results in src/core/search_engine.py
- [ ] T040 [US1] Implement snippet extraction with keyword highlighting in src/core/search_engine.py
- [ ] T041 [US1] Implement CitationBuilder for standardized citation assembly in src/core/citation_builder.py
- [ ] T042 [US1] Implement SearchService orchestration layer in src/services/search_service.py
- [ ] T043 [US1] Implement POST /api/v1/search endpoint in src/routes/search.py
- [ ] T044 [US1] Add query validation and sanitization in src/routes/search.py
- [ ] T045 [US1] Add response time tracking in search endpoint in src/routes/search.py
- [ ] T046 [US1] Implement empty result handling with query suggestions in src/services/search_service.py

**Checkpoint**: User Story 1 complete - users can search across agencies and get cited results

---

## Phase 4: User Story 2 - Permission-Aware Results (Priority: P2)

**Goal**: Filter search results based on user's Entra ID permissions to enforce document-level security

**Independent Test**: Search with different user accounts (DMV employee vs DOL employee), verify each user only sees documents they're authorized to access.

### Tests for User Story 2

- [ ] T047 [P] [US2] Contract test for permission filtering in tests/contract/test_permissions.py
- [ ] T048 [P] [US2] Integration test for permission-aware search in tests/integration/test_permissions.py
- [ ] T049 [P] [US2] Unit test for PermissionFilter.build_security_filter() in tests/unit/test_permission_filter.py

### Implementation for User Story 2

- [ ] T050 [P] [US2] Create IndexedDocument Pydantic model with permissions field in src/models/document.py
- [ ] T051 [US2] Implement PermissionFilter class in src/core/permission_filter.py
- [ ] T052 [US2] Implement build_security_filter() for Azure AI Search OData filter in src/core/permission_filter.py
- [ ] T053 [US2] Implement group-based permission hierarchy (Agency_Staff, Agency_Manager, Agency_Admin) in src/core/permission_filter.py
- [ ] T054 [US2] Implement cross-agency permission handling (AllAgencies_*) in src/core/permission_filter.py
- [ ] T055 [US2] Integrate PermissionFilter into SearchService.search() in src/services/search_service.py
- [ ] T056 [US2] Implement permission caching with 15-minute TTL in src/core/permission_filter.py
- [ ] T057 [US2] Implement GET /api/v1/user/permissions endpoint in src/routes/user.py
- [ ] T058 [US2] Handle permission changes during active session in src/core/permission_filter.py

**Checkpoint**: User Story 2 complete - search results are filtered by user permissions

---

## Phase 5: User Story 3 - Citation Tracking (Priority: P3)

**Goal**: Provide complete citation metadata and audit logging for LOADinG Act compliance

**Independent Test**: Perform a search, verify each result includes document title, agency source, publication date, and direct link to original document.

### Tests for User Story 3

- [ ] T059 [P] [US3] Contract test for GET /api/v1/audit/logs in tests/contract/test_audit.py
- [ ] T060 [P] [US3] Contract test for POST /api/v1/audit/logs/export in tests/contract/test_audit.py
- [ ] T061 [P] [US3] Integration test for audit log creation in tests/integration/test_audit.py
- [ ] T062 [P] [US3] Unit test for AuditService.log_access() in tests/unit/test_audit_service.py

### Implementation for User Story 3

- [ ] T063 [P] [US3] Create AccessLog Pydantic model in src/models/audit.py
- [ ] T064 [US3] Implement AuditService class in src/services/audit_service.py
- [ ] T065 [US3] Implement async log_access() with SQLite persistence in src/services/audit_service.py
- [ ] T066 [US3] Implement access logging for SEARCH, VIEW, EXPORT, CROSS_REFERENCE actions in src/services/audit_service.py
- [ ] T067 [US3] Integrate AuditService into SearchService for automatic search logging in src/services/search_service.py
- [ ] T068 [US3] Implement GET /api/v1/audit/logs endpoint (admin only) in src/routes/audit.py
- [ ] T069 [US3] Implement audit log filtering (user_id, action, date_range) in src/routes/audit.py
- [ ] T070 [US3] Implement POST /api/v1/audit/logs/export endpoint in src/routes/audit.py
- [ ] T071 [US3] Implement JSON and CSV export formats in src/services/audit_service.py
- [ ] T072 [US3] Add IP address and session tracking to audit logs in src/services/audit_service.py
- [ ] T073 [US3] Implement 7-year retention policy documentation in assets/compliance/retention_policy.md

**Checkpoint**: User Story 3 complete - all access is logged and citations are tracked

---

## Phase 6: User Story 4 - Cross-Agency References (Priority: P4)

**Goal**: Identify and display semantically related policies from other agencies

**Independent Test**: View a policy document, see "Related Policies" section showing semantically similar documents from other agencies.

### Tests for User Story 4

- [ ] T074 [P] [US4] Contract test for GET /api/v1/documents/{id}/cross-references in tests/contract/test_cross_refs.py
- [ ] T075 [P] [US4] Integration test for cross-reference detection in tests/integration/test_cross_refs.py
- [ ] T076 [P] [US4] Unit test for CrossReferenceService.find_related() in tests/unit/test_cross_refs.py

### Implementation for User Story 4

- [ ] T077 [P] [US4] Create CrossReference Pydantic model in src/models/cross_reference.py
- [ ] T078 [US4] Implement CrossReferenceService class in src/services/cross_reference_service.py
- [ ] T079 [US4] Implement vector similarity search using Azure AI Search embeddings in src/services/cross_reference_service.py
- [ ] T080 [US4] Implement classify_relationship() for relationship type detection in src/services/cross_reference_service.py
- [ ] T081 [US4] Implement configurable min_confidence threshold (default 0.7) in src/services/cross_reference_service.py
- [ ] T082 [US4] Implement GET /api/v1/documents/{document_id} endpoint in src/routes/documents.py
- [ ] T083 [US4] Implement GET /api/v1/documents/{document_id}/cross-references endpoint in src/routes/documents.py
- [ ] T084 [US4] Filter cross-references by user permissions in src/services/cross_reference_service.py
- [ ] T085 [US4] Log CROSS_REFERENCE actions in audit service in src/services/cross_reference_service.py

**Checkpoint**: User Story 4 complete - related policies are discoverable across agencies

---

## Phase 7: User Story 5 - Human-in-the-Loop Review (Priority: P5)

**Goal**: Flag complex queries for administrator review before delivering results

**Independent Test**: Submit a complex query involving multiple agencies and sensitive topics, verify the system flags it for review and notifies administrators.

### Tests for User Story 5

- [ ] T086 [P] [US5] Contract test for GET /api/v1/reviews in tests/contract/test_reviews.py
- [ ] T087 [P] [US5] Contract test for PUT /api/v1/reviews/{flag_id} in tests/contract/test_reviews.py
- [ ] T088 [P] [US5] Integration test for query flagging workflow in tests/integration/test_reviews.py
- [ ] T089 [P] [US5] Unit test for ReviewCriteria matching logic in tests/unit/test_review_service.py

### Implementation for User Story 5

- [ ] T090 [P] [US5] Create ReviewFlag Pydantic model in src/models/review.py
- [ ] T091 [P] [US5] Create ReviewCriteria configuration model in src/models/review.py
- [ ] T092 [P] [US5] Create ReviewUpdateRequest Pydantic model in src/models/review.py
- [ ] T093 [US5] Implement ReviewService class in src/services/review_service.py
- [ ] T094 [US5] Implement review criteria matching (multi_agency_conflict, sensitive_keywords, low_confidence, flagged_topics) in src/services/review_service.py
- [ ] T095 [US5] Implement flag_query() to create ReviewFlag records in src/services/review_service.py
- [ ] T096 [US5] Integrate review flagging into SearchService.search() in src/services/search_service.py
- [ ] T097 [US5] Return 202 Accepted with ReviewPendingResponse when query is flagged in src/routes/search.py
- [ ] T098 [US5] Implement GET /api/v1/reviews endpoint (admin only) in src/routes/reviews.py
- [ ] T099 [US5] Implement GET /api/v1/reviews/{flag_id} endpoint in src/routes/reviews.py
- [ ] T100 [US5] Implement PUT /api/v1/reviews/{flag_id} endpoint for approve/modify/reject in src/routes/reviews.py
- [ ] T101 [US5] Implement configurable review criteria via assets/review_criteria.json in src/services/review_service.py
- [ ] T102 [US5] Add admin notification placeholder for flagged queries in src/services/review_service.py

**Checkpoint**: User Story 5 complete - complex queries are flagged for human review

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Agency Management

- [ ] T103 [P] Implement GET /api/v1/agencies endpoint in src/routes/agencies.py
- [ ] T104 [P] Implement GET /api/v1/agencies/{agency_id} endpoint in src/routes/agencies.py
- [ ] T105 Create agency configuration files in assets/agency_configs/ (dmv.json, dol.json, otda.json, doh.json, ogs.json)

### User Features

- [ ] T106 Implement GET /api/v1/user/search-history endpoint in src/routes/user.py
- [ ] T107 [P] Create SearchQuerySummary model for search history in src/models/search.py

### Demo & Setup Scripts

- [ ] T108 [P] Create demo.py interactive demonstration script
- [ ] T109 [P] Create setup_knowledge_bases.py for index creation with sample data
- [ ] T110 Create sample_queries/ test data in assets/sample_queries/

### Semantic Kernel Integration

- [ ] T111 Implement KnowledgeHubPlugin for Semantic Kernel in src/plugins/knowledge_hub_plugin.py
- [ ] T112 [P] Configure Foundry IQ integration for intelligent retrieval in src/plugins/knowledge_hub_plugin.py

### Performance & Reliability

- [ ] T113 [P] Add request rate limiting middleware in src/middleware/rate_limiter.py
- [ ] T114 [P] Add response caching for repeated searches in src/core/search_engine.py
- [ ] T115 Implement graceful degradation when Azure services unavailable in src/core/search_engine.py
- [ ] T116 Add performance monitoring and metrics in src/middleware/metrics.py

### Security Hardening

- [ ] T117 [P] Input validation and sanitization for all endpoints
- [ ] T118 [P] SQL injection prevention in audit queries in src/db/database.py
- [ ] T119 Security headers configuration in Flask app

### Final Validation

- [ ] T120 Run quickstart.md validation steps
- [ ] T121 Verify all API endpoints match openapi.yaml contract
- [ ] T122 Run full test suite and ensure >80% coverage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 SearchService but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 SearchService but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses search infrastructure but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Integrates with US1 SearchService but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /api/v1/search in tests/contract/test_search.py"
Task: "Integration test for cross-agency search in tests/integration/test_search.py"
Task: "Unit test for SearchEngine.search() method in tests/unit/test_search_engine.py"

# Launch all models for User Story 1 together:
Task: "Create SearchQuery Pydantic model in src/models/search.py"
Task: "Create SearchResult Pydantic model in src/models/search.py"
Task: "Create SearchResponse Pydantic model in src/models/search.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (6 tasks)
2. Complete Phase 2: Foundational (24 tasks)
3. Complete Phase 3: User Story 1 (16 tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**MVP Total**: 46 tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (permission-aware)
4. Add User Story 3 → Test independently → Deploy/Demo (audit compliant)
5. Add User Story 4 → Test independently → Deploy/Demo (cross-references)
6. Add User Story 5 → Test independently → Deploy/Demo (human review)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core search)
   - Developer B: User Story 2 (permissions)
   - Developer C: User Story 3 (audit)
3. Stories complete and integrate independently

---

## Task Summary

| Phase | Description | Tasks | Parallel |
|-------|-------------|-------|----------|
| Phase 1 | Setup | 6 | 4 |
| Phase 2 | Foundational | 24 | 15 |
| Phase 3 | US1 - Search Across Agencies | 16 | 6 |
| Phase 4 | US2 - Permission-Aware Results | 12 | 4 |
| Phase 5 | US3 - Citation Tracking | 15 | 5 |
| Phase 6 | US4 - Cross-Agency References | 12 | 4 |
| Phase 7 | US5 - Human-in-the-Loop Review | 17 | 5 |
| Phase 8 | Polish & Cross-Cutting | 20 | 12 |
| **Total** | | **122** | **55** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
