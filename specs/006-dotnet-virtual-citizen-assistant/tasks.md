# Tasks: DotNet Virtual Citizen Assistant

**Input**: Design documents from `/specs/006-dotnet-virtual-citizen-assistant/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Main app**: `DotNet-Virtual-Citizen-Assistant/VirtualCitizenAgent/`
- **Upload utility**: `DotNet-Virtual-Citizen-Assistant/AzureSearchUploader/`
- **Tests**: `DotNet-Virtual-Citizen-Assistant/VirtualCitizenAgent.Tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and .NET 9 solution structure

- [X] T001 Create solution file in DotNet-Virtual-Citizen-Assistant/VirtualCitizenAgent.sln
- [X] T002 Create ASP.NET Core MVC project in DotNet-Virtual-Citizen-Assistant/VirtualCitizenAgent/VirtualCitizenAgent.csproj with .NET 9.0
- [X] T003 [P] Create console project in DotNet-Virtual-Citizen-Assistant/AzureSearchUploader/AzureSearchUploader.csproj
- [X] T004 [P] Create test project in DotNet-Virtual-Citizen-Assistant/VirtualCitizenAgent.Tests/VirtualCitizenAgent.Tests.csproj
- [X] T005 [P] Add NuGet references: Microsoft.SemanticKernel 1.65.0, Azure.Search.Documents, Azure.AI.OpenAI, Azure.Identity
- [X] T006 [P] Add test NuGet references: xunit, Moq, FluentAssertions, Microsoft.AspNetCore.Mvc.Testing
- [X] T007 [P] Configure appsettings.json with SearchConfiguration and OpenAI sections in VirtualCitizenAgent/appsettings.json
- [X] T008 [P] Configure launchSettings.json with http profile on port 5000 in VirtualCitizenAgent/Properties/launchSettings.json
- [ ] T009 [P] Add .editorconfig with C# 13 style rules in DotNet-Virtual-Citizen-Assistant/.editorconfig

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Configuration & DI

- [X] T010 Create SearchConfiguration class in VirtualCitizenAgent/Configuration/SearchConfiguration.cs
- [X] T011 [P] Create OpenAIConfiguration class in VirtualCitizenAgent/Configuration/OpenAIConfiguration.cs
- [X] T012 Configure dependency injection and configuration binding in VirtualCitizenAgent/Program.cs

### Core Models (Shared Across Stories)

- [X] T013 [P] Create MessageRole enum (User, Assistant, System) in VirtualCitizenAgent/Models/MessageRole.cs
- [X] T014 [P] Create SearchMode enum (Keyword, Semantic, Hybrid) in VirtualCitizenAgent/Models/SearchMode.cs
- [X] T015 [P] Create DocumentStatus enum (Active, Archived, Draft) in VirtualCitizenAgent/Models/DocumentStatus.cs
- [X] T016 [P] Create Document model in VirtualCitizenAgent/Models/Document.cs
- [X] T017 [P] Create DocumentSource model in VirtualCitizenAgent/Models/DocumentSource.cs
- [X] T018 [P] Create ServiceCategory model in VirtualCitizenAgent/Models/ServiceCategory.cs
- [X] T019 [P] Create FacetValue model in VirtualCitizenAgent/Models/FacetValue.cs

### Search Service (Foundation for US1, US2, US3)

- [X] T020 Create ISearchService interface in VirtualCitizenAgent/Services/ISearchService.cs
- [X] T021 Implement SearchService with Azure.Search.Documents SDK in VirtualCitizenAgent/Services/SearchService.cs
- [X] T022 Register SearchService in DI container in VirtualCitizenAgent/Program.cs

### Semantic Kernel Setup (Foundation for US1)

- [X] T023 Create DocumentSearchPlugin with 6 KernelFunction methods in VirtualCitizenAgent/Plugins/DocumentSearchPlugin.cs
- [X] T024 Configure Semantic Kernel with Azure OpenAI connector in VirtualCitizenAgent/Program.cs
- [X] T025 Register DocumentSearchPlugin with kernel in VirtualCitizenAgent/Program.cs

