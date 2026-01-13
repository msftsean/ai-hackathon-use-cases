using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// Results from a search operation.
/// </summary>
public class SearchResponse
{
    /// <summary>Original query text.</summary>
    [JsonPropertyName("query")]
    public string Query { get; set; } = string.Empty;

    /// <summary>Matching documents.</summary>
    [JsonPropertyName("results")]
    public List<SearchResult> Results { get; set; } = [];

    /// <summary>Total matching documents (for pagination).</summary>
    [JsonPropertyName("totalCount")]
    public long TotalCount { get; set; }

    /// <summary>Category facets for filtering.</summary>
    [JsonPropertyName("facets")]
    public Dictionary<string, List<FacetValue>>? Facets { get; set; }

    /// <summary>Search execution time in milliseconds.</summary>
    [JsonPropertyName("searchTimeMs")]
    public int SearchTimeMs { get; set; }
}
