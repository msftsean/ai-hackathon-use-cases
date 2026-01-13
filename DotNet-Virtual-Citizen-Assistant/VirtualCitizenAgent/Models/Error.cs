using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Models;

/// <summary>
/// Error response model for API responses.
/// </summary>
public class Error
{
    /// <summary>Error code for programmatic handling.</summary>
    [JsonPropertyName("code")]
    public string Code { get; set; } = string.Empty;

    /// <summary>Human-readable error message.</summary>
    [JsonPropertyName("message")]
    public string Message { get; set; } = string.Empty;

    /// <summary>Additional error details.</summary>
    [JsonPropertyName("details")]
    public string? Details { get; set; }

    /// <summary>Request correlation ID for tracing.</summary>
    [JsonPropertyName("correlationId")]
    public string? CorrelationId { get; set; }
}
