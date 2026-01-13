using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent.Services;

/// <summary>
/// Interface for category management operations.
/// </summary>
public interface ICategoryService
{
    /// <summary>
    /// Get all categories with document counts.
    /// </summary>
    Task<List<ServiceCategory>> GetAllCategoriesAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get category details including documents.
    /// </summary>
    Task<CategoryDetail?> GetCategoryByNameAsync(string categoryName, CancellationToken cancellationToken = default);
}
