using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// A citation reference to a source document.
/// </summary>
public class DocumentSource
{
    /// <summary>Reference to the Document.</summary>
    [JsonPropertyName("documentId")]
    public string DocumentId { get; set; } = string.Empty;

    /// <summary>Document title for display.</summary>
    [JsonPropertyName("title")]
    public string Title { get; set; } = string.Empty;

    /// <summary>Link to the full document.</summary>
    [JsonPropertyName("url")]
    public string Url { get; set; } = string.Empty;

    /// <summary>Relevance score to the query (0.0-1.0).</summary>
    [JsonPropertyName("relevance")]
    public float? Relevance { get; set; }
}
