# NYC Virtual Citizen Agent

A sophisticated AI-powered citizen service agent that provides intelligent, contextual responses about NYC government services using Retrieval-Augmented Generation (RAG). Built with .NET 9, Semantic Kernel, and Azure AI Services.

## 🎯 Features

✅ **RAG-Powered Chat Interface** - Interactive AI assistant with document retrieval  
✅ **Advanced Search** - Semantic and keyword search across government documents  
✅ **Service Categories** - Organized browsing of NYC services  
✅ **Document Details** - Full document viewing with print and sharing capabilities  
✅ **Real-time Results** - Live search with document counts and recommendations  
✅ **Responsive Design** - Works seamlessly on desktop and mobile devices  

## 📁 Project Structure

```
Virtual Citizen Agent/
├── .gitignore                       # Git ignore with .NET best practices
├── VirtualCitizenAgent.sln          # Solution file
├── VirtualCitizenAgent.code-workspace  # VS Code workspace configuration
├── README.md                        # This file
├── VirtualCitizenAgent/             # Main AI agent application
│   ├── Controllers/                 # API controllers (Search, Chat)
│   ├── Views/                       # Razor views (Home, Search, Categories)
│   ├── Models/                      # Data models
│   ├── Services/                    # Business logic services
│   ├── Plugins/                     # Semantic Kernel plugins
│   ├── Configuration/               # App configuration
│   ├── Data/                        # Data access layer
│   └── wwwroot/                     # Static web assets
└── AzureSearchUploader/             # Data upload utility
    ├── Models/                      # Data models for upload
    ├── Services/                    # Upload services
    ├── Data/                        # Sample JSON data
    └── Program.cs                   # Console application
```

## 🚀 Quick Start

### Option 1: Open VS Code Workspace (Recommended)
1. Open VS Code
2. File → Open Workspace from File
3. Select `VirtualCitizenAgent.code-workspace`

### Option 2: Open Folder
1. Open VS Code
2. File → Open Folder
3. Select the `Virtual Citizen Agent` folder

## 🏗️ Projects Overview

### VirtualCitizenAgent (Main Project)
**Purpose**: Core AI agent application for NYC citizen services

**Features**:
- 🤖 Semantic Kernel integration for AI capabilities
- 🌐 Web interface for citizen interactions
- 🧩 Extensible plugin system
- 🏗️ Clean architecture with organized folders

**Location**: `./VirtualCitizenAgent/`

**Run**: 
```bash
cd VirtualCitizenAgent
dotnet run
```

### AzureSearchUploader (Utility Project)
**Purpose**: Upload service documents to Azure AI Search

**Features**:
- 📄 JSON data processing
- 🔍 Azure AI Search integration
- 📊 Batch processing with retry logic
- ✅ Data validation and error handling

**Location**: `./AzureSearchUploader/`

**Run**:
```bash
cd AzureSearchUploader
dotnet run
```

## 🛠️ Development Workflow

### Building the Solution
```bash
# Build both projects
dotnet build

# Build specific project
dotnet build VirtualCitizenAgent
dotnet build AzureSearchUploader
```

### Running Projects
```bash
# Run main agent (from root)
dotnet run --project VirtualCitizenAgent

# Run data uploader (from root)
dotnet run --project AzureSearchUploader
```

### Adding Packages
```bash
# Add to main project
dotnet add VirtualCitizenAgent package PackageName

# Add to uploader project
dotnet add AzureSearchUploader package PackageName
```

## 🔧 VS Code Configuration

The workspace is configured with:
- **Solution Integration**: Recognizes both projects
- **Folder Exclusions**: Hides bin/obj folders
- **Extension Recommendations**: C# DevKit and related tools
- **Default Solution**: Points to VirtualCitizenAgent.sln

## 📝 Typical Development Process

1. **Data Upload**: Use AzureSearchUploader to populate Azure AI Search
2. **Agent Development**: Build AI capabilities in VirtualCitizenAgent
3. **Testing**: Test both data upload and agent responses
4. **Deployment**: Deploy agent with populated knowledge base

## 🤝 Contributing

