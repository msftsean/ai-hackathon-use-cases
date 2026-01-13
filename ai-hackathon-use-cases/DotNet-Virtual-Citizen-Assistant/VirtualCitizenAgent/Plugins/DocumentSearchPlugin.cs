using System.ComponentModel;
using Microsoft.SemanticKernel;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using VirtualCitizenAgent.Services;
using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Plugins;

/// <summary>
/// Semantic Kernel plugin for searching and retrieving citizen service documents
/// </summary>
public class DocumentSearchPlugin
{
    private readonly IDocumentSearchService _searchService;
    private readonly ILogger<DocumentSearchPlugin> _logger;

    public DocumentSearchPlugin(IDocumentSearchService searchService, ILogger<DocumentSearchPlugin> logger)
    {
        _searchService = searchService ?? throw new ArgumentNullException(nameof(searchService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>
    /// Searches for documents based on a user query
    /// </summary>
    /// <param name="query">The search query from the user</param>
    /// <param name="maxResults">Maximum number of results to return (default: 5)</param>
    /// <returns>JSON string containing search results</returns>
    [KernelFunction, Description("Searches for citizen service documents based on user query")]
    public async Task<string> SearchDocumentsAsync(
        [Description("User's search query about NYC services")] string query,
        [Description("Maximum number of results to return")] int maxResults = 5)
    {
        try
        {
            _logger.LogInformation("Searching documents for query: {Query}", query);

            if (string.IsNullOrWhiteSpace(query))
            {
                return JsonSerializer.Serialize(new { error = "Search query cannot be empty" });
            }

            var searchResults = await _searchService.SearchAsync(query, maxResults);
            
            var results = searchResults.Select(doc => new
            {
                id = doc.Id,
                title = doc.Title,
                content = doc.Content,
                service_type = doc.ServiceType,
                category = doc.Category,
                relevance_score = doc.RelevanceScore,
                last_updated = doc.LastUpdated.ToString("yyyy-MM-dd HH:mm:ss")
            }).ToArray();

            _logger.LogInformation("Found {Count} documents for query: {Query}", results.Length, query);

            return JsonSerializer.Serialize(new { 
                query = query,
                total_results = results.Length,
                documents = results 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching documents for query: {Query}", query);
            return JsonSerializer.Serialize(new { error = $"Search failed: {ex.Message}" });
        }
    }

    /// <summary>
    /// Retrieves a specific document by ID
    /// </summary>
    /// <param name="documentId">The ID of the document to retrieve</param>
    /// <returns>JSON string containing the document details</returns>
    [KernelFunction, Description("Retrieves a specific document by its ID")]
    public async Task<string> GetDocumentByIdAsync(
        [Description("The unique ID of the document to retrieve")] string documentId)
    {
        try
        {
            _logger.LogInformation("Retrieving document with ID: {DocumentId}", documentId);

            if (string.IsNullOrWhiteSpace(documentId))
            {
                return JsonSerializer.Serialize(new { error = "Document ID cannot be empty" });
            }

            var document = await _searchService.GetByIdAsync(documentId);
            
            if (document == null)
            {
                return JsonSerializer.Serialize(new { error = $"Document with ID '{documentId}' not found" });
            }

            var result = new
            {
                id = document.Id,
                title = document.Title,
                content = document.Content,
                service_type = document.ServiceType,
                category = document.Category,
                last_updated = document.LastUpdated.ToString("yyyy-MM-dd HH:mm:ss")
            };

            _logger.LogInformation("Retrieved document: {DocumentId}", documentId);

            return JsonSerializer.Serialize(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving document with ID: {DocumentId}", documentId);
            return JsonSerializer.Serialize(new { error = $"Retrieval failed: {ex.Message}" });
        }
    }

    /// <summary>
    /// Searches for documents within a specific service category
    /// </summary>
    /// <param name="category">The service category to search within</param>
    /// <param name="query">Optional search query within the category</param>
    /// <param name="maxResults">Maximum number of results to return (default: 10)</param>
    /// <returns>JSON string containing search results</returns>
    [KernelFunction, Description("Searches for documents within a specific service category")]
    public async Task<string> SearchByCategoryAsync(
        [Description("Service category (e.g., 'sanitation', 'transportation', 'permits')")] string category,
        [Description("Optional search query within the category")] string query = "",
        [Description("Maximum number of results to return")] int maxResults = 10)
    {
        try
        {
            _logger.LogInformation("Searching documents in category '{Category}' with query: {Query}", category, query);

            if (string.IsNullOrWhiteSpace(category))
            {
                return JsonSerializer.Serialize(new { error = "Category cannot be empty" });
            }

            var searchResults = await _searchService.SearchByCategoryAsync(category, query, maxResults);
            
            var results = searchResults.Select(doc => new
            {
                id = doc.Id,
                title = doc.Title,
                content = doc.Content,
                service_type = doc.ServiceType,
                category = doc.Category,
                relevance_score = doc.RelevanceScore,
                last_updated = doc.LastUpdated.ToString("yyyy-MM-dd HH:mm:ss")
            }).ToArray();

            _logger.LogInformation("Found {Count} documents in category '{Category}'", results.Length, category);

            return JsonSerializer.Serialize(new { 
                category = category,
                query = query,
                total_results = results.Length,
                documents = results 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching documents in category '{Category}' with query: {Query}", category, query);
            return JsonSerializer.Serialize(new { error = $"Category search failed: {ex.Message}" });
        }
    }

    /// <summary>
    /// Gets available service categories
    /// </summary>
    /// <returns>JSON string containing available categories</returns>
    [KernelFunction, Description("Gets a list of available service categories")]
    public async Task<string> GetAvailableCategoriesAsync()
    {
        try
        {
            _logger.LogInformation("Retrieving available service categories");

            var categories = await _searchService.GetAvailableCategoriesAsync();
            
            _logger.LogInformation("Retrieved {Count} categories", categories.Count());

            return JsonSerializer.Serialize(new { 
                total_categories = categories.Count(),
                categories = categories.OrderBy(c => c).ToArray()
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving available categories");
            return JsonSerializer.Serialize(new { error = $"Failed to retrieve categories: {ex.Message}" });
        }
    }

    /// <summary>
    /// Performs a semantic search for documents using natural language understanding
    /// </summary>
    /// <param name="semanticQuery">Natural language query about NYC services</param>
    /// <param name="maxResults">Maximum number of results to return (default: 5)</param>
    /// <returns>JSON string containing semantically ranked search results</returns>
    [KernelFunction, Description("Performs semantic search using natural language understanding")]
    public async Task<string> SemanticSearchAsync(
        [Description("Natural language query about NYC services (e.g., 'I need help with trash pickup')")] string semanticQuery,
        [Description("Maximum number of results to return")] int maxResults = 5)
    {
        try
        {
            _logger.LogInformation("Performing semantic search for query: {Query}", semanticQuery);

            if (string.IsNullOrWhiteSpace(semanticQuery))
            {
                return JsonSerializer.Serialize(new { error = "Semantic query cannot be empty" });
            }

            var searchResults = await _searchService.SemanticSearchAsync(semanticQuery, maxResults);
            
            var results = searchResults.Select(doc => new
            {
                id = doc.Id,
                title = doc.Title,
                content = doc.Content,
                service_type = doc.ServiceType,
                category = doc.Category,
                semantic_score = doc.SemanticScore,
                relevance_score = doc.RelevanceScore,
                last_updated = doc.LastUpdated.ToString("yyyy-MM-dd HH:mm:ss")
            }).ToArray();

            _logger.LogInformation("Found {Count} semantically relevant documents", results.Length);

            return JsonSerializer.Serialize(new { 
                semantic_query = semanticQuery,
                total_results = results.Length,
                documents = results 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing semantic search for query: {Query}", semanticQuery);
            return JsonSerializer.Serialize(new { error = $"Semantic search failed: {ex.Message}" });
        }
    }

    /// <summary>
    /// Gets documents that were recently updated
    /// </summary>
    /// <param name="daysBack">Number of days to look back for recent updates (default: 7)</param>
    /// <param name="maxResults">Maximum number of results to return (default: 10)</param>
    /// <returns>JSON string containing recently updated documents</returns>
    [KernelFunction, Description("Gets documents that were recently updated")]
    public async Task<string> GetRecentlyUpdatedDocumentsAsync(
        [Description("Number of days to look back for updates")] int daysBack = 7,
        [Description("Maximum number of results to return")] int maxResults = 10)
    {
        try
        {
            _logger.LogInformation("Retrieving documents updated in the last {Days} days", daysBack);

            var cutoffDate = DateTimeOffset.UtcNow.AddDays(-daysBack);
            var recentDocuments = await _searchService.GetRecentlyUpdatedAsync(cutoffDate, maxResults);
            
            var results = recentDocuments.Select(doc => new
            {
                id = doc.Id,
                title = doc.Title,
                content = doc.Content,
                service_type = doc.ServiceType,
                category = doc.Category,
                last_updated = doc.LastUpdated.ToString("yyyy-MM-dd HH:mm:ss"),
                days_since_update = (DateTimeOffset.UtcNow - doc.LastUpdated).Days
            }).ToArray();

            _logger.LogInformation("Found {Count} recently updated documents", results.Length);

            return JsonSerializer.Serialize(new { 
                days_back = daysBack,
                cutoff_date = cutoffDate.ToString("yyyy-MM-dd HH:mm:ss"),
                total_results = results.Length,
                documents = results 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving recently updated documents");
            return JsonSerializer.Serialize(new { error = $"Failed to retrieve recent documents: {ex.Message}" });
        }
    }
}