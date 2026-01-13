namespace VirtualCitizenAgent.Models;

/// <summary>
/// Search mode for document queries.
/// </summary>
public enum SearchMode
{
    /// <summary>Traditional keyword-based search using TF-IDF.</summary>
    Keyword,

    /// <summary>AI-powered semantic/vector search.</summary>
    Semantic,

    /// <summary>Combined keyword and semantic search.</summary>
    Hybrid
}
