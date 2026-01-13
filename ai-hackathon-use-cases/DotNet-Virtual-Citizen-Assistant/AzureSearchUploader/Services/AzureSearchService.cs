using Azure;
using Azure.Identity;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System.Diagnostics;
using AzureSearchUploader.Models;

namespace AzureSearchUploader.Services;

/// <summary>
/// Service for handling Azure AI Search operations for ServiceDocument uploads
/// </summary>
public class AzureSearchService
{
    private readonly SearchConfiguration _config;
    private readonly SearchIndexClient _indexClient;
    private readonly SearchClient _searchClient;
    private readonly ILogger<AzureSearchService> _logger;

    public AzureSearchService(IOptions<SearchConfiguration> config, ILogger<AzureSearchService> logger)
    {
        _config = config.Value;
        _logger = logger;

        // Initialize clients with appropriate authentication
        var serviceEndpoint = new Uri(_config.ServiceEndpoint);
        
        if (_config.UseManagedIdentity)
        {
            var credential = new DefaultAzureCredential();
            _indexClient = new SearchIndexClient(serviceEndpoint, credential);
            _searchClient = new SearchClient(serviceEndpoint, _config.IndexName, credential);
        }
        else
        {
            var apiKey = _config.ApiKey ?? throw new ArgumentException("API Key is required when not using managed identity");
            var keyCredential = new AzureKeyCredential(apiKey);
            _indexClient = new SearchIndexClient(serviceEndpoint, keyCredential);
            _searchClient = new SearchClient(serviceEndpoint, _config.IndexName, keyCredential);
        }

        _logger.LogInformation("Azure Search Service initialized with endpoint: {Endpoint}, Index: {Index}", 
            _config.ServiceEndpoint, _config.IndexName);
    }

    /// <summary>
    /// Creates or updates the search index with the proper schema for ServiceDocument
    /// </summary>
    public async Task<bool> EnsureIndexExistsAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Ensuring search index '{IndexName}' exists", _config.IndexName);

            // Create the index definition
            var index = new SearchIndex(_config.IndexName)
            {
                Fields = CreateIndexFields(),
                SemanticSearch = CreateSemanticSearchConfiguration()
            };

            // Create or update the index
            await _indexClient.CreateOrUpdateIndexAsync(index, cancellationToken: cancellationToken);
            
