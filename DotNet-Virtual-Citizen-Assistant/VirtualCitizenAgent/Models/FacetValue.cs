using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// A facet bucket for aggregation results.
/// </summary>
public class FacetValue
{
    /// <summary>Facet value.</summary>
    [JsonPropertyName("value")]
    public string Value { get; set; } = string.Empty;

    /// <summary>Number of matching documents.</summary>
    [JsonPropertyName("count")]
    public long Count { get; set; }
}