1. Open the workspace in VS Code using the `.code-workspace` file
2. Both projects will be available in the Explorer
3. IntelliSense and debugging work across both projects
4. Use integrated terminal for project-specific commands

## 🏗️ Architecture

### Core Components

- **RAG Pipeline**: Document retrieval → Context building → AI response generation
- **Semantic Kernel Integration**: AI orchestration and plugin management  
- **Azure AI Search**: Document indexing and semantic search capabilities
- **Document Search Plugin**: 6 kernel functions for comprehensive document operations
- **Chat Controller**: RESTful API for conversational interactions
- **Web Interface**: Modern responsive UI with Bootstrap 5

### AI Capabilities

- **Semantic Search**: Natural language understanding for document retrieval
- **Contextual Responses**: AI generates answers using retrieved document context
- **Source Attribution**: Responses include clickable document sources
- **Multi-turn Conversations**: Maintains context across chat interactions

## 🛠️ Technology Stack

- **.NET 9.0** - Modern C# runtime and framework
- **ASP.NET Core MVC** - Web application framework
- **Semantic Kernel 1.65.0** - AI orchestration and plugin system
- **Azure AI Services** - Search, embeddings, and language models
- **Bootstrap 5.3.0** - Modern responsive UI framework
- **Font Awesome** - Professional iconography
- **JavaScript ES6+** - Client-side interactivity

## 🚀 Quick Start

### Prerequisites