            _logger.LogInformation("Search index '{IndexName}' created or updated successfully", _config.IndexName);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create or update search index '{IndexName}'", _config.IndexName);
            return false;
        }
    }

    /// <summary>
    /// Uploads a batch of service documents to the search index
    /// </summary>
    public async Task<UploadResult> UploadDocumentsAsync(IEnumerable<ServiceDocument> documents, 
        CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();
        var result = new UploadResult();

        try
        {
            var documentList = documents.ToList();
            _logger.LogInformation("Starting upload of {Count} documents to index '{IndexName}'", 
                documentList.Count, _config.IndexName);

            // Process documents in batches
            var batches = CreateBatches(documentList, _config.BatchSize);
            
            foreach (var batch in batches)
            {
                await UploadBatchWithRetryAsync(batch, result, cancellationToken);
            }

            stopwatch.Stop();
            result.Duration = stopwatch.Elapsed;

            _logger.LogInformation("Upload completed. Success: {Success}, Failures: {Failures}, Duration: {Duration}ms",
                result.SuccessCount, result.FailureCount, result.Duration.TotalMilliseconds);

            return result;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            result.Duration = stopwatch.Elapsed;
            result.Errors.Add($"Unexpected error during upload: {ex.Message}");
            
            _logger.LogError(ex, "Unexpected error during document upload");
            return result;
        }
    }

    /// <summary>
    /// Uploads a single batch of documents with retry logic
    /// </summary>
    private async Task UploadBatchWithRetryAsync(IEnumerable<ServiceDocument> batch, UploadResult result, 
        CancellationToken cancellationToken)
    {
        var batchList = batch.ToList();
        var retryCount = 0;

        while (retryCount <= _config.MaxRetryAttempts)
        {
            try
            {
                var actions = batchList.Select(doc => IndexDocumentsAction.Upload(doc));
                var batchOperation = await _searchClient.IndexDocumentsAsync(
                    IndexDocumentsBatch.Create(actions.ToArray()), 
                    cancellationToken: cancellationToken);

                // Process results
                foreach (var indexResult in batchOperation.Value.Results)
                {
                    if (indexResult.Succeeded)
                    {
                        result.SuccessCount++;
                        _logger.LogDebug("Successfully uploaded document with ID: {DocumentId}", indexResult.Key);
                    }
                    else
                    {
                        result.FailureCount++;
                        var errorMessage = $"Failed to upload document {indexResult.Key}: {indexResult.ErrorMessage}";
                        result.Errors.Add(errorMessage);
                        _logger.LogWarning("Failed to upload document {DocumentId}: {Error}", indexResult.Key, indexResult.ErrorMessage);
                    }
                }

                return; // Success, exit retry loop
            }
            catch (RequestFailedException ex) when (IsRetriableError(ex))
            {
                retryCount++;
                if (retryCount > _config.MaxRetryAttempts)
                {
                    result.FailureCount += batchList.Count;
                    var errorMessage = $"Failed to upload batch after {_config.MaxRetryAttempts} retries: {ex.Message}";
                    result.Errors.Add(errorMessage);
                    _logger.LogError(ex, "Failed to upload batch after {RetryCount} retries", _config.MaxRetryAttempts);
                    return;
                }

                var delay = TimeSpan.FromSeconds(Math.Pow(2, retryCount)); // Exponential backoff
                _logger.LogWarning("Retrying batch upload (attempt {RetryCount}/{MaxRetries}) after {Delay}ms due to: {Error}",
                    retryCount, _config.MaxRetryAttempts, delay.TotalMilliseconds, ex.Message);
                
                await Task.Delay(delay, cancellationToken);
            }
            catch (Exception ex)
            {
                result.FailureCount += batchList.Count;
                var errorMessage = $"Non-retriable error during batch upload: {ex.Message}";
                result.Errors.Add(errorMessage);
                _logger.LogError(ex, "Non-retriable error during batch upload");
                return;
            }
        }
    }

    /// <summary>
    /// Creates the field definitions for the search index based on ServiceDocument model
    /// </summary>
    private static IList<SearchField> CreateIndexFields()
    {
        return new FieldBuilder().Build(typeof(ServiceDocument));
    }

    /// <summary>
    /// Creates semantic search configuration for enhanced search capabilities
    /// </summary>
    private static SemanticSearch CreateSemanticSearchConfiguration()
    {
        return new SemanticSearch
        {
            Configurations =
            {
                new SemanticConfiguration("service-semantic-config", new()
                {
                    TitleField = new SemanticField("title"),
                    ContentFields =
                    {
                        new SemanticField("content")
                    },
                    KeywordsFields =
                    {
                        new SemanticField("service_type"),
                        new SemanticField("category")
                    }
                })
            }
        };
    }

    /// <summary>
    /// Splits documents into batches for upload
    /// </summary>
    private static IEnumerable<IEnumerable<T>> CreateBatches<T>(IEnumerable<T> items, int batchSize)
    {
        var itemsList = items.ToList();
        for (int i = 0; i < itemsList.Count; i += batchSize)
        {
            yield return itemsList.Skip(i).Take(batchSize);
        }
    }

    /// <summary>
    /// Determines if an error is retriable
    /// </summary>
    private static bool IsRetriableError(RequestFailedException ex)
    {
        return ex.Status == 429 || // Too Many Requests
               ex.Status == 503 || // Service Unavailable
               ex.Status == 502 || // Bad Gateway
               ex.Status >= 500;   // Other server errors
    }

    /// <summary>
    /// Gets the current document count in the index
    /// </summary>
    public async Task<long> GetDocumentCountAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var searchResults = await _searchClient.SearchAsync<ServiceDocument>("*", 
                new SearchOptions { IncludeTotalCount = true, Size = 0 }, 
                cancellationToken);
            
            return searchResults.Value.TotalCount ?? 0;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get document count from index '{IndexName}'", _config.IndexName);
            return -1;
        }
    }

    /// <summary>
    /// Performs a test search to verify the index is working
    /// </summary>
    public async Task<bool> TestSearchAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var searchResults = await _searchClient.SearchAsync<ServiceDocument>("*", 
                new SearchOptions { Size = 1 }, 
                cancellationToken);
            
            _logger.LogInformation("Search test successful for index '{IndexName}'", _config.IndexName);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Search test failed for index '{IndexName}'", _config.IndexName);
            return false;
        }
    }

    /// <summary>
    /// Deletes all documents from the index (useful for testing)
    /// </summary>
    public async Task<bool> ClearIndexAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Clearing all documents from index '{IndexName}'", _config.IndexName);

            // Get all document IDs
            var searchResults = await _searchClient.SearchAsync<ServiceDocument>("*", 
                new SearchOptions 
                { 
                    Select = { "id" },
                    Size = 1000 // Adjust based on your needs
                }, 
                cancellationToken);

            var documentsToDelete = new List<ServiceDocument>();
            await foreach (var result in searchResults.Value.GetResultsAsync())
            {
                documentsToDelete.Add(new ServiceDocument { Id = result.Document.Id });
            }

            if (documentsToDelete.Any())
            {
                var deleteActions = documentsToDelete.Select(doc => IndexDocumentsAction.Delete(doc));
                await _searchClient.IndexDocumentsAsync(
                    IndexDocumentsBatch.Create(deleteActions.ToArray()), 
                    cancellationToken: cancellationToken);

                _logger.LogInformation("Deleted {Count} documents from index '{IndexName}'", 
                    documentsToDelete.Count, _config.IndexName);
            }

            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to clear index '{IndexName}'", _config.IndexName);
            return false;
        }
    }
}