using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// Response DTO for chat messages.
/// </summary>
public class ChatResponse
{
    /// <summary>Session ID for the conversation.</summary>
    [JsonPropertyName("sessionId")]
    public string SessionId { get; set; } = string.Empty;

    /// <summary>AI-generated response text.</summary>
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    /// <summary>Documents cited in the response.</summary>
    [JsonPropertyName("sources")]
    public List<DocumentSource> Sources { get; set; } = [];

    /// <summary>Confidence score (0.0-1.0).</summary>
    [JsonPropertyName("confidence")]
    public float? Confidence { get; set; }

    /// <summary>Response generation time in milliseconds.</summary>
    [JsonPropertyName("processingTimeMs")]
    public int ProcessingTimeMs { get; set; }
}
