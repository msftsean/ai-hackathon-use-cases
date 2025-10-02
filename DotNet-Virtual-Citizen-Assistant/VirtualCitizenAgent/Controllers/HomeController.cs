using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using VirtualCitizenAgent.Models;
using System.Diagnostics;

namespace VirtualCitizenAgent.Controllers;

public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;

    public HomeController(ILogger<HomeController> logger)
    {
        _logger = logger;
    }

    public IActionResult Index()
    {
        ViewData["Title"] = "NYC Virtual Citizen Agent";
        ViewData["CityName"] = "New York City";
        ViewData["BrandColor"] = "#1f5582"; // NYC Blue
        ViewData["AccentColor"] = "#ffc72c"; // NYC Yellow
        
        return View();
    }

    public IActionResult Search()
    {
        ViewData["Title"] = "Search NYC Services";
        ViewData["CityName"] = "New York City";
        ViewData["BrandColor"] = "#1f5582";
        ViewData["AccentColor"] = "#ffc72c";
        
        return View();
    }

    public IActionResult About()
    {
        ViewData["Title"] = "About NYC Virtual Citizen Agent";
        ViewData["CityName"] = "New York City";
        ViewData["BrandColor"] = "#1f5582";
        ViewData["AccentColor"] = "#ffc72c";
        
        return View();
    }

    public IActionResult Categories()
    {
        ViewData["Title"] = "Service Categories";
        ViewData["CityName"] = "New York City";
        ViewData["BrandColor"] = "#1f5582";
        ViewData["AccentColor"] = "#ffc72c";
        
        return View();
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}