### Layout & Static Assets

- [X] T026 [P] Add Bootstrap 5.3.0 to VirtualCitizenAgent/wwwroot/lib/bootstrap/
- [X] T027 [P] Add Font Awesome icons to VirtualCitizenAgent/wwwroot/lib/fontawesome/
- [X] T028 [P] Create _Layout.cshtml with responsive navigation in VirtualCitizenAgent/Views/Shared/_Layout.cshtml
- [X] T029 [P] Create site.css with custom styles in VirtualCitizenAgent/wwwroot/css/site.css
- [X] T030 Create _ViewImports.cshtml with tag helpers in VirtualCitizenAgent/Views/_ViewImports.cshtml
- [X] T031 [P] Create _ViewStart.cshtml in VirtualCitizenAgent/Views/_ViewStart.cshtml

### Error Handling & Health Check

- [X] T032 Create Error model for API responses in VirtualCitizenAgent/Models/Error.cs
- [X] T033 Create HealthController with /api/health endpoint in VirtualCitizenAgent/Controllers/HealthController.cs
- [X] T034 Configure global exception handling middleware in VirtualCitizenAgent/Program.cs

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - RAG-Powered Chat Interface (Priority: P1)

**Goal**: Citizens can ask questions in natural language and get AI responses with source citations

**Independent Test**: Enter "How do I get a parking permit?", receive AI response with cited sources

### Chat Models

- [X] T035 [P] [US1] Create ChatMessage model in VirtualCitizenAgent/Models/ChatMessage.cs
- [X] T036 [P] [US1] Create ChatSession model in VirtualCitizenAgent/Models/ChatSession.cs
- [X] T037 [P] [US1] Create ChatRequest DTO in VirtualCitizenAgent/Models/ChatRequest.cs
- [X] T038 [P] [US1] Create ChatResponse DTO in VirtualCitizenAgent/Models/ChatResponse.cs

### Chat Service

- [X] T039 [US1] Create IChatService interface in VirtualCitizenAgent/Services/IChatService.cs
- [X] T040 [US1] Implement ChatService with RAG pipeline in VirtualCitizenAgent/Services/ChatService.cs
- [X] T041 [US1] Add session management (create, get, delete) to ChatService
- [X] T042 [US1] Implement context window management for multi-turn conversations
- [X] T043 [US1] Register ChatService in DI container in VirtualCitizenAgent/Program.cs

### Chat API Controller

- [X] T044 [US1] Create ChatController with POST /api/chat endpoint in VirtualCitizenAgent/Controllers/ChatController.cs
- [X] T045 [US1] Add POST /api/chat/session endpoint for session creation
- [X] T046 [US1] Add GET /api/chat/session/{sessionId} endpoint for session history
- [X] T047 [US1] Add DELETE /api/chat/session/{sessionId} endpoint for session deletion
- [X] T048 [US1] Add request validation and error responses to ChatController

### Chat UI

- [X] T049 [US1] Create Chat/Index.cshtml view with chat interface in VirtualCitizenAgent/Views/Chat/Index.cshtml
- [X] T050 [US1] Create chat.js with WebSocket-like AJAX messaging in VirtualCitizenAgent/wwwroot/js/chat.js
- [X] T051 [US1] Add source citation badges with clickable links in chat UI
- [X] T052 [US1] Add loading indicators and error states to chat UI
- [X] T053 [US1] Add responsive mobile styling for chat interface

### Home Page Integration

- [X] T054 [US1] Create HomeController in VirtualCitizenAgent/Controllers/HomeController.cs
- [X] T055 [US1] Create Home/Index.cshtml with "AI Chat Assistant" link in VirtualCitizenAgent/Views/Home/Index.cshtml

**Checkpoint**: User Story 1 complete - citizens can chat with AI and get sourced answers

---

## Phase 4: User Story 2 - Advanced Document Search (Priority: P2)

