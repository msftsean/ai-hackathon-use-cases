using System.Text.Json.Serialization;

namespace AzureSearchUploader.Models;

/// <summary>
/// Document format for batch upload to Azure AI Search.
/// </summary>
public class UploadDocument
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("title")]
    public string Title { get; set; } = string.Empty;

    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    [JsonPropertyName("summary")]
    public string? Summary { get; set; }

    [JsonPropertyName("category")]
    public string Category { get; set; } = string.Empty;

    [JsonPropertyName("subCategory")]
    public string? SubCategory { get; set; }

    [JsonPropertyName("tags")]
    public List<string>? Tags { get; set; }

    [JsonPropertyName("url")]
    public string? Url { get; set; }

    [JsonPropertyName("lastUpdated")]
    public string? LastUpdated { get; set; }
}
