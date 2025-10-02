using FluentAssertions;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using System.ComponentModel;
using System.Text.Json;
using VirtualCitizenAgent.Tests.Helpers;
using DotNetEnv;

namespace VirtualCitizenAgent.Tests.Integration;

/// <summary>
/// Integration tests for OpenAI functionality with real Azure OpenAI service
/// These tests require actual Azure OpenAI credentials and should be run manually
/// or in a CI/CD environment with proper secrets configured
/// 
/// To run these tests:
/// 1. Set up Azure OpenAI service
/// 2. Configure user secrets or environment variables:
///    - OpenAI:DeploymentName
///    - OpenAI:Endpoint  
///    - OpenAI:ApiKey
/// 3. Mark tests with [Fact] instead of [Fact(Skip = "Requires real OpenAI credentials")]
/// </summary>
public class RealOpenAIIntegrationTests
{
    private readonly IConfiguration _configuration;

    public RealOpenAIIntegrationTests()
    {
        // Load .env file from the project root
        var envFilePath = Path.Combine(Directory.GetCurrentDirectory(), "..", "..", "..", "..", ".env");
        if (File.Exists(envFilePath))
        {
            DotNetEnv.Env.Load(envFilePath);
            Console.WriteLine($"📁 Loaded .env file from: {envFilePath}");
        }
        else
        {
            Console.WriteLine($"⚠️ .env file not found at: {envFilePath}");
        }

        // This configuration loads from user secrets, environment variables, and .env file
        _configuration = new ConfigurationBuilder()
            .AddUserSecrets<RealOpenAIIntegrationTests>()
            .AddEnvironmentVariables()
            .Build();
    }

    [Fact] // Enabled for real Azure OpenAI testing with .env file
    public async Task OpenAI_WithRealCredentials_ShouldGenerateResponse()
    {
        // Arrange
        if (!HasValidConfiguration())
        {
            var (endpoint, apiKey, deploymentName) = OpenAITestHelper.GetOpenAIConfiguration(_configuration);
            throw new SkipException($"OpenAI configuration not complete. Found: Endpoint={!string.IsNullOrEmpty(endpoint)}, ApiKey={!string.IsNullOrEmpty(apiKey)}, Deployment={!string.IsNullOrEmpty(deploymentName)}");
        }

        Console.WriteLine("🔌 Testing real Azure OpenAI connection...");
        var kernel = CreateKernelWithRealOpenAI();
        var chatService = kernel.GetRequiredService<IChatCompletionService>();

        // Act
        var response = await chatService.GetChatMessageContentAsync(
            "Say hello and briefly introduce yourself as the NYC Virtual Citizen Assistant!");

        // Assert
        response.Should().NotBeNull();
        response.Content.Should().NotBeNullOrEmpty();
        response.Content.Should().ContainAny("hello", "Hello", "assistant", "Assistant", "NYC");
        
        Console.WriteLine($"✅ Azure OpenAI Response: {response.Content}");
    }

    [Fact(Skip = "Requires real OpenAI credentials - enable manually for integration testing")]
    public async Task OpenAI_QueryEnhancement_ShouldImproveSearchTerms()
    {
        // Arrange
        if (!HasValidConfiguration())
        {
            throw new SkipException("OpenAI configuration not available");
        }

        var kernel = CreateKernelWithRealOpenAI();
        var chatService = kernel.GetRequiredService<IChatCompletionService>();

        var userQuery = "My garbage isn't being picked up";
        var enhancementPrompt = $@"
            Transform this user query into better search terms for a NYC government services database:
            User Query: '{userQuery}'
            
            Return only the enhanced search terms as a comma-separated list, focusing on official terminology.
            ";

        // Act
        var response = await chatService.GetChatMessageContentAsync(enhancementPrompt);

        // Assert
        response.Should().NotBeNull();
        response.Content.Should().NotBeNullOrEmpty();
        response.Content.Should().ContainAny("sanitation", "waste", "collection", "pickup");
    }

    [Fact(Skip = "Requires real OpenAI credentials - enable manually for integration testing")]
    public async Task OpenAI_WithKernelFunctions_ShouldInvokePluginFunctions()
    {
        // Arrange
        if (!HasValidConfiguration())
        {
            throw new SkipException("OpenAI configuration not available");
        }

        var kernel = CreateKernelWithRealOpenAI();
        
        // Add a simple test plugin
        kernel.ImportPluginFromType<TestAIPlugin>("TestAI");

        // Act
        var result = await kernel.InvokeAsync("TestAI", "GetServiceInfo", 
            new KernelArguments { ["serviceType"] = "trash collection" });

        // Assert
        result.Should().NotBeNull();
        result.GetValue<string>().Should().NotBeNullOrEmpty();
    }

    [Fact(Skip = "Requires real OpenAI credentials - enable manually for integration testing")]
    public async Task OpenAI_Performance_ShouldRespondWithinReasonableTime()
    {
        // Arrange
        if (!HasValidConfiguration())
        {
            throw new SkipException("OpenAI configuration not available");
        }

        var kernel = CreateKernelWithRealOpenAI();
        var chatService = kernel.GetRequiredService<IChatCompletionService>();
        var timeout = TimeSpan.FromSeconds(30); // Reasonable timeout for AI response

        // Act
        var startTime = DateTimeOffset.UtcNow;
        var response = await chatService.GetChatMessageContentAsync(
            "What NYC services are available for small business owners?");
        var elapsed = DateTimeOffset.UtcNow - startTime;

        // Assert
        response.Should().NotBeNull();
        elapsed.Should().BeLessThan(timeout, "OpenAI should respond within reasonable time");
    }

    private bool HasValidConfiguration()
    {
        try
        {
            OpenAITestHelper.ValidateOpenAIConfiguration(_configuration);
            return true;
        }
        catch
        {
            return false;
        }
    }

    private Kernel CreateKernelWithRealOpenAI()
    {
        var builder = Kernel.CreateBuilder();
        
        var (endpoint, apiKey, deploymentName) = OpenAITestHelper.GetOpenAIConfiguration(_configuration);
        
        Console.WriteLine($"🔧 Configuring Azure OpenAI: Endpoint={endpoint}, Deployment={deploymentName}");
        
        builder.Services.AddAzureOpenAIChatCompletion(
            deploymentName: deploymentName,
            endpoint: endpoint,
            apiKey: apiKey);

        builder.Services.AddLogging(b => b.AddConsole().SetMinimumLevel(LogLevel.Information));

        return builder.Build();
    }
}

/// <summary>
/// Simple test plugin to demonstrate AI-enhanced plugin functionality
/// </summary>
public class TestAIPlugin
{
    [KernelFunction, Description("Gets information about NYC services")]
    public string GetServiceInfo(
        [Description("Type of service to get information about")] string serviceType)
    {
        var serviceInfo = new
        {
            service_type = serviceType,
            description = $"Information about {serviceType} services in NYC",
            contact = "Call 311 for more information",
            online_resources = "Visit nyc.gov for online services",
            timestamp = DateTimeOffset.UtcNow
        };

        return JsonSerializer.Serialize(serviceInfo, new JsonSerializerOptions { WriteIndented = true });
    }
}

/// <summary>
/// Exception for skipping tests when required configuration is not available
/// </summary>
public class SkipException : Exception
{
    public SkipException(string message) : base(message) { }
}