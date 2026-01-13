using Microsoft.AspNetCore.Mvc;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Services;

namespace VirtualCitizenAgent.Controllers;

/// <summary>
/// Search API controller for document search operations.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class SearchController : ControllerBase
{
    private readonly ISearchService _searchService;
    private readonly ILogger<SearchController> _logger;

    public SearchController(ISearchService searchService, ILogger<SearchController> logger)
    {
        _searchService = searchService;
        _logger = logger;
    }

    /// <summary>
    /// Search documents with configurable mode.
    /// </summary>
    [HttpGet]
    [ProducesResponseType(typeof(SearchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(Error), StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> Search(
        [FromQuery] string query,
        [FromQuery] SearchMode mode = SearchMode.Semantic,
        [FromQuery] string? category = null,
        [FromQuery] int top = 10,
        [FromQuery] int skip = 0,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(query))
        {
            return BadRequest(new Error
            {
                Code = "INVALID_QUERY",
                Message = "Query parameter is required"
            });
        }

        if (top < 1 || top > 50)
        {
            return BadRequest(new Error
            {
                Code = "INVALID_TOP",
                Message = "Top must be between 1 and 50"
            });
        }

        try
        {
            var searchQuery = new SearchQuery
            {
                Query = query,
                Mode = mode,
                Category = category,
                Top = top,
                Skip = skip
            };

            var response = await _searchService.SearchAsync(searchQuery, cancellationToken);
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Search failed for query: {Query}", query);
            return StatusCode(500, new Error
            {
                Code = "SEARCH_ERROR",
                Message = "An error occurred while searching",
                CorrelationId = HttpContext.TraceIdentifier
            });
        }
    }

    /// <summary>
    /// Perform semantic search with AI-powered ranking.
    /// </summary>
    [HttpGet("semantic")]
    [ProducesResponseType(typeof(SearchResponse), StatusCodes.Status200OK)]
    public async Task<IActionResult> SemanticSearch(
        [FromQuery] string query,
        [FromQuery] string? category = null,
        [FromQuery] int top = 10,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(query))
        {
            return BadRequest(new Error
            {
                Code = "INVALID_QUERY",
                Message = "Query parameter is required"
            });
        }

        var response = await _searchService.SemanticSearchAsync(query, top, category, cancellationToken);
        return Ok(response);
    }

    /// <summary>
    /// Get a document by ID.
    /// </summary>
    [HttpGet("documents/{documentId}")]
    [ProducesResponseType(typeof(Document), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetDocument(string documentId, CancellationToken cancellationToken)
    {
        var document = await _searchService.GetDocumentByIdAsync(documentId, cancellationToken);

        if (document == null)
        {
            return NotFound(new Error
            {
                Code = "DOCUMENT_NOT_FOUND",
                Message = $"Document '{documentId}' not found"
            });
        }

        return Ok(document);
    }

    /// <summary>
    /// Get recently updated documents.
    /// </summary>
    [HttpGet("documents/recent")]
    [ProducesResponseType(typeof(List<Document>), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetRecentDocuments(
        [FromQuery] int days = 30,
        [FromQuery] int top = 10,
        CancellationToken cancellationToken = default)
    {
        var documents = await _searchService.GetRecentDocumentsAsync(days, top, cancellationToken);
        return Ok(documents);
    }
}

/// <summary>
/// MVC controller for search views.
/// </summary>
public class SearchViewController : Controller
{
    private readonly ISearchService _searchService;

    public SearchViewController(ISearchService searchService)
    {
        _searchService = searchService;
    }

    public async Task<IActionResult> Index(string? q = null, string? category = null)
    {
        ViewBag.Query = q;
        ViewBag.Category = category;

        if (!string.IsNullOrWhiteSpace(q))
        {
            var results = await _searchService.SearchAsync(new SearchQuery
            {
                Query = q,
                Category = category,
                Mode = SearchMode.Semantic,
                Top = 20
            });
            ViewBag.Results = results;
        }

        var categories = await _searchService.GetCategoriesAsync();
        ViewBag.Categories = categories;

        return View("~/Views/Search/Index.cshtml");
    }
}
