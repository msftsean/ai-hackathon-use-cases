using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Microsoft.AspNetCore.Hosting;
using Microsoft.SemanticKernel;
using VirtualCitizenAgent.Services;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Plugins;
using Moq;
using Microsoft.Extensions.Logging;

namespace VirtualCitizenAgent.Tests.Integration;

/// <summary>
/// Custom web application factory for testing with mocked dependencies
/// </summary>
public class TestWebApplicationFactory : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureAppConfiguration((context, config) =>
        {
            // Override configuration for testing
            config.AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["OpenAI:Endpoint"] = "https://test-endpoint.openai.azure.com/",
                ["OpenAI:ApiKey"] = "test-api-key", 
                ["OpenAI:DeploymentName"] = "test-deployment",
                ["AzureSearch:Endpoint"] = "https://test-search.search.windows.net",
                ["AzureSearch:ApiKey"] = "test-search-key",
                ["AzureSearch:IndexName"] = "test-index"
            });
        });

        builder.ConfigureServices(services =>
        {
            // Remove the real document search service and kernel
            var searchServiceDescriptor = services.SingleOrDefault(d => d.ServiceType == typeof(IDocumentSearchService));
            if (searchServiceDescriptor != null)
            {
                services.Remove(searchServiceDescriptor);
            }

            var kernelDescriptor = services.SingleOrDefault(d => d.ServiceType == typeof(Kernel));
            if (kernelDescriptor != null)
            {
                services.Remove(kernelDescriptor);
            }

            // Add a mock service for integration tests
            var mockSearchService = new Mock<IDocumentSearchService>();
            
            // Setup default mock behavior
            mockSearchService
                .Setup(s => s.SearchAsync(It.IsAny<string>(), It.IsAny<int>()))
                .ReturnsAsync(Array.Empty<SearchResultDocument>());

            mockSearchService
                .Setup(s => s.GetByIdAsync(It.IsAny<string>()))
                .ReturnsAsync((SearchResultDocument?)null);

            services.AddSingleton(mockSearchService.Object);

            // Create a working Kernel for integration tests with DocumentSearch plugin
            services.AddScoped<Kernel>(provider =>
            {
                var kernelBuilder = Kernel.CreateBuilder();
                
                // Use minimal configuration for testing - no Azure services needed
                kernelBuilder.Services.AddLogging(builder => builder.AddConsole().SetMinimumLevel(LogLevel.Warning));
                
                // Build the kernel
                var kernel = kernelBuilder.Build();
                
                // Create a mock DocumentSearchPlugin and register it
                var mockPlugin = new Mock<VirtualCitizenAgent.Plugins.DocumentSearchPlugin>(
                    mockSearchService.Object, 
                    provider.GetRequiredService<ILogger<VirtualCitizenAgent.Plugins.DocumentSearchPlugin>>());
                
                // Import the plugin to register its functions
                kernel.ImportPluginFromObject(mockPlugin.Object, "DocumentSearch");
                
                return kernel;
            });
        });
    }
}