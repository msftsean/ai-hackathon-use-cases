using FluentAssertions;
using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Tests.Models;

/// <summary>
/// Unit tests for SearchResultDocument model
/// </summary>
public class SearchResultDocumentTests
{
    [Fact]
    public void SearchResultDocument_DefaultConstructor_ShouldInitializeWithDefaultValues()
    {
        // Arrange & Act
        var document = new SearchResultDocument();

        // Assert
        document.Id.Should().BeEmpty();
        document.Title.Should().BeEmpty();
        document.Content.Should().BeEmpty();
        document.ServiceType.Should().BeEmpty();
        document.Category.Should().BeEmpty();
        document.LastUpdated.Should().Be(default(DateTimeOffset));
        document.RelevanceScore.Should().Be(0.0);
        document.SemanticScore.Should().Be(0.0);
        document.Highlights.Should().NotBeNull().And.BeEmpty();
        document.Metadata.Should().NotBeNull().And.BeEmpty();
    }

    [Fact]
    public void SearchResultDocument_PropertyAssignment_ShouldWorkCorrectly()
    {
        // Arrange
        var testDate = DateTimeOffset.UtcNow;
        var highlights = new List<string> { "highlight1", "highlight2" };
        var metadata = new Dictionary<string, object> { { "key1", "value1" }, { "key2", 42 } };

        // Act
        var document = new SearchResultDocument
        {
            Id = "test-id",
            Title = "Test Title",
            Content = "Test Content",
            ServiceType = "Test Service",
            Category = "Test Category",
            LastUpdated = testDate,
            RelevanceScore = 0.85,
            SemanticScore = 0.92,
            Highlights = highlights,
            Metadata = metadata
        };

        // Assert
        document.Id.Should().Be("test-id");
        document.Title.Should().Be("Test Title");
        document.Content.Should().Be("Test Content");
        document.ServiceType.Should().Be("Test Service");
        document.Category.Should().Be("Test Category");
        document.LastUpdated.Should().Be(testDate);
        document.RelevanceScore.Should().Be(0.85);
        document.SemanticScore.Should().Be(0.92);
        document.Highlights.Should().BeEquivalentTo(highlights);
        document.Metadata.Should().BeEquivalentTo(metadata);
    }

    [Theory]
    [InlineData(0.0)]
    [InlineData(0.5)]
    [InlineData(1.0)]
    [InlineData(-0.1)]
    [InlineData(1.1)]
    public void SearchResultDocument_RelevanceScore_ShouldAcceptAnyDoubleValue(double score)
    {
        // Arrange
        var document = new SearchResultDocument();

        // Act
        document.RelevanceScore = score;

        // Assert
        document.RelevanceScore.Should().Be(score);
    }

    [Theory]
    [InlineData(0.0)]
    [InlineData(0.5)]
    [InlineData(1.0)]
    [InlineData(-0.1)]
    [InlineData(1.1)]
    public void SearchResultDocument_SemanticScore_ShouldAcceptAnyDoubleValue(double score)
    {
        // Arrange
        var document = new SearchResultDocument();

        // Act
        document.SemanticScore = score;

        // Assert
        document.SemanticScore.Should().Be(score);
    }

    [Fact]
    public void SearchResultDocument_Highlights_CanBeModified()
    {
        // Arrange
        var document = new SearchResultDocument();
        var newHighlight = "new highlight";

        // Act
        document.Highlights.Add(newHighlight);

        // Assert
        document.Highlights.Should().Contain(newHighlight);
        document.Highlights.Should().HaveCount(1);
    }

    [Fact]
    public void SearchResultDocument_Metadata_CanBeModified()
    {
        // Arrange
        var document = new SearchResultDocument();
        var key = "testKey";
        var value = "testValue";

        // Act
        document.Metadata[key] = value;

        // Assert
        document.Metadata.Should().ContainKey(key);
        document.Metadata[key].Should().Be(value);
        document.Metadata.Should().HaveCount(1);
    }

    [Fact]
    public void SearchResultDocument_ToString_ShouldReturnTypeName()
    {
        // Arrange
        var document = new SearchResultDocument { Title = "Test Title" };

        // Act
        var result = document.ToString();

        // Assert
        result.Should().NotBeNull();
        // ToString() should return the type name by default
        result.Should().Contain("SearchResultDocument");
    }
}