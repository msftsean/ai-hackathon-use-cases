"""
Document processing models for eligibility determination
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class DocumentType(Enum):
    """Supported document types for eligibility processing"""
    INCOME_VERIFICATION = "income_verification"
    MEDICAL_RECORD = "medical_record"
    UTILITY_BILL = "utility_bill"
    IDENTITY_DOCUMENT = "identity_document"
    HOUSING_DOCUMENT = "housing_document"
    BANK_STATEMENT = "bank_statement"
    TAX_RETURN = "tax_return"
    EMPLOYMENT_RECORD = "employment_record"
    UNKNOWN = "unknown"


class ProcessingStatus(Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class DocumentMetadata:
    """Metadata for processed documents"""
    document_id: str
    file_name: str
    file_size: int
    mime_type: str
    upload_timestamp: datetime
    email_id: Optional[str] = None
    sender_email: Optional[str] = None
    confidence_score: float = 0.0
    processing_notes: List[str] = field(default_factory=list)


@dataclass
class ExtractedData:
    """Structured data extracted from documents"""
    document_type: DocumentType
    extracted_fields: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    
    def add_field(self, field_name: str, value: Any, confidence: float = 1.0):
        """Add an extracted field with confidence score"""
        self.extracted_fields[field_name] = value
        self.confidence_scores[field_name] = confidence
    
    def get_field(self, field_name: str, default=None):
        """Get an extracted field value"""
        return self.extracted_fields.get(field_name, default)


@dataclass
class ApplicantRecord:
    """Complete applicant record with all processed documents"""
    applicant_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    documents: List['ProcessedDocument'] = field(default_factory=list)
    eligibility_assessments: List['EligibilityAssessment'] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_document(self, document: 'ProcessedDocument'):
        """Add a processed document to the applicant record"""
        self.documents.append(document)
        self.updated_at = datetime.now()


@dataclass
class ProcessedDocument:
    """Complete processed document with metadata and extracted data"""
    metadata: DocumentMetadata
    document_type: DocumentType
    extracted_data: ExtractedData
    status: ProcessingStatus
    processing_timestamp: datetime = field(default_factory=datetime.now)
    review_notes: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check if document processing was successful"""
        return (self.status == ProcessingStatus.COMPLETED and 
                len(self.extracted_data.validation_errors) == 0)
    
    def requires_review(self) -> bool:
        """Check if document requires manual review"""
        return (self.status == ProcessingStatus.REQUIRES_REVIEW or
                self.metadata.confidence_score < 0.7)


@dataclass
class EligibilityCriteria:
    """Criteria for benefit eligibility determination"""
    program_name: str
    income_threshold: Optional[float] = None
    household_size_factor: bool = True
    required_documents: List[DocumentType] = field(default_factory=list)
    additional_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EligibilityAssessment:
    """Result of eligibility determination"""
    applicant_id: str
    program_name: str
    is_eligible: bool
    confidence_score: float
    assessed_income: Optional[float] = None
    household_size: Optional[int] = None
    missing_documents: List[DocumentType] = field(default_factory=list)
    assessment_notes: List[str] = field(default_factory=list)
    assessment_timestamp: datetime = field(default_factory=datetime.now)
    reviewed_by: Optional[str] = None
    
    def add_note(self, note: str):
        """Add an assessment note"""
        self.assessment_notes.append(f"{datetime.now().isoformat()}: {note}")