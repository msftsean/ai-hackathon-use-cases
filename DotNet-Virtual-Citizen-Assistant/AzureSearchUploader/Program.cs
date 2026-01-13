using Azure;
using Azure.Search.Documents;
using AzureSearchUploader.Services;
using Microsoft.Extensions.Configuration;

Console.WriteLine("===========================================");
Console.WriteLine("  NYC Citizen Services - Document Uploader");
Console.WriteLine("===========================================");
Console.WriteLine();

// Load configuration
var config = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false)
    .AddEnvironmentVariables()
    .Build();

var endpoint = config["SearchConfiguration:Endpoint"];
var apiKey = config["SearchConfiguration:ApiKey"];
var indexName = config["SearchConfiguration:IndexName"] ?? "citizen-services";

if (string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(apiKey))
{
    Console.WriteLine("ERROR: Azure AI Search configuration is missing.");
    Console.WriteLine("Please set SearchConfiguration:Endpoint and SearchConfiguration:ApiKey in appsettings.json");
    Console.WriteLine();
    Console.WriteLine("For demo mode without Azure, the sample data is shown below:");
    await ShowSampleDataAsync();
    return 1;
}

// Initialize search client
var searchClient = new SearchClient(new Uri(endpoint), indexName, new AzureKeyCredential(apiKey));
var uploadService = new DocumentUploadService(searchClient);

// Find data files
var dataPath = Path.Combine(Directory.GetCurrentDirectory(), "Data");
if (!Directory.Exists(dataPath))
{
    Console.WriteLine($"Data directory not found: {dataPath}");
    Console.WriteLine("Creating sample data...");
    await CreateSampleDataAsync(dataPath);
}

var jsonFiles = Directory.GetFiles(dataPath, "*.json");
if (jsonFiles.Length == 0)
{
    Console.WriteLine("No JSON files found in Data directory.");
    Console.WriteLine("Creating sample data...");
    await CreateSampleDataAsync(dataPath);
    jsonFiles = Directory.GetFiles(dataPath, "*.json");
}

Console.WriteLine($"Found {jsonFiles.Length} data file(s):");
foreach (var file in jsonFiles)
{
    Console.WriteLine($"  - {Path.GetFileName(file)}");
}
Console.WriteLine();

// Process each file
var totalResult = new AzureSearchUploader.Models.UploadResult();

foreach (var file in jsonFiles)
{
    Console.WriteLine($"Processing: {Path.GetFileName(file)}");

    try
    {
        var documents = await uploadService.LoadDocumentsFromFileAsync(file);
        Console.WriteLine($"  Loaded {documents.Count} documents");

        var result = await uploadService.UploadDocumentsAsync(documents);

        totalResult.TotalDocuments += result.TotalDocuments;
        totalResult.SuccessCount += result.SuccessCount;
        totalResult.FailedCount += result.FailedCount;
        totalResult.Errors.AddRange(result.Errors);
        totalResult.DurationMs += result.DurationMs;

        Console.WriteLine($"  Uploaded: {result.SuccessCount} success, {result.FailedCount} failed");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"  ERROR: {ex.Message}");
    }

    Console.WriteLine();
}

// Summary
Console.WriteLine("===========================================");
Console.WriteLine("               UPLOAD SUMMARY              ");
Console.WriteLine("===========================================");
Console.WriteLine($"Total documents: {totalResult.TotalDocuments}");
Console.WriteLine($"Successful:      {totalResult.SuccessCount}");
Console.WriteLine($"Failed:          {totalResult.FailedCount}");
Console.WriteLine($"Duration:        {totalResult.DurationMs}ms");

if (totalResult.Errors.Count > 0)
{
    Console.WriteLine();
    Console.WriteLine("Errors:");
    foreach (var error in totalResult.Errors.Take(10))
    {
        Console.WriteLine($"  - {error.DocumentId}: {error.ErrorMessage}");
    }
    if (totalResult.Errors.Count > 10)
    {
        Console.WriteLine($"  ... and {totalResult.Errors.Count - 10} more errors");
    }
}

return totalResult.FailedCount > 0 ? 1 : 0;

static async Task ShowSampleDataAsync()
{
    Console.WriteLine();
    Console.WriteLine("Sample document structure:");
    Console.WriteLine(@"[
  {
    ""id"": ""doc-001"",
    ""title"": ""How to Get a Parking Permit"",
    ""content"": ""Full document content..."",
    ""summary"": ""Guide to NYC parking permits"",
    ""category"": ""Transportation"",
    ""tags"": [""parking"", ""permit""],
    ""url"": ""https://www.nyc.gov/parking-permit""
  }
]");
    await Task.CompletedTask;
}

