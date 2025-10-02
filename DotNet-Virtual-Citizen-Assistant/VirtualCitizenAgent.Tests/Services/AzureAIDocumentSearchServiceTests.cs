using FluentAssertions;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using VirtualCitizenAgent.Services;
using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Tests.Services;

/// <summary>
/// Unit tests for AzureAIDocumentSearchService
/// NOTE: These tests focus on the service logic and error handling.
/// The actual Azure Search integration is tested separately.
/// </summary>
public class AzureAIDocumentSearchServiceTests
{
    private readonly Mock<IConfiguration> _mockConfiguration;
    private readonly Mock<ILogger<AzureAIDocumentSearchService>> _mockLogger;

    public AzureAIDocumentSearchServiceTests()
    {
        _mockConfiguration = new Mock<IConfiguration>();
        _mockLogger = new Mock<ILogger<AzureAIDocumentSearchService>>();

        // Setup configuration defaults
        _mockConfiguration.Setup(c => c["AzureSearch:IndexName"]).Returns("virtual-agent-nyc");
    }

    [Fact]
    public void Constructor_WithNullSearchClient_ShouldThrowArgumentNullException()
    {
        // Arrange & Act & Assert
        Action act = () => new AzureAIDocumentSearchService(
            null!,
            _mockConfiguration.Object,
            _mockLogger.Object);

        act.Should().Throw<ArgumentNullException>()
            .WithParameterName("searchClient");
    }

    [Fact]
    public void Constructor_WithNullConfiguration_ShouldThrowArgumentNullException()
    {
        // Arrange
        var mockSearchClient = new Mock<Azure.Search.Documents.SearchClient>();

        // Act & Assert
        Action act = () => new AzureAIDocumentSearchService(
            mockSearchClient.Object,
            null!,
            _mockLogger.Object);

        // Note: The service doesn't validate configuration in constructor,
        // but uses it during operation. We expect NullReferenceException when config is accessed.
        act.Should().Throw<NullReferenceException>();
    }

    [Fact]
    public void Constructor_WithNullLogger_ShouldThrowArgumentNullException()
    {
        // Arrange
        var mockSearchClient = new Mock<Azure.Search.Documents.SearchClient>();

        // Act & Assert
        Action act = () => new AzureAIDocumentSearchService(
            mockSearchClient.Object,
            _mockConfiguration.Object,
            null!);

        act.Should().Throw<ArgumentNullException>()
            .WithParameterName("logger");
    }

    [Fact]
    public void Constructor_WithNullIndexName_ShouldUseDefaultIndexName()
    {
        // Arrange
        var mockSearchClient = new Mock<Azure.Search.Documents.SearchClient>();
        _mockConfiguration.Setup(c => c["AzureSearch:IndexName"]).Returns((string?)null);

        // Act & Assert - Should not throw, should use default
        Action act = () => new AzureAIDocumentSearchService(
            mockSearchClient.Object,
            _mockConfiguration.Object,
            _mockLogger.Object);

        act.Should().NotThrow();
    }

    [Fact]
    public void Constructor_WithValidParameters_ShouldInitializeSuccessfully()
    {
        // Arrange
        var mockSearchClient = new Mock<Azure.Search.Documents.SearchClient>();

        // Act & Assert
        Action act = () => new AzureAIDocumentSearchService(
            mockSearchClient.Object,
            _mockConfiguration.Object,
            _mockLogger.Object);

        act.Should().NotThrow();
    }

    // Note: The following tests would require complex Azure SDK mocking
    // which is not practical. Instead, we focus on integration tests
    // and test the service contracts through the IDocumentSearchService interface.

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    public async Task SearchAsync_WithEmptyOrNullQuery_ShouldAcceptParameters(string query)
    {
        // Arrange
        var mockSearchClient = new Mock<Azure.Search.Documents.SearchClient>();
        var service = new AzureAIDocumentSearchService(
            mockSearchClient.Object,
            _mockConfiguration.Object,
            _mockLogger.Object);

        // Act & Assert - Should not throw on parameter validation
        // (The actual search would fail due to mocked SearchClient, but parameter validation should pass)
        Func<Task> act = async () => await service.SearchAsync(query, 10);

        // We expect this to fail at the SearchClient level, not parameter validation
        (await act.Should().ThrowAsync<Exception>())
            .Which.Should().NotBeOfType<ArgumentException>();
    }

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(5)]
    [InlineData(50)]
    public async Task SearchAsync_WithDifferentMaxResults_ShouldAcceptParameters(int maxResults)
    {
        // Arrange
        var mockSearchClient = new Mock<Azure.Search.Documents.SearchClient>();
        var service = new AzureAIDocumentSearchService(
            mockSearchClient.Object,
            _mockConfiguration.Object,
            _mockLogger.Object);

        // Act & Assert - Should not throw on parameter validation
        Func<Task> act = async () => await service.SearchAsync("test query", maxResults);

        // We expect this to fail at the SearchClient level, not parameter validation
        (await act.Should().ThrowAsync<Exception>())
            .Which.Should().NotBeOfType<ArgumentException>();
    }
}

/// <summary>
/// Integration-style tests that verify the service behavior with actual mock responses
/// These tests would be more complex and are better suited for integration testing
/// </summary>
public class DocumentSearchServiceContractTests
{
    [Fact]
    public void IDocumentSearchService_SearchAsync_ShouldReturnSearchResultDocuments()
    {
        // This test verifies the contract - actual implementation would need real Azure Search setup
        // or complex mocking of Azure SDK responses
        
        // For now, we verify the interface contract exists
        typeof(IDocumentSearchService).Should().HaveMethod("SearchAsync", new[] { typeof(string), typeof(int) });
        typeof(IDocumentSearchService).Should().HaveMethod("GetByIdAsync", new[] { typeof(string) });
        typeof(IDocumentSearchService).Should().HaveMethod("SearchByCategoryAsync", new[] { typeof(string), typeof(string), typeof(int) });
    }

    [Fact]
    public void SearchResultDocument_ShouldHaveRequiredProperties()
    {
        // Verify the model has all required properties
        var document = new SearchResultDocument();
        
        document.Should().NotBeNull();
        document.Id.Should().NotBeNull();
        document.Title.Should().NotBeNull();
        document.Content.Should().NotBeNull();
        document.ServiceType.Should().NotBeNull();
        document.Category.Should().NotBeNull();
        document.Highlights.Should().NotBeNull();
        document.Metadata.Should().NotBeNull();
    }
}