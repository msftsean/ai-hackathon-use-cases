using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Services;

/// <summary>
/// Interface for document search operations
/// </summary>
public interface IDocumentSearchService
{
    /// <summary>
    /// Performs a general search across all documents
    /// </summary>
    /// <param name="query">Search query</param>
    /// <param name="maxResults">Maximum number of results</param>
    /// <returns>Collection of search results</returns>
    Task<IEnumerable<SearchResultDocument>> SearchAsync(string query, int maxResults = 10);

    /// <summary>
    /// Retrieves a document by its unique ID
    /// </summary>
    /// <param name="id">Document ID</param>
    /// <returns>Document or null if not found</returns>
    Task<SearchResultDocument?> GetByIdAsync(string id);

    /// <summary>
    /// Searches for documents within a specific category
    /// </summary>
    /// <param name="category">Service category</param>
    /// <param name="query">Optional search query within category</param>
    /// <param name="maxResults">Maximum number of results</param>
    /// <returns>Collection of search results</returns>
    Task<IEnumerable<SearchResultDocument>> SearchByCategoryAsync(string category, string query = "", int maxResults = 10);

    /// <summary>
    /// Gets all available service categories
    /// </summary>
    /// <returns>Collection of category names</returns>
    Task<IEnumerable<string>> GetAvailableCategoriesAsync();

    /// <summary>
    /// Performs semantic search using natural language understanding
    /// </summary>
    /// <param name="semanticQuery">Natural language query</param>
    /// <param name="maxResults">Maximum number of results</param>
    /// <returns>Collection of semantically ranked results</returns>
    Task<IEnumerable<SearchResultDocument>> SemanticSearchAsync(string semanticQuery, int maxResults = 5);

    /// <summary>
    /// Gets documents that were recently updated
    /// </summary>
    /// <param name="cutoffDate">Date threshold for "recent" updates</param>
    /// <param name="maxResults">Maximum number of results</param>
    /// <returns>Collection of recently updated documents</returns>
    Task<IEnumerable<SearchResultDocument>> GetRecentlyUpdatedAsync(DateTimeOffset cutoffDate, int maxResults = 10);
}