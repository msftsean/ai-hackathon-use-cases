using System.Diagnostics;
using System.Text.Json;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using AzureSearchUploader.Models;
using Polly;
using Polly.Retry;

namespace AzureSearchUploader.Services;

/// <summary>
/// Service for uploading documents to Azure AI Search with retry logic.
/// </summary>
public class DocumentUploadService : IDocumentUploadService
{
    private readonly SearchClient _searchClient;
    private readonly AsyncRetryPolicy _retryPolicy;
    private const int BatchSize = 100;

    public DocumentUploadService(SearchClient searchClient)
    {
        _searchClient = searchClient;

        // Configure retry policy with exponential backoff
        _retryPolicy = Policy
            .Handle<RequestFailedException>(ex => ex.Status == 429 || ex.Status >= 500)
            .WaitAndRetryAsync(
                retryCount: 3,
                sleepDurationProvider: attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)),
                onRetry: (exception, timeSpan, retryCount, context) =>
                {
                    Console.WriteLine($"Retry {retryCount} after {timeSpan.TotalSeconds}s due to: {exception.Message}");
                });
    }

    public async Task<UploadResult> UploadDocumentsAsync(IEnumerable<UploadDocument> documents, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();
        var result = new UploadResult();
        var documentList = documents.ToList();
        result.TotalDocuments = documentList.Count;

        Console.WriteLine($"Uploading {result.TotalDocuments} documents...");

        // Process in batches
        var batches = documentList
            .Select((doc, index) => new { doc, index })
            .GroupBy(x => x.index / BatchSize)
            .Select(g => g.Select(x => x.doc).ToList())
            .ToList();

        foreach (var batch in batches)
        {
            try
            {
                // Validate documents before upload
                var validDocuments = batch.Where(ValidateDocument).ToList();
                var invalidCount = batch.Count - validDocuments.Count;

                if (invalidCount > 0)
                {
                    Console.WriteLine($"Skipped {invalidCount} invalid documents in batch");
                    result.FailedCount += invalidCount;
                }

                if (validDocuments.Count == 0) continue;

                // Convert to search documents
                var searchDocuments = validDocuments.Select(ConvertToSearchDocument).ToList();

                // Upload with retry
                await _retryPolicy.ExecuteAsync(async () =>
                {
                    var response = await _searchClient.MergeOrUploadDocumentsAsync(searchDocuments, cancellationToken: cancellationToken);

                    foreach (var indexResult in response.Value.Results)
                    {
                        if (indexResult.Succeeded)
                        {
                            result.SuccessCount++;
                        }
                        else
                        {
                            result.FailedCount++;
                            result.Errors.Add(new UploadError
                            {
                                DocumentId = indexResult.Key,
                                ErrorMessage = indexResult.ErrorMessage ?? "Unknown error",
                                StatusCode = indexResult.Status
                            });
                        }
                    }
                });

                Console.WriteLine($"Processed batch: {result.SuccessCount}/{result.TotalDocuments} successful");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Batch upload failed: {ex.Message}");
                result.FailedCount += batch.Count;
                foreach (var doc in batch)
                {
                    result.Errors.Add(new UploadError
                    {
                        DocumentId = doc.Id,
                        ErrorMessage = ex.Message
                    });
                }
            }
        }

        stopwatch.Stop();
        result.DurationMs = stopwatch.ElapsedMilliseconds;

        return result;
    }

    public async Task<List<UploadDocument>> LoadDocumentsFromFileAsync(string filePath, CancellationToken cancellationToken = default)
    {
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException($"Document file not found: {filePath}");
        }

        var json = await File.ReadAllTextAsync(filePath, cancellationToken);

        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        // Try parsing as array or as object with documents property
        try
        {
            var documents = JsonSerializer.Deserialize<List<UploadDocument>>(json, options);
            return documents ?? [];
        }
        catch
        {
            var wrapper = JsonSerializer.Deserialize<DocumentWrapper>(json, options);
            return wrapper?.Documents ?? [];
        }
    }

    private static bool ValidateDocument(UploadDocument doc)
    {
        if (string.IsNullOrWhiteSpace(doc.Id))
        {
            Console.WriteLine("Validation failed: Missing document ID");
            return false;
        }

        if (string.IsNullOrWhiteSpace(doc.Title))
        {
            Console.WriteLine($"Validation failed: Missing title for document {doc.Id}");
            return false;
        }

        if (string.IsNullOrWhiteSpace(doc.Content))
        {
            Console.WriteLine($"Validation failed: Missing content for document {doc.Id}");
            return false;
        }

        if (string.IsNullOrWhiteSpace(doc.Category))
        {
            Console.WriteLine($"Validation failed: Missing category for document {doc.Id}");
            return false;
        }

        return true;
    }

    private static SearchDocument ConvertToSearchDocument(UploadDocument doc)
    {
        var searchDoc = new SearchDocument
        {
            ["id"] = doc.Id,
            ["title"] = doc.Title,
            ["content"] = doc.Content,
            ["category"] = doc.Category
        };

        if (!string.IsNullOrEmpty(doc.Summary))
            searchDoc["summary"] = doc.Summary;

        if (!string.IsNullOrEmpty(doc.SubCategory))
            searchDoc["subCategory"] = doc.SubCategory;

        if (doc.Tags != null && doc.Tags.Count > 0)
            searchDoc["tags"] = doc.Tags;

        if (!string.IsNullOrEmpty(doc.Url))
            searchDoc["url"] = doc.Url;

        if (!string.IsNullOrEmpty(doc.LastUpdated) && DateTimeOffset.TryParse(doc.LastUpdated, out var date))
            searchDoc["lastUpdated"] = date;
        else
            searchDoc["lastUpdated"] = DateTimeOffset.UtcNow;

        return searchDoc;
    }

    private class DocumentWrapper
    {
        public List<UploadDocument> Documents { get; set; } = [];
    }
}
