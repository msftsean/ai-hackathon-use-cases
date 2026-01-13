using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using VirtualCitizenAgent.Configuration;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Services;

namespace VirtualCitizenAgent.Tests.Unit;

public class ChatServiceTests
{
    private readonly ChatService _sut;
    private readonly Mock<ISearchService> _searchServiceMock;

    public ChatServiceTests()
    {
        _searchServiceMock = new Mock<ISearchService>();
        var config = Options.Create(new OpenAIConfiguration
        {
            UseMockService = true
        });
        var logger = Mock.Of<ILogger<ChatService>>();

        _sut = new ChatService(_searchServiceMock.Object, config, logger);
    }

    [Fact]
    public async Task CreateSessionAsync_ReturnsNewSession()
    {
        // Act
        var session = await _sut.CreateSessionAsync();

        // Assert
        session.Should().NotBeNull();
        session.SessionId.Should().NotBeNullOrEmpty();
        session.Messages.Should().BeEmpty();
        session.CreatedAt.Should().BeCloseTo(DateTimeOffset.UtcNow, TimeSpan.FromSeconds(5));
    }

    [Fact]
    public async Task GetSessionAsync_WithValidId_ReturnsSession()
    {
        // Arrange
        var createdSession = await _sut.CreateSessionAsync();

        // Act
        var retrievedSession = await _sut.GetSessionAsync(createdSession.SessionId);

        // Assert
        retrievedSession.Should().NotBeNull();
        retrievedSession!.SessionId.Should().Be(createdSession.SessionId);
    }

    [Fact]
    public async Task GetSessionAsync_WithInvalidId_ReturnsNull()
    {
        // Act
        var session = await _sut.GetSessionAsync("invalid-session-id");

        // Assert
        session.Should().BeNull();
    }

    [Fact]
    public async Task DeleteSessionAsync_WithValidId_ReturnsTrue()
    {
        // Arrange
        var session = await _sut.CreateSessionAsync();

        // Act
        var result = await _sut.DeleteSessionAsync(session.SessionId);

        // Assert
        result.Should().BeTrue();

        var deletedSession = await _sut.GetSessionAsync(session.SessionId);
        deletedSession.Should().BeNull();
    }

    [Fact]
    public async Task SendMessageAsync_WithValidRequest_ReturnsResponse()
    {
        // Arrange
        var searchResponse = new SearchResponse
        {
            Query = "parking",
            Results =
            [
                new SearchResult
                {
                    Document = new Document
                    {
                        Id = "doc-001",
                        Title = "Parking Permit",
                        Content = "How to get a parking permit",
                        Category = "Transportation"
                    },
                    Score = 0.9
                }
            ]
        };

        _searchServiceMock
            .Setup(x => x.SemanticSearchAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<string?>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(searchResponse);

        var request = new ChatRequest
        {
            Message = "How do I get a parking permit?"
        };

        // Act
        var response = await _sut.SendMessageAsync(request);

        // Assert
        response.Should().NotBeNull();
        response.SessionId.Should().NotBeNullOrEmpty();
        response.Content.Should().NotBeNullOrEmpty();
        response.ProcessingTimeMs.Should().BeGreaterThan(0);
    }

    [Fact]
    public async Task SendMessageAsync_MaintainsSessionContext()
    {
        // Arrange
        _searchServiceMock
            .Setup(x => x.SemanticSearchAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<string?>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SearchResponse { Results = [] });

        var firstRequest = new ChatRequest { Message = "Hello" };
        var firstResponse = await _sut.SendMessageAsync(firstRequest);

        var secondRequest = new ChatRequest
        {
            SessionId = firstResponse.SessionId,
            Message = "What about parking?"
        };

        // Act
        var secondResponse = await _sut.SendMessageAsync(secondRequest);

        // Assert
        secondResponse.SessionId.Should().Be(firstResponse.SessionId);

        var session = await _sut.GetSessionAsync(firstResponse.SessionId);
        session!.Messages.Should().HaveCount(4); // 2 user + 2 assistant messages
    }
}
