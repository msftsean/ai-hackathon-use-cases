using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// A conversation session containing message history.
/// </summary>
public class ChatSession
{
    /// <summary>Unique session identifier.</summary>
    [JsonPropertyName("sessionId")]
    public string SessionId { get; set; } = Guid.NewGuid().ToString();

    /// <summary>Session start time.</summary>
    [JsonPropertyName("createdAt")]
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;

    /// <summary>Most recent message time.</summary>
    [JsonPropertyName("lastActivityAt")]
    public DateTimeOffset LastActivityAt { get; set; } = DateTimeOffset.UtcNow;

    /// <summary>Ordered message history.</summary>
    [JsonPropertyName("messages")]
    public List<ChatMessage> Messages { get; set; } = [];

    /// <summary>Additional session data.</summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }

    /// <summary>
    /// Check if the session has expired (30 minutes of inactivity).
    /// </summary>
    public bool IsExpired => DateTimeOffset.UtcNow - LastActivityAt > TimeSpan.FromMinutes(30);

    /// <summary>
    /// Check if maximum messages reached (100 messages per session).
    /// </summary>
    public bool IsAtCapacity => Messages.Count >= 100;
}
