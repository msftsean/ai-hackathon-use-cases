using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using System.Text.Json;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Plugins;
using VirtualCitizenAgent.Services;

namespace VirtualCitizenAgent.Tests.Plugins;

/// <summary>
/// Unit tests for DocumentSearchPlugin
/// </summary>
public class DocumentSearchPluginTests
{
    private readonly Mock<IDocumentSearchService> _mockSearchService;
    private readonly Mock<ILogger<DocumentSearchPlugin>> _mockLogger;
    private readonly DocumentSearchPlugin _plugin;

    public DocumentSearchPluginTests()
    {
        _mockSearchService = new Mock<IDocumentSearchService>();
        _mockLogger = new Mock<ILogger<DocumentSearchPlugin>>();
        _plugin = new DocumentSearchPlugin(_mockSearchService.Object, _mockLogger.Object);
    }

    [Fact]
    public void Constructor_WithNullSearchService_ShouldThrowArgumentNullException()
    {
        // Arrange, Act & Assert
        var action = () => new DocumentSearchPlugin(null!, _mockLogger.Object);

        action.Should().Throw<ArgumentNullException>()
            .WithParameterName("searchService");
    }

    [Fact]
    public void Constructor_WithNullLogger_ShouldThrowArgumentNullException()
    {
        // Arrange, Act & Assert
        var action = () => new DocumentSearchPlugin(_mockSearchService.Object, null!);

        action.Should().Throw<ArgumentNullException>()
            .WithParameterName("logger");
    }

