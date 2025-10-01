using System.Text.Json;
using Microsoft.Extensions.Logging;
using AzureSearchUploader.Models;

namespace AzureSearchUploader.Services;

/// <summary>
/// Service for loading and parsing JSON data files containing service documents
/// </summary>
public class JsonDataLoader
{
    private readonly ILogger<JsonDataLoader> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public JsonDataLoader(ILogger<JsonDataLoader> logger)
    {
        _logger = logger;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            WriteIndented = true
        };
    }

    /// <summary>
    /// Loads service documents from a JSON file
    /// </summary>
    /// <param name="filePath">Path to the JSON file containing the documents</param>
    /// <returns>Collection of ServiceDocument objects</returns>
    public async Task<IEnumerable<ServiceDocument>> LoadFromFileAsync(string filePath)
    {
        try
        {
            _logger.LogInformation("Loading data from file: {FilePath}", filePath);

            if (!File.Exists(filePath))
            {
                _logger.LogError("File not found: {FilePath}", filePath);
                return Enumerable.Empty<ServiceDocument>();
            }

            var jsonContent = await File.ReadAllTextAsync(filePath);
            
            // Try to parse as array first, then as single object
            try
            {
                var documents = JsonSerializer.Deserialize<ServiceDocument[]>(jsonContent, _jsonOptions);
                if (documents != null)
                {
                    _logger.LogInformation("Successfully loaded {Count} documents from {FilePath}", documents.Length, filePath);
                    return documents;
                }
            }
            catch (JsonException)
            {
                // If array parsing fails, try parsing as single object
                var singleDocument = JsonSerializer.Deserialize<ServiceDocument>(jsonContent, _jsonOptions);
                if (singleDocument != null)
                {
                    _logger.LogInformation("Successfully loaded 1 document from {FilePath}", filePath);
                    return new[] { singleDocument };
                }
            }

            _logger.LogError("Failed to parse JSON content from {FilePath}", filePath);
            return Enumerable.Empty<ServiceDocument>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading data from file: {FilePath}", filePath);
            return Enumerable.Empty<ServiceDocument>();
        }
    }

    /// <summary>
    /// Loads service documents from a JSON string
    /// </summary>
    /// <param name="jsonContent">JSON string containing the documents</param>
    /// <returns>Collection of ServiceDocument objects</returns>
    public IEnumerable<ServiceDocument> LoadFromJson(string jsonContent)
    {
        try
        {
            _logger.LogInformation("Loading data from JSON string");

            if (string.IsNullOrWhiteSpace(jsonContent))
            {
                _logger.LogWarning("JSON content is null or empty");
                return Enumerable.Empty<ServiceDocument>();
            }

            // Try to parse as array first, then as single object
            try
            {
                var documents = JsonSerializer.Deserialize<ServiceDocument[]>(jsonContent, _jsonOptions);
                if (documents != null)
                {
                    _logger.LogInformation("Successfully loaded {Count} documents from JSON string", documents.Length);
                    return documents;
                }
            }
            catch (JsonException)
            {
                // If array parsing fails, try parsing as single object
                var singleDocument = JsonSerializer.Deserialize<ServiceDocument>(jsonContent, _jsonOptions);
                if (singleDocument != null)
                {
                    _logger.LogInformation("Successfully loaded 1 document from JSON string");
                    return new[] { singleDocument };
                }
            }

            _logger.LogError("Failed to parse JSON content");
            return Enumerable.Empty<ServiceDocument>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error parsing JSON content");
            return Enumerable.Empty<ServiceDocument>();
        }
    }

    /// <summary>
    /// Validates that all required fields are present in the documents
    /// </summary>
    /// <param name="documents">Documents to validate</param>
    /// <returns>Validated documents (invalid ones are filtered out)</returns>
    public IEnumerable<ServiceDocument> ValidateDocuments(IEnumerable<ServiceDocument> documents)
    {
        var validDocuments = new List<ServiceDocument>();
        var documentList = documents.ToList();

        _logger.LogInformation("Validating {Count} documents", documentList.Count);

        foreach (var doc in documentList)
        {
            var errors = new List<string>();

            if (string.IsNullOrWhiteSpace(doc.Id))
                errors.Add("ID is required");

            if (string.IsNullOrWhiteSpace(doc.Title))
                errors.Add("Title is required");

            if (string.IsNullOrWhiteSpace(doc.Content))
                errors.Add("Content is required");

            if (string.IsNullOrWhiteSpace(doc.ServiceType))
                errors.Add("Service Type is required");

            if (string.IsNullOrWhiteSpace(doc.Category))
                errors.Add("Category is required");

            if (errors.Any())
            {
                _logger.LogWarning("Document with ID '{DocumentId}' failed validation: {Errors}", 
                    doc.Id ?? "NULL", string.Join(", ", errors));
            }
            else
            {
                validDocuments.Add(doc);
            }
        }

        _logger.LogInformation("Validation complete. {ValidCount} valid documents out of {TotalCount}", 
            validDocuments.Count, documentList.Count);

        return validDocuments;
    }

    /// <summary>
    /// Saves documents to a JSON file (useful for creating sample data)
    /// </summary>
    /// <param name="documents">Documents to save</param>
    /// <param name="filePath">Output file path</param>
    public async Task SaveToFileAsync(IEnumerable<ServiceDocument> documents, string filePath)
    {
        try
        {
            var documentList = documents.ToList();
            _logger.LogInformation("Saving {Count} documents to {FilePath}", documentList.Count, filePath);

            var jsonContent = JsonSerializer.Serialize(documentList, _jsonOptions);
            
            // Ensure directory exists
            var directory = Path.GetDirectoryName(filePath);
            if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            await File.WriteAllTextAsync(filePath, jsonContent);
            _logger.LogInformation("Successfully saved documents to {FilePath}", filePath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error saving documents to file: {FilePath}", filePath);
            throw;
        }
    }
}