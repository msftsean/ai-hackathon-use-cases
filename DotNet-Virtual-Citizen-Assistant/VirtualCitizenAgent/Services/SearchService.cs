using System.Diagnostics;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Options;
using VirtualCitizenAgent.Configuration;
using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Services;

/// <summary>
/// Search service implementation using Azure AI Search.
/// </summary>
public class SearchService : ISearchService
{
    private readonly SearchClient? _searchClient;
    private readonly SearchConfiguration _config;
    private readonly ILogger<SearchService> _logger;
    private readonly bool _useMock;

    // Mock data for offline development
    private static readonly List<Document> MockDocuments =
    [
        new()
        {
            Id = "doc-001",
            Title = "How to Get a Parking Permit",
            Content = "To obtain a parking permit in NYC, you need to provide proof of residency, vehicle registration, and a valid driver's license. Visit your local DMV office or apply online at nyc.gov/parking. Permits are valid for one year and must be renewed annually.",
            Summary = "Guide to obtaining NYC parking permits",
            Category = "Transportation",
            SubCategory = "Parking",
            Tags = ["parking", "permit", "DMV", "vehicle"],
            Url = "https://www.nyc.gov/parking-permit",
            Status = DocumentStatus.Active
        },
        new()
        {
            Id = "doc-002",
            Title = "Business License Application Process",
            Content = "Starting a business in NYC requires obtaining the appropriate licenses and permits. The type of license depends on your business activity. Common licenses include General Vendor License, Food Service Establishment Permit, and Home Occupation Permit. Apply through NYC Business Express portal.",
            Summary = "Step-by-step guide to business licensing",
            Category = "Business",
            SubCategory = "Licensing",
            Tags = ["business", "license", "permit", "startup"],
            Url = "https://www.nyc.gov/business-license",
            Status = DocumentStatus.Active
        },
        new()
        {
            Id = "doc-003",
            Title = "Affordable Housing Programs",
            Content = "NYC offers several affordable housing programs including Section 8 vouchers, NYC Housing Connect lottery, and Mitchell-Lama housing. Eligibility is based on household income and size. Apply through Housing Connect at housingconnect.nyc.gov.",
            Summary = "Overview of affordable housing options",
            Category = "Housing",
            SubCategory = "Affordable Housing",
            Tags = ["housing", "affordable", "section 8", "lottery"],
            Url = "https://www.nyc.gov/affordable-housing",
            Status = DocumentStatus.Active
        },
        new()
        {
            Id = "doc-004",
            Title = "Public School Enrollment",
            Content = "NYC public school enrollment varies by grade level. Pre-K and Kindergarten have specific application periods through MySchools.nyc. Middle and high school applications also go through MySchools. Zoned schools accept students based on residence.",
            Summary = "Guide to enrolling in NYC public schools",
            Category = "Education",
            SubCategory = "K-12",
            Tags = ["school", "enrollment", "education", "MySchools"],
            Url = "https://www.schools.nyc.gov/enrollment",
            Status = DocumentStatus.Active
        },
        new()
        {
            Id = "doc-005",
            Title = "Health Insurance Enrollment",
            Content = "New Yorkers can enroll in health insurance through NY State of Health marketplace. Enrollment periods typically run November through January. Medicaid and Child Health Plus have year-round enrollment. Financial assistance is available based on income.",
            Summary = "Health insurance options and enrollment info",
            Category = "Health",
            SubCategory = "Insurance",
            Tags = ["health", "insurance", "medicaid", "enrollment"],
            Url = "https://nystateofhealth.ny.gov",
            Status = DocumentStatus.Active
        },
        new()
        {
            Id = "doc-006",
            Title = "Property Tax Payment Options",
            Content = "NYC property taxes can be paid online, by mail, or in person. The Department of Finance offers payment plans for those who qualify. Property tax bills are issued quarterly for most properties. Exemptions are available for seniors, veterans, and disabled individuals.",
            Summary = "How to pay NYC property taxes",
            Category = "Finance",
            SubCategory = "Taxes",
            Tags = ["property tax", "payment", "exemption", "finance"],
            Url = "https://www.nyc.gov/finance/property-tax",
            Status = DocumentStatus.Active
        },
        new()
        {
            Id = "doc-007",
            Title = "Subway and Bus Fare Information",
            Content = "The MTA operates NYC's subway and bus system. A single ride costs $2.90 with OMNY or MetroCard. Weekly unlimited passes cost $34 and monthly passes cost $132. Reduced fare is available for seniors, people with disabilities, and eligible Medicare recipients.",
            Summary = "NYC transit fares and passes",
            Category = "Transportation",
            SubCategory = "Public Transit",
            Tags = ["subway", "bus", "MTA", "fare", "MetroCard", "OMNY"],
            Url = "https://new.mta.info/fares",
            Status = DocumentStatus.Active
        },
        new()
        {
            Id = "doc-008",
            Title = "Building Permit Requirements",
            Content = "Most construction work in NYC requires a permit from the Department of Buildings. This includes alterations, new construction, and demolition. Permits ensure work meets NYC Building Code. Apply through DOB NOW or visit a Borough Office.",
            Summary = "When and how to get building permits",
            Category = "Housing",
            SubCategory = "Construction",
            Tags = ["building", "permit", "construction", "DOB"],
            Url = "https://www.nyc.gov/buildings",
            Status = DocumentStatus.Active
        }
    ];

