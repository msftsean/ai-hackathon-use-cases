# Tasks: Emergency Response Planning Agent

**Input**: Design documents from `/specs/003-emergency-response-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are included as this is a production-ready system requiring 80+ tests per spec.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
```text
Emergency-Response-Agent/
├── src/
│   ├── config/
│   ├── models/
│   ├── services/
│   ├── orchestration/
│   └── api/
├── tests/
├── static/
└── assets/
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure per plan.md in Emergency-Response-Agent/
- [ ] T002 Create pyproject.toml with Python 3.11+ and dependencies from research.md
- [ ] T003 [P] Create requirements.txt with semantic-kernel, pydantic, aiohttp, flask
- [ ] T004 [P] Create .env.example with OPENWEATHER_API_KEY, AZURE_OPENAI_KEY placeholders
- [ ] T005 [P] Create src/__init__.py with package initialization
- [ ] T006 Implement Settings class with Pydantic in src/config/settings.py
- [ ] T007 [P] Configure logging infrastructure in src/config/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create all enumerations (EmergencyType, SeverityLevel, ResponsePhase, CoordinationStatus) in src/models/__init__.py
- [ ] T009 [P] Create EmergencyScenario Pydantic model with validators in src/models/emergency_models.py
- [ ] T010 [P] Create EmergencyResponsePlan Pydantic model in src/models/emergency_models.py
- [ ] T011 [P] Create ResourceAllocation dataclass in src/models/emergency_models.py
- [ ] T012 [P] Create WeatherCondition dataclass in src/models/emergency_models.py
- [ ] T013 [P] Create TrafficCondition dataclass in src/models/emergency_models.py
- [ ] T014 [P] Create EvacuationRoute dataclass in src/models/emergency_models.py
- [ ] T015 [P] Create HistoricalIncident dataclass in src/models/emergency_models.py
- [ ] T016 [P] Create AgentResponse dataclass in src/models/emergency_models.py
- [ ] T017 [P] Create MultiAgentTask dataclass in src/models/emergency_models.py
- [ ] T018 Setup Flask app factory with Blueprint registration in src/main.py
- [ ] T019 [P] Create base API routes structure in src/api/__init__.py
- [ ] T020 Implement health check endpoint in src/api/routes.py
- [ ] T021 [P] Create test infrastructure with pytest-asyncio in tests/__init__.py
- [ ] T022 [P] Create tests/test_setup.py with basic import and configuration tests

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Emergency Scenario Simulation (Priority: P1) MVP

**Goal**: Emergency managers can create scenarios and generate comprehensive response plans with resource allocations, timelines, and agency coordination.

**Independent Test**: Create a hurricane scenario with severity 4, verify response plan includes lead agency (OEM), 500+ personnel, 100+ vehicles, and 5 timeline milestones.

### Tests for User Story 1

- [ ] T023 [P] [US1] Create test_models.py with EmergencyScenario validation tests in tests/test_models.py
- [ ] T024 [P] [US1] Create test_models.py with EmergencyResponsePlan validation tests in tests/test_models.py
- [ ] T025 [P] [US1] Create test_emergency_coordinator.py with scenario analysis tests in tests/test_emergency_coordinator.py
- [ ] T026 [P] [US1] Create test_emergency_coordinator.py with resource calculation tests in tests/test_emergency_coordinator.py
- [ ] T027 [P] [US1] Create test_emergency_coordinator.py with timeline generation tests in tests/test_emergency_coordinator.py

### Implementation for User Story 1

- [ ] T028 [US1] Create EmergencyResponseCoordinator class skeleton in src/orchestration/emergency_coordinator.py
- [ ] T029 [US1] Implement coordinate_response() main method in src/orchestration/emergency_coordinator.py
- [ ] T030 [US1] Implement _perform_scenario_analysis() with severity assessment in src/orchestration/emergency_coordinator.py
- [ ] T031 [US1] Implement _assess_population_impact() with zone calculations in src/orchestration/emergency_coordinator.py
- [ ] T032 [US1] Implement _estimate_resource_requirements() with FEMA-aligned calculations in src/orchestration/emergency_coordinator.py
- [ ] T033 [US1] Implement _determine_lead_agency() with type-to-agency mapping in src/orchestration/emergency_coordinator.py
- [ ] T034 [US1] Implement _identify_supporting_agencies() with type-specific logic in src/orchestration/emergency_coordinator.py
- [ ] T035 [US1] Implement _generate_response_plan() combining all analysis in src/orchestration/emergency_coordinator.py
- [ ] T036 [US1] Implement _allocate_resources() with personnel/equipment breakdown in src/orchestration/emergency_coordinator.py
- [ ] T037 [US1] Implement _create_timeline() with 5-milestone structure in src/orchestration/emergency_coordinator.py
- [ ] T038 [US1] Implement _generate_immediate_actions() with type-specific actions in src/orchestration/emergency_coordinator.py
- [ ] T039 [US1] Implement _generate_short_term_actions() in src/orchestration/emergency_coordinator.py
- [ ] T040 [US1] Implement _generate_recovery_actions() in src/orchestration/emergency_coordinator.py
- [ ] T041 [US1] Create POST /scenarios endpoint in src/api/routes.py
- [ ] T042 [US1] Create POST /scenarios/{id}/plan endpoint in src/api/routes.py
- [ ] T043 [US1] Create GET /scenarios endpoint with filtering in src/api/routes.py
- [ ] T044 [US1] Create GET /scenarios/{id} endpoint in src/api/routes.py
- [ ] T045 [US1] Create GET /plans/{id} endpoint in src/api/routes.py
- [ ] T046 [P] [US1] Create test_integration.py with end-to-end scenario creation tests in tests/test_integration.py

