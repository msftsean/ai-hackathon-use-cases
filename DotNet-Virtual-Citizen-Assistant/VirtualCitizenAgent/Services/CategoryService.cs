using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Services;

/// <summary>
/// Category service implementation using search service for facet aggregation.
/// </summary>
public class CategoryService : ICategoryService
{
    private readonly ISearchService _searchService;
    private readonly ILogger<CategoryService> _logger;

    private static readonly Dictionary<string, (string DisplayName, string Description, string Icon)> CategoryMetadata = new()
    {
        ["transportation"] = ("Transportation", "Public transit, parking, vehicle registration, and traffic information", "fa-bus"),
        ["business"] = ("Business", "Business licenses, permits, regulations, and small business resources", "fa-briefcase"),
        ["housing"] = ("Housing", "Affordable housing, building permits, tenant rights, and property information", "fa-home"),
        ["education"] = ("Education", "Public schools, enrollment, adult education, and educational resources", "fa-graduation-cap"),
        ["health"] = ("Health", "Health insurance, clinics, mental health services, and public health information", "fa-heartbeat"),
        ["finance"] = ("Finance", "Taxes, benefits, financial assistance, and city payments", "fa-dollar-sign"),
        ["environment"] = ("Environment", "Parks, recycling, sustainability, and environmental programs", "fa-leaf"),
        ["safety"] = ("Public Safety", "Emergency services, police, fire department, and safety resources", "fa-shield-alt")
    };

    public CategoryService(ISearchService searchService, ILogger<CategoryService> logger)
    {
        _searchService = searchService;
        _logger = logger;
    }

    public async Task<List<ServiceCategory>> GetAllCategoriesAsync(CancellationToken cancellationToken = default)
    {
        var categories = await _searchService.GetCategoriesAsync(cancellationToken);

        // Enhance categories with metadata
        foreach (var category in categories)
        {
            var key = category.Name.ToLowerInvariant();
            if (CategoryMetadata.TryGetValue(key, out var metadata))
            {
                category.Description = metadata.Description;
                category.Icon = metadata.Icon;
            }
        }

        return categories;
    }

    public async Task<CategoryDetail?> GetCategoryByNameAsync(string categoryName, CancellationToken cancellationToken = default)
    {
        var categoryDetail = await _searchService.GetCategoryByNameAsync(categoryName, cancellationToken);

        if (categoryDetail != null)
        {
            var key = categoryDetail.Name.ToLowerInvariant();
            if (CategoryMetadata.TryGetValue(key, out var metadata))
            {
                categoryDetail.Description = metadata.Description;
                categoryDetail.Icon = metadata.Icon;
            }
        }

        return categoryDetail;
    }
}
