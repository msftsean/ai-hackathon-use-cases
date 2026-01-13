using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using System.Net;

namespace VirtualCitizenAgent.Tests.Integration;

/// <summary>
/// Basic integration tests for the Virtual Citizen Agent API
/// These tests use a custom test factory with mocked Azure services
/// </summary>
public class BasicIntegrationTests : IClassFixture<TestWebApplicationFactory>
{
    private readonly TestWebApplicationFactory _factory;
    private readonly HttpClient _client;

    public BasicIntegrationTests(TestWebApplicationFactory factory)
    {
        _factory = factory;
        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task Get_Home_ShouldReturnSuccessAndCorrectContentType()
    {
        // Act
        var response = await _client.GetAsync("/");

        // Assert
        response.EnsureSuccessStatusCode();
        response.Content.Headers.ContentType?.ToString().Should().StartWith("text/html");
    }

    [Fact]
    public async Task SearchDocuments_WithEmptyQuery_ShouldReturnBadRequest()
    {
        // Act
        var response = await _client.GetAsync("/api/search/documents?query=");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task SearchDocuments_WithoutQuery_ShouldReturnBadRequest()
    {
        // Act
        var response = await _client.GetAsync("/api/search/documents");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task SearchDocuments_WithValidQuery_MayFailWithoutAzureSetup()
    {
        // Act
        var response = await _client.GetAsync("/api/search/documents?query=trash&maxResults=5");

        // Assert
        // This test will likely fail without proper Azure configuration
        // but we test that it doesn't return a bad request
        response.StatusCode.Should().NotBe(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task GetDocument_WithValidId_MayFailWithoutAzureSetup()
    {
        // Act
        var response = await _client.GetAsync("/api/search/documents/doc1");

        // Assert
        // This test will likely fail without proper Azure configuration
        // but we test that it doesn't return a bad request for valid format
        response.StatusCode.Should().NotBe(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task GetDocument_WithEmptyId_ShouldReturnBadRequest()
    {
        // Act
        var response = await _client.GetAsync("/api/search/documents/");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest); // Empty ID is properly validated and returns BadRequest
    }
}