**Checkpoint**: User Story 1 complete - can create scenarios and generate full response plans

---

## Phase 4: User Story 2 - Real-Time Weather Integration (Priority: P2)

**Goal**: Emergency coordinators get real-time weather data integrated into their planning with risk assessments and recommendations.

**Independent Test**: Request weather for NYC coordinates, verify temperature, wind, humidity returned. Test wind >40mph returns "high" wind risk.

### Tests for User Story 2

- [ ] T047 [P] [US2] Create test_weather_service.py with API integration tests in tests/test_weather_service.py
- [ ] T048 [P] [US2] Create test_weather_service.py with mock fallback tests in tests/test_weather_service.py
- [ ] T049 [P] [US2] Create test_weather_service.py with risk assessment tests in tests/test_weather_service.py

### Implementation for User Story 2

- [ ] T050 [US2] Create WeatherService class skeleton in src/services/weather_service.py
- [ ] T051 [US2] Implement get_current_conditions() with OpenWeatherMap API in src/services/weather_service.py
- [ ] T052 [US2] Implement get_forecast() for multi-hour forecasts in src/services/weather_service.py
- [ ] T053 [US2] Implement _generate_mock_weather_data() fallback in src/services/weather_service.py
- [ ] T054 [US2] Implement assess_weather_risk() with wind/temp/precipitation analysis in src/services/weather_service.py
- [ ] T055 [US2] Implement analyze_weather_impact() for emergency-specific analysis in src/services/weather_service.py
- [ ] T056 [US2] Add weather integration to EmergencyResponseCoordinator._perform_scenario_analysis() in src/orchestration/emergency_coordinator.py
- [ ] T057 [US2] Create GET /weather/current endpoint in src/api/routes.py
- [ ] T058 [US2] Create GET /weather/forecast endpoint in src/api/routes.py
- [ ] T059 [US2] Create POST /weather/risk endpoint in src/api/routes.py

**Checkpoint**: User Story 2 complete - weather data and risk assessment integrated

---

## Phase 5: User Story 3 - Multi-Agency Resource Coordination (Priority: P2)

**Goal**: System calculates resource requirements and assigns appropriate agencies based on emergency type.

**Independent Test**: Generate plan for fire emergency, verify FDNY as lead agency with appropriate supporting agencies.

### Tests for User Story 3

- [ ] T060 [P] [US3] Create tests for agency assignment logic in tests/test_emergency_coordinator.py
- [ ] T061 [P] [US3] Create tests for resource calculation with type multipliers in tests/test_emergency_coordinator.py
- [ ] T062 [P] [US3] Create tests for supporting agency selection in tests/test_emergency_coordinator.py

### Implementation for User Story 3

- [ ] T063 [US3] Enhance _determine_lead_agency() with all 8 emergency types in src/orchestration/emergency_coordinator.py
- [ ] T064 [US3] Enhance _identify_supporting_agencies() with type-specific additions in src/orchestration/emergency_coordinator.py
- [ ] T065 [US3] Implement _create_communication_plan() with agency coordination in src/orchestration/emergency_coordinator.py
- [ ] T066 [US3] Add resource multipliers for all emergency types (hurricane 2.0x, fire 1.8x, etc.) in src/orchestration/emergency_coordinator.py
- [ ] T067 [US3] Implement equipment-specific allocations per emergency type in src/orchestration/emergency_coordinator.py
- [ ] T068 [US3] Add inter-agency communication channels to response plan in src/orchestration/emergency_coordinator.py

**Checkpoint**: User Story 3 complete - full agency coordination working

