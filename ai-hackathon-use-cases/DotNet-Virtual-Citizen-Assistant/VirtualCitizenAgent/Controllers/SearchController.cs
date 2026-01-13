using Microsoft.AspNetCore.Mvc;
using Microsoft.SemanticKernel;
using Microsoft.Extensions.Logging;
using System.Text.Json;

namespace VirtualCitizenAgent.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SearchController : ControllerBase
{
    private readonly Kernel _kernel;
    private readonly ILogger<SearchController> _logger;

    public SearchController(Kernel kernel, ILogger<SearchController> logger)
    {
        _kernel = kernel;
        _logger = logger;
    }

    [HttpGet("documents")]
    public async Task<IActionResult> SearchDocuments([FromQuery] string query, [FromQuery] int maxResults = 5)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                return BadRequest(new { error = "Query parameter is required" });
            }

            _logger.LogInformation("Searching documents for query: {Query}", query);

            var result = await _kernel.InvokeAsync("DocumentSearch", "SearchDocuments",
                new KernelArguments
                {
                    ["query"] = query,
                    ["maxResults"] = maxResults
                });

            var jsonResult = result.GetValue<string>() ?? "{}";
            var searchResults = JsonSerializer.Deserialize<object>(jsonResult);

            return Ok(searchResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching documents for query: {Query}", query);
            return StatusCode(500, new { error = "An error occurred while searching documents" });
        }
    }

    [HttpGet("documents/{id}")]
    public async Task<IActionResult> GetDocument(string id)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(id))
            {
                return BadRequest(new { error = "Document ID is required" });
            }

            _logger.LogInformation("Retrieving document with ID: {DocumentId}", id);

            var result = await _kernel.InvokeAsync("DocumentSearch", "GetDocumentById",
                new KernelArguments
                {
                    ["documentId"] = id
                });

            var jsonResult = result.GetValue<string>() ?? "{}";
            var document = JsonSerializer.Deserialize<object>(jsonResult);

            return Ok(document);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving document with ID: {DocumentId}", id);
            return StatusCode(500, new { error = "An error occurred while retrieving the document" });
        }
    }

    [HttpGet("categories")]
    public async Task<IActionResult> GetCategories()
    {
        try
        {
            _logger.LogInformation("Retrieving available categories");

            var result = await _kernel.InvokeAsync("DocumentSearch", "GetAvailableCategories");

            var jsonResult = result.GetValue<string>() ?? "{}";
            var categories = JsonSerializer.Deserialize<object>(jsonResult);

            return Ok(categories);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving categories");
            return StatusCode(500, new { error = "An error occurred while retrieving categories" });
        }
    }

    [HttpGet("categories/{category}")]
    public async Task<IActionResult> SearchByCategory(string category, [FromQuery] string query = "", [FromQuery] int maxResults = 10)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(category))
            {
                return BadRequest(new { error = "Category parameter is required" });
            }

            _logger.LogInformation("Searching in category '{Category}' with query: {Query}", category, query);

            var result = await _kernel.InvokeAsync("DocumentSearch", "SearchByCategory",
                new KernelArguments
                {
                    ["category"] = category,
                    ["query"] = query,
                    ["maxResults"] = maxResults
                });

            var jsonResult = result.GetValue<string>() ?? "{}";
            var searchResults = JsonSerializer.Deserialize<object>(jsonResult);

            return Ok(searchResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching category '{Category}' with query: {Query}", category, query);
            return StatusCode(500, new { error = "An error occurred while searching the category" });
        }
    }

    [HttpGet("semantic")]
    public async Task<IActionResult> SemanticSearch([FromQuery] string query, [FromQuery] int maxResults = 5)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                return BadRequest(new { error = "Query parameter is required" });
            }

            _logger.LogInformation("Performing semantic search for query: {Query}", query);

            var result = await _kernel.InvokeAsync("DocumentSearch", "SemanticSearch",
                new KernelArguments
                {
                    ["semanticQuery"] = query,
                    ["maxResults"] = maxResults
                });

            var jsonResult = result.GetValue<string>() ?? "{}";
            var searchResults = JsonSerializer.Deserialize<object>(jsonResult);

            return Ok(searchResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing semantic search for query: {Query}", query);
            return StatusCode(500, new { error = "An error occurred while performing semantic search" });
        }
    }

    [HttpGet("recent")]
    public async Task<IActionResult> GetRecentDocuments([FromQuery] int daysBack = 7, [FromQuery] int maxResults = 10)
    {
        try
        {
            _logger.LogInformation("Retrieving documents updated in the last {Days} days", daysBack);

            var result = await _kernel.InvokeAsync("DocumentSearch", "GetRecentlyUpdatedDocuments",
                new KernelArguments
                {
                    ["daysBack"] = daysBack,
                    ["maxResults"] = maxResults
                });

            var jsonResult = result.GetValue<string>() ?? "{}";
            var recentDocuments = JsonSerializer.Deserialize<object>(jsonResult);

            return Ok(recentDocuments);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving recent documents");
            return StatusCode(500, new { error = "An error occurred while retrieving recent documents" });
        }
    }
}