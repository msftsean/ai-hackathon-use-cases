using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// A single search result with relevance information.
/// </summary>
public class SearchResult
{
    /// <summary>The matched document.</summary>
    [JsonPropertyName("document")]
    public Document Document { get; set; } = new();

    /// <summary>Relevance score.</summary>
    [JsonPropertyName("score")]
    public double Score { get; set; }

    /// <summary>Highlighted snippets by field name.</summary>
    [JsonPropertyName("highlights")]
    public Dictionary<string, List<string>>? Highlights { get; set; }

    /// <summary>Semantic captions.</summary>
    [JsonPropertyName("captions")]
    public List<string>? Captions { get; set; }
}