**Goal**: Citizens can search for documents using keywords or semantic search

**Independent Test**: Search "business license application", receive ranked document results

### Search Models

- [X] T056 [P] [US2] Create SearchQuery model in VirtualCitizenAgent/Models/SearchQuery.cs
- [X] T057 [P] [US2] Create SearchResult model in VirtualCitizenAgent/Models/SearchResult.cs
- [X] T058 [P] [US2] Create SearchResponse model in VirtualCitizenAgent/Models/SearchResponse.cs

### Search Enhancements

- [X] T059 [US2] Add semantic search method to ISearchService/SearchService
- [X] T060 [US2] Add keyword search method to ISearchService/SearchService
- [X] T061 [US2] Add hybrid search method to ISearchService/SearchService
- [X] T062 [US2] Add category filtering to search methods
- [X] T063 [US2] Add highlight fields and captions to search results

### Search API Controller

- [X] T064 [US2] Create SearchController in VirtualCitizenAgent/Controllers/SearchController.cs
- [X] T065 [US2] Add GET /api/search endpoint with query, mode, category, top, skip params
- [X] T066 [US2] Add GET /api/search/semantic endpoint for AI-powered search
- [X] T067 [US2] Add request validation and pagination to SearchController

### Search UI

- [X] T068 [US2] Create Search/Index.cshtml with search form in VirtualCitizenAgent/Views/Search/Index.cshtml
- [X] T069 [US2] Add search mode toggle (keyword/semantic/hybrid) to search UI
- [X] T070 [US2] Create search result cards with title, snippet, category, date
- [X] T071 [US2] Add category filter dropdown to search UI
- [X] T072 [US2] Create search.js for dynamic search interactions in VirtualCitizenAgent/wwwroot/js/search.js
- [X] T073 [US2] Add pagination controls to search results
- [X] T074 [US2] Add responsive mobile styling for search page

**Checkpoint**: User Story 2 complete - citizens can search documents with multiple modes

---

## Phase 5: User Story 3 - Service Categories Browser (Priority: P3)

**Goal**: Citizens can browse services by category with visual grid layout

**Independent Test**: View categories page, see grid with icons and counts, click to filter

### Category Models

- [X] T075 [P] [US3] Create CategoryDetail model (extends ServiceCategory) in VirtualCitizenAgent/Models/CategoryDetail.cs

### Category Service

- [X] T076 [US3] Create ICategoryService interface in VirtualCitizenAgent/Services/ICategoryService.cs
- [X] T077 [US3] Implement CategoryService with facet aggregation in VirtualCitizenAgent/Services/CategoryService.cs
- [X] T078 [US3] Add GetAllCategories method returning ServiceCategory list with counts
- [X] T079 [US3] Add GetCategoryByName method returning CategoryDetail with documents
- [X] T080 [US3] Register CategoryService in DI container in VirtualCitizenAgent/Program.cs

### Category API Controller

- [X] T081 [US3] Create CategoriesController in VirtualCitizenAgent/Controllers/CategoriesController.cs
- [X] T082 [US3] Add GET /api/categories endpoint listing all categories
- [X] T083 [US3] Add GET /api/categories/{category} endpoint for category details

### Category UI

- [X] T084 [US3] Create Categories/Index.cshtml with category grid in VirtualCitizenAgent/Views/Categories/Index.cshtml
- [X] T085 [US3] Create category card partial with icon, name, count in VirtualCitizenAgent/Views/Categories/_CategoryCard.cshtml
- [X] T086 [US3] Add click navigation from category to filtered search results
- [X] T087 [US3] Add responsive grid layout for mobile/tablet/desktop
- [X] T088 [US3] Add Font Awesome icons for each category type

**Checkpoint**: User Story 3 complete - citizens can browse categories visually

---

## Phase 6: User Story 4 - Document Details View (Priority: P4)

**Goal**: Citizens can view full document content with print and share capabilities

**Independent Test**: Click a search result, view full content, print or copy share link

### Document API

