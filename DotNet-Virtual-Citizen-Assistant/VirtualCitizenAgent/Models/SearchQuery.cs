using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// A user's search request.
/// </summary>
public class SearchQuery
{
    /// <summary>Search query text.</summary>
    [Required]
    [StringLength(500, MinimumLength = 1)]
    [JsonPropertyName("query")]
    public string Query { get; set; } = string.Empty;

    /// <summary>Search mode (default: Semantic).</summary>
    [JsonPropertyName("mode")]
    public SearchMode Mode { get; set; } = SearchMode.Semantic;

    /// <summary>Filter by category.</summary>
    [JsonPropertyName("category")]
    public string? Category { get; set; }

    /// <summary>Number of results to return (1-50, default 10).</summary>
    [Range(1, 50)]
    [JsonPropertyName("top")]
    public int Top { get; set; } = 10;

    /// <summary>Pagination offset (default 0).</summary>
    [Range(0, int.MaxValue)]
    [JsonPropertyName("skip")]
    public int Skip { get; set; } = 0;

    /// <summary>Fields to highlight in results.</summary>
    [JsonPropertyName("highlightFields")]
    public List<string>? HighlightFields { get; set; }
}
