# Research: DotNet Virtual Citizen Assistant

**Feature**: 006-dotnet-virtual-citizen-assistant
**Date**: 2026-01-12

## Research Tasks Completed

### 1. Semantic Kernel Integration

**Decision**: Semantic Kernel 1.65.0 with Azure OpenAI connectors

**Rationale**:
- Native .NET library for AI orchestration
- First-class plugin system with KernelFunction attributes
- Built-in support for Azure OpenAI and Azure AI Search
- Supports function calling and automatic function invocation
- Active development and long-term Microsoft support

**Alternatives Considered**:
- LangChain.NET: Less mature, smaller community
- Direct Azure OpenAI SDK: No orchestration layer, manual prompt management
- OpenAI .NET SDK: Limited Azure integration

**Pattern**:
```csharp
// Kernel setup with Azure OpenAI
var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    deploymentName: "gpt-4",
    endpoint: endpoint,
    apiKey: apiKey
);

// Plugin registration
builder.Plugins.AddFromType<DocumentSearchPlugin>();

var kernel = builder.Build();

// Chat completion with function calling
var result = await kernel.InvokePromptAsync(userMessage,
    new KernelArguments(new OpenAIPromptExecutionSettings {
        ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions
    }));
```

### 2. RAG Pipeline Architecture

**Decision**: Azure AI Search retrieval → Context injection → Semantic Kernel completion

**Rationale**:
- Azure AI Search provides semantic ranking and vector search
- Retrieval before generation ensures grounded responses
- Source documents enable citation tracking
- Configurable context window management

**Pattern**:
```csharp
public class ChatService : IChatService
{
    public async Task<ChatResponse> GetResponseAsync(string userMessage, ChatSession session)
    {
        // 1. Retrieve relevant documents
        var documents = await _searchService.SemanticSearchAsync(userMessage, top: 5);

        // 2. Build context from retrieved documents
        var context = BuildContextFromDocuments(documents);

        // 3. Generate response with context
        var prompt = $"""
            You are a helpful NYC city services assistant.
            Use the following documents to answer the question.
            Always cite your sources.

            Documents:
            {context}

            Question: {userMessage}
            """;

        var response = await _kernel.InvokePromptAsync(prompt);

        // 4. Return response with sources
        return new ChatResponse
        {
            Content = response.ToString(),
            Sources = documents.Select(d => d.ToSource()).ToList()
        };
    }
}
```

### 3. DocumentSearchPlugin Design

**Decision**: 6 kernel functions covering all search operations

**Rationale**:
- Semantic Kernel plugins enable function calling from AI
- Descriptive attributes help AI choose correct function
- JSON serialization for interoperability
- Async methods for scalability

**Plugin Functions**:
```csharp
[KernelFunction("SearchDocuments")]
[Description("Search for NYC city service documents by keyword")]
public async Task<string> SearchDocumentsAsync(
    [Description("Search query string")] string query,
    [Description("Number of results to return")] int top = 10)

[KernelFunction("GetDocumentById")]
[Description("Retrieve a specific document by its unique identifier")]
public async Task<string> GetDocumentByIdAsync(
    [Description("Document ID")] string documentId)

[KernelFunction("SearchByCategory")]
[Description("Search for documents within a specific category")]
public async Task<string> SearchByCategoryAsync(
    [Description("Category name")] string category,
    [Description("Number of results")] int top = 10)

[KernelFunction("GetAvailableCategories")]
[Description("List all available service categories with document counts")]
public async Task<string> GetAvailableCategoriesAsync()

[KernelFunction("SemanticSearch")]
[Description("AI-powered semantic search for conceptually related documents")]
public async Task<string> SemanticSearchAsync(
    [Description("Natural language query")] string query,
    [Description("Number of results")] int top = 5)

[KernelFunction("GetRecentlyUpdatedDocuments")]
[Description("Find documents updated within a specified time period")]
public async Task<string> GetRecentlyUpdatedDocumentsAsync(
    [Description("Days to look back")] int days = 30)
```

### 4. Azure AI Search Integration

**Decision**: Azure.Search.Documents SDK with semantic configuration

**Rationale**:
- Native .NET SDK with async support
- Supports both keyword and semantic (vector) search
- Built-in faceting for category counts
- Managed Identity authentication support

**Pattern**:
```csharp
public class SearchService : ISearchService
{
    private readonly SearchClient _searchClient;

    public async Task<IEnumerable<SearchResult>> SearchAsync(string query, SearchOptions options)
    {
        var searchOptions = new SearchOptions
        {
            QueryType = SearchQueryType.Semantic,
            SemanticSearch = new SemanticSearchOptions
            {
                SemanticConfigurationName = "citizen-services-semantic",
                QueryCaption = new QueryCaption(QueryCaptionType.Extractive)
            },
            Size = options.Top,
            IncludeTotalCount = true,
            HighlightFields = { "content" }
        };

        var results = await _searchClient.SearchAsync<Document>(query, searchOptions);
        return results.Value.GetResults().Select(r => r.ToSearchResult());
    }
}
```

