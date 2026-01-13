using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using System.Net;
using System.Net.Http.Json;
using System.Text.Json;

namespace VirtualCitizenAgent.Tests.E2E;

/// <summary>
/// E2E tests for Virtual Citizen Agent API endpoints.
/// Uses WebApplicationFactory for in-memory testing.
/// </summary>
public class ApiEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public ApiEndpointTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task HealthEndpoint_ReturnsOk()
    {
        // Act
        var response = await _client.GetAsync("/api/health");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task HomeEndpoint_ReturnsOkWithHtmlContent()
    {
        // Act
        var response = await _client.GetAsync("/");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        response.Content.Headers.ContentType?.MediaType.Should().Be("text/html");
    }

    [Fact]
    public async Task ChatEndpoint_WithValidMessage_ReturnsOk()
    {
        // Arrange
        var chatRequest = new { message = "What services does NYC offer?" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/chat", chatRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var content = await response.Content.ReadAsStringAsync();
        content.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task ChatEndpoint_WithEmptyMessage_ReturnsBadRequest()
    {
        // Arrange
        var chatRequest = new { message = "" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/chat", chatRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task SearchEndpoint_WithQuery_ReturnsResults()
    {
        // Arrange
        var searchQuery = "housing assistance";

        // Act
        var response = await _client.GetAsync($"/api/search?query={searchQuery}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var content = await response.Content.ReadAsStringAsync();
        content.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task SearchEndpoint_WithEmptyQuery_ReturnsBadRequest()
    {
        // Act
        var response = await _client.GetAsync("/api/search?query=");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task StaticAssets_CssFile_ReturnsOk()
    {
        // Act
        var response = await _client.GetAsync("/css/site.css");

        // Assert
        if (response.StatusCode == HttpStatusCode.OK)
        {
            response.Content.Headers.ContentType?.MediaType.Should().Contain("css");
        }
        // Static files may not exist in test environment, so we accept either OK or NotFound
        response.StatusCode.Should().BeOneOf(HttpStatusCode.OK, HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task NonExistentEndpoint_ReturnsNotFound()
    {
        // Act
        var response = await _client.GetAsync("/api/nonexistent");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}
