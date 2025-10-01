using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Azure.Search.Documents;
using Azure.Identity;
using Azure;
using VirtualCitizenAgent.Services;
using VirtualCitizenAgent.Plugins;
using VirtualCitizenAgent.Models;

namespace VirtualCitizenAgent;

class Program
{
    static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        // Add services to the container
        ConfigureServices(builder.Services, builder.Configuration);

        var app = builder.Build();

        // Configure the HTTP request pipeline
        ConfigureApp(app);

        app.Run();
    }

    private static void ConfigureServices(IServiceCollection services, IConfiguration configuration)
    {
        // Add MVC services
        services.AddControllersWithViews();
        
        // Add CORS for API access
        services.AddCors(options =>
        {
            options.AddDefaultPolicy(builder =>
            {
                builder.AllowAnyOrigin()
                       .AllowAnyMethod()
                       .AllowAnyHeader();
            });
        });

        // Register Azure Search Client
        services.AddSingleton(provider =>
        {
            var config = provider.GetRequiredService<IConfiguration>();
            var endpoint = config["AzureSearch:Endpoint"];
            var indexName = config["AzureSearch:IndexName"];
            var apiKey = config["AzureSearch:ApiKey"];
            
            var useManagedIdentity = config.GetValue<bool>("AzureSearch:UseManagedIdentity", false);

            if (string.IsNullOrEmpty(endpoint))
                throw new InvalidOperationException("AzureSearch:Endpoint is required in configuration");

            // Use API Key authentication if available, otherwise fall back to managed identity
            if (!useManagedIdentity && !string.IsNullOrEmpty(apiKey))
            {
                var credential = new AzureKeyCredential(apiKey);
                return new SearchClient(new Uri(endpoint), indexName ?? "documents", credential);
            }
            else
            {
                // Use DefaultAzureCredential for managed identity or Azure CLI authentication
                var credential = new DefaultAzureCredential();
                return new SearchClient(new Uri(endpoint), indexName ?? "documents", credential);
            }
        });

        // Register document search service
        services.AddScoped<IDocumentSearchService, AzureAIDocumentSearchService>();

        // Register plugins first
        services.AddScoped<DocumentSearchPlugin>();

       
        services.AddScoped<Kernel>(provider =>
        {
            var kernelBuilder = Kernel.CreateBuilder();

            var config = provider.GetRequiredService<IConfiguration>();
            var deploymentName = config["OpenAI:DeploymentName"]!;
            var endpoint = config["OpenAI:Endpoint"]!;
            var apiKeyOpenAI = config["OpenAI:ApiKey"]!;

            kernelBuilder.Services.AddAzureOpenAIChatCompletion(
                    deploymentName: deploymentName,
                    endpoint: endpoint,
                    apiKey: apiKeyOpenAI);
            
            // Add logging
            kernelBuilder.Services.AddLogging(builder => builder.AddConsole().SetMinimumLevel(LogLevel.Debug));
            
            // Build the kernel first
            var kernel = kernelBuilder.Build();
            
            // Get the plugin instance from DI and add it manually
            var plugin = provider.GetRequiredService<DocumentSearchPlugin>();
            var pluginFunctions = kernel.ImportPluginFromObject(plugin, "DocumentSearch");
            

            

            var logger = provider.GetRequiredService<ILogger<Program>>();
            logger.LogInformation("🔌 DocumentSearch plugin registered with {FunctionCount} functions", pluginFunctions.Count());
            
            // List all registered functions for debugging
            foreach (var func in pluginFunctions)
            {
                logger.LogInformation("  ✅ Function: {FunctionName}", func.Name);
            }
            
            return kernel;
        });
    }

    private static void ConfigureApp(WebApplication app)
    {
        // Configure the HTTP request pipeline
        if (!app.Environment.IsDevelopment())
        {
            app.UseExceptionHandler("/Home/Error");
            app.UseHsts();
        }

        app.UseHttpsRedirection();
        app.UseStaticFiles();

        app.UseRouting();
        app.UseCors();

        app.MapControllerRoute(
            name: "default",
            pattern: "{controller=Home}/{action=Index}/{id?}");



        var logger = app.Services.GetRequiredService<ILogger<Program>>();
        logger.LogInformation("🏙️ NYC Virtual Citizen Agent web application started!");
    }
}
