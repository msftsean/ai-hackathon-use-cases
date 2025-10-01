namespace VirtualCitizenAgent.Models;

/// <summary>
/// Represents a document returned from search operations
/// </summary>
public class SearchResultDocument
{
    /// <summary>
    /// Unique identifier for the document
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Document title
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Full content of the document
    /// </summary>
    public string Content { get; set; } = string.Empty;

    /// <summary>
    /// Type of service this document relates to
    /// </summary>
    public string ServiceType { get; set; } = string.Empty;

    /// <summary>
    /// Category classification for the document
    /// </summary>
    public string Category { get; set; } = string.Empty;

    /// <summary>
    /// When the document was last updated
    /// </summary>
    public DateTimeOffset LastUpdated { get; set; }

    /// <summary>
    /// Search relevance score (0.0 to 1.0)
    /// </summary>
    public double RelevanceScore { get; set; }

    /// <summary>
    /// Semantic search score for natural language queries (0.0 to 1.0)
    /// </summary>
    public double SemanticScore { get; set; }

    /// <summary>
    /// Highlighted snippets from search matches
    /// </summary>
    public IList<string> Highlights { get; set; } = new List<string>();

    /// <summary>
    /// Additional metadata about the document
    /// </summary>
    public IDictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
}