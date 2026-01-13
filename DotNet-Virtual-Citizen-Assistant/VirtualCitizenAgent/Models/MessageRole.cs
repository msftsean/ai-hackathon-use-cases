namespace VirtualCitizenAgent.Models;

/// <summary>
/// Role of a message sender in a chat conversation.
/// </summary>
public enum MessageRole
{
    /// <summary>Message from the citizen user.</summary>
    User,

    /// <summary>Response from the AI assistant.</summary>
    Assistant,

    /// <summary>System instructions (internal use only).</summary>
    System
}
