"""Data models for Document Eligibility Agent."""

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .document import Document
    from .extraction import Extraction
    from .extraction_model import ExtractionModel
    from .processing_log import ProcessingLog
    from .validation_rule import ValidationRule


# Document Types (from data-model.md)
class DocumentType(str, Enum):
    """Types of documents supported for processing."""
    W2 = "w2"
    PAYSTUB = "paystub"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    DRIVERS_LICENSE = "drivers_license"
    BIRTH_CERTIFICATE = "birth_certificate"
    LEASE_AGREEMENT = "lease_agreement"
    OTHER = "other"


# Document Processing Status
class DocumentStatus(str, Enum):
    """Processing status states for documents."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VALIDATING = "validating"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESUBMIT_REQUESTED = "resubmit_requested"
    FAILED = "failed"


# Document Source
class DocumentSource(str, Enum):
    """How the document was received."""
    EMAIL = "email"
    UPLOAD = "upload"
    FAX = "fax"
    SCAN = "scan"


# Document Priority
class DocumentPriority(str, Enum):
    """Processing priority levels."""
    EXPEDITED = "expedited"
    RESUBMISSION = "resubmission"
    STANDARD = "standard"
    LOW = "low"


# Validation Status
class ValidationStatus(str, Enum):
    """Validation result status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    PENDING = "pending"


# PII Types
class PIIType(str, Enum):
    """Types of personally identifiable information."""
    SSN = "ssn"
    BANK_ACCOUNT = "bank_account"
    ROUTING_NUMBER = "routing_number"
    DATE_OF_BIRTH = "date_of_birth"
    DRIVERS_LICENSE_NUMBER = "drivers_license_number"
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"


# Audit Log Actions (LOADinG Act compliance)
class LogAction(str, Enum):
    """Actions logged for audit trail."""
    UPLOADED = "uploaded"
    PROCESSING_STARTED = "processing_started"
    PROCESSING_COMPLETED = "processing_completed"
    PROCESSING_FAILED = "processing_failed"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    ASSIGNED = "assigned"
    VIEWED = "viewed"
    PII_ACCESSED = "pii_accessed"
    FIELD_CORRECTED = "field_corrected"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESUBMIT_REQUESTED = "resubmit_requested"
    EXPORTED = "exported"


# Validation Rule Types
class RuleType(str, Enum):
    """Types of validation rules."""
    AGE = "age"
    REQUIRED_FIELD = "required_field"
    FORMAT = "format"
    RANGE = "range"
    CROSS_REFERENCE = "cross_reference"
    CUSTOM = "custom"


# Severity Levels
class Severity(str, Enum):
    """Validation rule severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Export model classes
__all__ = [
    # Enums
    "DocumentType",
    "DocumentStatus",
    "DocumentSource",
    "DocumentPriority",
    "ValidationStatus",
    "PIIType",
    "LogAction",
    "RuleType",
    "Severity",
    # Models (lazy imports)
    "Document",
    "Extraction",
    "ProcessingLog",
    "ValidationRule",
    "ExtractionModel",
]


def __getattr__(name: str):
    """Lazy import models to avoid circular imports."""
    if name == "Document":
        from .document import Document
        return Document
    elif name == "Extraction":
        from .extraction import Extraction
        return Extraction
    elif name == "ProcessingLog":
        from .processing_log import ProcessingLog
        return ProcessingLog
    elif name == "ValidationRule":
        from .validation_rule import ValidationRule
        return ValidationRule
    elif name == "ExtractionModel":
        from .extraction_model import ExtractionModel
        return ExtractionModel
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
