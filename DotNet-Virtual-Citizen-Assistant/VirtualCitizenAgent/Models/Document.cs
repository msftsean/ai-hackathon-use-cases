using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// A searchable service document in Azure AI Search.
/// </summary>
public class Document
{
    /// <summary>Unique document identifier (key field).</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>Document title.</summary>
    [JsonPropertyName("title")]
    public string Title { get; set; } = string.Empty;

    /// <summary>Full document text content.</summary>
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    /// <summary>Brief description of the document.</summary>
    [JsonPropertyName("summary")]
    public string? Summary { get; set; }

    /// <summary>Service category (e.g., Transportation, Housing).</summary>
    [JsonPropertyName("category")]
    public string Category { get; set; } = string.Empty;

    /// <summary>More specific categorization.</summary>
    [JsonPropertyName("subCategory")]
    public string? SubCategory { get; set; }

    /// <summary>Searchable keywords.</summary>
    [JsonPropertyName("tags")]
    public List<string> Tags { get; set; } = [];

    /// <summary>External source link.</summary>
    [JsonPropertyName("url")]
    public string? Url { get; set; }

    /// <summary>Last modification time.</summary>
    [JsonPropertyName("lastUpdated")]
    public DateTimeOffset LastUpdated { get; set; } = DateTimeOffset.UtcNow;

    /// <summary>Publication status.</summary>
    [JsonPropertyName("status")]
    public DocumentStatus Status { get; set; } = DocumentStatus.Active;

    /// <summary>Embedding vector for semantic search (1536 dimensions).</summary>
    [JsonPropertyName("contentVector")]
    public IReadOnlyList<float>? ContentVector { get; set; }
}
