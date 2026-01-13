# Tasks: Policy Compliance Checker

**Input**: Design documents from `/specs/004-policy-compliance-checker/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Tests are included as the specification mentions a test suite with 59 tests across multiple categories.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project root**: `Policy-Compliance-Checker/`
- **Source code**: `src/`
- **Tests**: `tests/`
- **Assets**: `assets/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan (src/core/, src/plugins/, src/config/, src/services/, tests/, assets/)
- [ ] T002 Initialize Python 3.11+ project with pyproject.toml and requirements.txt
- [ ] T003 [P] Configure pytest 8.4.2+ with test directories (tests/contract/, tests/integration/, tests/unit/)
- [ ] T004 [P] Create .env.example with Azure OpenAI configuration template
- [ ] T005 [P] Configure ruff for linting and formatting

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create Severity enum (CRITICAL, HIGH, MEDIUM, LOW) in src/models/enums.py
- [ ] T007 [P] Create DocumentFormat enum (PDF, DOCX, MARKDOWN, TEXT) in src/models/enums.py
- [ ] T008 [P] Create RuleCategory enum (DATA_PROTECTION, HR_POLICY, IT_SECURITY, LEGAL_COMPLIANCE, ACCESSIBILITY, CUSTOM) in src/models/enums.py
- [ ] T009 [P] Create AnalysisStatus enum (PENDING, PROCESSING, COMPLETED, FAILED) in src/models/enums.py
- [ ] T010 Implement Settings class with Pydantic Settings in src/config/settings.py
- [ ] T011 [P] Create base Pydantic models for API responses in src/models/base.py
- [ ] T012 [P] Setup Flask 3.x application factory in src/app.py
- [ ] T013 Setup error handling middleware for Flask in src/middleware/error_handler.py
- [ ] T014 [P] Create logging configuration in src/config/logging.py
- [ ] T015 Setup Semantic Kernel 1.37.0 with Azure OpenAI integration in src/plugins/kernel_setup.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Upload and Analyze Policy Document (Priority: P1) MVP

**Goal**: Enable users to upload policy documents (PDF, DOCX, Markdown) and receive automated compliance analysis

**Independent Test**: Upload a sample policy document (e.g., employee code of conduct), receive analysis results with identified violations and recommendations within 30 seconds

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Contract test for POST /documents endpoint in tests/contract/test_documents_api.py
- [ ] T017 [P] [US1] Contract test for POST /documents/{id}/analyze endpoint in tests/contract/test_analyze_api.py
- [ ] T018 [P] [US1] Unit tests for DocumentParser in tests/unit/test_document_parser.py
- [ ] T019 [P] [US1] Integration test for document upload and analysis workflow in tests/integration/test_document_analysis.py

### Implementation for User Story 1

- [ ] T020 [P] [US1] Create PolicyDocument Pydantic model in src/models/policy_document.py
- [ ] T021 [P] [US1] Create DocumentSection Pydantic model in src/models/policy_document.py
- [ ] T022 [US1] Implement PDF parser using pypdf 6.1.1+ in src/core/document_parser.py
- [ ] T023 [US1] Implement DOCX parser using python-docx in src/core/document_parser.py
- [ ] T024 [US1] Implement Markdown parser using markdown-it-py in src/core/document_parser.py
- [ ] T025 [US1] Implement text file parser in src/core/document_parser.py
- [ ] T026 [US1] Create DocumentParser facade with format detection in src/core/document_parser.py
- [ ] T027 [US1] Implement file validation (size limit 10MB, format check) in src/core/document_parser.py
- [ ] T028 [US1] Create document storage service (in-memory) in src/services/document_service.py
- [ ] T029 [US1] Implement POST /api/v1/documents endpoint in src/api/documents.py
- [ ] T030 [US1] Implement GET /api/v1/documents endpoint in src/api/documents.py
- [ ] T031 [US1] Implement GET /api/v1/documents/{id} endpoint in src/api/documents.py
- [ ] T032 [US1] Implement DELETE /api/v1/documents/{id} endpoint in src/api/documents.py
- [ ] T033 [US1] Create PolicyAnalysisPlugin for Semantic Kernel in src/plugins/policy_analysis_plugin.py
- [ ] T034 [US1] Implement POST /api/v1/documents/{id}/analyze endpoint in src/api/documents.py
- [ ] T035 [US1] Add sample policy documents to assets/test_documents/
- [ ] T036 [US1] Create entry point in src/main.py with CLI and API modes

**Checkpoint**: User Story 1 complete - document upload and basic analysis functional

---

## Phase 4: User Story 2 - Apply Compliance Rules (Priority: P2)

**Goal**: Enable users to apply predefined compliance rules to documents and receive categorized violations

**Independent Test**: Select a rule template (e.g., "Data Protection Rules"), apply to a document, receive a list of rule matches and violations

### Tests for User Story 2

