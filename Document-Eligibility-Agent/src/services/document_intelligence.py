"""
Document Intelligence service for OCR and data extraction
"""
import os
import logging
from typing import Dict, Any, Optional, List
from ..models.document_types import ExtractedData, DocumentType, ProcessingStatus

# Try to import Azure services, fall back to mocks if not available
try:
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    AZURE_SERVICES_AVAILABLE = True
except ImportError:
    # Mock classes when Azure services aren't installed
    class DocumentAnalysisClient:
        def __init__(self, endpoint, credential):
            pass
        
        def begin_analyze_document(self, model_id, document):
            class MockPoller:
                def result(self):
                    class MockResult:
                        def __init__(self):
                            self.fields = {}
                            self.tables = []
                            self.content = "Mock extracted text content"
                    return MockResult()
            return MockPoller()
    
    class AzureKeyCredential:
        def __init__(self, key):
            pass
    
    class DefaultAzureCredential:
        def __init__(self):
            pass
    
    AZURE_SERVICES_AVAILABLE = False


class DocumentIntelligenceService:
    """Service for processing documents using Azure AI Document Intelligence"""
    
    def __init__(self, endpoint: str = None, api_key: str = None):
        """
        Initialize Document Intelligence service
        
        Args:
            endpoint: Azure Form Recognizer endpoint
            api_key: Azure Form Recognizer API key
        """
        self.logger = logging.getLogger(__name__)
        
        self.endpoint = endpoint or os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.api_key = api_key or os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        if not self.endpoint:
            raise ValueError("Azure Document Intelligence endpoint is required")
        
        # Initialize client with API key or default credentials
        if self.api_key:
            credential = AzureKeyCredential(self.api_key)
        else:
            credential = DefaultAzureCredential()
        
        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint,
            credential=credential
        )
    
    async def analyze_document(self, document_content: bytes, document_type: DocumentType) -> ExtractedData:
        """
        Analyze document and extract structured data
        
        Args:
            document_content: Document content as bytes
            document_type: Type of document to process
            
        Returns:
            Extracted data with confidence scores
        """
        try:
            self.logger.info(f"Analyzing document of type: {document_type.value}")
            
            # Choose appropriate model based on document type
            model_id = self._get_model_for_document_type(document_type)
            
            # Analyze document
            poller = self.client.begin_analyze_document(
                model_id=model_id,
                document=document_content
            )
            result = poller.result()
            
            # Extract data based on document type
            extracted_data = ExtractedData(document_type=document_type)
            
            if document_type == DocumentType.INCOME_VERIFICATION:
                self._extract_income_data(result, extracted_data)
            elif document_type == DocumentType.MEDICAL_RECORD:
                self._extract_medical_data(result, extracted_data)
            elif document_type == DocumentType.UTILITY_BILL:
                self._extract_utility_data(result, extracted_data)
            elif document_type == DocumentType.IDENTITY_DOCUMENT:
                self._extract_identity_data(result, extracted_data)
            elif document_type == DocumentType.BANK_STATEMENT:
                self._extract_bank_data(result, extracted_data)
            else:
                self._extract_general_data(result, extracted_data)
            
            self.logger.info(f"Successfully extracted {len(extracted_data.extracted_fields)} fields")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing document: {str(e)}")
            extracted_data = ExtractedData(document_type=document_type)
            extracted_data.validation_errors.append(f"Analysis failed: {str(e)}")
            return extracted_data
    
    def _get_model_for_document_type(self, document_type: DocumentType) -> str:
        """Get appropriate Form Recognizer model for document type"""
        model_mapping = {
            DocumentType.INCOME_VERIFICATION: "prebuilt-invoice",  # Best fit for structured income docs
            DocumentType.MEDICAL_RECORD: "prebuilt-healthInsuranceCard",
            DocumentType.UTILITY_BILL: "prebuilt-invoice",
            DocumentType.IDENTITY_DOCUMENT: "prebuilt-idDocument", 
            DocumentType.BANK_STATEMENT: "prebuilt-document",
            DocumentType.TAX_RETURN: "prebuilt-tax.us.w2",
            DocumentType.HOUSING_DOCUMENT: "prebuilt-document",
            DocumentType.EMPLOYMENT_RECORD: "prebuilt-document"
        }
        return model_mapping.get(document_type, "prebuilt-document")
    
    def _extract_income_data(self, result, extracted_data: ExtractedData):
        """Extract income-specific data from analysis result"""
        # Extract common income fields
        for field_name, field in result.fields.items():
            if field.confidence and field.confidence > 0.5:
                if 'amount' in field_name.lower() or 'total' in field_name.lower():
                    extracted_data.add_field(f"income_{field_name}", field.value, field.confidence)
                elif 'date' in field_name.lower():
                    extracted_data.add_field(f"date_{field_name}", field.value, field.confidence)
                elif 'name' in field_name.lower() or 'employee' in field_name.lower():
                    extracted_data.add_field(f"employee_{field_name}", field.value, field.confidence)
        
        # Extract table data for detailed income breakdown
        if result.tables:
            for table_idx, table in enumerate(result.tables):
                table_data = []
                for row in table.cells:
                    table_data.append({
                        'row': row.row_index,
                        'column': row.column_index,
                        'content': row.content,
                        'confidence': row.confidence
                    })
                extracted_data.add_field(f"income_table_{table_idx}", table_data, 0.8)
    
    def _extract_medical_data(self, result, extracted_data: ExtractedData):
        """Extract medical record specific data"""
        for field_name, field in result.fields.items():
            if field.confidence and field.confidence > 0.5:
                if 'patient' in field_name.lower():
                    extracted_data.add_field(f"patient_{field_name}", field.value, field.confidence)
                elif 'insurance' in field_name.lower():
                    extracted_data.add_field(f"insurance_{field_name}", field.value, field.confidence)
                elif 'date' in field_name.lower():
                    extracted_data.add_field(f"medical_date_{field_name}", field.value, field.confidence)
    
    def _extract_utility_data(self, result, extracted_data: ExtractedData):
        """Extract utility bill specific data"""
        for field_name, field in result.fields.items():
            if field.confidence and field.confidence > 0.5:
                if 'amount' in field_name.lower() or 'total' in field_name.lower():
                    extracted_data.add_field(f"utility_{field_name}", field.value, field.confidence)
                elif 'address' in field_name.lower():
                    extracted_data.add_field(f"service_address", field.value, field.confidence)
                elif 'date' in field_name.lower():
                    extracted_data.add_field(f"service_date_{field_name}", field.value, field.confidence)
    
    def _extract_identity_data(self, result, extracted_data: ExtractedData):
        """Extract identity document specific data"""
        for field_name, field in result.fields.items():
            if field.confidence and field.confidence > 0.5:
                if 'name' in field_name.lower():
                    extracted_data.add_field(f"id_{field_name}", field.value, field.confidence)
                elif 'address' in field_name.lower():
                    extracted_data.add_field(f"id_address", field.value, field.confidence)
                elif 'number' in field_name.lower():
                    extracted_data.add_field(f"id_number", field.value, field.confidence)
                elif 'date' in field_name.lower():
                    extracted_data.add_field(f"id_date_{field_name}", field.value, field.confidence)
    
    def _extract_bank_data(self, result, extracted_data: ExtractedData):
        """Extract bank statement specific data"""
        for field_name, field in result.fields.items():
            if field.confidence and field.confidence > 0.5:
                if 'balance' in field_name.lower() or 'amount' in field_name.lower():
                    extracted_data.add_field(f"bank_{field_name}", field.value, field.confidence)
                elif 'account' in field_name.lower():
                    extracted_data.add_field(f"account_{field_name}", field.value, field.confidence)
        
        # Extract transaction data from tables
        if result.tables:
            for table_idx, table in enumerate(result.tables):
                transactions = []
                for row in table.cells:
                    if row.row_index > 0:  # Skip header row
                        transactions.append({
                            'date': row.content if row.column_index == 0 else None,
                            'description': row.content if row.column_index == 1 else None,
                            'amount': row.content if row.column_index == 2 else None,
                            'confidence': row.confidence
                        })
                extracted_data.add_field(f"transactions", transactions, 0.8)
    
    def _extract_general_data(self, result, extracted_data: ExtractedData):
        """Extract general data for unknown document types"""
        # Extract all key-value pairs with reasonable confidence
        for field_name, field in result.fields.items():
            if field.confidence and field.confidence > 0.6:
                extracted_data.add_field(field_name, field.value, field.confidence)
        
        # Extract text content
        if result.content:
            extracted_data.add_field("full_text", result.content, 0.9)
    
    def validate_extracted_data(self, extracted_data: ExtractedData) -> List[str]:
        """
        Validate extracted data for completeness and accuracy
        
        Args:
            extracted_data: Extracted data to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Document type specific validation
        if extracted_data.document_type == DocumentType.INCOME_VERIFICATION:
            if not any('amount' in key or 'total' in key for key in extracted_data.extracted_fields.keys()):
                errors.append("No income amount found in document")
            if not any('date' in key for key in extracted_data.extracted_fields.keys()):
                errors.append("No date information found in document")
        
        elif extracted_data.document_type == DocumentType.IDENTITY_DOCUMENT:
            if not any('name' in key for key in extracted_data.extracted_fields.keys()):
                errors.append("No name found in identity document")
        
        elif extracted_data.document_type == DocumentType.UTILITY_BILL:
            if not any('address' in key for key in extracted_data.extracted_fields.keys()):
                errors.append("No address found in utility bill")
        
        # Check confidence scores
        low_confidence_fields = [
            field for field, confidence in extracted_data.confidence_scores.items()
            if confidence < 0.6
        ]
        if low_confidence_fields:
            errors.append(f"Low confidence fields: {', '.join(low_confidence_fields)}")
        
        return errors


# Mock implementation for testing
class MockDocumentIntelligenceService(DocumentIntelligenceService):
    """Mock document intelligence service for testing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def analyze_document(self, document_content: bytes, document_type: DocumentType) -> ExtractedData:
        """Return mock extracted data based on document type"""
        extracted_data = ExtractedData(document_type=document_type)
        
        if document_type == DocumentType.INCOME_VERIFICATION:
            extracted_data.add_field("income_amount", 3500.00, 0.95)
            extracted_data.add_field("pay_period", "Monthly", 0.88)
            extracted_data.add_field("employee_name", "John Doe", 0.92)
            extracted_data.add_field("employer", "Acme Corporation", 0.85)
            extracted_data.add_field("pay_date", "2024-03-15", 0.90)
            
        elif document_type == DocumentType.MEDICAL_RECORD:
            extracted_data.add_field("patient_name", "Jane Smith", 0.94)
            extracted_data.add_field("insurance_provider", "Blue Cross", 0.87)
            extracted_data.add_field("policy_number", "BC123456789", 0.89)
            extracted_data.add_field("visit_date", "2024-03-10", 0.91)
            
        elif document_type == DocumentType.UTILITY_BILL:
            extracted_data.add_field("service_address", "123 Main St, City, ST 12345", 0.93)
            extracted_data.add_field("utility_amount", 125.50, 0.96)
            extracted_data.add_field("service_period", "February 2024", 0.87)
            extracted_data.add_field("account_number", "UTIL789012", 0.84)
            
        elif document_type == DocumentType.BANK_STATEMENT:
            extracted_data.add_field("account_balance", 2750.25, 0.97)
            extracted_data.add_field("account_number", "****1234", 0.92)
            extracted_data.add_field("statement_period", "March 2024", 0.89)
            
        return extracted_data