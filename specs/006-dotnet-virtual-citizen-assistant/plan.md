# Implementation Plan: DotNet Virtual Citizen Assistant

**Branch**: `006-dotnet-virtual-citizen-assistant` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-dotnet-virtual-citizen-assistant/spec.md`

## Summary

RAG-powered AI assistant for NYC government services built with .NET 9, Semantic Kernel 1.65.0, and Azure AI Services. Provides conversational AI chat interface with document retrieval, advanced search, category browsing, and document viewing. Includes separate utility for batch uploading service documents to Azure AI Search.

## Technical Context

**Language/Version**: .NET 9.0 / C# 13
**Primary Dependencies**: Semantic Kernel 1.65.0, ASP.NET Core MVC, Azure.Search.Documents, Azure.AI.OpenAI
**Storage**: Azure AI Search (document index), session storage (chat history)
**Testing**: xUnit, Moq, FluentAssertions
**Target Platform**: Linux/Windows server, Azure App Service, Docker
**Project Type**: web - ASP.NET Core MVC + Console utility
**Performance Goals**: Chat response <5s, Search response <2s for 95% of queries
**Constraints**: Requires Azure OpenAI and Azure AI Search services, mobile-responsive UI
**Scale/Scope**: 100+ concurrent users, thousands of NYC service documents

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Existing project structure | PASS | Uses existing DotNet-Virtual-Citizen-Assistant folder with VirtualCitizenAgent.sln |
| .NET 9.0 consistent | PASS | Modern C# with latest framework |
| Semantic Kernel for AI | PASS | Standard Semantic Kernel 1.65.0 for AI orchestration |
| Mock services for offline | PASS | Fallback when Azure unavailable |

## Project Structure

### Documentation (this feature)

```text
specs/006-dotnet-virtual-citizen-assistant/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
DotNet-Virtual-Citizen-Assistant/
├── VirtualCitizenAgent.sln           # Solution file
├── VirtualCitizenAgent/              # Main web application
│   ├── Controllers/
│   │   ├── HomeController.cs         # Home page
│   │   ├── SearchController.cs       # Search API and views
│   │   ├── ChatController.cs         # Chat API
│   │   └── CategoriesController.cs   # Categories views
│   ├── Views/
│   │   ├── Home/                     # Home page views
│   │   ├── Search/                   # Search views
│   │   ├── Categories/               # Category views
│   │   └── Shared/                   # Layout and partials
│   ├── Models/
│   │   ├── ChatMessage.cs
│   │   ├── ChatSession.cs
│   │   ├── Document.cs
│   │   ├── SearchResult.cs
│   │   └── ServiceCategory.cs
│   ├── Services/
│   │   ├── ISearchService.cs
│   │   ├── SearchService.cs
│   │   ├── IChatService.cs
│   │   └── ChatService.cs
│   ├── Plugins/
│   │   └── DocumentSearchPlugin.cs   # Semantic Kernel plugin
│   ├── Configuration/
│   │   └── SearchConfiguration.cs
│   ├── Data/
│   │   └── ServiceDocument.cs
│   ├── wwwroot/
│   │   ├── css/
│   │   ├── js/
│   │   └── lib/                      # Bootstrap 5, Font Awesome
│   ├── appsettings.json
│   └── Program.cs
├── AzureSearchUploader/              # Data upload utility
│   ├── Models/
│   │   └── UploadDocument.cs
│   ├── Services/
│   │   └── DocumentUploadService.cs
│   ├── Data/
│   │   └── *.json                    # Sample JSON data
│   └── Program.cs
├── VirtualCitizenAgent.Tests/        # Test project
│   ├── Unit/
│   ├── Integration/
│   └── TestHelpers/
└── README.md
```

**Structure Decision**: Web application structure with separate utility project. Main project is ASP.NET Core MVC for web UI and API. Utility project is console app for data management. Test project covers both.

## Complexity Tracking

No constitution violations to justify.
