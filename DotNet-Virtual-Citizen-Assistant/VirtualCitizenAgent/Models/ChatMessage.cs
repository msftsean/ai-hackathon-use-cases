using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// A single message in a chat conversation.
/// </summary>
public class ChatMessage
{
    /// <summary>Unique message identifier.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>Parent session reference.</summary>
    [JsonPropertyName("sessionId")]
    public string SessionId { get; set; } = string.Empty;

    /// <summary>Who sent the message.</summary>
    [JsonPropertyName("role")]
    public MessageRole Role { get; set; }

    /// <summary>Message text content.</summary>
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    /// <summary>When the message was sent.</summary>
    [JsonPropertyName("timestamp")]
    public DateTimeOffset Timestamp { get; set; } = DateTimeOffset.UtcNow;

    /// <summary>Cited documents (assistant messages only).</summary>
    [JsonPropertyName("sources")]
    public List<DocumentSource>? Sources { get; set; }
}
