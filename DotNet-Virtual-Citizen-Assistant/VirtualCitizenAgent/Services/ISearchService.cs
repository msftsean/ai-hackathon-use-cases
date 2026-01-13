using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Services;

/// <summary>
/// Interface for document search operations.
/// </summary>
public interface ISearchService
{
    /// <summary>
    /// Search documents with the specified query.
    /// </summary>
    Task<SearchResponse> SearchAsync(SearchQuery query, CancellationToken cancellationToken = default);

    /// <summary>
    /// Perform semantic search with AI-powered ranking.
    /// </summary>
    Task<SearchResponse> SemanticSearchAsync(string query, int top = 10, string? category = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Perform keyword search with traditional TF-IDF ranking.
    /// </summary>
    Task<SearchResponse> KeywordSearchAsync(string query, int top = 10, string? category = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Perform hybrid search combining keyword and semantic.
    /// </summary>
    Task<SearchResponse> HybridSearchAsync(string query, int top = 10, string? category = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get a document by its ID.
    /// </summary>
    Task<Document?> GetDocumentByIdAsync(string documentId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get recently updated documents.
    /// </summary>
    Task<List<Document>> GetRecentDocumentsAsync(int days = 30, int top = 10, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get all categories with document counts.
    /// </summary>
    Task<List<ServiceCategory>> GetCategoriesAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get category details with documents.
    /// </summary>
    Task<CategoryDetail?> GetCategoryByNameAsync(string categoryName, CancellationToken cancellationToken = default);
}
