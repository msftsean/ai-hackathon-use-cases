using FluentAssertions;
using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Tests.Models;

/// <summary>
/// Unit tests for ErrorViewModel model
/// </summary>
public class ErrorViewModelTests
{
    [Fact]
    public void ErrorViewModel_DefaultConstructor_ShouldInitializeWithNullRequestId()
    {
        // Arrange & Act
        var model = new ErrorViewModel();

        // Assert
        model.RequestId.Should().BeNull();
    }

    [Fact]
    public void ErrorViewModel_RequestId_CanBeSetAndRetrieved()
    {
        // Arrange
        var model = new ErrorViewModel();
        var requestId = "test-request-id-123";

        // Act
        model.RequestId = requestId;

        // Assert
        model.RequestId.Should().Be(requestId);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("valid-request-id")]
    public void ErrorViewModel_RequestId_ShouldAcceptAnyStringValue(string? requestId)
    {
        // Arrange
        var model = new ErrorViewModel();

        // Act
        model.RequestId = requestId;

        // Assert
        model.RequestId.Should().Be(requestId);
    }

    [Fact]
    public void ErrorViewModel_ShowRequestId_ShouldReturnTrueWhenRequestIdIsNotNullOrEmpty()
    {
        // Arrange
        var model = new ErrorViewModel { RequestId = "test-id" };

        // Act
        var result = model.ShowRequestId;

        // Assert
        result.Should().BeTrue();
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    public void ErrorViewModel_ShowRequestId_ShouldReturnFalseWhenRequestIdIsNullOrEmpty(string? requestId)
    {
        // Arrange
        var model = new ErrorViewModel { RequestId = requestId };

        // Act
        var result = model.ShowRequestId;

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public void ErrorViewModel_ShowRequestId_ShouldReturnTrueForWhitespaceRequestId()
    {
        // Arrange
        var model = new ErrorViewModel { RequestId = "   " };

        // Act
        var result = model.ShowRequestId;

        // Assert
        // The ShowRequestId property uses !string.IsNullOrEmpty(), not IsNullOrWhiteSpace()
        result.Should().BeTrue();
    }
}