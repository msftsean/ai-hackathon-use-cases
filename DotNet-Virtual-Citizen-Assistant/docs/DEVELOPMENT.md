# Development Guide

## Project Structure Overview

This document provides detailed information about the project structure and development workflow.

## 📁 Detailed Folder Structure

### VirtualCitizenAgent (Main Application)

```
VirtualCitizenAgent/
├── Controllers/                     # HTTP API Controllers
│   ├── SearchController.cs          # Document search endpoints
│   ├── ChatController.cs            # AI chat endpoints
│   └── HomeController.cs            # Web page controllers
├── Views/                           # Razor View Templates
│   ├── Home/
│   │   ├── Index.cshtml             # Home page with chat interface
│   │   ├── Search.cshtml            # Advanced search page
│   │   ├── Categories.cshtml        # Service categories browser
│   │   └── About.cshtml             # About page
│   ├── Shared/
│   │   ├── _Layout.cshtml           # Main layout template
│   │   └── Error.cshtml             # Error page template
├── Models/                          # Data Models
│   └── ServiceDocument.cs           # Document model
├── Services/                        # Business Logic Services
│   ├── IDocumentSearchService.cs    # Search service interface
│   └── AzureAIDocumentSearchService.cs # Azure AI Search implementation
├── Plugins/                         # Semantic Kernel Plugins
│   └── DocumentSearchPlugin.cs      # Main search plugin (6 functions)
├── Configuration/                   # Application Configuration
├── Data/                           # Data Access Layer
├── wwwroot/                        # Static Web Assets
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript files
│   ├── lib/                        # Third-party libraries
│   └── favicon.ico                 # Site icon
├── appsettings.json                # App configuration
├── Program.cs                      # Application entry point
└── VirtualCitizenAgent.csproj      # Project file
```

### AzureSearchUploader (Data Upload Utility)

```
AzureSearchUploader/
├── Models/                         # Data Models
│   └── ServiceDocument.cs          # Document model for upload
├── Services/                       # Upload Services
│   ├── IAzureSearchService.cs      # Search service interface
│   ├── AzureSearchService.cs       # Azure search operations
│   └── JsonDataLoader.cs           # JSON file processing
├── Data/                           # Sample Data
│   └── services.json               # Example service documents
├── appsettings.json                # Upload configuration
├── Program.cs                      # Console application entry
└── AzureSearchUploader.csproj      # Project file
```

## 🔧 Development Workflow

### 1. Data Preparation and Upload

Before developing or testing the main application, you need to populate Azure AI Search with documents:

```bash
cd AzureSearchUploader
# Configure appsettings.json with your Azure credentials
dotnet run
```

### 2. Main Application Development

With data uploaded, develop and test the main application:

```bash
cd VirtualCitizenAgent
dotnet run
```

### 3. Plugin Development

When adding new AI capabilities:

1. **Create Plugin**: Add new plugin class in `Plugins/` folder
2. **Register Plugin**: Update `Program.cs` to register the plugin
3. **Add Controller**: Create API endpoints in controllers
4. **Update UI**: Add frontend functionality as needed

### 4. Testing Workflow

```bash
# Test data upload
cd AzureSearchUploader
dotnet test

# Test main application
cd ../VirtualCitizenAgent
dotnet test

# Integration testing
# 1. Upload test data
# 2. Run main application
# 3. Test chat and search functionality
```

## 🏗️ Architecture Patterns

### Clean Architecture
- **Controllers**: Handle HTTP requests/responses
- **Services**: Business logic and external integrations
- **Models**: Data structures and validation
- **Plugins**: AI-specific functionality

### Dependency Injection
All services are registered in `Program.cs`:
- `IDocumentSearchService` → `AzureAIDocumentSearchService`
- `Kernel` → Semantic Kernel instance
- `DocumentSearchPlugin` → Registered as scoped service

### RAG Pattern Implementation
1. **Query** → User asks question
2. **Retrieve** → Search relevant documents
3. **Augment** → Build context from documents
4. **Generate** → AI creates response with context

## 🔌 Plugin System

### Current Plugins

#### DocumentSearchPlugin
- **SearchDocuments**: General text search
- **GetDocumentById**: Retrieve specific document
- **SearchByCategory**: Category-filtered search
- **GetAvailableCategories**: List categories
- **SemanticSearch**: AI-powered search
- **GetRecentlyUpdatedDocuments**: Recent updates

### Adding New Plugins

1. **Create Plugin Class**:
```csharp
public class YourPlugin
{
    [KernelFunction, Description("Function description")]
    public async Task<string> YourFunctionAsync(string parameter)
    {
        // Implementation
        return JsonSerializer.Serialize(result);
    }
}
```

2. **Register in Program.cs**:
```csharp
builder.Services.AddScoped<YourPlugin>();

// After kernel creation
kernel.ImportPluginFromObject(serviceProvider.GetRequiredService<YourPlugin>(), "YourPlugin");
```

3. **Use in Controllers**:
```csharp
var result = await _kernel.InvokeAsync("YourPlugin", "YourFunction", arguments);
```

## 🎨 Frontend Development

### Technologies Used
- **Bootstrap 5.3.0**: UI framework
- **Font Awesome**: Icons
- **Vanilla JavaScript**: No framework dependencies
- **Razor Pages**: Server-side rendering