    public SearchService(IOptions<SearchConfiguration> config, ILogger<SearchService> logger)
    {
        _config = config.Value;
        _logger = logger;
        _useMock = _config.UseMockService || string.IsNullOrEmpty(_config.Endpoint);

        if (!_useMock)
        {
            var credential = new AzureKeyCredential(_config.ApiKey);
            _searchClient = new SearchClient(new Uri(_config.Endpoint), _config.IndexName, credential);
        }
    }

    public async Task<SearchResponse> SearchAsync(SearchQuery query, CancellationToken cancellationToken = default)
    {
        return query.Mode switch
        {
            Models.SearchMode.Keyword => await KeywordSearchAsync(query.Query, query.Top, query.Category, cancellationToken),
            Models.SearchMode.Semantic => await SemanticSearchAsync(query.Query, query.Top, query.Category, cancellationToken),
            Models.SearchMode.Hybrid => await HybridSearchAsync(query.Query, query.Top, query.Category, cancellationToken),
            _ => await SemanticSearchAsync(query.Query, query.Top, query.Category, cancellationToken)
        };
    }

    public async Task<SearchResponse> SemanticSearchAsync(string query, int top = 10, string? category = null, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        if (_useMock)
        {
            return await MockSearchAsync(query, top, category, stopwatch);
        }

        var options = new SearchOptions
        {
            Size = top,
            QueryType = SearchQueryType.Semantic,
            SemanticSearch = new SemanticSearchOptions
            {
                SemanticConfigurationName = _config.SemanticConfigurationName,
                QueryCaption = new QueryCaption(QueryCaptionType.Extractive),
                QueryAnswer = new QueryAnswer(QueryAnswerType.Extractive)
            },
            Select = { "id", "title", "content", "summary", "category", "subCategory", "tags", "url", "lastUpdated" }
        };

        if (!string.IsNullOrEmpty(category))
        {
            options.Filter = $"category eq '{category}'";
        }

        return await ExecuteSearchAsync(query, options, stopwatch, cancellationToken);
    }

    public async Task<SearchResponse> KeywordSearchAsync(string query, int top = 10, string? category = null, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        if (_useMock)
        {
            return await MockSearchAsync(query, top, category, stopwatch);
        }

        var options = new SearchOptions
        {
            Size = top,
            QueryType = SearchQueryType.Simple,
            Select = { "id", "title", "content", "summary", "category", "subCategory", "tags", "url", "lastUpdated" },
            HighlightFields = { "content", "title" }
        };

        if (!string.IsNullOrEmpty(category))
        {
            options.Filter = $"category eq '{category}'";
        }

        return await ExecuteSearchAsync(query, options, stopwatch, cancellationToken);
    }

    public async Task<SearchResponse> HybridSearchAsync(string query, int top = 10, string? category = null, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        if (_useMock)
        {
            return await MockSearchAsync(query, top, category, stopwatch);
        }

        var options = new SearchOptions
        {
            Size = top,
            QueryType = SearchQueryType.Semantic,
            SemanticSearch = new SemanticSearchOptions
            {
                SemanticConfigurationName = _config.SemanticConfigurationName,
                QueryCaption = new QueryCaption(QueryCaptionType.Extractive)
            },
            Select = { "id", "title", "content", "summary", "category", "subCategory", "tags", "url", "lastUpdated" },
            HighlightFields = { "content", "title" }
        };

        if (!string.IsNullOrEmpty(category))
        {
            options.Filter = $"category eq '{category}'";
        }

        return await ExecuteSearchAsync(query, options, stopwatch, cancellationToken);
    }

