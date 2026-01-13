using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// Extended category information with related documents.
/// </summary>
public class CategoryDetail : ServiceCategory
{
    /// <summary>Documents in this category.</summary>
    [JsonPropertyName("documents")]
    public List<Document> Documents { get; set; } = [];
}
