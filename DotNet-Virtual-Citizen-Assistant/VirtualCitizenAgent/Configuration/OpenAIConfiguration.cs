namespace VirtualCitizenAgent.Configuration;

/// <summary>
/// Configuration for Azure OpenAI service.
/// </summary>
public class OpenAIConfiguration
{
    public const string SectionName = "OpenAI";

    /// <summary>
    /// Azure OpenAI endpoint URL.
    /// </summary>
    public string Endpoint { get; set; } = string.Empty;

    /// <summary>
    /// Azure OpenAI API key.
    /// </summary>
    public string ApiKey { get; set; } = string.Empty;

    /// <summary>
    /// Name of the GPT deployment for chat.
    /// </summary>
    public string DeploymentName { get; set; } = "gpt-4";

    /// <summary>
    /// Name of the embedding deployment for vector search.
    /// </summary>
    public string EmbeddingDeploymentName { get; set; } = "text-embedding-ada-002";

    /// <summary>
    /// Whether to use mock service for offline development.
    /// </summary>
    public bool UseMockService { get; set; } = true;
}