- **.NET 9.0 SDK** - [Download here](https://dotnet.microsoft.com/download/dotnet/9.0)
- **Azure Subscription** - For AI Search and other services
- **Visual Studio Code** - Recommended IDE with C# Dev Kit

### 1. Clone and Setup

```bash
git clone [your-repo-url]
cd "Virtual Citizen Agent"
```

### 2. Configure Azure Services

Update `appsettings.json` in both projects with your Azure credentials:

```json
{
  "SearchConfiguration": {
    "ServiceEndpoint": "https://your-search-service.search.windows.net",
    "UseManagedIdentity": true,
    "IndexName": "citizen-services"
  }
}
```

### 3. Upload Sample Data

```bash
cd AzureSearchUploader
dotnet run
```

### 4. Run the Application

```bash
cd ../VirtualCitizenAgent
dotnet run
```

Navigate to `http://localhost:5000` to access the application.

## 💬 Using the Chat Interface

1. **Access the Chat**: Click "AI Chat Assistant" on the home page
2. **Ask Questions**: Natural language queries like "How do I get a parking permit?"
3. **Explore Sources**: Click source badges to view full documents
4. **Try Examples**: Use suggested questions to get started

### Example Queries

- "When is my trash picked up?"
- "How do I apply for a business license?"
- "What are the subway service updates?"
- "How do I report a street problem?"

## 🔍 Search Features

### Advanced Search Page
- **Keyword Search**: Traditional text-based search
- **Semantic Search**: Natural language understanding
- **Category Filters**: Filter by service categories
- **Recent Updates**: Find newly updated documents

### Categories Browser
- **Visual Grid**: Browse services by category cards
- **Document Counts**: See available documents per category
- **Quick Access**: Direct links to category-specific searches

## 🛡️ Security & Best Practices

### Authentication
- Azure Managed Identity (recommended)
- API key authentication (development)
- Role-based access control ready

### Data Privacy
- No personally identifiable information stored
- Session-based chat history (temporary)
- Secure API communications

### Performance
- Efficient document retrieval with caching
- Batch processing for data uploads
- Responsive design with progressive loading

## 🧩 Plugin Development

The DocumentSearchPlugin provides 6 kernel functions:

1. **SearchDocuments** - General document search
2. **GetDocumentById** - Retrieve specific documents
3. **SearchByCategory** - Category-filtered search
4. **GetAvailableCategories** - List all categories
5. **SemanticSearch** - AI-powered semantic search
6. **GetRecentlyUpdatedDocuments** - Find recent updates

### Adding New Plugins

```csharp
[KernelFunction, Description("Your plugin description")]
public async Task<string> YourFunctionAsync(
    [Description("Parameter description")] string parameter)
{
    // Implementation
    return JsonSerializer.Serialize(result);
}
```

## 🚀 Deployment

### Azure App Service
```bash
# Publish to Azure
dotnet publish -c Release
```

### Docker Support
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:9.0
COPY bin/Release/net9.0/publish/ App/
WORKDIR /App
ENTRYPOINT ["dotnet", "VirtualCitizenAgent.dll"]
```

## � Testing

The project includes comprehensive test coverage with automated unit tests and integration tests.

### Running Tests
```bash
# Run all tests
dotnet test

# Run with detailed output
dotnet test --verbosity normal

# Run specific test project
dotnet test VirtualCitizenAgent.Tests
```

### Test Coverage
- **Total Tests**: 101
- **Unit Tests**: 98 (covering services, models, controllers, plugins)
- **Integration Tests**: 3 (manual configuration required)
- **Test Coverage**: Models, Services, Controllers, Plugins, API contracts

### Manual Integration Test Configuration

The project includes 3 integration tests that require real Azure OpenAI credentials for manual execution:

#### 1. Set Up Azure OpenAI Service
1. Create an Azure OpenAI resource in the Azure portal
2. Deploy a GPT-4 or GPT-3.5-turbo model
3. Note your endpoint, deployment name, and API key

#### 2. Configure Test Credentials

**Option A: Using .env file (Recommended for development)**
Create a `.env` file in the project root:
```bash
OPENAI__ENDPOINT=https://your-resource.openai.azure.com/
OPENAI__DEPLOYMENTNAME=your-deployment-name
OPENAI__APIKEY=your-api-key
```

**Option B: Using User Secrets**
```bash
cd VirtualCitizenAgent.Tests
dotnet user-secrets set "OpenAI:Endpoint" "https://your-resource.openai.azure.com/"
dotnet user-secrets set "OpenAI:DeploymentName" "your-deployment-name"
dotnet user-secrets set "OpenAI:ApiKey" "your-api-key"
```

**Option C: Using Environment Variables**
```bash
export OPENAI__ENDPOINT="https://your-resource.openai.azure.com/"
export OPENAI__DEPLOYMENTNAME="your-deployment-name"
export OPENAI__APIKEY="your-api-key"
```

#### 3. Enable Integration Tests

Edit `VirtualCitizenAgent.Tests/Integration/RealOpenAIIntegrationTests.cs` and change:
```csharp
// From:
[Fact(Skip = "Requires real OpenAI credentials - enable manually for integration testing")]

// To:
[Fact]
```

#### 4. Integration Tests Description

- **`OpenAI_WithRealCredentials_ShouldGenerateResponse`**: Tests basic Azure OpenAI connectivity and response generation
- **`OpenAI_QueryEnhancement_ShouldImproveSearchTerms`**: Tests AI-powered query enhancement for search optimization
- **`OpenAI_WithKernelFunctions_ShouldInvokePluginFunctions`**: Tests Semantic Kernel plugin integration with AI functions

#### 5. Run Integration Tests
```bash
# Run all tests including integration tests
dotnet test VirtualCitizenAgent.Tests --verbosity normal

# Run only integration tests
dotnet test VirtualCitizenAgent.Tests --filter "Category=Integration" --verbosity normal
```

### Test Architecture
- **FluentAssertions**: For readable test assertions
- **Moq**: For mocking dependencies
- **xUnit**: Test framework with parallel execution
- **TestWebApplicationFactory**: For integration testing ASP.NET Core applications

## �🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow coding standards**: Clean architecture principles
4. **Add tests**: Ensure functionality works correctly (maintain 100% unit test pass rate)
5. **Update documentation**: Keep README and comments current
6. **Submit pull request**: Describe your changes clearly

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions and support:

1. **Check Documentation**: Review this README and inline code comments
2. **Search Issues**: Look for existing GitHub issues
3. **Create Issue**: Submit detailed bug reports or feature requests
4. **Discussions**: Use GitHub Discussions for questions

---

**Built with ❤️ for NYC citizens using modern .NET and AI technologies**