### 5. ASP.NET Core MVC Structure

**Decision**: MVC pattern with API controllers for chat/search endpoints

**Rationale**:
- Standard .NET web architecture
- Razor views for server-rendered pages
- API controllers for AJAX chat interactions
- Clear separation of concerns

**Controller Structure**:
- `HomeController`: Landing page, navigation
- `SearchController`: Search page, search API, document details
- `ChatController`: Chat API endpoint for AI interactions
- `CategoriesController`: Category browsing pages

### 6. Authentication & Authorization

**Decision**: Azure Managed Identity with optional API key fallback

**Rationale**:
- Managed Identity eliminates credential management in production
- API key support for local development
- No user authentication required for public service information
- RBAC-ready structure for future admin features

**Pattern**:
```csharp
// Configuration model
public class SearchConfiguration
{
    public string ServiceEndpoint { get; set; }
    public string IndexName { get; set; }
    public bool UseManagedIdentity { get; set; }
    public string? ApiKey { get; set; } // For development only
}

// Credential selection
TokenCredential credential = configuration.UseManagedIdentity
    ? new DefaultAzureCredential()
    : new AzureKeyCredential(configuration.ApiKey);
```

### 7. Web UI Framework

**Decision**: Bootstrap 5.3.0 with Font Awesome icons

**Rationale**:
- Responsive design out of the box
- Modern component library
- Consistent with government accessibility standards
- No JavaScript framework overhead

**Features**:
- Mobile-first responsive layout
- Accessible components (ARIA labels, keyboard navigation)
- Print-friendly document views
- Progressive loading for search results

### 8. Testing Strategy

**Decision**: xUnit with FluentAssertions and Moq

**Rationale**:
- Standard .NET testing framework
- FluentAssertions for readable assertions
- Moq for dependency injection testing
- WebApplicationFactory for integration tests

**Test Structure**:
```csharp
// Unit test example
public class SearchServiceTests
{
    private readonly Mock<SearchClient> _mockSearchClient;
    private readonly SearchService _service;

    [Fact]
    public async Task SearchAsync_WithValidQuery_ReturnsResults()
    {
        // Arrange
        _mockSearchClient.Setup(x => x.SearchAsync<Document>(
            It.IsAny<string>(),
            It.IsAny<SearchOptions>(),
            default))
            .ReturnsAsync(mockResponse);

        // Act
        var results = await _service.SearchAsync("parking permit");

        // Assert
        results.Should().NotBeEmpty();
        results.First().Title.Should().Contain("Parking");
    }
}
```

### 9. Data Upload Pipeline

**Decision**: Console application with batch processing and retry logic

**Rationale**:
- Separate utility from main application
- JSON file format for easy content management
- Batch indexing with configurable size
- Automatic retry for transient failures

**Pattern**:
```csharp
public class DocumentUploadService
{
    public async Task UploadDocumentsAsync(IEnumerable<UploadDocument> documents)
    {
        var batches = documents.Chunk(100); // 100 docs per batch

        foreach (var batch in batches)
        {
            await Policy
                .Handle<RequestFailedException>()
                .WaitAndRetryAsync(3, retryAttempt =>
                    TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)))
                .ExecuteAsync(async () =>
                {
                    await _indexClient.MergeOrUploadDocumentsAsync(batch);
                });
        }
    }
}
```

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle multi-turn conversations? | Session-based chat history with context window management |
| How to generate citations? | Source documents attached to responses with clickable links |
| How to balance keyword vs semantic search? | Configurable search modes with semantic as default |
| How to handle Azure service failures? | Graceful degradation with user-friendly error messages |
| How to manage document updates? | MergeOrUpload semantics for upsert behavior |

## Dependencies Confirmed

```text
# Main Application
Microsoft.SemanticKernel (1.65.0)
Azure.Search.Documents (11.5.0+)
Azure.AI.OpenAI (2.0.0+)
Azure.Identity (1.11.0+)
Microsoft.AspNetCore.Mvc.Razor.RuntimeCompilation

# Testing
xunit (2.7.0+)
xunit.runner.visualstudio
Moq (4.20.0+)
FluentAssertions (6.12.0+)
Microsoft.AspNetCore.Mvc.Testing
coverlet.collector

# Upload Utility
Azure.Search.Documents (11.5.0+)
Azure.Identity (1.11.0+)
Polly (8.3.0+)
System.Text.Json
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Azure OpenAI rate limits | Implement request throttling and queue |
| Token limit exceeded | Truncate context with relevance prioritization |
| Search index unavailable | Cache recent searches, show graceful error |
| Chat context overflow | Sliding window over message history |
| Mobile performance | Lazy loading, optimized images, minimal JS |
