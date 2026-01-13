# Tasks: Document Eligibility Agent

**Input**: Design documents from `/specs/002-document-eligibility-agent/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/api.yaml ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
```text
Document-Eligibility-Agent/
├── src/
│   ├── agent/           # Document processing logic
│   ├── models/          # Data models
│   ├── services/        # Azure service integrations
│   ├── api/             # Flask routes
│   └── config/          # Settings
├── tests/
├── static/              # Web interface
└── sample_documents/    # Test fixtures
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan in Document-Eligibility-Agent/
- [x] T002 Create pyproject.toml with Python 3.11+ and dependencies (azure-ai-documentintelligence, flask, celery, redis, msgraph-sdk)
- [x] T003 [P] Create requirements.txt with all dependencies from plan.md
- [x] T004 [P] Create .env.example with all configuration variables from quickstart.md
- [x] T005 [P] Create src/__init__.py package file
- [x] T006 [P] Create src/config/__init__.py package file
- [x] T007 Create src/config/settings.py with pydantic-settings BaseSettings class

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Data Models (from data-model.md)

- [x] T008 [P] Create src/models/__init__.py with all enum exports (DocumentType, DocumentStatus, DocumentSource, DocumentPriority, ValidationStatus, PIIType, LogAction)
- [x] T009 [P] Create src/models/document.py with Document model (all fields from data-model.md)
- [x] T010 [P] Create src/models/extraction.py with Extraction model (confidence scoring, bounding box, PII flags)
- [x] T011 [P] Create src/models/processing_log.py with ProcessingLog model (audit trail for LOADinG Act)
- [x] T012 [P] Create src/models/validation_rule.py with ValidationRule model (configurable rules)
- [x] T013 [P] Create src/models/extraction_model.py with ExtractionModel model (Document Intelligence model tracking)

### Service Foundations

- [x] T014 Create src/services/__init__.py with service factory pattern and mock mode toggle
- [x] T015 [P] Create src/services/storage_service.py with Azure Blob Storage operations (mock + real implementations)
- [x] T016 [P] Create src/services/audit_service.py with LOADinG Act compliance logging

### API Foundation

- [x] T017 Create src/api/__init__.py package file
- [x] T018 Create src/api/middleware.py with error handling, request logging, CORS middleware
- [x] T019 Create src/main.py Flask application factory with Blueprint registration

### Sample Documents

- [x] T020 [P] Add sample_documents/w2_sample.pdf (test W-2 form)
- [x] T021 [P] Add sample_documents/paystub_sample.pdf (test pay stub)
- [x] T022 [P] Add sample_documents/utility_bill_sample.pdf (test utility bill)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Automated Document Intake (Priority: P1) 🎯 MVP

**Goal**: Documents automatically extracted from emails and categorized for processing

**Independent Test**: Send email with PDF attachment to intake mailbox and verify document appears in processing queue within 2 minutes

### Implementation for User Story 1

- [x] T023 [P] [US1] Create src/services/email_service.py with Microsoft Graph API integration (mock + real) for mailbox monitoring
- [x] T024 [P] [US1] Create src/agent/__init__.py package file
- [x] T025 [US1] Create src/agent/document_processor.py with main orchestration (email polling, attachment extraction, document queuing)
- [x] T026 [US1] Create src/services/document_intelligence.py with Azure Document Intelligence wrapper (mock + real) for document type classification
- [x] T027 [US1] Implement document categorization logic in src/agent/document_processor.py (income, identity, residency, medical)
- [x] T028 [US1] Implement duplicate detection using content_hash in src/agent/document_processor.py
- [x] T029 [US1] Add processing status logging via audit_service in src/agent/document_processor.py
- [x] T030 [US1] Create src/api/routes.py with POST /documents endpoint (manual upload alternative to email)
- [x] T031 [US1] Add GET /queue endpoint to src/api/routes.py for viewing processing queue
- [x] T032 [US1] Add GET /health endpoint to src/api/routes.py for service health checks

