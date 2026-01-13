using Microsoft.AspNetCore.Mvc;

namespace VirtualCitizenAgent.Controllers;

/// <summary>
/// Health check endpoints for monitoring and load balancing.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class HealthController : ControllerBase
{
    private readonly ILogger<HealthController> _logger;

    public HealthController(ILogger<HealthController> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Basic health check endpoint.
    /// </summary>
    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new
        {
            status = "healthy",
            timestamp = DateTimeOffset.UtcNow,
            version = "1.0.0"
        });
    }

    /// <summary>
    /// Readiness check for Kubernetes/container orchestration.
    /// </summary>
    [HttpGet("ready")]
    public IActionResult Ready()
    {
        // Add actual readiness checks here (e.g., database connectivity)
        return Ok(new
        {
            status = "ready",
            timestamp = DateTimeOffset.UtcNow
        });
    }

    /// <summary>
    /// Liveness check for Kubernetes/container orchestration.
    /// </summary>
    [HttpGet("live")]
    public IActionResult Live()
    {
        return Ok(new
        {
            status = "live",
            timestamp = DateTimeOffset.UtcNow
        });
    }
}
