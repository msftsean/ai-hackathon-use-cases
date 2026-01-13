using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using VirtualCitizenAgent.Models;
using System.Text.Json.Serialization;

namespace VirtualCitizenAgent.Services;

/// <summary>
/// Implementation of document search using Azure AI Search
/// </summary>
public class AzureAIDocumentSearchService : IDocumentSearchService
{
    private readonly SearchClient _searchClient;
    private readonly ILogger<AzureAIDocumentSearchService> _logger;
    private readonly string _indexName;

    public AzureAIDocumentSearchService(
        SearchClient searchClient,
        IConfiguration configuration,
        ILogger<AzureAIDocumentSearchService> logger)
    {
        _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _indexName = configuration["AzureSearch:IndexName"] ?? "virtual-agent-nyc";
    }

    public async Task<IEnumerable<SearchResultDocument>> SearchAsync(string query, int maxResults = 10)
    {
        try
        {
            _logger.LogInformation("Performing search for query: '{Query}' with maxResults: {MaxResults}", query, maxResults);
            
            var searchOptions = new SearchOptions
            {
                Size = maxResults,
                IncludeTotalCount = true,
                SearchFields = { "title", "content", "service_type" },
                HighlightFields = { "content" },
                HighlightPreTag = "<mark>",
                HighlightPostTag = "</mark>"
            };

            var searchResults = await _searchClient.SearchAsync<ServiceDocument>(query, searchOptions);
            
            _logger.LogInformation("Search completed. Total count: {TotalCount}, Found: {ResultCount}", 
                searchResults.Value.TotalCount, searchResults.Value.GetResults().Count());
            
            return await ConvertSearchResultsAsync(searchResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing search for query: {Query}", query);
            throw;
        }
    }

    public async Task<SearchResultDocument?> GetByIdAsync(string id)
    {
        try
        {
            var response = await _searchClient.GetDocumentAsync<ServiceDocument>(id);
            return ConvertToSearchResult(response.Value);
        }
        catch (RequestFailedException ex) when (ex.Status == 404)
        {
            _logger.LogWarning("Document with ID {Id} not found", id);
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving document with ID: {Id}", id);
            throw;
        }
    }

    public async Task<IEnumerable<SearchResultDocument>> SearchByCategoryAsync(string category, string query = "", int maxResults = 10)
    {
        try
        {
            var filter = $"category eq '{category.Replace("'", "''")}'";
            var searchText = string.IsNullOrWhiteSpace(query) ? "*" : query;

            var searchOptions = new SearchOptions
            {
                Size = maxResults,
                Filter = filter,
                IncludeTotalCount = true,
                SearchFields = { "title", "content", "service_type" },
                HighlightFields = { "content" },
                HighlightPreTag = "<mark>",
                HighlightPostTag = "</mark>"
            };

            var searchResults = await _searchClient.SearchAsync<ServiceDocument>(searchText, searchOptions);
            
            return await ConvertSearchResultsAsync(searchResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching by category: {Category} with query: {Query}", category, query);
            throw;
        }
    }

    public async Task<IEnumerable<string>> GetAvailableCategoriesAsync()
    {
        try
        {
            var searchOptions = new SearchOptions
            {
                Size = 0, // We only want facets, not documents
                Facets = { "category" }
            };

            var searchResults = await _searchClient.SearchAsync<ServiceDocument>("*", searchOptions);
            
            var categories = new List<string>();
            if (searchResults.Value.Facets.TryGetValue("category", out var facetResults))
            {
                categories.AddRange(facetResults.Select(f => f.Value?.ToString() ?? "").Where(s => !string.IsNullOrEmpty(s)));
            }

            return categories.Distinct().OrderBy(c => c);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving available categories");
            throw;
        }
    }

    public async Task<IEnumerable<SearchResultDocument>> SemanticSearchAsync(string semanticQuery, int maxResults = 5)
    {
        try
        {
            var searchOptions = new SearchOptions
            {
                Size = maxResults,
                QueryType = SearchQueryType.Semantic,
                IncludeTotalCount = true,
                SearchFields = { "title", "content", "service_type" },
                HighlightFields = { "content" },
                HighlightPreTag = "<mark>",
                HighlightPostTag = "</mark>"
            };

            var searchResults = await _searchClient.SearchAsync<ServiceDocument>(semanticQuery, searchOptions);
            
            return await ConvertSemanticSearchResultsAsync(searchResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing semantic search for query: {Query}", semanticQuery);
            throw;
        }
    }

    public async Task<IEnumerable<SearchResultDocument>> GetRecentlyUpdatedAsync(DateTimeOffset cutoffDate, int maxResults = 10)
    {
        try
        {
            var filter = $"last_updated ge {cutoffDate:yyyy-MM-ddTHH:mm:ssZ}";

            var searchOptions = new SearchOptions
            {
                Size = maxResults,
                Filter = filter,
                OrderBy = { "last_updated desc" },
                IncludeTotalCount = true
            };

            var searchResults = await _searchClient.SearchAsync<ServiceDocument>("*", searchOptions);
            
            return await ConvertSearchResultsAsync(searchResults);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving recently updated documents since: {CutoffDate}", cutoffDate);
            throw;
        }
    }

    private async Task<IEnumerable<SearchResultDocument>> ConvertSearchResultsAsync(Response<SearchResults<ServiceDocument>> searchResults)
    {
        var results = new List<SearchResultDocument>();

        await foreach (var result in searchResults.Value.GetResultsAsync())
        {
            var searchResult = ConvertToSearchResult(result.Document, result.Score);
            
            // Add highlights
            if (result.Highlights?.Any() == true)
            {
                foreach (var highlight in result.Highlights)
                {
                    searchResult.Highlights.Add(string.Join(" ... ", highlight.Value));
                }
            }

            results.Add(searchResult);
        }

        return results;
    }

    private async Task<IEnumerable<SearchResultDocument>> ConvertSemanticSearchResultsAsync(Response<SearchResults<ServiceDocument>> searchResults)
    {
        var results = new List<SearchResultDocument>();

        await foreach (var result in searchResults.Value.GetResultsAsync())
        {
            var searchResult = ConvertToSearchResult(result.Document, result.Score);
            
            // For semantic search, mark as semantic
            searchResult.SemanticScore = result.Score ?? 0.0;

            // Add highlights if available
            if (result.Highlights?.Any() == true)
            {
                foreach (var highlight in result.Highlights)
                {
                    searchResult.Highlights.Add(string.Join(" ... ", highlight.Value));
                }
            }

            results.Add(searchResult);
        }

        return results;
    }

    private SearchResultDocument ConvertToSearchResult(ServiceDocument document, double? score = null)
    {
        return new SearchResultDocument
        {
            Id = document.Id,
            Title = document.Title,
            Content = document.Content,
            ServiceType = document.ServiceType,
            Category = document.Category,
            LastUpdated = document.LastUpdated,
            RelevanceScore = score ?? 0.0,
            SemanticScore = 0.0, // Will be set by semantic search if applicable
            Metadata = new Dictionary<string, object>
            {
                ["service_type"] = document.ServiceType,
                ["category"] = document.Category,
                ["last_updated"] = document.LastUpdated
            }
        };
    }
}

/// <summary>
/// Document model matching the Azure Search index schema
/// </summary>
public class ServiceDocument
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("service_type")]
    public string ServiceType { get; set; } = string.Empty;
    
    [JsonPropertyName("title")]
    public string Title { get; set; } = string.Empty;
    
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;
    
    [JsonPropertyName("category")]
    public string Category { get; set; } = string.Empty;
    
    [JsonPropertyName("last_updated")]
    public DateTimeOffset LastUpdated { get; set; }
}