- [ ] T037 [P] [US2] Contract test for GET /rules endpoint in tests/contract/test_rules_api.py
- [ ] T038 [P] [US2] Unit tests for ComplianceEngine in tests/unit/test_compliance_engine.py
- [ ] T039 [P] [US2] Unit tests for severity scoring algorithm in tests/unit/test_compliance_engine.py
- [ ] T040 [P] [US2] Integration test for rule application workflow in tests/integration/test_rule_application.py

### Implementation for User Story 2

- [ ] T041 [P] [US2] Create ComplianceRule Pydantic model in src/models/compliance_rule.py
- [ ] T042 [P] [US2] Create ComplianceViolation Pydantic model in src/models/compliance_violation.py
- [ ] T043 [US2] Implement regex-based rule evaluation in src/core/compliance_engine.py
- [ ] T044 [US2] Implement severity weight calculation (CRITICAL=25, HIGH=15, MEDIUM=5, LOW=1) in src/core/compliance_engine.py
- [ ] T045 [US2] Implement compliance score calculation (100 - weighted penalties) in src/core/compliance_engine.py
- [ ] T046 [US2] Create RuleService for rule management in src/services/rule_service.py
- [ ] T047 [US2] Implement GET /api/v1/rules endpoint in src/api/rules.py
- [ ] T048 [US2] Implement GET /api/v1/rules/{id} endpoint in src/api/rules.py
- [ ] T049 [US2] Create Data Protection rule template in assets/rule_templates/data_protection.json
- [ ] T050 [US2] Create HR Policy rule template in assets/rule_templates/hr_policy.json
- [ ] T051 [US2] Create IT Security rule template in assets/rule_templates/it_security.json
- [ ] T052 [US2] Create Legal Compliance rule template in assets/rule_templates/legal_compliance.json
- [ ] T053 [US2] Create Accessibility rule template in assets/rule_templates/accessibility.json
- [ ] T054 [US2] Implement GET /api/v1/templates endpoint in src/api/templates.py
- [ ] T055 [US2] Implement GET /api/v1/templates/{id} endpoint in src/api/templates.py
- [ ] T056 [US2] Update analyze endpoint to use ComplianceEngine in src/api/documents.py

**Checkpoint**: User Story 2 complete - rule-based compliance checking functional

---

## Phase 5: User Story 3 - Create Custom Compliance Rules (Priority: P3)

**Goal**: Enable users to create custom compliance rules with patterns and keywords for organization-specific needs

**Independent Test**: Create a custom rule with name, pattern, severity, and category, then verify it is applied during analysis

### Tests for User Story 3

- [ ] T057 [P] [US3] Contract test for POST /rules endpoint in tests/contract/test_rules_api.py
- [ ] T058 [P] [US3] Contract test for PUT /rules/{id} endpoint in tests/contract/test_rules_api.py
- [ ] T059 [P] [US3] Unit tests for regex validation in tests/unit/test_rule_validation.py
- [ ] T060 [P] [US3] Integration test for custom rule creation workflow in tests/integration/test_custom_rules.py

### Implementation for User Story 3

- [ ] T061 [US3] Implement regex pattern validation in src/services/rule_service.py
- [ ] T062 [US3] Implement POST /api/v1/rules endpoint (create custom rule) in src/api/rules.py
- [ ] T063 [US3] Implement PUT /api/v1/rules/{id} endpoint (update rule) in src/api/rules.py
- [ ] T064 [US3] Implement DELETE /api/v1/rules/{id} endpoint (delete custom rule) in src/api/rules.py
- [ ] T065 [US3] Add rule is_builtin flag protection (cannot delete builtin rules) in src/services/rule_service.py
- [ ] T066 [US3] Update ComplianceEngine to include custom rules in analysis in src/core/compliance_engine.py

**Checkpoint**: User Story 3 complete - custom rule creation functional

---

## Phase 6: User Story 4 - Generate Compliance Report (Priority: P4)

**Goal**: Enable users to generate detailed compliance reports with recommendations for stakeholder communication

**Independent Test**: After analysis, generate a report that includes summary, violations list, severity breakdown, and recommendations

### Tests for User Story 4

- [ ] T067 [P] [US4] Contract test for GET /reports/{id} endpoint in tests/contract/test_reports_api.py
- [ ] T068 [P] [US4] Contract test for GET /reports/{id}/export endpoint in tests/contract/test_reports_api.py
- [ ] T069 [P] [US4] Unit tests for ReportService in tests/unit/test_report_service.py
- [ ] T070 [P] [US4] Integration test for report generation workflow in tests/integration/test_report_generation.py

### Implementation for User Story 4

- [ ] T071 [P] [US4] Create ComplianceReport Pydantic model in src/models/compliance_report.py
- [ ] T072 [P] [US4] Create ReportSummary Pydantic model in src/models/compliance_report.py
- [ ] T073 [P] [US4] Create RuleTemplate Pydantic model in src/models/rule_template.py
- [ ] T074 [US4] Implement ReportService with report generation logic in src/services/report_service.py
- [ ] T075 [US4] Implement recommendation generation based on violations in src/services/report_service.py
- [ ] T076 [US4] Implement GET /api/v1/reports/{id} endpoint in src/api/reports.py
- [ ] T077 [US4] Implement JSON export format in src/services/report_service.py
- [ ] T078 [US4] Implement HTML export format in src/services/report_service.py
- [ ] T079 [US4] Implement GET /api/v1/reports/{id}/export endpoint in src/api/reports.py
- [ ] T080 [US4] Add AI-powered insights using PolicyAnalysisPlugin in src/services/report_service.py

