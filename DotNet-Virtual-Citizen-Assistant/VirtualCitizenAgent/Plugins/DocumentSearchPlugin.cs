using System.ComponentModel;
using Microsoft.SemanticKernel;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Services;

namespace VirtualCitizenAgent.Plugins;

/// <summary>
/// Semantic Kernel plugin for document search operations.
/// </summary>
public class DocumentSearchPlugin
{
    private readonly ISearchService _searchService;

    public DocumentSearchPlugin(ISearchService searchService)
    {
        _searchService = searchService;
    }

    [KernelFunction("search_documents")]
    [Description("Search for NYC government service documents using semantic search")]
    public async Task<string> SearchDocumentsAsync(
        [Description("The search query describing what information the user is looking for")] string query,
        [Description("Optional category filter (e.g., Transportation, Housing, Business)")] string? category = null,
        [Description("Number of results to return (default 5)")] int top = 5)
    {
        var results = await _searchService.SemanticSearchAsync(query, top, category);

        if (results.Results.Count == 0)
        {
            return "No relevant documents found for the query.";
        }

        var response = $"Found {results.TotalCount} relevant documents:\n\n";
        foreach (var result in results.Results)
        {
            response += $"**{result.Document.Title}**\n";
            response += $"Category: {result.Document.Category}\n";
            response += $"Summary: {result.Document.Summary ?? result.Document.Content[..Math.Min(200, result.Document.Content.Length)]}...\n";
            if (!string.IsNullOrEmpty(result.Document.Url))
            {
                response += $"Link: {result.Document.Url}\n";
            }
            response += "\n---\n";
        }

        return response;
    }

    [KernelFunction("get_document")]
    [Description("Get the full content of a specific document by its ID")]
    public async Task<string> GetDocumentAsync(
        [Description("The unique identifier of the document")] string documentId)
    {
        var document = await _searchService.GetDocumentByIdAsync(documentId);

        if (document == null)
        {
            return $"Document with ID '{documentId}' not found.";
        }

        return $"""
            **{document.Title}**

            Category: {document.Category}
            Last Updated: {document.LastUpdated:yyyy-MM-dd}

            {document.Content}

            {(string.IsNullOrEmpty(document.Url) ? "" : $"Source: {document.Url}")}
            """;
    }

    [KernelFunction("list_categories")]
    [Description("List all available service categories")]
    public async Task<string> ListCategoriesAsync()
    {
        var categories = await _searchService.GetCategoriesAsync();

        if (categories.Count == 0)
        {
            return "No categories available.";
        }

        var response = "Available service categories:\n\n";
        foreach (var category in categories)
        {
            response += $"- **{category.DisplayName}** ({category.DocumentCount} documents)\n";
        }

        return response;
    }

    [KernelFunction("get_category_documents")]
    [Description("Get all documents in a specific category")]
    public async Task<string> GetCategoryDocumentsAsync(
        [Description("The category name (e.g., Transportation, Housing)")] string categoryName)
    {
        var category = await _searchService.GetCategoryByNameAsync(categoryName);

        if (category == null)
        {
            return $"Category '{categoryName}' not found.";
        }

        var response = $"**{category.DisplayName}** - {category.DocumentCount} documents\n\n";
        foreach (var doc in category.Documents.Take(10))
        {
            response += $"- {doc.Title}\n";
        }

        if (category.Documents.Count > 10)
        {
            response += $"\n...and {category.Documents.Count - 10} more documents.";
        }

        return response;
    }

    [KernelFunction("get_recent_updates")]
    [Description("Get recently updated documents")]
    public async Task<string> GetRecentUpdatesAsync(
        [Description("Number of days to look back (default 30)")] int days = 30,
        [Description("Maximum number of documents to return (default 5)")] int top = 5)
    {
        var documents = await _searchService.GetRecentDocumentsAsync(days, top);

        if (documents.Count == 0)
        {
            return $"No documents updated in the last {days} days.";
        }

        var response = $"Recently updated documents (last {days} days):\n\n";
        foreach (var doc in documents)
        {
            response += $"- **{doc.Title}** (Updated: {doc.LastUpdated:yyyy-MM-dd})\n";
        }

        return response;
    }

    [KernelFunction("keyword_search")]
    [Description("Search for documents using keyword matching (useful for specific terms)")]
    public async Task<string> KeywordSearchAsync(
        [Description("Keywords to search for")] string keywords,
        [Description("Number of results to return (default 5)")] int top = 5)
    {
        var results = await _searchService.KeywordSearchAsync(keywords, top);

        if (results.Results.Count == 0)
        {
            return "No documents found matching those keywords.";
        }

        var response = $"Found {results.TotalCount} documents matching '{keywords}':\n\n";
        foreach (var result in results.Results)
        {
            response += $"- **{result.Document.Title}** ({result.Document.Category})\n";
        }

        return response;
    }
}