- [X] T089 [US4] Add GET /api/documents/{documentId} endpoint to SearchController
- [X] T090 [US4] Add GET /api/documents/recent endpoint with days and top params
- [X] T091 [US4] Add GetDocumentById method to ISearchService/SearchService
- [X] T092 [US4] Add GetRecentDocuments method to ISearchService/SearchService

### Document UI

- [X] T093 [US4] Create Documents/Details.cshtml with full content view in VirtualCitizenAgent/Views/Documents/Details.cshtml
- [X] T094 [US4] Add document metadata display (category, tags, last updated)
- [X] T095 [US4] Add print button with print-friendly CSS in VirtualCitizenAgent/wwwroot/css/print.css
- [X] T096 [US4] Add share button that copies URL to clipboard
- [X] T097 [US4] Create documents.js for print/share interactions in VirtualCitizenAgent/wwwroot/js/documents.js
- [X] T098 [US4] Add "Related Documents" section based on category/tags
- [X] T099 [US4] Create DocumentsController for MVC views in VirtualCitizenAgent/Controllers/DocumentsController.cs

**Checkpoint**: User Story 4 complete - citizens can view, print, and share documents

---

## Phase 7: User Story 5 - Data Upload Utility (Priority: P5)

**Goal**: Administrators can batch upload service documents to Azure AI Search

**Independent Test**: Run AzureSearchUploader with JSON files, verify documents indexed

### Upload Models

- [X] T100 [P] [US5] Create UploadDocument model in AzureSearchUploader/Models/UploadDocument.cs
- [X] T101 [P] [US5] Create UploadResult model in AzureSearchUploader/Models/UploadResult.cs
- [X] T102 [P] [US5] Create UploadError model in AzureSearchUploader/Models/UploadError.cs

### Upload Service

- [X] T103 [US5] Create IDocumentUploadService interface in AzureSearchUploader/Services/IDocumentUploadService.cs
- [X] T104 [US5] Implement DocumentUploadService with batch processing in AzureSearchUploader/Services/DocumentUploadService.cs
- [X] T105 [US5] Add Polly retry logic for transient failures
- [X] T106 [US5] Add document validation before upload
- [X] T107 [US5] Implement MergeOrUpload semantics for upsert behavior

### Upload Program

- [X] T108 [US5] Create Program.cs with command-line interface in AzureSearchUploader/Program.cs
- [X] T109 [US5] Add appsettings.json configuration for search credentials in AzureSearchUploader/appsettings.json
- [X] T110 [US5] Add JSON file reading from AzureSearchUploader/Data/ directory
- [X] T111 [US5] Add progress logging and summary statistics output

### Sample Data

- [X] T112 [P] [US5] Create Transportation category sample JSON in AzureSearchUploader/Data/transportation.json
- [X] T113 [P] [US5] Create Business category sample JSON in AzureSearchUploader/Data/business.json
- [X] T114 [P] [US5] Create Housing category sample JSON in AzureSearchUploader/Data/housing.json
- [X] T115 [P] [US5] Create Health category sample JSON in AzureSearchUploader/Data/health.json
- [X] T116 [P] [US5] Create Education category sample JSON in AzureSearchUploader/Data/education.json

**Checkpoint**: User Story 5 complete - administrators can populate search index

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Unit Tests

- [X] T117 [P] Create SearchServiceTests in VirtualCitizenAgent.Tests/Unit/SearchServiceTests.cs
- [X] T118 [P] Create ChatServiceTests in VirtualCitizenAgent.Tests/Unit/ChatServiceTests.cs
- [ ] T119 [P] Create CategoryServiceTests in VirtualCitizenAgent.Tests/Unit/CategoryServiceTests.cs
- [ ] T120 [P] Create DocumentSearchPluginTests in VirtualCitizenAgent.Tests/Unit/DocumentSearchPluginTests.cs
- [ ] T121 [P] Create SearchControllerTests in VirtualCitizenAgent.Tests/Unit/SearchControllerTests.cs
- [ ] T122 [P] Create ChatControllerTests in VirtualCitizenAgent.Tests/Unit/ChatControllerTests.cs
- [ ] T123 [P] Create CategoriesControllerTests in VirtualCitizenAgent.Tests/Unit/CategoriesControllerTests.cs

