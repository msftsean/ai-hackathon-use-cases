using Microsoft.AspNetCore.Mvc;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Services;

namespace VirtualCitizenAgent.Controllers;

/// <summary>
/// Categories API controller.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class CategoriesController : ControllerBase
{
    private readonly ICategoryService _categoryService;
    private readonly ILogger<CategoriesController> _logger;

    public CategoriesController(ICategoryService categoryService, ILogger<CategoriesController> logger)
    {
        _categoryService = categoryService;
        _logger = logger;
    }

    /// <summary>
    /// Get all service categories.
    /// </summary>
    [HttpGet]
    [ProducesResponseType(typeof(List<ServiceCategory>), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetCategories(CancellationToken cancellationToken)
    {
        var categories = await _categoryService.GetAllCategoriesAsync(cancellationToken);
        return Ok(categories);
    }

    /// <summary>
    /// Get category details by name.
    /// </summary>
    [HttpGet("{categoryName}")]
    [ProducesResponseType(typeof(CategoryDetail), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetCategory(string categoryName, CancellationToken cancellationToken)
    {
        var category = await _categoryService.GetCategoryByNameAsync(categoryName, cancellationToken);

        if (category == null)
        {
            return NotFound(new Error
            {
                Code = "CATEGORY_NOT_FOUND",
                Message = $"Category '{categoryName}' not found"
            });
        }

        return Ok(category);
    }
}

/// <summary>
/// MVC controller for categories views.
/// </summary>
public class CategoriesViewController : Controller
{
    private readonly ICategoryService _categoryService;

    public CategoriesViewController(ICategoryService categoryService)
    {
        _categoryService = categoryService;
    }

    public async Task<IActionResult> Index()
    {
        var categories = await _categoryService.GetAllCategoriesAsync();
        return View("~/Views/Categories/Index.cshtml", categories);
    }

    public async Task<IActionResult> Details(string id)
    {
        var category = await _categoryService.GetCategoryByNameAsync(id);

        if (category == null)
        {
            return NotFound();
        }

        return View("~/Views/Categories/Details.cshtml", category);
    }
}