    [Fact]
    public async Task SearchDocumentsAsync_WithValidQuery_ShouldReturnFormattedResults()
    {
        // Arrange
        var query = "trash pickup";
        var maxResults = 5;
        var mockDocuments = new List<SearchResultDocument>
        {
            new SearchResultDocument
            {
                Id = "doc1",
                Title = "Trash Pickup Schedule",
                Content = "Information about trash pickup schedules in NYC",
                ServiceType = "Sanitation",
                Category = "Waste Management",
                RelevanceScore = 0.95,
                LastUpdated = new DateTimeOffset(2024, 1, 15, 10, 30, 0, TimeSpan.Zero)
            },
            new SearchResultDocument
            {
                Id = "doc2",
                Title = "Recycling Guidelines",
                Content = "Guidelines for recycling in NYC",
                ServiceType = "Sanitation",
                Category = "Waste Management",
                RelevanceScore = 0.87,
                LastUpdated = new DateTimeOffset(2024, 2, 1, 14, 15, 0, TimeSpan.Zero)
            }
        };

        _mockSearchService
            .Setup(s => s.SearchAsync(query, maxResults))
            .ReturnsAsync(mockDocuments);

        // Act
        var result = await _plugin.SearchDocumentsAsync(query, maxResults);

        // Assert
        result.Should().NotBeNull();
        
        var parsedResult = JsonSerializer.Deserialize<JsonElement>(result);
        parsedResult.GetProperty("query").GetString().Should().Be(query);
        parsedResult.GetProperty("total_results").GetInt32().Should().Be(2);
        
        var documents = parsedResult.GetProperty("documents").EnumerateArray().ToList();
        documents.Should().HaveCount(2);
        
        documents[0].GetProperty("id").GetString().Should().Be("doc1");
        documents[0].GetProperty("title").GetString().Should().Be("Trash Pickup Schedule");
        documents[0].GetProperty("content").GetString().Should().Be("Information about trash pickup schedules in NYC");
        documents[0].GetProperty("service_type").GetString().Should().Be("Sanitation");
        documents[0].GetProperty("category").GetString().Should().Be("Waste Management");
        documents[0].GetProperty("relevance_score").GetDouble().Should().Be(0.95);
        documents[0].GetProperty("last_updated").GetString().Should().Be("2024-01-15 10:30:00");

        // Verify service was called correctly
        _mockSearchService.Verify(s => s.SearchAsync(query, maxResults), Times.Once);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public async Task SearchDocumentsAsync_WithEmptyOrNullQuery_ShouldReturnError(string? query)
    {
        // Act
        var result = await _plugin.SearchDocumentsAsync(query!, 5);

        // Assert
        result.Should().NotBeNull();
        
        var parsedResult = JsonSerializer.Deserialize<JsonElement>(result);
        parsedResult.GetProperty("error").GetString().Should().Be("Search query cannot be empty");

        // Verify service was not called
        _mockSearchService.Verify(s => s.SearchAsync(It.IsAny<string>(), It.IsAny<int>()), Times.Never);
    }

    [Fact]
    public async Task SearchDocumentsAsync_WhenServiceThrowsException_ShouldReturnErrorResult()
    {
        // Arrange
        var query = "test query";
        var exception = new InvalidOperationException("Service error");

        _mockSearchService
            .Setup(s => s.SearchAsync(It.IsAny<string>(), It.IsAny<int>()))
            .ThrowsAsync(exception);

        // Act
        var result = await _plugin.SearchDocumentsAsync(query);

        // Assert
        result.Should().NotBeNull();
        
        var parsedResult = JsonSerializer.Deserialize<JsonElement>(result);
        parsedResult.GetProperty("error").GetString().Should().Contain("Search failed: Service error");

        // Verify error was logged
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Error,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Error searching documents")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task SearchDocumentsAsync_WithNoResults_ShouldReturnEmptyResults()
    {
        // Arrange
        var query = "nonexistent query";
        var emptyResults = new List<SearchResultDocument>();

        _mockSearchService
            .Setup(s => s.SearchAsync(query, It.IsAny<int>()))
            .ReturnsAsync(emptyResults);

        // Act
        var result = await _plugin.SearchDocumentsAsync(query);

        // Assert
        result.Should().NotBeNull();
        
        var parsedResult = JsonSerializer.Deserialize<JsonElement>(result);
        parsedResult.GetProperty("query").GetString().Should().Be(query);
        parsedResult.GetProperty("total_results").GetInt32().Should().Be(0);
        
        var documents = parsedResult.GetProperty("documents").EnumerateArray().ToList();
        documents.Should().BeEmpty();
    }

    [Theory]
    [InlineData(1)]
    [InlineData(5)]
    [InlineData(10)]
    [InlineData(50)]
    public async Task SearchDocumentsAsync_WithDifferentMaxResults_ShouldPassCorrectValue(int maxResults)
    {
        // Arrange
        var query = "test";
        var mockDocuments = new List<SearchResultDocument>();

        _mockSearchService
            .Setup(s => s.SearchAsync(query, maxResults))
            .ReturnsAsync(mockDocuments);

        // Act
        var result = await _plugin.SearchDocumentsAsync(query, maxResults);

        // Assert
        result.Should().NotBeNull();
        
        // Verify service was called with correct maxResults
        _mockSearchService.Verify(s => s.SearchAsync(query, maxResults), Times.Once);
    }

    [Fact]
    public async Task SearchDocumentsAsync_WithDefaultMaxResults_ShouldUseDefaultValue()
    {
        // Arrange
        var query = "test";
        var mockDocuments = new List<SearchResultDocument>();

        _mockSearchService
            .Setup(s => s.SearchAsync(query, 5))
            .ReturnsAsync(mockDocuments);

        // Act
        var result = await _plugin.SearchDocumentsAsync(query);

        // Assert
        result.Should().NotBeNull();
        
        // Verify service was called with default maxResults (5)
        _mockSearchService.Verify(s => s.SearchAsync(query, 5), Times.Once);
    }

    [Fact]
    public async Task GetDocumentByIdAsync_WithValidId_ShouldReturnFormattedDocument()
    {
        // Arrange
        var documentId = "doc123";
        var mockDocument = new SearchResultDocument
        {
            Id = documentId,
            Title = "Test Document",
            Content = "Test content for the document",
            ServiceType = "TestService",
            Category = "TestCategory",
            RelevanceScore = 1.0,
            LastUpdated = new DateTimeOffset(2024, 3, 1, 9, 0, 0, TimeSpan.Zero)
        };

        _mockSearchService
            .Setup(s => s.GetByIdAsync(documentId))
            .ReturnsAsync(mockDocument);

        // Act
        var result = await _plugin.GetDocumentByIdAsync(documentId);

        // Assert
        result.Should().NotBeNull();
        
        var parsedResult = JsonSerializer.Deserialize<JsonElement>(result);
        parsedResult.GetProperty("id").GetString().Should().Be(documentId);
        parsedResult.GetProperty("title").GetString().Should().Be("Test Document");
        parsedResult.GetProperty("content").GetString().Should().Be("Test content for the document");
        parsedResult.GetProperty("service_type").GetString().Should().Be("TestService");
        parsedResult.GetProperty("category").GetString().Should().Be("TestCategory");
        // Note: GetDocumentByIdAsync doesn't return relevance_score
        parsedResult.GetProperty("last_updated").GetString().Should().Be("2024-03-01 09:00:00");

        // Verify service was called correctly
        _mockSearchService.Verify(s => s.GetByIdAsync(documentId), Times.Once);
    }

    [Fact]
    public async Task GetDocumentByIdAsync_WithNonExistentId_ShouldReturnNotFoundError()
    {
        // Arrange
        var documentId = "nonexistent-id";

        _mockSearchService
            .Setup(s => s.GetByIdAsync(documentId))
            .ReturnsAsync((SearchResultDocument?)null);

        // Act
        var result = await _plugin.GetDocumentByIdAsync(documentId);

        // Assert
        result.Should().NotBeNull();
        
        var parsedResult = JsonSerializer.Deserialize<JsonElement>(result);
        parsedResult.GetProperty("error").GetString().Should().Be($"Document with ID '{documentId}' not found");
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public async Task GetDocumentByIdAsync_WithEmptyOrNullId_ShouldReturnError(string? documentId)
    {
        // Act
        var result = await _plugin.GetDocumentByIdAsync(documentId!);

        // Assert
        result.Should().NotBeNull();
        
        var parsedResult = JsonSerializer.Deserialize<JsonElement>(result);
        parsedResult.GetProperty("error").GetString().Should().Be("Document ID cannot be empty");

        // Verify service was not called
        _mockSearchService.Verify(s => s.GetByIdAsync(It.IsAny<string>()), Times.Never);
    }

    [Fact]
    public async Task GetDocumentByIdAsync_WhenServiceThrowsException_ShouldReturnErrorResult()
    {
        // Arrange
        var documentId = "doc123";
        var exception = new InvalidOperationException("Service error");

        _mockSearchService
            .Setup(s => s.GetByIdAsync(documentId))
            .ThrowsAsync(exception);

        // Act
        var result = await _plugin.GetDocumentByIdAsync(documentId);

        // Assert
        result.Should().NotBeNull();
        
        var parsedResult = JsonSerializer.Deserialize<JsonElement>(result);
        parsedResult.GetProperty("error").GetString().Should().Contain("Retrieval failed: Service error");

        // Verify error was logged
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Error,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Error retrieving document")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }
}