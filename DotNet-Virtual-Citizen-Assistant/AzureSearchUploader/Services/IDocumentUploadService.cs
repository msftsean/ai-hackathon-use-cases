using AzureSearchUploader.Models;

namespace AzureSearchUploader.Services;

/// <summary>
/// Interface for document upload operations.
/// </summary>
public interface IDocumentUploadService
{
    /// <summary>
    /// Upload a batch of documents to Azure AI Search.
    /// </summary>
    Task<UploadResult> UploadDocumentsAsync(IEnumerable<UploadDocument> documents, CancellationToken cancellationToken = default);

    /// <summary>
    /// Load documents from a JSON file.
    /// </summary>
    Task<List<UploadDocument>> LoadDocumentsFromFileAsync(string filePath, CancellationToken cancellationToken = default);
}
