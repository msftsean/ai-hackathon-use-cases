using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using AzureSearchUploader.Models;
using AzureSearchUploader.Services;

namespace AzureSearchUploader;

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("🔍 Azure AI Search Uploader - Service Documents");
        Console.WriteLine("===============================================");

        // Build configuration
        var configuration = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
            .AddEnvironmentVariables()
            .AddCommandLine(args)
            .Build();

        // Build host with dependency injection
        var host = Host.CreateDefaultBuilder(args)
            .ConfigureServices((context, services) =>
            {
                // Configure options
                services.Configure<SearchConfiguration>(configuration.GetSection("SearchConfiguration"));
                
                // Register services
                services.AddSingleton<AzureSearchService>();
                services.AddSingleton<JsonDataLoader>();
                
                // Configure logging
                services.AddLogging(builder =>
                {
                    builder.AddConsole();
                    builder.AddConfiguration(configuration.GetSection("Logging"));
                });
            })
            .UseConsoleLifetime()
            .Build();

        try
        {
            // Get services from DI container
            var logger = host.Services.GetRequiredService<ILogger<Program>>();
            var searchService = host.Services.GetRequiredService<AzureSearchService>();
            var dataLoader = host.Services.GetRequiredService<JsonDataLoader>();
            var searchConfig = configuration.GetSection("SearchConfiguration").Get<SearchConfiguration>();

            logger.LogInformation("Starting Azure AI Search data upload process");
            logger.LogInformation("Target Index: {IndexName} at {Endpoint}", 
                searchConfig?.IndexName, searchConfig?.ServiceEndpoint);

            // Step 1: Ensure the search index exists
            Console.WriteLine("\n📋 Step 1: Ensuring search index exists...");
            var indexCreated = await searchService.EnsureIndexExistsAsync();
            if (!indexCreated)
            {
                Console.WriteLine("❌ Failed to create or verify search index. Exiting.");
                return;
            }
            Console.WriteLine("✅ Search index verified successfully");

            // Step 2: Check if we should clear the index
            var clearIndex = configuration.GetValue<bool>("DataConfiguration:ClearIndexBeforeUpload", false);
            if (clearIndex)
            {
                Console.WriteLine("\n🗑️ Step 2: Clearing existing documents from index...");
                var cleared = await searchService.ClearIndexAsync();
                if (cleared)
                {
                    Console.WriteLine("✅ Index cleared successfully");
                }
                else
                {
                    Console.WriteLine("⚠️ Failed to clear index, continuing anyway...");
                }
            }

            // Step 3: Load data from JSON file
            Console.WriteLine("\n📂 Step 3: Loading data from JSON file...");
            var inputFilePath = configuration.GetValue<string>("DataConfiguration:InputFilePath", "./Data/services.json");
            
            if (!File.Exists(inputFilePath))
            {
                Console.WriteLine($"❌ Input file not found: {inputFilePath}");
                Console.WriteLine("Please create a JSON file with your service documents or specify a different path.");
                Console.WriteLine("\nExample JSON format:");
                Console.WriteLine(GetExampleJsonFormat());
                return;
            }

            var documents = await dataLoader.LoadFromFileAsync(inputFilePath);
            var documentList = documents.ToList();

            if (!documentList.Any())
            {
                Console.WriteLine("❌ No documents found in the input file.");
                return;
            }

            Console.WriteLine($"✅ Loaded {documentList.Count} documents from {inputFilePath}");

            // Step 4: Validate documents
            Console.WriteLine("\n✅ Step 4: Validating documents...");
            var validDocuments = dataLoader.ValidateDocuments(documentList).ToList();
            
            if (!validDocuments.Any())
            {
                Console.WriteLine("❌ No valid documents found after validation.");
                return;
            }

            Console.WriteLine($"✅ {validDocuments.Count} documents passed validation");

            // Step 5: Upload documents to Azure AI Search
            Console.WriteLine("\n⬆️ Step 5: Uploading documents to Azure AI Search...");
            var uploadResult = await searchService.UploadDocumentsAsync(validDocuments);
            
            // Display results
            Console.WriteLine($"\n📈 Upload Results:");
            Console.WriteLine($"   ✅ Successfully uploaded: {uploadResult.SuccessCount} documents");
            Console.WriteLine($"   ❌ Failed uploads: {uploadResult.FailureCount} documents");
            Console.WriteLine($"   ⏱️ Duration: {uploadResult.Duration.TotalSeconds:F2} seconds");
            
            if (uploadResult.Errors.Any())
            {
                Console.WriteLine($"\n❗ Errors encountered:");
                foreach (var error in uploadResult.Errors.Take(5)) // Show first 5 errors
                {
                    Console.WriteLine($"   • {error}");
                }
                if (uploadResult.Errors.Count > 5)
                {
                    Console.WriteLine($"   ... and {uploadResult.Errors.Count - 5} more errors");
                }
            }

            // Step 6: Verify upload with document count
            Console.WriteLine("\n🔍 Step 6: Verifying upload...");
            var documentCount = await searchService.GetDocumentCountAsync();
            if (documentCount >= 0)
            {
                Console.WriteLine($"✅ Current document count in index: {documentCount}");
            }

            // Step 7: Test search functionality
            Console.WriteLine("\n🧪 Step 7: Testing search functionality...");
            var searchTest = await searchService.TestSearchAsync();
            if (searchTest)
            {
                Console.WriteLine("✅ Search functionality test passed");
            }
            else
            {
                Console.WriteLine("❌ Search functionality test failed");
            }

            // Summary
            Console.WriteLine("\n🎉 Upload process completed!");
            Console.WriteLine($"Your Azure AI Search index '{searchConfig?.IndexName}' has been updated with your service documents.");
            
            if (uploadResult.IsSuccess)
            {
                logger.LogInformation("Data upload completed successfully. {SuccessCount} documents uploaded", 
                    uploadResult.SuccessCount);
            }
            else
            {
                logger.LogWarning("Data upload completed with errors. Success: {SuccessCount}, Failures: {FailureCount}", 
                    uploadResult.SuccessCount, uploadResult.FailureCount);
            }
        }
        catch (Exception ex)
        {
            var logger = host.Services.GetRequiredService<ILogger<Program>>();
            logger.LogError(ex, "Fatal error during data upload process");
            
            Console.WriteLine($"\n💥 Fatal Error: {ex.Message}");
            Console.WriteLine("\nPlease check your configuration and try again.");
            Console.WriteLine("Common issues:");
            Console.WriteLine("• Verify your Azure AI Search service endpoint is correct");
            Console.WriteLine("• Ensure you have proper authentication (Managed Identity or API Key)");
            Console.WriteLine("• Check that your Azure AI Search service is running");
            Console.WriteLine("• Verify network connectivity to Azure");
            Console.WriteLine("• Make sure your JSON file exists and is properly formatted");
        }
        finally
        {
            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }

    private static string GetExampleJsonFormat()
    {
        return @"[
    {
        ""id"": ""1"",
        ""service_type"": ""waste_management"",
        ""title"": ""Trash Pickup Schedule"",
        ""content"": ""Trash pickup occurs twice weekly in Manhattan. Monday and Thursday for odd-numbered addresses, Tuesday and Friday for even-numbered addresses. Place bins curbside by 7 AM."",
        ""category"": ""sanitation"",
        ""last_updated"": ""2025-09-29T10:30:00Z""
    },
    {
        ""id"": ""2"",
        ""service_type"": ""transportation"",
        ""title"": ""Subway Service Updates"",
        ""content"": ""Current subway service alerts and updates for NYC transit system."",
        ""category"": ""transportation"",
        ""last_updated"": ""2025-09-29T10:30:00Z""
    }
]";
    }
}