**Checkpoint**: User Story 4 complete - report generation functional

---

## Phase 7: User Story 5 - Compare Policy Versions (Priority: P5)

**Goal**: Enable users to compare two policy document versions and identify changes with compliance impact

**Independent Test**: Upload two versions of the same policy, receive a diff report highlighting additions, removals, and compliance impact

### Tests for User Story 5

- [ ] T081 [P] [US5] Contract test for POST /compare endpoint in tests/contract/test_compare_api.py
- [ ] T082 [P] [US5] Unit tests for comparison algorithm in tests/unit/test_comparison.py
- [ ] T083 [P] [US5] Integration test for version comparison workflow in tests/integration/test_comparison.py

### Implementation for User Story 5

- [ ] T084 [P] [US5] Create TextChange Pydantic model in src/models/comparison.py
- [ ] T085 [P] [US5] Create ComparisonResult Pydantic model in src/models/comparison.py
- [ ] T086 [US5] Implement text diff algorithm in src/core/comparison_engine.py
- [ ] T087 [US5] Implement section-level comparison in src/core/comparison_engine.py
- [ ] T088 [US5] Implement compliance impact analysis in src/core/comparison_engine.py
- [ ] T089 [US5] Create ComparisonService in src/services/comparison_service.py
- [ ] T090 [US5] Implement POST /api/v1/compare endpoint in src/api/compare.py

**Checkpoint**: User Story 5 complete - version comparison functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T091 Implement GET /api/v1/health endpoint in src/api/health.py
- [ ] T092 [P] Create demo.py interactive demo script at project root
- [ ] T093 [P] Add API Blueprint registration in src/app.py for all endpoints
- [ ] T094 Run all tests and ensure 59+ tests pass
- [ ] T095 [P] Validate quickstart.md instructions work end-to-end
- [ ] T096 Add graceful degradation when Azure OpenAI unavailable in src/plugins/policy_analysis_plugin.py
- [ ] T097 Performance optimization for documents up to 10MB
- [ ] T098 Security review for file upload handling

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 -> P2 -> P3 -> P4 -> P5)
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1's analyze endpoint
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US2's rule system
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses analysis results from US1/US2
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Uses documents from US1

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /documents endpoint in tests/contract/test_documents_api.py"
Task: "Contract test for POST /documents/{id}/analyze endpoint in tests/contract/test_analyze_api.py"
Task: "Unit tests for DocumentParser in tests/unit/test_document_parser.py"
Task: "Integration test for document upload and analysis workflow in tests/integration/test_document_analysis.py"

# Launch all models for User Story 1 together:
Task: "Create PolicyDocument Pydantic model in src/models/policy_document.py"
Task: "Create DocumentSection Pydantic model in src/models/policy_document.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test independently -> Deploy/Demo (MVP!)
3. Add User Story 2 -> Test independently -> Deploy/Demo
4. Add User Story 3 -> Test independently -> Deploy/Demo
5. Add User Story 4 -> Test independently -> Deploy/Demo
6. Add User Story 5 -> Test independently -> Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (document upload/analysis)
   - Developer B: User Story 2 (rule engine)
   - Developer C: User Story 4 (report generation)
3. Stories complete and integrate independently

---

## Summary

| Phase | Task Count | Description |
|-------|------------|-------------|
| Phase 1: Setup | 5 | Project initialization |
| Phase 2: Foundational | 10 | Core infrastructure |
| Phase 3: US1 (P1) | 21 | Document upload and analysis |
| Phase 4: US2 (P2) | 20 | Compliance rule application |
| Phase 5: US3 (P3) | 10 | Custom rule creation |
| Phase 6: US4 (P4) | 14 | Report generation |
| Phase 7: US5 (P5) | 10 | Version comparison |
| Phase 8: Polish | 8 | Cross-cutting concerns |
| **Total** | **98** | |

### Task Count Per User Story

- User Story 1: 21 tasks (4 tests + 17 implementation)
- User Story 2: 20 tasks (4 tests + 16 implementation)
- User Story 3: 10 tasks (4 tests + 6 implementation)
- User Story 4: 14 tasks (4 tests + 10 implementation)
- User Story 5: 10 tasks (3 tests + 7 implementation)

### Parallel Opportunities

- Phase 1: 3 of 5 tasks parallelizable
- Phase 2: 7 of 10 tasks parallelizable
- Each user story: Tests parallelizable, models parallelizable
- User stories can run in parallel after Phase 2

### Suggested MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1)**
- 36 tasks total
- Delivers: Document upload, parsing, and basic analysis
- Independently testable and demonstrable

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