**Checkpoint**: Document intake from email/upload working, documents appear in queue

---

## Phase 4: User Story 2 - Intelligent Data Extraction (Priority: P2)

**Goal**: Key data fields automatically extracted from documents with confidence scores

**Independent Test**: Upload W-2 form and verify employer name, wages, and tax year are extracted with >90% confidence

### Implementation for User Story 2

- [x] T033 [US2] Create src/agent/extraction_agent.py with field extraction logic using Document Intelligence
- [x] T034 [US2] Implement W-2 field mapping in src/agent/extraction_agent.py (employer_name, employer_ein, employee_ssn, wages, federal_tax, tax_year)
- [x] T035 [US2] Implement pay stub field mapping in src/agent/extraction_agent.py (employer_name, employee_name, gross_pay, net_pay, pay_period, pay_date)
- [x] T036 [US2] Implement utility bill field mapping in src/agent/extraction_agent.py (provider_name, account_number, service_address, billing_date, amount_due)
- [x] T037 [US2] Implement confidence score calculation in src/agent/extraction_agent.py (0.5*OCR + 0.3*field + 0.2*validation)
- [x] T038 [US2] Implement low-confidence highlighting logic in src/agent/extraction_agent.py (threshold: 0.85)
- [x] T039 [US2] Add GET /extractions/{document_id} endpoint to src/api/routes.py
- [x] T040 [US2] Add PATCH /extractions/{document_id}/fields/{field_name} endpoint for manual corrections in src/api/routes.py
- [x] T041 [US2] Integrate extraction_agent into document_processor.py pipeline

**Checkpoint**: Documents are extracted with field values and confidence scores visible

---

## Phase 5: User Story 3 - Document Validation (Priority: P3)

**Goal**: Documents automatically checked for common issues with pass/fail/review status

**Independent Test**: Upload income document dated 90 days ago and verify system flags as potentially outdated

### Implementation for User Story 3

- [x] T042 [US3] Create src/agent/validation_agent.py with validation rule engine
- [x] T043 [US3] Implement document age validation in src/agent/validation_agent.py (60 days for income, 30 days for bank, 2 years for W-2)
- [x] T044 [US3] Implement document completeness validation in src/agent/validation_agent.py (all pages present check)
- [x] T045 [US3] Implement quality/alteration detection in src/agent/validation_agent.py (blur, rotation, potential edits)
- [x] T046 [US3] Implement cross-reference validation in src/agent/validation_agent.py (name matching, address matching)
- [x] T047 [US3] Implement validation result aggregation in src/agent/validation_agent.py (passed/failed/warning/pending)
- [x] T048 [US3] Integrate validation_agent into document_processor.py pipeline (after extraction)
- [x] T049 [US3] Update GET /documents/{document_id} endpoint to include validation results in src/api/routes.py

**Checkpoint**: Documents show validation status with clear pass/fail/review indicators

---

## Phase 6: User Story 4 - PII Detection and Redaction (Priority: P4)

**Goal**: Sensitive information automatically identified and protected with audit logging

**Independent Test**: Upload document with SSN and verify it's masked in queue view but visible to authorized reviewer

### Implementation for User Story 4

- [ ] T050 [US4] Create src/services/pii_service.py with Azure AI Language PII detection integration (mock + real)
- [ ] T051 [US4] Implement SSN detection and masking in src/services/pii_service.py
- [ ] T052 [US4] Implement bank account detection and masking in src/services/pii_service.py
- [ ] T053 [US4] Implement DOB and address PII detection in src/services/pii_service.py
- [ ] T054 [US4] Implement display_value masking logic in src/models/extraction.py
- [ ] T055 [US4] Add PII access audit logging to src/services/audit_service.py (PII_ACCESSED action)
- [ ] T056 [US4] Add include_pii query parameter to GET /extractions/{document_id} in src/api/routes.py (requires permission)
- [ ] T057 [US4] Implement PII redaction for exports in src/services/storage_service.py
- [ ] T058 [US4] Update GET /documents/{document_id}/download to support redact_pii parameter in src/api/routes.py

