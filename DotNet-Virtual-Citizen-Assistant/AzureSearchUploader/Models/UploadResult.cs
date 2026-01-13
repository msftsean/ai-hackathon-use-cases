namespace AzureSearchUploader.Models;

/// <summary>
/// Result of a batch upload operation.
/// </summary>
public class UploadResult
{
    public int TotalDocuments { get; set; }
    public int SuccessCount { get; set; }
    public int FailedCount { get; set; }
    public List<UploadError> Errors { get; set; } = [];
    public long DurationMs { get; set; }
}

/// <summary>
/// Error details for failed document upload.
/// </summary>
public class UploadError
{
    public string DocumentId { get; set; } = string.Empty;
    public string ErrorMessage { get; set; } = string.Empty;
    public int? StatusCode { get; set; }
}