---

## Phase 6: User Story 4 - Evacuation Route Planning (Priority: P3)

**Goal**: Coordinators get optimized evacuation routes with capacity calculations and bottleneck identification.

**Independent Test**: Request Zone A evacuation routes, verify routes with capacity, timing, and bottlenecks returned.

### Tests for User Story 4

- [ ] T069 [P] [US4] Create test_traffic_service.py with traffic condition tests in tests/test_traffic_service.py
- [ ] T070 [P] [US4] Create test_traffic_service.py with evacuation route tests in tests/test_traffic_service.py
- [ ] T071 [P] [US4] Create test_traffic_service.py with capacity calculation tests in tests/test_traffic_service.py

### Implementation for User Story 4

- [ ] T072 [US4] Create TrafficService class skeleton in src/services/traffic_service.py
- [ ] T073 [US4] Implement get_traffic_conditions() with mock data in src/services/traffic_service.py
- [ ] T074 [US4] Implement optimize_evacuation_routes() with NYC routes in src/services/traffic_service.py
- [ ] T075 [US4] Implement calculate_evacuation_capacity() with hourly throughput in src/services/traffic_service.py
- [ ] T076 [US4] Implement _analyze_bottlenecks() with severity assessment in src/services/traffic_service.py
- [ ] T077 [US4] Implement get_public_transportation_status() for MTA integration in src/services/traffic_service.py
- [ ] T078 [US4] Create GET /evacuation/routes endpoint in src/api/routes.py
- [ ] T079 [US4] Create POST /evacuation/capacity endpoint in src/api/routes.py
- [ ] T080 [US4] Create GET /traffic/conditions endpoint in src/api/routes.py

**Checkpoint**: User Story 4 complete - evacuation planning functional

---

## Phase 7: User Story 5 - Historical Incident Analysis (Priority: P3)

**Goal**: Planners can search past incidents to inform current planning with lessons learned.

**Independent Test**: Search for "hurricane" incidents, verify matching incidents with lessons learned returned.

### Tests for User Story 5

- [ ] T081 [P] [US5] Create test_search_service.py with search tests in tests/test_search_service.py
- [ ] T082 [P] [US5] Create test_search_service.py with filtering tests in tests/test_search_service.py

### Implementation for User Story 5

- [ ] T083 [US5] Create SearchService class skeleton in src/services/search_service.py
- [ ] T084 [US5] Implement search_historical_incidents() with in-memory search in src/services/search_service.py
- [ ] T085 [US5] Implement get_incident_by_id() in src/services/search_service.py
- [ ] T086 [US5] Implement add_incident() for recording new incidents in src/services/search_service.py
- [ ] T087 [US5] Create sample historical data in assets/historical_data/sample_incidents.json
- [ ] T088 [US5] Load sample historical data on startup in src/services/search_service.py
- [ ] T089 [US5] Create GET /historical/search endpoint in src/api/routes.py
- [ ] T090 [US5] Create GET /historical/{id} endpoint in src/api/routes.py

**Checkpoint**: User Story 5 complete - historical analysis available

---

## Phase 8: User Story 6 - Emergency Dashboard Interface (Priority: P3)

**Goal**: Emergency managers can create scenarios and view plans through a web dashboard.

**Independent Test**: Access dashboard, create scenario, verify plan displays with all components.

### Tests for User Story 6

- [ ] T091 [P] [US6] Create static file serving tests in tests/test_integration.py

### Implementation for User Story 6

- [ ] T092 [P] [US6] Create index.html with WCAG 2.1 AA compliant structure in static/index.html
- [ ] T093 [P] [US6] Create styles.css with accessible design in static/styles.css
- [ ] T094 [US6] Create dashboard.js with scenario creation form in static/dashboard.js
- [ ] T095 [US6] Implement scenario list view with filtering in static/dashboard.js
- [ ] T096 [US6] Implement response plan detail view in static/dashboard.js
- [ ] T097 [US6] Implement weather and resource visualization in static/dashboard.js
- [ ] T098 [US6] Implement timeline milestone display in static/dashboard.js
- [ ] T099 [US6] Add keyboard shortcuts (matching Document-Eligibility-Agent) in static/dashboard.js
- [ ] T100 [US6] Configure static file serving in src/main.py

