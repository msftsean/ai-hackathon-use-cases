using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.SemanticKernel;
using VirtualCitizenAgent.Tests.Integration;

namespace VirtualCitizenAgent.Tests.Helpers;

/// <summary>
/// Helper class for testing OpenAI configuration and setup
/// </summary>
public static class OpenAITestHelper
{
    /// <summary>
    /// Creates a test configuration with OpenAI settings
    /// </summary>
    public static IConfiguration CreateTestConfiguration(
        string? deploymentName = "test-deployment",
        string? endpoint = "https://test.openai.azure.com/",
        string? apiKey = "test-api-key")
    {
        var config = new Dictionary<string, string?>
        {
            ["OpenAI:DeploymentName"] = deploymentName,
            ["OpenAI:Endpoint"] = endpoint,
            ["OpenAI:ApiKey"] = apiKey,
            ["AzureSearch:Endpoint"] = "https://test-search.search.windows.net",
            ["AzureSearch:IndexName"] = "test-index",
            ["AzureSearch:ApiKey"] = "test-search-key"
        };

        return new ConfigurationBuilder()
            .AddInMemoryCollection(config)
            .Build();
    }

    /// <summary>
    /// Creates a kernel with test OpenAI configuration
    /// </summary>
    public static Kernel CreateTestKernel(IConfiguration? configuration = null)
    {
        configuration ??= CreateTestConfiguration();
        
        var builder = Kernel.CreateBuilder();
        
        // Add test OpenAI configuration - this will fail at runtime without real credentials
        // but allows us to test the configuration setup
        try
        {
            builder.Services.AddAzureOpenAIChatCompletion(
                deploymentName: configuration["OpenAI:DeploymentName"]!,
                endpoint: configuration["OpenAI:Endpoint"]!,
                apiKey: configuration["OpenAI:ApiKey"]!);
        }
        catch (Exception)
        {
            // Expected to fail with test credentials - we're just testing configuration
        }

        return builder.Build();
    }

    /// <summary>
    /// Validates OpenAI configuration keys (supports both .env and OpenAI: prefixed keys)
    /// </summary>
    public static void ValidateOpenAIConfiguration(IConfiguration configuration)
    {
        // Try .env style keys first, then fallback to OpenAI: prefixed keys
        var endpoint = configuration["AZURE_OPENAI_ENDPOINT"] ?? configuration["OpenAI:Endpoint"];
        var apiKey = configuration["AZURE_OPENAI_API_KEY"] ?? configuration["OpenAI:ApiKey"];
        var deploymentName = configuration["AZURE_OPENAI_DEPLOYMENT"] ?? configuration["OpenAI:DeploymentName"];

        if (string.IsNullOrEmpty(endpoint))
        {
            throw new InvalidOperationException("Azure OpenAI endpoint is missing. Set AZURE_OPENAI_ENDPOINT or OpenAI:Endpoint");
        }

        if (string.IsNullOrEmpty(apiKey))
        {
            throw new InvalidOperationException("Azure OpenAI API key is missing. Set AZURE_OPENAI_API_KEY or OpenAI:ApiKey");
        }

        if (string.IsNullOrEmpty(deploymentName))
        {
            throw new InvalidOperationException("Azure OpenAI deployment name is missing. Set AZURE_OPENAI_DEPLOYMENT or OpenAI:DeploymentName");
        }
    }

    /// <summary>
    /// Gets OpenAI configuration values (supports both .env and OpenAI: prefixed keys)
    /// </summary>
    public static (string endpoint, string apiKey, string deploymentName) GetOpenAIConfiguration(IConfiguration configuration)
    {
        var endpoint = configuration["AZURE_OPENAI_ENDPOINT"] ?? configuration["OpenAI:Endpoint"];
        var apiKey = configuration["AZURE_OPENAI_API_KEY"] ?? configuration["OpenAI:ApiKey"];
        var deploymentName = configuration["AZURE_OPENAI_DEPLOYMENT"] ?? configuration["OpenAI:DeploymentName"];
        
        return (endpoint!, apiKey!, deploymentName!);
    }

    /// <summary>
    /// Creates a mock chat completion response for testing
    /// </summary>
    public static string CreateMockChatResponse(string userQuery, string responseContent)
    {
        return $$"""
        {
            "user_query": "{{userQuery}}",
            "ai_response": "{{responseContent}}",
            "model": "test-model",
            "timestamp": "{{DateTimeOffset.UtcNow:yyyy-MM-ddTHH:mm:ssZ}}"
        }
        """;
    }

    /// <summary>
    /// Simulates an AI-enhanced search query transformation
    /// </summary>
    public static string EnhanceSearchQuery(string originalQuery)
    {
        // This simulates what an AI service might do to improve search queries
        var enhancements = new Dictionary<string, string>
        {
            ["trash"] = "trash collection waste management sanitation",
            ["garbage"] = "garbage pickup waste disposal sanitation services",
            ["parking"] = "parking permits violations meters NYC DOT",
            ["school"] = "education enrollment NYC DOE schools",
            ["permit"] = "permits licensing applications NYC government"
        };

        if (string.IsNullOrWhiteSpace(originalQuery))
        {
            return "general city services information";
        }

        var enhancedQuery = originalQuery.ToLowerInvariant();
        
        foreach (var enhancement in enhancements)
        {
            if (enhancedQuery.Contains(enhancement.Key))
            {
                enhancedQuery = enhancedQuery.Replace(enhancement.Key, enhancement.Value);
                break;
            }
        }

        return enhancedQuery;
    }
}

/// <summary>
/// Test scenarios for OpenAI integration
/// </summary>
public static class OpenAITestScenarios
{
    public static class UserQueries
    {
        public const string TrashCollection = "When is my trash picked up?";
        public const string ParkingPermit = "How do I get a parking permit?";
        public const string SchoolEnrollment = "How do I enroll my child in school?";
        public const string BusinessPermit = "What permits do I need to start a business?";
        public const string UtilityBill = "How do I pay my water bill online?";
    }

    public static class ExpectedAIEnhancements
    {
        public const string TrashEnhanced = "NYC sanitation department garbage collection schedule pickup days residential commercial";
        public const string ParkingEnhanced = "NYC DOT parking permit application residential visitor commercial street parking";
        public const string SchoolEnhanced = "NYC DOE school enrollment application process kindergarten elementary middle high school";
        public const string BusinessEnhanced = "NYC business permit license application SBS small business services";
        public const string UtilityEnhanced = "NYC DEP water bill payment online account management utilities";
    }

    public static class MockAIResponses
    {
        public const string TrashResponse = @"
        Based on your location, trash collection typically occurs on specific days depending on your address. 
        Here are the key points:
        - Regular trash collection happens twice per week for most NYC areas
        - You can find your specific collection day using the NYC311 app or website
        - Recycling is collected on the same days as regular trash
        - Put trash out after 6 PM the night before collection or by 6 AM on collection day
        ";

        public const string ParkingResponse = @"
        To get a parking permit in NYC:
        1. Visit the NYC DOT website or go to a DOT office
        2. Provide proof of residency and vehicle registration
        3. Pay the required fee (varies by permit type)
        4. Wait for processing (typically 7-10 business days)
        5. Available permits include residential, commercial, and visitor permits
        ";
    }
}