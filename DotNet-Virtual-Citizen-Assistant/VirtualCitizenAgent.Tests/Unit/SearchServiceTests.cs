using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using VirtualCitizenAgent.Configuration;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Services;

namespace VirtualCitizenAgent.Tests.Unit;

public class SearchServiceTests
{
    private readonly SearchService _sut;

    public SearchServiceTests()
    {
        var config = Options.Create(new SearchConfiguration
        {
            UseMockService = true
        });
        var logger = Mock.Of<ILogger<SearchService>>();
        _sut = new SearchService(config, logger);
    }

    [Fact]
    public async Task SearchAsync_WithValidQuery_ReturnsResults()
    {
        // Arrange
        var query = new SearchQuery { Query = "parking permit" };

        // Act
        var result = await _sut.SearchAsync(query);

        // Assert
        result.Should().NotBeNull();
        result.Results.Should().NotBeEmpty();
        result.Query.Should().Be("parking permit");
    }

    [Fact]
    public async Task SearchAsync_WithCategoryFilter_FiltersResults()
    {
        // Arrange
        var query = new SearchQuery
        {
            Query = "permit",
            Category = "Transportation"
        };

        // Act
        var result = await _sut.SearchAsync(query);

        // Assert
        result.Should().NotBeNull();
        result.Results.Should().OnlyContain(r =>
            r.Document.Category.Equals("Transportation", StringComparison.OrdinalIgnoreCase));
    }

    [Fact]
    public async Task GetDocumentByIdAsync_WithValidId_ReturnsDocument()
    {
        // Arrange
        var documentId = "doc-001";

        // Act
        var result = await _sut.GetDocumentByIdAsync(documentId);

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(documentId);
    }

    [Fact]
    public async Task GetDocumentByIdAsync_WithInvalidId_ReturnsNull()
    {
        // Arrange
        var documentId = "invalid-id";

        // Act
        var result = await _sut.GetDocumentByIdAsync(documentId);

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetCategoriesAsync_ReturnsAllCategories()
    {
        // Act
        var result = await _sut.GetCategoriesAsync();

        // Assert
        result.Should().NotBeEmpty();
        result.Should().OnlyContain(c => !string.IsNullOrEmpty(c.Name));
        result.Should().OnlyContain(c => c.DocumentCount > 0);
    }

    [Fact]
    public async Task SemanticSearchAsync_ReturnsResultsWithCaptions()
    {
        // Arrange
        var query = "parking";

        // Act
        var result = await _sut.SemanticSearchAsync(query);

        // Assert
        result.Should().NotBeNull();
        result.Results.Should().NotBeEmpty();
    }

    [Fact]
    public async Task GetRecentDocumentsAsync_ReturnsDocuments()
    {
        // Act
        var result = await _sut.GetRecentDocumentsAsync(days: 30, top: 5);

        // Assert
        result.Should().NotBeEmpty();
        result.Count.Should().BeLessOrEqualTo(5);
    }
}