### Integration Tests

- [ ] T124 Create RealOpenAIIntegrationTests (skipped by default) in VirtualCitizenAgent.Tests/Integration/RealOpenAIIntegrationTests.cs
- [ ] T125 Create SearchIntegrationTests with WebApplicationFactory in VirtualCitizenAgent.Tests/Integration/SearchIntegrationTests.cs
- [ ] T126 Create ChatIntegrationTests with WebApplicationFactory in VirtualCitizenAgent.Tests/Integration/ChatIntegrationTests.cs

### Test Helpers

- [ ] T127 [P] Create MockSearchClient test helper in VirtualCitizenAgent.Tests/TestHelpers/MockSearchClient.cs
- [X] T128 [P] Create TestDocumentFactory for test data in VirtualCitizenAgent.Tests/TestHelpers/TestDocumentFactory.cs

### Accessibility & Mobile

- [ ] T129 Add ARIA labels to all interactive elements
- [ ] T130 Add keyboard navigation support to chat and search
- [ ] T131 Verify mobile responsive breakpoints for all views
- [ ] T132 Add skip navigation links for screen readers

### Security

- [ ] T133 Add input sanitization to chat and search inputs
- [ ] T134 Add rate limiting middleware in VirtualCitizenAgent/Middleware/RateLimitingMiddleware.cs
- [ ] T135 Add Content Security Policy headers
- [ ] T136 Validate Azure Managed Identity configuration for production

### Performance

- [ ] T137 Add response caching for category list
- [ ] T138 Add output caching for static search results
- [ ] T139 Configure connection pooling for Azure services
- [ ] T140 Add lazy loading for search results pagination

### Documentation

- [X] T141 Create README.md with setup instructions in DotNet-Virtual-Citizen-Assistant/README.md
- [ ] T142 Add XML documentation comments to all public APIs
- [ ] T143 Run quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 -> P2 -> P3 -> P4 -> P5)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Shares SearchService with US1
- **User Story 3 (P3)**: Can start after Foundational - Uses SearchService facets
- **User Story 4 (P4)**: Can start after Foundational - Uses SearchService getById
- **User Story 5 (P5)**: Can start after Foundational - Independent upload utility

### Within Each User Story

- Models before services
- Services before controllers
- Controllers before views
- API before UI
- Core implementation before integrations

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All enum and model creation tasks marked [P] can run in parallel
- All sample data creation tasks marked [P] can run in parallel
- All test file creation tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Create ChatMessage model in VirtualCitizenAgent/Models/ChatMessage.cs"
Task: "Create ChatSession model in VirtualCitizenAgent/Models/ChatSession.cs"
Task: "Create ChatRequest DTO in VirtualCitizenAgent/Models/ChatRequest.cs"
Task: "Create ChatResponse DTO in VirtualCitizenAgent/Models/ChatResponse.cs"
```

---

## Parallel Example: User Story 5 Sample Data

```bash
# Launch all sample JSON files together:
Task: "Create Transportation category sample JSON in AzureSearchUploader/Data/transportation.json"
Task: "Create Business category sample JSON in AzureSearchUploader/Data/business.json"
Task: "Create Housing category sample JSON in AzureSearchUploader/Data/housing.json"
Task: "Create Health category sample JSON in AzureSearchUploader/Data/health.json"
Task: "Create Education category sample JSON in AzureSearchUploader/Data/education.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T034)
3. Complete Phase 3: User Story 1 (T035-T055)
4. **STOP and VALIDATE**: Test chat interface independently
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
   - Developer A: User Story 1 (Chat)
   - Developer B: User Story 2 (Search)
   - Developer C: User Story 3 (Categories)
   - Developer D: User Story 4 (Documents)
   - Developer E: User Story 5 (Upload Utility)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