static async Task CreateSampleDataAsync(string dataPath)
{
    Directory.CreateDirectory(dataPath);

    var transportationData = @"[
  {
    ""id"": ""trans-001"",
    ""title"": ""How to Get a Parking Permit"",
    ""content"": ""To obtain a parking permit in NYC, you need to provide proof of residency, vehicle registration, and a valid driver's license. Visit your local DMV office or apply online at nyc.gov/parking. Permits are valid for one year and must be renewed annually. Different permit types are available for residential, commercial, and disability parking."",
    ""summary"": ""Guide to obtaining NYC parking permits"",
    ""category"": ""Transportation"",
    ""subCategory"": ""Parking"",
    ""tags"": [""parking"", ""permit"", ""DMV"", ""vehicle""],
    ""url"": ""https://www.nyc.gov/parking-permit""
  },
  {
    ""id"": ""trans-002"",
    ""title"": ""Subway and Bus Fare Information"",
    ""content"": ""The MTA operates NYC's subway and bus system. A single ride costs $2.90 with OMNY or MetroCard. Weekly unlimited passes cost $34 and monthly passes cost $132. Reduced fare is available for seniors (65+), people with disabilities, and eligible Medicare recipients. OMNY contactless payment is accepted on all buses and subways."",
    ""summary"": ""NYC transit fares and passes"",
    ""category"": ""Transportation"",
    ""subCategory"": ""Public Transit"",
    ""tags"": [""subway"", ""bus"", ""MTA"", ""fare"", ""MetroCard"", ""OMNY""],
    ""url"": ""https://new.mta.info/fares""
  }
]";

    var businessData = @"[
  {
    ""id"": ""biz-001"",
    ""title"": ""Business License Application Process"",
    ""content"": ""Starting a business in NYC requires obtaining the appropriate licenses and permits. The type of license depends on your business activity. Common licenses include General Vendor License, Food Service Establishment Permit, and Home Occupation Permit. Apply through NYC Business Express portal. Processing times vary by license type."",
    ""summary"": ""Step-by-step guide to business licensing"",
    ""category"": ""Business"",
    ""subCategory"": ""Licensing"",
    ""tags"": [""business"", ""license"", ""permit"", ""startup""],
    ""url"": ""https://www.nyc.gov/business-license""
  }
]";

    var housingData = @"[
  {
    ""id"": ""housing-001"",
    ""title"": ""Affordable Housing Programs"",
    ""content"": ""NYC offers several affordable housing programs including Section 8 vouchers, NYC Housing Connect lottery, and Mitchell-Lama housing. Eligibility is based on household income and size. Apply through Housing Connect at housingconnect.nyc.gov. Income limits vary by program and apartment size."",
    ""summary"": ""Overview of affordable housing options"",
    ""category"": ""Housing"",
    ""subCategory"": ""Affordable Housing"",
    ""tags"": [""housing"", ""affordable"", ""section 8"", ""lottery""],
    ""url"": ""https://www.nyc.gov/affordable-housing""
  },
  {
    ""id"": ""housing-002"",
    ""title"": ""Building Permit Requirements"",
    ""content"": ""Most construction work in NYC requires a permit from the Department of Buildings. This includes alterations, new construction, and demolition. Permits ensure work meets NYC Building Code. Apply through DOB NOW or visit a Borough Office. Some minor work may be exempt from permits."",
    ""summary"": ""When and how to get building permits"",
    ""category"": ""Housing"",
    ""subCategory"": ""Construction"",
    ""tags"": [""building"", ""permit"", ""construction"", ""DOB""],
    ""url"": ""https://www.nyc.gov/buildings""
  }
]";

    var healthData = @"[
  {
    ""id"": ""health-001"",
    ""title"": ""Health Insurance Enrollment"",
    ""content"": ""New Yorkers can enroll in health insurance through NY State of Health marketplace. Enrollment periods typically run November through January. Medicaid and Child Health Plus have year-round enrollment. Financial assistance is available based on income. Free in-person assistance is available at enrollment centers."",
    ""summary"": ""Health insurance options and enrollment info"",
    ""category"": ""Health"",
    ""subCategory"": ""Insurance"",
    ""tags"": [""health"", ""insurance"", ""medicaid"", ""enrollment""],
    ""url"": ""https://nystateofhealth.ny.gov""
  }
]";

    var educationData = @"[
  {
    ""id"": ""edu-001"",
    ""title"": ""Public School Enrollment"",
    ""content"": ""NYC public school enrollment varies by grade level. Pre-K and Kindergarten have specific application periods through MySchools.nyc. Middle and high school applications also go through MySchools. Zoned schools accept students based on residence. Charter schools have separate application processes."",
    ""summary"": ""Guide to enrolling in NYC public schools"",
    ""category"": ""Education"",
    ""subCategory"": ""K-12"",
    ""tags"": [""school"", ""enrollment"", ""education"", ""MySchools""],
    ""url"": ""https://www.schools.nyc.gov/enrollment""
  }
]";

    await File.WriteAllTextAsync(Path.Combine(dataPath, "transportation.json"), transportationData);
    await File.WriteAllTextAsync(Path.Combine(dataPath, "business.json"), businessData);
    await File.WriteAllTextAsync(Path.Combine(dataPath, "housing.json"), housingData);
    await File.WriteAllTextAsync(Path.Combine(dataPath, "health.json"), healthData);
    await File.WriteAllTextAsync(Path.Combine(dataPath, "education.json"), educationData);

    Console.WriteLine("Sample data files created.");
}
