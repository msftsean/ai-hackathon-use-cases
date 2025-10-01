using System.Text.Json.Serialization;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

namespace AzureSearchUploader.Models;

/// <summary>
/// Represents a citizen service document for Azure AI Search based on the provided JSON format
/// </summary>
public class ServiceDocument
{
    /// <summary>
    /// Unique identifier for the document
    /// </summary>
    [SimpleField(IsKey = true, IsFilterable = true)]
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Type of service (e.g., "waste_management", "transportation", "permits")
    /// </summary>
    [SearchableField(IsFilterable = true, IsFacetable = true)]
    [JsonPropertyName("service_type")]
    public string ServiceType { get; set; } = string.Empty;

    /// <summary>
    /// Title of the service or document
    /// </summary>
    [SearchableField(IsFilterable = true, IsSortable = true)]
    [JsonPropertyName("title")]
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Main content/description of the service
    /// </summary>
    [SearchableField(AnalyzerName = LexicalAnalyzerName.Values.EnMicrosoft)]
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    /// <summary>
    /// Category of the service (e.g., "sanitation", "transportation", "permits")
    /// </summary>
    [SearchableField(IsFilterable = true, IsFacetable = true)]
    [JsonPropertyName("category")]
    public string Category { get; set; } = string.Empty;

    /// <summary>
    /// When the document was last updated (ISO format)
    /// </summary>
    [SimpleField(IsFilterable = true, IsSortable = true)]
    [JsonPropertyName("last_updated")]
    public DateTimeOffset LastUpdated { get; set; } = DateTimeOffset.UtcNow;
}

/// <summary>
/// Configuration settings for Azure AI Search service
/// </summary>
public class SearchConfiguration
{
    /// <summary>
    /// Azure AI Search service endpoint URL
    /// </summary>
    public string ServiceEndpoint { get; set; } = string.Empty;

    /// <summary>
    /// Name of the search index to use for data upload
    /// </summary>
    public string IndexName { get; set; } = string.Empty;

    /// <summary>
    /// API key for Azure AI Search service (optional if using managed identity)
    /// </summary>
    public string? ApiKey { get; set; }

    /// <summary>
    /// Whether to use managed identity for authentication (recommended for production)
    /// </summary>
    public bool UseManagedIdentity { get; set; } = true;

    /// <summary>
    /// Batch size for document uploads (default: 100)
    /// </summary>
    public int BatchSize { get; set; } = 100;

    /// <summary>
    /// Maximum retry attempts for failed operations
    /// </summary>
    public int MaxRetryAttempts { get; set; } = 3;
}

/// <summary>
/// Represents the result of an upload operation
/// </summary>
public class UploadResult
{
    /// <summary>
    /// Number of documents successfully uploaded
    /// </summary>
    public int SuccessCount { get; set; }

    /// <summary>
    /// Number of documents that failed to upload
    /// </summary>
    public int FailureCount { get; set; }

    /// <summary>
    /// List of error messages for failed uploads
    /// </summary>
    public List<string> Errors { get; set; } = new();

    /// <summary>
    /// Total time taken for the upload operation
    /// </summary>
    public TimeSpan Duration { get; set; }

    /// <summary>
    /// Whether the overall operation was successful
    /// </summary>
    public bool IsSuccess => FailureCount == 0;
}