**Checkpoint**: User Story 6 complete - full web dashboard available

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T101 Create demo.py interactive demonstration script in demo.py
- [ ] T102 [P] Create run_all_tests.py test runner in run_all_tests.py
- [ ] T103 [P] Add comprehensive logging to all services
- [ ] T104 [P] Add error handling with proper HTTP status codes in src/api/routes.py
- [ ] T105 [P] Create sample scenario data in assets/scenario_simulations/
- [ ] T106 [P] Create response templates in assets/response_templates/
- [ ] T107 Add performance timing to coordinate_response() in src/orchestration/emergency_coordinator.py
- [ ] T108 Verify all 80+ tests pass with run_all_tests.py
- [ ] T109 [P] Run quickstart.md validation - verify all steps work
- [ ] T110 [P] Security review - ensure no secrets in code, validate all inputs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (P1): Core scenario simulation - MVP
  - US2 (P2): Weather integration - enhances US1
  - US3 (P2): Agency coordination - enhances US1
  - US4 (P3): Evacuation planning - independent module
  - US5 (P3): Historical analysis - independent module
  - US6 (P3): Dashboard - depends on API from US1-US5
- **Polish (Phase 9)**: Depends on desired user stories being complete

### User Story Dependencies

| Story | Can Start After | Depends On | Enhances |
|-------|-----------------|------------|----------|
| US1 (Scenario Simulation) | Phase 2 | None | - |
| US2 (Weather Integration) | Phase 2 | None | US1 |
| US3 (Agency Coordination) | Phase 2 | None | US1 |
| US4 (Evacuation Planning) | Phase 2 | None | - |
| US5 (Historical Analysis) | Phase 2 | None | - |
| US6 (Dashboard) | US1 complete | US1 API | All |

### Within Each User Story

1. Tests written and FAIL before implementation
2. Models before services
3. Services before orchestration
4. Orchestration before API endpoints
5. API endpoints before UI

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005, T007 can run in parallel
**Phase 2 (Foundational)**: T009-T017 can run in parallel, T021-T022 can run in parallel
**Phase 3-8**: All test tasks [P] can run in parallel within each phase
**Cross-Story**: US1, US2, US3, US4, US5 can be developed in parallel by different team members

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch all model tasks together:
Task: "Create EmergencyScenario Pydantic model in src/models/emergency_models.py"
Task: "Create EmergencyResponsePlan Pydantic model in src/models/emergency_models.py"
Task: "Create ResourceAllocation dataclass in src/models/emergency_models.py"
Task: "Create WeatherCondition dataclass in src/models/emergency_models.py"
Task: "Create TrafficCondition dataclass in src/models/emergency_models.py"
Task: "Create EvacuationRoute dataclass in src/models/emergency_models.py"
Task: "Create HistoricalIncident dataclass in src/models/emergency_models.py"
Task: "Create AgentResponse dataclass in src/models/emergency_models.py"
Task: "Create MultiAgentTask dataclass in src/models/emergency_models.py"
```

## Parallel Example: User Story 1 Tests

```bash
# Launch all US1 tests together:
Task: "Create test_models.py with EmergencyScenario validation tests"
Task: "Create test_models.py with EmergencyResponsePlan validation tests"
Task: "Create test_emergency_coordinator.py with scenario analysis tests"
Task: "Create test_emergency_coordinator.py with resource calculation tests"
Task: "Create test_emergency_coordinator.py with timeline generation tests"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T022)
3. Complete Phase 3: User Story 1 (T023-T046)
4. **STOP and VALIDATE**: Test scenario creation and plan generation
5. Deploy/demo if ready - this is a working MVP!

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 = Can create scenarios and generate plans
2. **+Weather**: Add US2 = Weather-informed planning
3. **+Agencies**: Add US3 = Full agency coordination
4. **+Evacuation**: Add US4 = Evacuation route planning
5. **+Historical**: Add US5 = Learn from past incidents
6. **+Dashboard**: Add US6 = Full web interface

### Parallel Team Strategy

With multiple developers after Phase 2 completes:

- **Developer A**: User Story 1 (core planning) + User Story 6 (dashboard)
- **Developer B**: User Story 2 (weather) + User Story 3 (agencies)
- **Developer C**: User Story 4 (evacuation) + User Story 5 (historical)

---

## Task Summary

| Phase | Description | Task Count | Parallel Tasks |
|-------|-------------|------------|----------------|
| 1 | Setup | 7 | 4 |
| 2 | Foundational | 15 | 12 |
| 3 | US1: Scenario Simulation (MVP) | 24 | 6 |
| 4 | US2: Weather Integration | 13 | 3 |
| 5 | US3: Agency Coordination | 9 | 3 |
| 6 | US4: Evacuation Planning | 12 | 3 |
| 7 | US5: Historical Analysis | 10 | 2 |
| 8 | US6: Dashboard Interface | 10 | 3 |
| 9 | Polish | 10 | 6 |
| **Total** | | **110** | **42** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests included because spec requires 80+ tests for production readiness