    public async Task<Document?> GetDocumentByIdAsync(string documentId, CancellationToken cancellationToken = default)
    {
        if (_useMock)
        {
            await Task.Delay(10, cancellationToken);
            return MockDocuments.FirstOrDefault(d => d.Id == documentId);
        }

        try
        {
            var response = await _searchClient!.GetDocumentAsync<Document>(documentId, cancellationToken: cancellationToken);
            return response.Value;
        }
        catch (RequestFailedException ex) when (ex.Status == 404)
        {
            return null;
        }
    }

    public async Task<List<Document>> GetRecentDocumentsAsync(int days = 30, int top = 10, CancellationToken cancellationToken = default)
    {
        if (_useMock)
        {
            await Task.Delay(10, cancellationToken);
            return MockDocuments
                .OrderByDescending(d => d.LastUpdated)
                .Take(top)
                .ToList();
        }

        var cutoffDate = DateTimeOffset.UtcNow.AddDays(-days);
        var options = new SearchOptions
        {
            Size = top,
            Filter = $"lastUpdated ge {cutoffDate:O}",
            OrderBy = { "lastUpdated desc" },
            Select = { "id", "title", "summary", "category", "url", "lastUpdated" }
        };

        var results = await _searchClient!.SearchAsync<Document>("*", options, cancellationToken);
        var documents = new List<Document>();

        await foreach (var result in results.Value.GetResultsAsync())
        {
            documents.Add(result.Document);
        }

        return documents;
    }

    public async Task<List<ServiceCategory>> GetCategoriesAsync(CancellationToken cancellationToken = default)
    {
        if (_useMock)
        {
            await Task.Delay(10, cancellationToken);
            return MockDocuments
                .GroupBy(d => d.Category)
                .Select(g => new ServiceCategory
                {
                    Name = g.Key.ToLowerInvariant().Replace(" ", "-"),
                    DisplayName = g.Key,
                    DocumentCount = g.Count(),
                    Icon = GetCategoryIcon(g.Key),
                    SubCategories = g.Where(d => d.SubCategory != null).Select(d => d.SubCategory!).Distinct().ToList()
                })
                .OrderBy(c => c.DisplayName)
                .ToList();
        }

        var options = new SearchOptions
        {
            Size = 0,
            Facets = { "category,count:100" }
        };

        var results = await _searchClient!.SearchAsync<Document>("*", options, cancellationToken);
        var categories = new List<ServiceCategory>();

        if (results.Value.Facets.TryGetValue("category", out var facets))
        {
            foreach (var facet in facets)
            {
                var name = facet.Value?.ToString() ?? "";
                categories.Add(new ServiceCategory
                {
                    Name = name.ToLowerInvariant().Replace(" ", "-"),
                    DisplayName = name,
                    DocumentCount = (int)(facet.Count ?? 0),
                    Icon = GetCategoryIcon(name)
                });
            }
        }

        return categories.OrderBy(c => c.DisplayName).ToList();
    }

    public async Task<CategoryDetail?> GetCategoryByNameAsync(string categoryName, CancellationToken cancellationToken = default)
    {
        if (_useMock)
        {
            await Task.Delay(10, cancellationToken);
            var docs = MockDocuments.Where(d =>
                d.Category.Equals(categoryName, StringComparison.OrdinalIgnoreCase) ||
                d.Category.ToLowerInvariant().Replace(" ", "-") == categoryName.ToLowerInvariant()
            ).ToList();

            if (docs.Count == 0) return null;

            return new CategoryDetail
            {
                Name = categoryName.ToLowerInvariant().Replace(" ", "-"),
                DisplayName = docs.First().Category,
                DocumentCount = docs.Count,
                Icon = GetCategoryIcon(docs.First().Category),
                Documents = docs,
                SubCategories = docs.Where(d => d.SubCategory != null).Select(d => d.SubCategory!).Distinct().ToList()
            };
        }

        var options = new SearchOptions
        {
            Size = 50,
            Filter = $"category eq '{categoryName}'",
            Select = { "id", "title", "summary", "category", "subCategory", "url", "lastUpdated" }
        };

        var results = await _searchClient!.SearchAsync<Document>("*", options, cancellationToken);
        var documents = new List<Document>();

        await foreach (var result in results.Value.GetResultsAsync())
        {
            documents.Add(result.Document);
        }

        if (documents.Count == 0) return null;

        return new CategoryDetail
        {
            Name = categoryName.ToLowerInvariant().Replace(" ", "-"),
            DisplayName = documents.First().Category,
            DocumentCount = documents.Count,
            Icon = GetCategoryIcon(documents.First().Category),
            Documents = documents,
            SubCategories = documents.Where(d => d.SubCategory != null).Select(d => d.SubCategory!).Distinct().ToList()
        };
    }

