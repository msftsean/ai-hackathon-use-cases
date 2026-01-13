namespace VirtualCitizenAgent.Models;

/// <summary>
/// Publication status of a document.
/// </summary>
public enum DocumentStatus
{
    /// <summary>Document is current and searchable.</summary>
    Active,

    /// <summary>Document is outdated but preserved for reference.</summary>
    Archived,

    /// <summary>Document is not yet published.</summary>
    Draft
}
