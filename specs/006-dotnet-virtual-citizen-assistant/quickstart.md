# Quickstart: DotNet Virtual Citizen Assistant

**Feature**: 006-dotnet-virtual-citizen-assistant
**Estimated Setup Time**: 20 minutes

## Prerequisites

- .NET 9.0 SDK - [Download here](https://dotnet.microsoft.com/download/dotnet/9.0)
- Visual Studio Code with C# Dev Kit (recommended)
- Azure subscription with:
  - Azure AI Search service
  - Azure OpenAI service with GPT-4 deployment
  - (Optional) Azure App Service for deployment

## Step 1: Environment Setup

```bash
# Navigate to project directory
cd DotNet-Virtual-Citizen-Assistant

# Restore dependencies
dotnet restore

# Build the solution
dotnet build
```

## Step 2: Configure Azure Services

Update `VirtualCitizenAgent/appsettings.json`:

```json
{
  "SearchConfiguration": {
    "ServiceEndpoint": "https://your-search-service.search.windows.net",
    "IndexName": "citizen-services",
    "UseManagedIdentity": false,
    "ApiKey": "your-search-api-key"
  },
  "OpenAI": {
    "Endpoint": "https://your-openai-service.openai.azure.com/",
    "DeploymentName": "gpt-4",
    "ApiKey": "your-openai-api-key"
  }
}
```

**Production Note**: Set `UseManagedIdentity: true` and remove API keys when deploying to Azure.

## Step 3: Upload Sample Data

```bash
# Navigate to uploader project
cd AzureSearchUploader

# Update appsettings.json with your search credentials

# Run the uploader
dotnet run
```

Expected output:
```
Starting document upload...
Processing batch 1 of 5...
Successfully indexed 100 documents
...
Upload complete: 500 documents indexed
```

## Step 4: Verify Installation

```bash
# Run all tests
dotnet test

# Expected output: 101 tests passed
# - 98 unit tests
# - 3 integration tests (skipped unless credentials configured)
```

## Step 5: Run the Application

```bash
# Navigate to main project
cd VirtualCitizenAgent

# Run the application
dotnet run
```

Navigate to `http://localhost:5000` to access the application.

## Step 6: Try the Features

### Chat Interface

1. Click "AI Chat Assistant" on the home page
2. Ask a question: "How do I get a parking permit?"
3. View the AI response with source citations
4. Click source badges to view full documents

### Search

1. Click "Search" in the navigation
2. Enter a query: "business license"
3. Toggle between keyword and semantic search
4. Click a result to view full document

### Categories

1. Click "Categories" in the navigation
2. Browse the category grid
3. Click a category to see related documents

## Quick Examples

### C# API Usage

```csharp
// Search for documents
var searchService = serviceProvider.GetRequiredService<ISearchService>();
var results = await searchService.SearchAsync("parking permit", new SearchOptions
{
    Mode = SearchMode.Semantic,
    Top = 10
});

foreach (var result in results.Results)
{
    Console.WriteLine($"{result.Document.Title} (Score: {result.Score:F2})");
}
```

### Chat with RAG

```csharp
// Send chat message with RAG
var chatService = serviceProvider.GetRequiredService<IChatService>();
var response = await chatService.SendMessageAsync(
    sessionId: Guid.NewGuid().ToString(),
    message: "What are the requirements for a food vendor license?"
);

Console.WriteLine($"Response: {response.Content}");
Console.WriteLine($"Sources: {string.Join(", ", response.Sources.Select(s => s.Title))}");
```

### Using DocumentSearchPlugin

```csharp
// Create Semantic Kernel with plugin
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(deploymentName, endpoint, apiKey)
    .Build();

kernel.Plugins.AddFromType<DocumentSearchPlugin>(serviceProvider);

// AI can now call plugin functions automatically
var result = await kernel.InvokePromptAsync(
    "Find documents about trash collection schedules",
    new KernelArguments(new OpenAIPromptExecutionSettings
    {
        ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions
    })
);
```

## Running Tests

```bash
# Run all tests
dotnet test

# Run with verbose output
dotnet test --verbosity normal

# Run specific test category
dotnet test --filter "Category=Unit"
dotnet test --filter "Category=Integration"

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

### Enabling Integration Tests

Integration tests require real Azure OpenAI credentials. To enable:

1. Create `.env` file in project root:
```bash
OPENAI__ENDPOINT=https://your-resource.openai.azure.com/
OPENAI__DEPLOYMENTNAME=gpt-4
OPENAI__APIKEY=your-api-key
```

2. Edit `VirtualCitizenAgent.Tests/Integration/RealOpenAIIntegrationTests.cs`:
```csharp
// Change from:
[Fact(Skip = "Requires real OpenAI credentials")]
// To:
[Fact]
```

3. Run integration tests:
```bash
dotnet test --filter "Category=Integration"
```

## Sample Data

Test with provided sample data in `AzureSearchUploader/Data/`:

### Document Categories

- **Transportation**: Parking permits, subway info, bus routes
- **Business**: Licenses, permits, regulations
- **Housing**: Rental assistance, building codes
- **Health**: Clinics, vaccinations, inspections
- **Education**: Schools, programs, enrollment

### Sample Queries

- "How do I get a parking permit in Brooklyn?"
- "What are the requirements for a food vendor license?"
- "When is my trash picked up?"
- "How do I report a pothole?"
- "What subway lines are running this weekend?"

## Troubleshooting

### "Search service unavailable" errors

- Verify Azure AI Search endpoint and API key in `appsettings.json`
- Check that the index `citizen-services` exists
- Run `AzureSearchUploader` to create/populate the index

### "OpenAI service unavailable" errors

- Verify Azure OpenAI endpoint and API key
- Check that the deployment name matches your Azure OpenAI deployment
- Ensure the deployment is in the same region as the endpoint

### "No results found" for searches

- Run `AzureSearchUploader` to populate the search index
- Verify documents are indexed: check Azure Portal → AI Search → Indexes
- Try a simpler query to test basic functionality

### Build errors

```bash
# Clean and rebuild
dotnet clean
dotnet restore
dotnet build
```

### Port conflicts

Change the port in `Properties/launchSettings.json`:
```json
{
  "profiles": {
    "http": {
      "applicationUrl": "http://localhost:5001"
    }
  }
}
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/chat | Send chat message, get AI response |
| POST | /api/chat/session | Create new chat session |
| GET | /api/chat/session/{id} | Get session history |
| DELETE | /api/chat/session/{id} | Delete session |
| GET | /api/search?q={query} | Search documents |
| GET | /api/search/semantic?q={query} | Semantic search |
| GET | /api/documents/{id} | Get document by ID |
| GET | /api/documents/recent | Get recent updates |
| GET | /api/categories | List all categories |
| GET | /api/categories/{name} | Get category details |
| GET | /api/health | Health check |

## Deployment

### Azure App Service

```bash
# Publish the application
dotnet publish -c Release -o ./publish

# Deploy using Azure CLI
az webapp deploy --resource-group your-rg --name your-app --src-path ./publish
```

### Docker

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM base AS final
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "VirtualCitizenAgent.dll"]
```

```bash
# Build and run Docker image
docker build -t virtual-citizen-agent .
docker run -p 5000:80 virtual-citizen-agent
```

## Next Steps

1. Customize the document categories for your city
2. Add more service documents to the search index
3. Configure Azure Managed Identity for production
4. Set up monitoring with Application Insights
5. Implement user authentication if needed

## Support

- Run tests to verify setup: `dotnet test`
- Check sample data for expected document formats
- Review inline code comments and XML documentation