**Checkpoint**: PII is masked by default, revealed only with proper authorization and audit logging

---

## Phase 7: User Story 5 - Case Routing and Assignment (Priority: P5)

**Goal**: Documents automatically routed to appropriate workers based on case type and workload

**Independent Test**: Submit SNAP-related document and verify it's routed to SNAP-specialized worker queue

### Implementation for User Story 5

- [ ] T059 [US5] Create src/services/routing_service.py with document routing logic
- [ ] T060 [US5] Implement case type routing rules in src/services/routing_service.py (match document type to worker specialization)
- [ ] T061 [US5] Implement priority flagging in src/services/routing_service.py (expedited, resubmission detection)
- [ ] T062 [US5] Implement workload balancing in src/services/routing_service.py (consider current queue sizes)
- [ ] T063 [US5] Add supervisor routing rule configuration in src/services/routing_service.py
- [ ] T064 [US5] Add manual reassignment capability to PUT /documents/{document_id}/assign in src/api/routes.py
- [ ] T065 [US5] Integrate routing_service into document_processor.py pipeline (after validation)
- [ ] T066 [US5] Add assigned_to filter to GET /queue endpoint in src/api/routes.py

**Checkpoint**: Documents are automatically routed to appropriate workers, supervisors can configure rules

---

## Phase 8: User Story 6 - Batch Processing Dashboard (Priority: P6)

**Goal**: Efficient workflow for processing multiple documents with bulk actions

**Independent Test**: Load queue of 10 documents and verify bulk approval completes in <30 seconds

### Implementation for User Story 6

- [x] T067 [US6] Create static/index.html with queue dashboard layout (WCAG 2.1 AA compliant)
- [x] T068 [US6] Create static/styles.css with accessible styling (4.5:1 contrast ratios, focus indicators)
- [x] T069 [US6] Create static/queue.js with queue interaction logic (filtering, sorting, selection)
- [x] T070 [US6] Implement bulk approval action in static/queue.js
- [x] T071 [US6] Implement bulk request-resubmission action in static/queue.js
- [x] T072 [US6] Add keyboard shortcuts for common actions in static/queue.js (approve, reject, next, previous)
- [x] T073 [US6] Add progress tracking and daily statistics display in static/queue.js
- [x] T074 [US6] Implement auto-save for partial reviews in static/queue.js
- [x] T075 [US6] Add POST /queue/bulk-approve endpoint to src/api/routes.py
- [x] T076 [US6] Add GET /queue/stats endpoint to src/api/routes.py for statistics
- [x] T077 [US6] Add POST /documents/{document_id}/approve endpoint to src/api/routes.py
- [x] T078 [US6] Add POST /documents/{document_id}/reject endpoint to src/api/routes.py
- [x] T079 [US6] Add POST /documents/{document_id}/reprocess endpoint to src/api/routes.py

**Checkpoint**: Workers can efficiently process documents in batch with keyboard navigation and bulk actions

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T080 Create demo.py script for running mock mode demonstration
- [x] T081 [P] Update src/main.py to serve static files from static/ directory
- [x] T082 [P] Add DELETE /documents/{document_id} endpoint to src/api/routes.py
- [x] T083 [P] Add GET /health/ready endpoint to src/api/routes.py for readiness checks
- [ ] T084 Implement Celery task queue integration in src/agent/document_processor.py for async processing
- [ ] T085 [P] Create tests/unit/test_extraction.py with extraction agent unit tests
- [ ] T086 [P] Create tests/unit/test_validation.py with validation agent unit tests
- [ ] T087 [P] Create tests/unit/test_document.py with document model unit tests
- [ ] T088 [P] Create tests/integration/test_api.py with API endpoint integration tests
- [ ] T089 [P] Create tests/integration/test_document_intelligence.py with Document Intelligence integration tests
- [ ] T090 Create tests/evaluation/test_cases.jsonl with 8 document processing scenarios
- [ ] T091 Create tests/evaluation/red_team_cases.jsonl with 8 adversarial test cases
- [ ] T092 Create tests/evaluation/run_evals.py evaluation runner script
- [ ] T093 Run quickstart.md validation to verify setup instructions work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Polish (Phase 9)**: Depends on at least User Stories 1-3 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Builds on US1 document intake
- **User Story 3 (P3)**: Can start after Foundational - Requires extraction from US2
- **User Story 4 (P4)**: Can start after Foundational - Works with extractions from US2
- **User Story 5 (P5)**: Can start after Foundational - Works after validation from US3
- **User Story 6 (P6)**: Can start after Foundational - UI for all document operations

