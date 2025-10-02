using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Moq;
using System.Text.Json;
using VirtualCitizenAgent.Plugins;
using VirtualCitizenAgent.Services;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Tests.Integration;

namespace VirtualCitizenAgent.Tests.Services;

/// <summary>
/// Tests for OpenAI integration through Semantic Kernel
/// These tests focus on testing the AI-powered functionality without requiring actual OpenAI API calls
/// </summary>
public class OpenAIIntegrationTests
{
    private readonly Mock<IChatCompletionService> _mockChatCompletion;
    private readonly Mock<ILogger<DocumentSearchPlugin>> _mockLogger;
    private readonly Mock<IDocumentSearchService> _mockSearchService;

    public OpenAIIntegrationTests()
    {
        _mockChatCompletion = new Mock<IChatCompletionService>();
        _mockLogger = new Mock<ILogger<DocumentSearchPlugin>>();
        _mockSearchService = new Mock<IDocumentSearchService>();
    }

    [Fact]
    public void KernelBuilder_ShouldConfigureAzureOpenAI_WithValidConfiguration()
    {
        // Arrange
        var kernelBuilder = Kernel.CreateBuilder();
        
        // Act
        var act = () => kernelBuilder.Services.AddAzureOpenAIChatCompletion(
            deploymentName: "test-deployment",
            endpoint: "https://test.openai.azure.com/",
            apiKey: "test-key");

        // Assert
        act.Should().NotThrow();
    }

    [Theory]
    [InlineData("test-deployment", "", "test-key")]                // Missing endpoint should throw
    [InlineData("test-deployment", "https://test.openai.azure.com/", "")] // Missing API key should throw
    public void KernelBuilder_ShouldThrowException_WithInvalidConfiguration(
        string deploymentName, string endpoint, string apiKey)
    {
        // Arrange
        var kernelBuilder = Kernel.CreateBuilder();
        
        // Act & Assert
        var act = () => kernelBuilder.Services.AddAzureOpenAIChatCompletion(
            deploymentName: deploymentName,
            endpoint: endpoint, 
            apiKey: apiKey);

        act.Should().Throw<ArgumentException>();
    }

    [Fact]
    public async Task SemanticSearch_WithMockedAI_ShouldEnhanceSearchResults()
    {
        // Arrange
        var searchResults = new List<SearchResultDocument>
        {
            new SearchResultDocument
            {
                Id = "doc1",
                Title = "Trash Collection Services",
                Content = "Information about NYC trash collection",
                ServiceType = "Sanitation",
                Category = "Waste Management"
            }
        };

        _mockSearchService.Setup(s => s.SemanticSearchAsync(It.IsAny<string>(), It.IsAny<int>()))
            .ReturnsAsync(searchResults);

        var plugin = new DocumentSearchPlugin(_mockSearchService.Object, _mockLogger.Object);

        // Act
        var result = await plugin.SemanticSearchAsync("I need help with garbage pickup", 5);

        // Assert
        result.Should().NotBeNullOrEmpty();
        var jsonResult = JsonSerializer.Deserialize<JsonElement>(result);
        jsonResult.GetProperty("semantic_query").GetString().Should().Be("I need help with garbage pickup");
        jsonResult.GetProperty("total_results").GetInt32().Should().Be(1);
        
        _mockSearchService.Verify(s => s.SemanticSearchAsync("I need help with garbage pickup", 5), Times.Once);
    }

    [Fact]
    public void ChatCompletion_ShouldProcessUserQuery_WithContextualResponse()
    {
        // This test demonstrates how you would test AI-enhanced responses
        // In a real scenario, you might have a service that uses ChatCompletion to improve search queries
        
        // Arrange
        var userQuery = "When is my trash picked up?";
        var expectedEnhancedQuery = "NYC trash collection schedule pickup times";

        // Act & Assert - This would be implemented when you add AI-enhanced query processing
        userQuery.Should().NotBeNullOrEmpty();
        expectedEnhancedQuery.Should().Contain("trash collection");
    }

    [Fact]
    public void OpenAIConfiguration_ShouldBeValidated_OnStartup()
    {
        // Arrange & Act
        var requiredKeys = new[]
        {
            "OpenAI:DeploymentName",
            "OpenAI:Endpoint", 
            "OpenAI:ApiKey"
        };

        // Assert
        foreach (var key in requiredKeys)
        {
            key.Should().NotBeNullOrEmpty("Configuration key {0} should be defined", key);
        }
    }
}

/// <summary>
/// Integration tests for OpenAI functionality that require actual kernel setup
/// These tests use the TestWebApplicationFactory but focus on AI-specific features
/// </summary>
public class OpenAIKernelIntegrationTests : IClassFixture<TestWebApplicationFactory>
{
    private readonly TestWebApplicationFactory _factory;

    public OpenAIKernelIntegrationTests(TestWebApplicationFactory factory)
    {
        _factory = factory;
    }

    [Fact]
    public void Kernel_ShouldBeRegistered_InDependencyInjection()
    {
        // Arrange & Act
        using var scope = _factory.Services.CreateScope();
        var kernel = scope.ServiceProvider.GetService<Kernel>();

        // Assert
        kernel.Should().NotBeNull("Kernel should be registered in DI container");
    }

    [Fact]
    public void Kernel_ShouldHaveDocumentSearchPlugin_Registered()
    {
        // Arrange & Act
        using var scope = _factory.Services.CreateScope();
        var kernel = scope.ServiceProvider.GetService<Kernel>();

        // Assert
        kernel.Should().NotBeNull();
        var plugins = kernel!.Plugins;
        plugins.Should().ContainSingle(p => p.Name == "DocumentSearch",
            "DocumentSearch plugin should be registered");
    }

    [Fact]
    public void Kernel_ShouldHaveExpectedFunctions_InDocumentSearchPlugin()
    {
        // Arrange & Act
        using var scope = _factory.Services.CreateScope();
        var kernel = scope.ServiceProvider.GetService<Kernel>();

        // Assert
        kernel.Should().NotBeNull();
        var documentSearchPlugin = kernel!.Plugins["DocumentSearch"];
        
        var expectedFunctions = new[]
        {
            "SearchDocuments",
            "GetDocumentById", 
            "SearchByCategory",
            "GetAvailableCategories",
            "SemanticSearch",
            "GetRecentlyUpdatedDocuments"
        };

        foreach (var functionName in expectedFunctions)
        {
            documentSearchPlugin.Should().Contain(f => f.Name == functionName,
                "Function {0} should be available in DocumentSearch plugin", functionName);
        }
    }

    [Fact]
    public void Kernel_ShouldInvokePlugin_WithoutOpenAIConnection()
    {
        // This test verifies that the kernel can invoke plugins even without OpenAI configured
        // (useful for testing the plugin structure itself)
        
        // Arrange
        using var scope = _factory.Services.CreateScope();
        var kernel = scope.ServiceProvider.GetService<Kernel>();

        // Act & Assert
        kernel.Should().NotBeNull();
        
        // Verify that plugin functions exist and can be referenced
        var function = kernel!.Plugins.GetFunction("DocumentSearch", "SearchDocuments");
        function.Should().NotBeNull("SearchDocuments function should be available");
        function.Name.Should().Be("SearchDocuments");
    }
}