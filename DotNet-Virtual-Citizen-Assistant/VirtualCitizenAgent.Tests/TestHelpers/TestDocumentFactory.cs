using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Tests.TestHelpers;

/// <summary>
/// Factory for creating test documents.
/// </summary>
public static class TestDocumentFactory
{
    public static Document CreateDocument(
        string? id = null,
        string? title = null,
        string? content = null,
        string? category = null)
    {
        return new Document
        {
            Id = id ?? Guid.NewGuid().ToString(),
            Title = title ?? "Test Document",
            Content = content ?? "This is test content for the document.",
            Summary = "Test summary",
            Category = category ?? "TestCategory",
            Tags = ["test", "sample"],
            LastUpdated = DateTimeOffset.UtcNow,
            Status = DocumentStatus.Active
        };
    }

    public static SearchResult CreateSearchResult(
        Document? document = null,
        double score = 0.9)
    {
        return new SearchResult
        {
            Document = document ?? CreateDocument(),
            Score = score,
            Captions = ["Test caption"]
        };
    }

    public static SearchResponse CreateSearchResponse(
        string query = "test",
        int resultCount = 3)
    {
        var results = Enumerable.Range(1, resultCount)
            .Select(i => CreateSearchResult(
                CreateDocument(
                    id: $"doc-{i}",
                    title: $"Test Document {i}",
                    category: i % 2 == 0 ? "CategoryA" : "CategoryB"
                ),
                score: 1.0 - (i * 0.1)
            ))
            .ToList();

        return new SearchResponse
        {
            Query = query,
            Results = results,
            TotalCount = resultCount,
            SearchTimeMs = 50
        };
    }

    public static ChatSession CreateChatSession(int messageCount = 0)
    {
        var session = new ChatSession();

        for (int i = 0; i < messageCount; i++)
        {
            session.Messages.Add(new ChatMessage
            {
                SessionId = session.SessionId,
                Role = i % 2 == 0 ? MessageRole.User : MessageRole.Assistant,
                Content = $"Message {i + 1}"
            });
        }

        return session;
    }
}