### Key JavaScript Files
- **Chat functionality**: Embedded in `Index.cshtml`
- **Search functionality**: Embedded in `Search.cshtml`
- **Category browser**: Embedded in `Categories.cshtml`

### CSS Organization
- **Bootstrap**: Primary styling framework
- **Custom styles**: Embedded in view files for component-specific styling
- **Responsive design**: Mobile-first approach

## 🔧 Configuration Management

### appsettings.json Structure

#### VirtualCitizenAgent
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "SearchConfiguration": {
    "ServiceEndpoint": "https://your-service.search.windows.net",
    "UseManagedIdentity": true,
    "IndexName": "citizen-services"
  },
  "CityName": "New York City"
}
```

#### AzureSearchUploader
```json
{
  "SearchConfiguration": {
    "ServiceEndpoint": "https://your-service.search.windows.net",
    "IndexName": "citizen-services",
    "UseManagedIdentity": true,
    "BatchSize": 100,
    "MaxRetryAttempts": 3
  },
  "DataConfiguration": {
    "InputFilePath": "./Data/services.json",
    "ClearIndexBeforeUpload": false
  }
}
```

### Environment-Specific Configuration
- **Development**: `appsettings.Development.json` (not tracked in git)
- **Production**: Environment variables or Azure Key Vault
- **Secrets**: Use .NET User Secrets for development

## 🧪 Testing Strategy

### Current Test Status (✅ All Tests Passing)
- **Total Tests**: 101
- **Passed**: 98 automated tests
- **Skipped**: 3 integration tests (manual configuration required)
- **Failed**: 0
- **Warnings**: 0

### Test Categories

#### Unit Tests (98 tests)
- **Service Tests**: Business logic validation
  - `DocumentSearchService`: Search functionality
  - `AIEnhancedQueryService`: AI query enhancement
  - `OpenAIKernelIntegration`: Semantic Kernel integration
  
- **Plugin Tests**: Semantic Kernel functions
  - `DocumentSearchPlugin`: 6 plugin functions testing
  - Parameter validation and error handling
  - Mock service integration
  
- **Controller Tests**: HTTP API endpoints
  - `SearchController`: Document search endpoints
  - Parameter validation and response formatting
  - Dependency injection testing
  
- **Model Tests**: Data model validation
  - `ErrorViewModel`: Error handling models
  - `SearchResultDocument`: Search result serialization

#### Integration Tests (3 tests - Manual Setup Required)
- **`OpenAI_WithRealCredentials_ShouldGenerateResponse`**: Basic Azure OpenAI connectivity
- **`OpenAI_QueryEnhancement_ShouldImproveSearchTerms`**: AI query enhancement
- **`OpenAI_WithKernelFunctions_ShouldInvokePluginFunctions`**: Plugin function execution

### Test Configuration

#### Automated Tests
All unit tests run automatically with no configuration needed. They use:
- **Mocked Dependencies**: No external service calls
- **In-Memory Data**: Fast test execution
- **Parallel Execution**: Optimized test performance

#### Manual Integration Tests
These tests require real Azure OpenAI credentials:

1. **Create Azure OpenAI Resource**
2. **Configure Credentials** (choose one method):
   - `.env` file in project root
   - .NET User Secrets
   - Environment variables
3. **Enable Tests**: Remove `Skip` attribute
4. **Run Tests**: `dotnet test --verbosity normal`

### Running Tests

```bash
# Run all automated tests (excludes manual integration tests)
dotnet test

# Run with detailed output
dotnet test --verbosity normal

# Run specific test categories
dotnet test --filter "Category=Unit"
dotnet test --filter "TestCategory=Service"

# Run tests with coverage (requires coverlet)
dotnet test --collect:"XPlat Code Coverage"
```

### Test Architecture
- **Framework**: xUnit 2.5.3 with async/await support
- **Assertions**: FluentAssertions 6.12.1 for readable test code
- **Mocking**: Moq 4.20.72 for dependency mocking
- **Integration**: TestWebApplicationFactory for ASP.NET Core testing
- **Configuration**: Supports multiple configuration sources

### Adding New Tests

1. **Unit Tests**: Add to appropriate test class in `VirtualCitizenAgent.Tests/`
2. **Integration Tests**: Add to integration test classes with proper setup
3. **Mocking**: Use Moq for external dependencies
4. **Assertions**: Use FluentAssertions for clear test failures
5. **Naming**: Follow pattern `MethodName_Scenario_ExpectedResult`

### Test Data Management
- **Mock Services**: Realistic test data without external dependencies
- **Test Fixtures**: Reusable test setup and data
- **Configuration**: Separate test configurations for different scenarios

## 🚀 Deployment

### Local Development
```bash
dotnet run --environment Development
```

### Production Deployment
```bash
# Build release version
dotnet publish -c Release -o ./publish

# Deploy to Azure App Service
# (Use Azure DevOps, GitHub Actions, or manual deployment)
```

### Environment Variables
- `ASPNETCORE_ENVIRONMENT`: Set to "Production"
- `SearchConfiguration__ServiceEndpoint`: Azure Search endpoint
- `SearchConfiguration__UseManagedIdentity`: Use managed identity

## 📚 Additional Resources

- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [ASP.NET Core Documentation](https://learn.microsoft.com/en-us/aspnet/core/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.3/)

---

This guide provides the foundation for understanding and extending the NYC Virtual Citizen Agent. For specific implementation details, refer to the inline code documentation and comments.