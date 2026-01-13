namespace VirtualCitizenAgent.Configuration;

/// <summary>
/// Configuration for Azure AI Search service.
/// </summary>
public class SearchConfiguration
{
    public const string SectionName = "SearchConfiguration";

    /// <summary>
    /// Azure AI Search endpoint URL.
    /// </summary>
    public string Endpoint { get; set; } = string.Empty;

    /// <summary>
    /// Name of the search index.
    /// </summary>
    public string IndexName { get; set; } = "citizen-services";

    /// <summary>
    /// Azure AI Search API key.
    /// </summary>
    public string ApiKey { get; set; } = string.Empty;

    /// <summary>
    /// Name of the semantic configuration for semantic search.
    /// </summary>
    public string SemanticConfigurationName { get; set; } = "citizen-services-semantic";

    /// <summary>
    /// Whether to use mock service for offline development.
    /// </summary>
    public bool UseMockService { get; set; } = true;
}
