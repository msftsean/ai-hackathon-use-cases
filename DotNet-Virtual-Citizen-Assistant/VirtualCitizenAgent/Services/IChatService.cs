using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Services;

/// <summary>
/// Interface for chat operations with RAG capabilities.
/// </summary>
public interface IChatService
{
    /// <summary>
    /// Send a message and get an AI response with sources.
    /// </summary>
    Task<ChatResponse> SendMessageAsync(ChatRequest request, CancellationToken cancellationToken = default);

    /// <summary>
    /// Create a new chat session.
    /// </summary>
    Task<ChatSession> CreateSessionAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get a chat session by ID.
    /// </summary>
    Task<ChatSession?> GetSessionAsync(string sessionId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete a chat session.
    /// </summary>
    Task<bool> DeleteSessionAsync(string sessionId, CancellationToken cancellationToken = default);
}
