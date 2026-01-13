using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// Request DTO for chat messages.
/// </summary>
public class ChatRequest
{
    /// <summary>Session ID for multi-turn conversations (optional for new sessions).</summary>
    [JsonPropertyName("sessionId")]
    public string? SessionId { get; set; }

    /// <summary>User's message content.</summary>
    [Required]
    [StringLength(10000, MinimumLength = 1)]
    [JsonPropertyName("message")]
    public string Message { get; set; } = string.Empty;
}