### Recommended Implementation Order

For a single developer:
```
Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 9 (MVP complete)
                                                   → Phase 6 (US4) → Phase 7 (US5) → Phase 8 (US6)
```

### Parallel Opportunities

Within each phase, tasks marked [P] can run in parallel:

**Phase 2 Parallel Group**:
- T008, T009, T010, T011, T012, T013 (all models)
- T015, T016 (services)
- T020, T021, T022 (sample documents)

**Phase 9 Parallel Group**:
- T085, T086, T087 (unit tests)
- T088, T089 (integration tests)

---

## Parallel Example: Foundation Phase

```bash
# Launch all models in parallel:
Task: "Create src/models/__init__.py with enums"
Task: "Create src/models/document.py with Document model"
Task: "Create src/models/extraction.py with Extraction model"
Task: "Create src/models/processing_log.py with ProcessingLog model"
Task: "Create src/models/validation_rule.py with ValidationRule model"
Task: "Create src/models/extraction_model.py with ExtractionModel model"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only) - Hackathon Day 1-2

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Document Intake)
4. **CHECKPOINT**: Test email/upload intake independently
5. Complete Phase 4: User Story 2 (Data Extraction)
6. **CHECKPOINT**: Test extraction with sample W-2
7. Complete Phase 5: User Story 3 (Validation)
8. **CHECKPOINT**: Test validation rules
9. Complete essential Phase 9 tasks (demo.py, basic tests)
10. **DEMO READY**: MVP with intake, extraction, validation

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test intake → Basic queue visible
3. Add User Story 2 → Test extraction → See extracted fields
4. Add User Story 3 → Test validation → See pass/fail status
5. Add User Story 4 → Test PII masking → See masked SSNs
6. Add User Story 5 → Test routing → Documents auto-assigned
7. Add User Story 6 → Test dashboard → Efficient bulk processing

### Post-Hackathon Scope

- Additional document types (bank statements, driver's licenses, leases)
- Custom model training for specialized documents
- Case management system integration
- Mobile document capture
- Fraud detection patterns

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Mock mode (USE_MOCK_SERVICES=true) for offline development
- All Azure services have mock implementations for hackathon
- Confidence threshold 0.85 for auto-approval
- 7-year retention for compliance (LOADinG Act)

---

## Summary

| Phase | User Story | Task Count | Parallel Tasks |
|-------|------------|------------|----------------|
| 1 | Setup | 7 | 4 |
| 2 | Foundational | 15 | 11 |
| 3 | US1: Document Intake | 10 | 2 |
| 4 | US2: Data Extraction | 9 | 0 |
| 5 | US3: Validation | 8 | 0 |
| 6 | US4: PII Detection | 9 | 0 |
| 7 | US5: Case Routing | 8 | 0 |
| 8 | US6: Batch Dashboard | 13 | 0 |
| 9 | Polish | 14 | 8 |
| **Total** | | **93** | **25** |

**MVP Scope**: Phases 1-5 + minimal Phase 9 = ~49 tasks
**Full Implementation**: All 93 tasks
