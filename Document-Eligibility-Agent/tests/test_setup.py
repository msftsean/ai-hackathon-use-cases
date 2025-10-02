"""
Setup validation tests for Document Eligibility Agent
"""
import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.services.email_processor import EmailProcessorService, MockEmailProcessorService
from src.services.document_intelligence import DocumentIntelligenceService, MockDocumentIntelligenceService
from src.plugins.document_processing_plugins import (
    DocumentClassificationPlugin,
    DataExtractionPlugin, 
    EligibilityCalculationPlugin
)
from src.models.document_types import DocumentType, ProcessingStatus


class TestSetupValidation:
    """Test setup and configuration validation"""
    
    def test_environment_variables(self):
        """Test that required environment variables can be loaded"""
        # Test with mock environment variables
        with patch.dict(os.environ, {
            'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
            'AZURE_DOCUMENT_INTELLIGENCE_KEY': 'test_key_123',
            'MICROSOFT_GRAPH_CLIENT_ID': 'test_client_id',
            'MICROSOFT_GRAPH_CLIENT_SECRET': 'test_secret',
            'MICROSOFT_GRAPH_TENANT_ID': 'test_tenant_id'
        }):
            # Should not raise any exceptions
            email_service = EmailProcessorService()
            assert email_service.client_id == 'test_client_id'
            assert email_service.client_secret == 'test_secret'
            assert email_service.tenant_id == 'test_tenant_id'
    
    def test_mock_services_initialization(self):
        """Test that mock services initialize correctly"""
        # Mock email service
        mock_email = MockEmailProcessorService()
        assert mock_email is not None
        assert len(mock_email.mock_emails) > 0
        
        # Mock document intelligence service
        mock_doc_intel = MockDocumentIntelligenceService()
        assert mock_doc_intel is not None
    
    def test_plugin_initialization(self):
        """Test that all plugins initialize correctly"""
        classification_plugin = DocumentClassificationPlugin()
        assert classification_plugin is not None
        
        extraction_plugin = DataExtractionPlugin()
        assert extraction_plugin is not None
        
        eligibility_plugin = EligibilityCalculationPlugin()
        assert eligibility_plugin is not None
        assert len(eligibility_plugin.program_criteria) > 0
        assert 'SNAP' in eligibility_plugin.program_criteria
        assert 'Medicaid' in eligibility_plugin.program_criteria
    
    @pytest.mark.asyncio
    async def test_mock_email_service_functionality(self):
        """Test mock email service basic functionality"""
        mock_email = MockEmailProcessorService()
        
        # Test inbox monitoring
        messages = await mock_email.monitor_inbox()
        assert len(messages) > 0
        assert 'subject' in messages[0]
        
        # Test attachment retrieval
        message_id = messages[0]['id']
        attachments = await mock_email.get_message_attachments('me', message_id)
        assert len(attachments) > 0
        assert attachments[0].file_name is not None
        
        # Test attachment download
        attachment_id = attachments[0].document_id
        content = await mock_email.download_attachment('me', message_id, attachment_id)
        assert content is not None
        assert len(content) > 0
    
    @pytest.mark.asyncio
    async def test_mock_document_intelligence_functionality(self):
        """Test mock document intelligence service"""
        mock_doc_intel = MockDocumentIntelligenceService()
        
        # Test income document analysis
        content = b"Mock pay stub content"
        result = await mock_doc_intel.analyze_document(content, DocumentType.INCOME_VERIFICATION)
        
        assert result.document_type == DocumentType.INCOME_VERIFICATION
        assert len(result.extracted_fields) > 0
        assert 'income_amount' in result.extracted_fields
        assert result.confidence_scores['income_amount'] > 0.8
        
        # Test medical document analysis
        result = await mock_doc_intel.analyze_document(content, DocumentType.MEDICAL_RECORD)
        assert result.document_type == DocumentType.MEDICAL_RECORD
        assert 'patient_name' in result.extracted_fields
    
    def test_document_classification(self):
        """Test document classification functionality"""
        plugin = DocumentClassificationPlugin()
        
        # Test income document classification
        result = plugin.classify_document_type("pay_stub_march.pdf", "gross pay salary")
        assert result == DocumentType.INCOME_VERIFICATION.value
        
        # Test medical document classification
        result = plugin.classify_document_type("insurance_card.jpg", "patient medical")
        assert result == DocumentType.MEDICAL_RECORD.value
        
        # Test utility bill classification
        result = plugin.classify_document_type("electric_bill.pdf", "utility electric")
        assert result == DocumentType.UTILITY_BILL.value
    
    def test_eligibility_calculation(self):
        """Test eligibility calculation logic"""
        plugin = EligibilityCalculationPlugin()
        
        # Test SNAP eligibility - should be eligible
        result = plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=1500.0,
            household_size=2,
            available_documents=[
                DocumentType.INCOME_VERIFICATION.value,
                DocumentType.IDENTITY_DOCUMENT.value,
                DocumentType.UTILITY_BILL.value
            ]
        )
        
        assert result['eligible'] is True
        assert result['confidence'] > 0.8
        assert len(result['missing_documents']) == 0
        
        # Test SNAP eligibility - should not be eligible (high income)
        result = plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=5000.0,
            household_size=1,
            available_documents=[DocumentType.INCOME_VERIFICATION.value]
        )
        
        assert result['eligible'] is False
        assert 'income' in result['reason'].lower()
    
    def test_data_extraction_validation(self):
        """Test data extraction and validation"""
        plugin = DataExtractionPlugin()
        
        # Test quality validation with good data
        good_data = {
            'income_amount': '3500.00',
            'employee_name': 'John Doe',
            'pay_date': '2024-03-15'
        }
        
        result = plugin.validate_extraction_quality(good_data)
        assert result['quality_score'] > 0.8
        assert result['completeness'] == 1.0
        assert len(result['issues']) == 0
        
        # Test quality validation with poor data
        poor_data = {
            'income_amount': '',
            'employee_name': None,
            'pay_date': '   '
        }
        
        result = plugin.validate_extraction_quality(poor_data)
        assert result['quality_score'] < 0.5
        assert len(result['issues']) > 0
    
    def test_document_type_enum(self):
        """Test document type enumeration"""
        # Test all document types are accessible
        assert DocumentType.INCOME_VERIFICATION.value == "income_verification"
        assert DocumentType.MEDICAL_RECORD.value == "medical_record"
        assert DocumentType.UTILITY_BILL.value == "utility_bill"
        assert DocumentType.IDENTITY_DOCUMENT.value == "identity_document"
        assert DocumentType.UNKNOWN.value == "unknown"
    
    def test_processing_status_enum(self):
        """Test processing status enumeration"""
        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"
        assert ProcessingStatus.REQUIRES_REVIEW.value == "requires_review"


def run_setup_tests():
    """Run all setup validation tests"""
    print("🧪 Running Document Eligibility Agent Setup Tests")
    print("=" * 60)
    
    test_class = TestSetupValidation()
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            print(f"Running {method_name}...", end=" ")
            method = getattr(test_class, method_name)
            
            if asyncio.iscoroutinefunction(method):
                asyncio.run(method())
            else:
                method()
            
            print("✅ PASSED")
            passed += 1
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All setup tests passed! System is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check configuration and dependencies.")
        return False


if __name__ == "__main__":
    success = run_setup_tests()
    exit(0 if success else 1)