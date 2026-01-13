using Microsoft.AspNetCore.Mvc;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Services;

namespace VirtualCitizenAgent.Controllers;

/// <summary>
/// Chat API controller for RAG-powered conversations.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class ChatController : ControllerBase
{
    private readonly IChatService _chatService;
    private readonly ILogger<ChatController> _logger;

    public ChatController(IChatService chatService, ILogger<ChatController> logger)
    {
        _chatService = chatService;
        _logger = logger;
    }

    /// <summary>
    /// Send a chat message and receive an AI response.
    /// </summary>
    [HttpPost]
    [ProducesResponseType(typeof(ChatResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(Error), StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> Chat([FromBody] ChatRequest request, CancellationToken cancellationToken)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(new Error
            {
                Code = "INVALID_REQUEST",
                Message = "Invalid request parameters",
                Details = string.Join("; ", ModelState.Values.SelectMany(v => v.Errors).Select(e => e.ErrorMessage))
            });
        }

        try
        {
            var response = await _chatService.SendMessageAsync(request, cancellationToken);
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Chat request failed");
            return StatusCode(500, new Error
            {
                Code = "CHAT_ERROR",
                Message = "An error occurred while processing your message",
                CorrelationId = HttpContext.TraceIdentifier
            });
        }
    }

    /// <summary>
    /// Create a new chat session.
    /// </summary>
    [HttpPost("session")]
    [ProducesResponseType(typeof(ChatSession), StatusCodes.Status200OK)]
    public async Task<IActionResult> CreateSession(CancellationToken cancellationToken)
    {
        var session = await _chatService.CreateSessionAsync(cancellationToken);
        return Ok(session);
    }

    /// <summary>
    /// Get a chat session by ID.
    /// </summary>
    [HttpGet("session/{sessionId}")]
    [ProducesResponseType(typeof(ChatSession), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetSession(string sessionId, CancellationToken cancellationToken)
    {
        var session = await _chatService.GetSessionAsync(sessionId, cancellationToken);

        if (session == null)
        {
            return NotFound(new Error
            {
                Code = "SESSION_NOT_FOUND",
                Message = $"Session '{sessionId}' not found"
            });
        }

        return Ok(session);
    }

    /// <summary>
    /// Delete a chat session.
    /// </summary>
    [HttpDelete("session/{sessionId}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteSession(string sessionId, CancellationToken cancellationToken)
    {
        var deleted = await _chatService.DeleteSessionAsync(sessionId, cancellationToken);

        if (!deleted)
        {
            return NotFound(new Error
            {
                Code = "SESSION_NOT_FOUND",
                Message = $"Session '{sessionId}' not found"
            });
        }

        return NoContent();
    }
}

/// <summary>
/// MVC controller for chat views.
/// </summary>
public class ChatViewController : Controller
{
    public IActionResult Index()
    {
        return View("~/Views/Chat/Index.cshtml");
    }
}
