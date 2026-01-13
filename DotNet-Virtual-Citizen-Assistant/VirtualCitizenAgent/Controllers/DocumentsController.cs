using Microsoft.AspNetCore.Mvc;
using VirtualCitizenAgent.Models;
using VirtualCitizenAgent.Services;

namespace VirtualCitizenAgent.Controllers;

/// <summary>
/// MVC controller for document views.
/// </summary>
public class DocumentsController : Controller
{
    private readonly ISearchService _searchService;

    public DocumentsController(ISearchService searchService)
    {
        _searchService = searchService;
    }

    public async Task<IActionResult> Details(string id)
    {
        var document = await _searchService.GetDocumentByIdAsync(id);

        if (document == null)
        {
            return NotFound();
        }

        // Get related documents from the same category
        var relatedResults = await _searchService.SearchAsync(new SearchQuery
        {
            Query = document.Title,
            Category = document.Category,
            Top = 5
        });

        ViewBag.RelatedDocuments = relatedResults.Results
            .Where(r => r.Document.Id != id)
            .Take(4)
            .Select(r => r.Document)
            .ToList();

        return View(document);
    }
}
