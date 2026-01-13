using System.Collections.Concurrent;
using System.Diagnostics;
using Microsoft.Extensions.Options;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using VirtualCitizenAgent.Configuration;
using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Services;

/// <summary>
/// Chat service implementation with RAG pipeline using Semantic Kernel.
/// </summary>
public class ChatService : IChatService
{
    private readonly Kernel? _kernel;
    private readonly ISearchService _searchService;
    private readonly OpenAIConfiguration _config;
    private readonly ILogger<ChatService> _logger;
    private readonly bool _useMock;

    // In-memory session storage (use distributed cache in production)
    private static readonly ConcurrentDictionary<string, ChatSession> Sessions = new();

    private const string SystemPrompt = """
        You are a helpful NYC Virtual Citizen Assistant. Your role is to help citizens find information about NYC government services.

        Guidelines:
        - Always be helpful, accurate, and respectful
        - Use the provided document context to answer questions
        - If you're not sure about something, say so
        - Cite your sources when providing information
        - Keep responses concise but complete
        - If a question is outside NYC government services, politely redirect

        When answering questions:
        1. Search for relevant documents using the provided context
        2. Synthesize information from multiple sources if needed
        3. Provide clear, actionable guidance
        4. Include relevant links when available
        """;

    public ChatService(
        ISearchService searchService,
        IOptions<OpenAIConfiguration> config,
        ILogger<ChatService> logger,
        Kernel? kernel = null)
    {
        _searchService = searchService;
        _config = config.Value;
        _logger = logger;
        _kernel = kernel;
        _useMock = _config.UseMockService || string.IsNullOrEmpty(_config.Endpoint) || kernel == null;
    }

    public async Task<ChatResponse> SendMessageAsync(ChatRequest request, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        // Get or create session
        var session = string.IsNullOrEmpty(request.SessionId)
            ? await CreateSessionAsync(cancellationToken)
            : await GetSessionAsync(request.SessionId, cancellationToken) ?? await CreateSessionAsync(cancellationToken);

        // Check session limits
        if (session.IsExpired)
        {
            session = await CreateSessionAsync(cancellationToken);
        }

        if (session.IsAtCapacity)
        {
            return new ChatResponse
            {
                SessionId = session.SessionId,
                Content = "This session has reached its message limit. Please start a new conversation.",
                ProcessingTimeMs = (int)stopwatch.ElapsedMilliseconds
            };
        }

        // Add user message to session
        var userMessage = new ChatMessage
        {
            SessionId = session.SessionId,
            Role = MessageRole.User,
            Content = request.Message
        };
        session.Messages.Add(userMessage);
        session.LastActivityAt = DateTimeOffset.UtcNow;

        // Search for relevant documents
        var searchResponse = await _searchService.SemanticSearchAsync(request.Message, top: 5, cancellationToken: cancellationToken);
        var sources = searchResponse.Results
            .Select(r => new DocumentSource
            {
                DocumentId = r.Document.Id,
                Title = r.Document.Title,
                Url = r.Document.Url ?? $"/documents/{r.Document.Id}",
                Relevance = (float)r.Score
            })
            .ToList();

        // Generate response
        string responseContent;
        float? confidence = null;

        if (_useMock)
        {
            responseContent = await GenerateMockResponseAsync(request.Message, searchResponse.Results, cancellationToken);
            confidence = searchResponse.Results.Count > 0 ? 0.85f : 0.3f;
        }
        else
        {
            (responseContent, confidence) = await GenerateKernelResponseAsync(request.Message, searchResponse.Results, session, cancellationToken);
        }

        // Add assistant message to session
        var assistantMessage = new ChatMessage
        {
            SessionId = session.SessionId,
            Role = MessageRole.Assistant,
            Content = responseContent,
            Sources = sources
        };
        session.Messages.Add(assistantMessage);

        stopwatch.Stop();

        return new ChatResponse
        {
            SessionId = session.SessionId,
            Content = responseContent,
            Sources = sources,
            Confidence = confidence,
            ProcessingTimeMs = (int)stopwatch.ElapsedMilliseconds
        };
    }

    public Task<ChatSession> CreateSessionAsync(CancellationToken cancellationToken = default)
    {
        var session = new ChatSession();
        Sessions[session.SessionId] = session;
        return Task.FromResult(session);
    }

    public Task<ChatSession?> GetSessionAsync(string sessionId, CancellationToken cancellationToken = default)
    {
        Sessions.TryGetValue(sessionId, out var session);
        return Task.FromResult(session);
    }

    public Task<bool> DeleteSessionAsync(string sessionId, CancellationToken cancellationToken = default)
    {
        var removed = Sessions.TryRemove(sessionId, out _);
        return Task.FromResult(removed);
    }

    private async Task<string> GenerateMockResponseAsync(string query, List<SearchResult> results, CancellationToken cancellationToken)
    {
        await Task.Delay(100, cancellationToken); // Simulate processing time

        if (results.Count == 0)
        {
            return "I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or ask about a specific NYC government service?";
        }

        var topResult = results.First();
        var response = $"Based on the information I found about \"{topResult.Document.Title}\":\n\n";
        response += topResult.Document.Content;

        if (!string.IsNullOrEmpty(topResult.Document.Url))
        {
            response += $"\n\nFor more details, you can visit: {topResult.Document.Url}";
        }

        if (results.Count > 1)
        {
            response += "\n\nI also found related information about:";
            foreach (var result in results.Skip(1).Take(2))
            {
                response += $"\n- {result.Document.Title}";
            }
        }

        return response;
    }

    private async Task<(string content, float? confidence)> GenerateKernelResponseAsync(
        string query,
        List<SearchResult> results,
        ChatSession session,
        CancellationToken cancellationToken)
    {
        try
        {
            var chatCompletionService = _kernel!.GetRequiredService<IChatCompletionService>();

            var chatHistory = new ChatHistory(SystemPrompt);

            // Add context from search results
            if (results.Count > 0)
            {
                var context = "Relevant documents found:\n\n";
                foreach (var result in results.Take(3))
                {
                    context += $"Document: {result.Document.Title}\n";
                    context += $"Content: {result.Document.Content}\n";
                    if (!string.IsNullOrEmpty(result.Document.Url))
                    {
                        context += $"URL: {result.Document.Url}\n";
                    }
                    context += "\n---\n\n";
                }
                chatHistory.AddSystemMessage($"Use the following context to answer the user's question:\n\n{context}");
            }

            // Add conversation history (last 10 messages for context window management)
            foreach (var msg in session.Messages.TakeLast(10))
            {
                if (msg.Role == MessageRole.User)
                    chatHistory.AddUserMessage(msg.Content);
                else if (msg.Role == MessageRole.Assistant)
                    chatHistory.AddAssistantMessage(msg.Content);
            }

            // Add current query
            chatHistory.AddUserMessage(query);

            var response = await chatCompletionService.GetChatMessageContentAsync(
                chatHistory,
                cancellationToken: cancellationToken);

            var confidence = results.Count > 0 ? 0.9f : 0.5f;

            return (response.Content ?? "I apologize, but I couldn't generate a response. Please try again.", confidence);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to generate response with Semantic Kernel");
            return await GenerateMockResponseAsync(query, results, cancellationToken)
                .ContinueWith(t => (t.Result, (float?)0.5f), cancellationToken);
        }
    }
}
