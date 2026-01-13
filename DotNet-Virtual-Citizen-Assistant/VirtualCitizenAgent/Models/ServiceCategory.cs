using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// A grouping of documents by service type.
/// </summary>
public class ServiceCategory
{
    /// <summary>Category identifier.</summary>
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    /// <summary>Human-readable name.</summary>
    [JsonPropertyName("displayName")]
    public string DisplayName { get; set; } = string.Empty;

    /// <summary>Category description.</summary>
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    /// <summary>Font Awesome icon class.</summary>
    [JsonPropertyName("icon")]
    public string? Icon { get; set; }

    /// <summary>Number of documents in this category.</summary>
    [JsonPropertyName("documentCount")]
    public int DocumentCount { get; set; }

    /// <summary>Child categories.</summary>
    [JsonPropertyName("subCategories")]
    public List<string> SubCategories { get; set; } = [];
}