    private async Task<SearchResponse> ExecuteSearchAsync(string query, SearchOptions options, Stopwatch stopwatch, CancellationToken cancellationToken)
    {
        try
        {
            var searchResults = await _searchClient!.SearchAsync<Document>(query, options, cancellationToken);
            var results = new List<SearchResult>();

            await foreach (var result in searchResults.Value.GetResultsAsync())
            {
                var searchResult = new SearchResult
                {
                    Document = result.Document,
                    Score = result.Score ?? 0
                };

                if (result.Highlights != null && result.Highlights.Count > 0)
                {
                    searchResult.Highlights = result.Highlights.ToDictionary(
                        h => h.Key,
                        h => h.Value.ToList()
                    );
                }

                if (result.SemanticSearch?.Captions != null)
                {
                    searchResult.Captions = result.SemanticSearch.Captions
                        .Select(c => c.Text)
                        .Where(t => !string.IsNullOrEmpty(t))
                        .ToList()!;
                }

                results.Add(searchResult);
            }

            stopwatch.Stop();

            return new SearchResponse
            {
                Query = query,
                Results = results,
                TotalCount = searchResults.Value.TotalCount ?? results.Count,
                SearchTimeMs = (int)stopwatch.ElapsedMilliseconds
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Search failed for query: {Query}", query);
            throw;
        }
    }

    private async Task<SearchResponse> MockSearchAsync(string query, int top, string? category, Stopwatch stopwatch)
    {
        await Task.Delay(50); // Simulate network latency

        var queryLower = query.ToLowerInvariant();
        var results = MockDocuments
            .Where(d => category == null ||
                d.Category.Equals(category, StringComparison.OrdinalIgnoreCase) ||
                d.Category.ToLowerInvariant().Replace(" ", "-") == category.ToLowerInvariant())
            .Select(d => new
            {
                Document = d,
                Score = CalculateMockScore(d, queryLower)
            })
            .Where(r => r.Score > 0)
            .OrderByDescending(r => r.Score)
            .Take(top)
            .Select(r => new SearchResult
            {
                Document = r.Document,
                Score = r.Score,
                Captions = [GetMockCaption(r.Document, queryLower)]
            })
            .ToList();

        stopwatch.Stop();

        return new SearchResponse
        {
            Query = query,
            Results = results,
            TotalCount = results.Count,
            SearchTimeMs = (int)stopwatch.ElapsedMilliseconds,
            Facets = new Dictionary<string, List<FacetValue>>
            {
                ["category"] = MockDocuments
                    .GroupBy(d => d.Category)
                    .Select(g => new FacetValue { Value = g.Key, Count = g.Count() })
                    .ToList()
            }
        };
    }

    private static double CalculateMockScore(Document doc, string query)
    {
        var terms = query.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        double score = 0;

        foreach (var term in terms)
        {
            if (doc.Title.Contains(term, StringComparison.OrdinalIgnoreCase))
                score += 2.0;
            if (doc.Content.Contains(term, StringComparison.OrdinalIgnoreCase))
                score += 1.0;
            if (doc.Tags.Any(t => t.Contains(term, StringComparison.OrdinalIgnoreCase)))
                score += 1.5;
            if (doc.Category.Contains(term, StringComparison.OrdinalIgnoreCase))
                score += 0.5;
        }

        return score;
    }

    private static string GetMockCaption(Document doc, string query)
    {
        var content = doc.Content;
        var terms = query.Split(' ', StringSplitOptions.RemoveEmptyEntries);

        foreach (var term in terms)
        {
            var index = content.IndexOf(term, StringComparison.OrdinalIgnoreCase);
            if (index >= 0)
            {
                var start = Math.Max(0, index - 50);
                var end = Math.Min(content.Length, index + term.Length + 100);
                return "..." + content[start..end] + "...";
            }
        }

        return content.Length > 150 ? content[..150] + "..." : content;
    }

    private static string GetCategoryIcon(string category)
    {
        return category.ToLowerInvariant() switch
        {
            "transportation" => "fa-bus",
            "business" => "fa-briefcase",
            "housing" => "fa-home",
            "education" => "fa-graduation-cap",
            "health" => "fa-heartbeat",
            "finance" => "fa-dollar-sign",
            _ => "fa-file-alt"
        };
    }
}
