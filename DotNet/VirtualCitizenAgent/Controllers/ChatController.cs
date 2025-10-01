using Microsoft.AspNetCore.Mvc;
using Microsoft.SemanticKernel;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using System.Text;

namespace VirtualCitizenAgent.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ChatController : ControllerBase
{
    private readonly Kernel _kernel;
    private readonly ILogger<ChatController> _logger;

    public ChatController(Kernel kernel, ILogger<ChatController> logger)
    {
        _kernel = kernel;
        _logger = logger;
    }

    [HttpPost("message")]
    public async Task<IActionResult> SendMessage([FromBody] ChatMessageRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Message))
            {
                return BadRequest(new { error = "Message cannot be empty" });
            }

            _logger.LogInformation("Processing chat message: {Message}", request.Message);

            // Step 1: Use semantic search to find relevant documents
            var searchResult = await _kernel.InvokeAsync("DocumentSearch", "SemanticSearch",
                new KernelArguments
                {
                    ["semanticQuery"] = request.Message,
                    ["maxResults"] = 5
                });

            var searchJson = searchResult.GetValue<string>() ?? "{}";
            var searchData = JsonSerializer.Deserialize<JsonElement>(searchJson);

            // Step 2: Extract relevant documents and build context
            var contextBuilder = new StringBuilder();
            var sources = new List<DocumentSource>();

            if (searchData.TryGetProperty("documents", out var documentsArray) && documentsArray.GetArrayLength() > 0)
            {
                contextBuilder.AppendLine("Based on the following NYC government documents:");
                contextBuilder.AppendLine();

                foreach (var doc in documentsArray.EnumerateArray())
                {
                    var title = doc.GetProperty("title").GetString();
                    var content = doc.GetProperty("content").GetString();
                    var category = doc.GetProperty("category").GetString();
                    var serviceType = doc.GetProperty("service_type").GetString();
                    var id = doc.GetProperty("id").GetString();

                    // Add to context for AI
                    contextBuilder.AppendLine($"Document: {title}");
                    contextBuilder.AppendLine($"Category: {category} | Service: {serviceType}");
                    contextBuilder.AppendLine($"Content: {content}");
                    contextBuilder.AppendLine();

                    // Add to sources for response
                    sources.Add(new DocumentSource
                    {
                        Id = id,
                        Title = title,
                        Category = category,
                        ServiceType = serviceType
                    });
                }
            }
            else
            {
                contextBuilder.AppendLine("No specific documents found for this query. Provide general assistance based on knowledge of NYC government services.");
            }

            // Step 3: Create system prompt for RAG
            var systemPrompt = @"You are the NYC Virtual Citizen Agent, an AI assistant helping NYC residents with government services and information.

INSTRUCTIONS:
- Use the provided document context to answer questions accurately
- Be helpful, friendly, and professional
- If the context doesn't contain enough information, say so and suggest how the user might find more help
- Provide specific, actionable guidance when possible
- Reference the document sources when citing information
- Keep responses concise but comprehensive
- Focus on NYC-specific services and procedures

USER QUESTION: " + request.Message + @"

CONTEXT FROM NYC DOCUMENTS:
" + contextBuilder.ToString();

            // Step 4: Generate AI response using the kernel
            var aiResponse = await _kernel.InvokePromptAsync(systemPrompt);
            var responseText = aiResponse.GetValue<string>() ?? "I apologize, but I couldn't generate a response at this time.";

            // Step 5: Return structured response
            var response = new ChatMessageResponse
            {
                Message = responseText,
                Sources = sources,
                Timestamp = DateTimeOffset.UtcNow
            };

            _logger.LogInformation("Generated chat response with {SourceCount} sources", sources.Count);

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing chat message: {Message}", request.Message);
            return StatusCode(500, new { error = "An error occurred while processing your message" });
        }
    }

    [HttpGet("history")]
    public async Task<IActionResult> GetChatHistory()
    {
        // For now, return empty history. In a production system, 
        // you'd store and retrieve chat history from a database
        var history = new List<ChatMessageResponse>();
        return Ok(new { messages = history });
    }
}

public class ChatMessageRequest
{
    public string Message { get; set; } = string.Empty;
}

public class ChatMessageResponse
{
    public string Message { get; set; } = string.Empty;
    public List<DocumentSource> Sources { get; set; } = new();
    public DateTimeOffset Timestamp { get; set; }
}

public class DocumentSource
{
    public string Id { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public string ServiceType { get; set; } = string.Empty;
}