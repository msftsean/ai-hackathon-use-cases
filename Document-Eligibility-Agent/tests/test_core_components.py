"""
Core component tests for Document Eligibility Agent
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.models.document_types import (
    DocumentType, ProcessingStatus, DocumentMetadata, ExtractedData,
    ProcessedDocument, ApplicantRecord, EligibilityAssessment
)
from src.services.email_processor import MockEmailProcessorService
from src.services.document_intelligence import MockDocumentIntelligenceService
from src.plugins.document_processing_plugins import (
    DocumentClassificationPlugin,
    DataExtractionPlugin,
    EligibilityCalculationPlugin
)


class TestDocumentModels:
    """Test document data models"""
    
    def test_document_metadata_creation(self):
        """Test DocumentMetadata creation and methods"""
        metadata = DocumentMetadata(
            document_id="test_123",
            file_name="pay_stub.pdf",
            file_size=2048,
            mime_type="application/pdf",
            upload_timestamp=datetime.now()
        )
        
        assert metadata.document_id == "test_123"
        assert metadata.file_name == "pay_stub.pdf"
        assert metadata.file_size == 2048
        assert metadata.confidence_score == 0.0
        assert len(metadata.processing_notes) == 0
    
    def test_extracted_data_operations(self):
        """Test ExtractedData field operations"""
        extracted_data = ExtractedData(document_type=DocumentType.INCOME_VERIFICATION)
        
        # Test adding fields
        extracted_data.add_field("income_amount", 3500.0, 0.95)
        extracted_data.add_field("employee_name", "John Doe", 0.88)
        
        assert extracted_data.get_field("income_amount") == 3500.0
        assert extracted_data.get_field("employee_name") == "John Doe"
        assert extracted_data.get_field("nonexistent", "default") == "default"
        
        assert extracted_data.confidence_scores["income_amount"] == 0.95
        assert extracted_data.confidence_scores["employee_name"] == 0.88
    
    def test_processed_document_validation(self):
        """Test ProcessedDocument validation methods"""
        metadata = DocumentMetadata(
            document_id="test_doc",
            file_name="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            upload_timestamp=datetime.now(),
            confidence_score=0.85
        )
        
        extracted_data = ExtractedData(document_type=DocumentType.INCOME_VERIFICATION)
        extracted_data.add_field("income", 2500.0, 0.90)
        
        # Test valid document
        doc = ProcessedDocument(
            metadata=metadata,
            document_type=DocumentType.INCOME_VERIFICATION,
            extracted_data=extracted_data,
            status=ProcessingStatus.COMPLETED
        )
        
        assert doc.is_valid() is True
        assert doc.requires_review() is False
        
        # Test document requiring review (low confidence)
        metadata.confidence_score = 0.6
        doc_low_confidence = ProcessedDocument(
            metadata=metadata,
            document_type=DocumentType.INCOME_VERIFICATION,
            extracted_data=extracted_data,
            status=ProcessingStatus.COMPLETED
        )
        
        assert doc_low_confidence.requires_review() is True
    
    def test_applicant_record_operations(self):
        """Test ApplicantRecord document management"""
        applicant = ApplicantRecord(
            applicant_id="APP_001",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@email.com"
        )
        
        assert len(applicant.documents) == 0
        assert len(applicant.eligibility_assessments) == 0
        
        # Add a document
        metadata = DocumentMetadata(
            document_id="doc_1",
            file_name="income.pdf",
            file_size=1024,
            mime_type="application/pdf",
            upload_timestamp=datetime.now()
        )
        
        extracted_data = ExtractedData(document_type=DocumentType.INCOME_VERIFICATION)
        doc = ProcessedDocument(
            metadata=metadata,
            document_type=DocumentType.INCOME_VERIFICATION,
            extracted_data=extracted_data,
            status=ProcessingStatus.COMPLETED
        )
        
        applicant.add_document(doc)
        assert len(applicant.documents) == 1
        assert applicant.updated_at > applicant.created_at
    
    def test_eligibility_assessment_operations(self):
        """Test EligibilityAssessment note management"""
        assessment = EligibilityAssessment(
            applicant_id="APP_001",
            program_name="SNAP",
            is_eligible=True,
            confidence_score=0.92
        )
        
        assert len(assessment.assessment_notes) == 0
        
        assessment.add_note("Income verification complete")
        assessment.add_note("All required documents provided")
        
        assert len(assessment.assessment_notes) == 2
        assert "Income verification complete" in assessment.assessment_notes[0]


class TestEmailProcessor:
    """Test email processing functionality"""
    
    @pytest.mark.asyncio
    async def test_mock_email_monitoring(self):
        """Test mock email inbox monitoring"""
        service = MockEmailProcessorService()
        
        messages = await service.monitor_inbox()
        assert len(messages) >= 2  # Mock has at least 2 emails
        
        # Test filtering
        filtered_messages = await service.monitor_inbox(filter_subject="SNAP")
        assert len(filtered_messages) <= len(messages)
    
    @pytest.mark.asyncio
    async def test_attachment_processing(self):
        """Test email attachment processing"""
        service = MockEmailProcessorService()
        
        messages = await service.monitor_inbox()
        message_id = messages[0]['id']
        
        # Get attachments
        attachments = await service.get_message_attachments('me', message_id)
        assert len(attachments) > 0
        
        attachment = attachments[0]
        assert attachment.file_name is not None
        assert attachment.file_size > 0
        assert attachment.email_id == message_id
        
        # Download attachment
        content = await service.download_attachment('me', message_id, attachment.document_id)
        assert content is not None
        assert isinstance(content, bytes)
    
    def test_document_type_classification(self):
        """Test document type classification logic"""
        service = MockEmailProcessorService()
        
        # Test various filename patterns
        test_cases = [
            ("pay_stub_march.pdf", DocumentType.INCOME_VERIFICATION),
            ("medical_record.pdf", DocumentType.MEDICAL_RECORD),
            ("utility_bill.pdf", DocumentType.UTILITY_BILL),
            ("drivers_license.jpg", DocumentType.IDENTITY_DOCUMENT),
            ("bank_statement.pdf", DocumentType.BANK_STATEMENT),
            ("lease_agreement.pdf", DocumentType.HOUSING_DOCUMENT),
            ("random_document.txt", DocumentType.UNKNOWN)
        ]
        
        for filename, expected_type in test_cases:
            result = service.classify_document_type(filename)
            assert result == expected_type, f"Failed for {filename}: expected {expected_type}, got {result}"
    
    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test email batch processing"""
        service = MockEmailProcessorService()
        
        documents = await service.process_email_batch('me', batch_size=5)
        assert len(documents) > 0
        
        for doc_metadata in documents:
            assert doc_metadata.email_id is not None
            assert doc_metadata.sender_email is not None
            assert doc_metadata.file_name is not None


class TestDocumentIntelligence:
    """Test document intelligence service"""
    
    @pytest.mark.asyncio
    async def test_mock_document_analysis(self):
        """Test mock document analysis for different types"""
        service = MockDocumentIntelligenceService()
        
        # Test income document
        content = b"Mock pay stub content"
        result = await service.analyze_document(content, DocumentType.INCOME_VERIFICATION)
        
        assert result.document_type == DocumentType.INCOME_VERIFICATION
        assert len(result.extracted_fields) > 0
        assert 'income_amount' in result.extracted_fields
        assert result.confidence_scores['income_amount'] > 0.8
        
        # Test medical document
        result = await service.analyze_document(content, DocumentType.MEDICAL_RECORD)
        assert result.document_type == DocumentType.MEDICAL_RECORD
        assert 'patient_name' in result.extracted_fields
        
        # Test utility bill
        result = await service.analyze_document(content, DocumentType.UTILITY_BILL)
        assert result.document_type == DocumentType.UTILITY_BILL
        assert 'service_address' in result.extracted_fields
    
    def test_data_validation(self):
        """Test extracted data validation"""
        service = MockDocumentIntelligenceService()
        
        # Create test extracted data
        extracted_data = ExtractedData(document_type=DocumentType.INCOME_VERIFICATION)
        extracted_data.add_field("income_amount", 3500.0, 0.95)
        extracted_data.add_field("pay_date", "2024-03-15", 0.90)
        
        errors = service.validate_extracted_data(extracted_data)
        assert len(errors) == 0  # Should be valid
        
        # Test invalid data
        invalid_data = ExtractedData(document_type=DocumentType.INCOME_VERIFICATION)
        invalid_data.add_field("unrelated_field", "test", 0.5)
        
        errors = service.validate_extracted_data(invalid_data)
        assert len(errors) > 0  # Should have validation errors


class TestSemanticKernelPlugins:
    """Test Semantic Kernel plugins"""
    
    def test_document_classification_plugin(self):
        """Test document classification plugin"""
        plugin = DocumentClassificationPlugin()
        
        # Test classification with filename and text
        result = plugin.classify_document_type(
            "paycheck_stub.pdf", 
            "gross pay total $3500 employee john doe"
        )
        assert result == DocumentType.INCOME_VERIFICATION.value
        
        # Test classification validation
        extracted_fields = {
            'income_amount': 3500.0,
            'pay_date': '2024-03-15',
            'employee_name': 'John Doe'
        }
        
        confidence = plugin.validate_classification(
            DocumentType.INCOME_VERIFICATION.value,
            extracted_fields
        )
        assert confidence > 0.8
    
    def test_data_extraction_plugin(self):
        """Test data extraction plugin"""
        plugin = DataExtractionPlugin()
        
        # Test income information extraction
        sample_text = """
        PAYCHECK STUB
        Employee: John Doe
        Gross Pay: $3,500.00
        Pay Period: Monthly
        Employer: Acme Corporation
        Date: March 15, 2024
        """
        
        result = plugin.extract_key_information(
            DocumentType.INCOME_VERIFICATION.value,
            sample_text
        )
        
        assert len(result) > 0
        assert 'income_amount' in result or any('pay' in key.lower() for key in result.keys())
        
        # Test extraction quality validation
        quality_result = plugin.validate_extraction_quality(result)
        assert 'quality_score' in quality_result
        assert 'completeness' in quality_result
        assert 'issues' in quality_result
    
    def test_eligibility_calculation_plugin(self):
        """Test eligibility calculation plugin"""
        plugin = EligibilityCalculationPlugin()
        
        # Test SNAP eligibility calculation
        result = plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=1800.0,
            household_size=2,
            available_documents=[
                DocumentType.INCOME_VERIFICATION.value,
                DocumentType.IDENTITY_DOCUMENT.value,
                DocumentType.UTILITY_BILL.value
            ]
        )
        
        assert 'eligible' in result
        assert 'confidence' in result
        assert 'income_assessment' in result
        
        # Test with high income (should be ineligible)
        high_income_result = plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=5000.0,
            household_size=1,
            available_documents=[DocumentType.INCOME_VERIFICATION.value]
        )
        
        assert high_income_result['eligible'] is False
        assert 'income' in high_income_result['reason'].lower()
        
        # Test recommendation generation
        recommendations = plugin.generate_recommendations(
            result,
            {'applicant_id': 'APP_001', 'monthly_income': 1800.0}
        )
        
        assert len(recommendations) > 0
        assert any('eligible' in rec.lower() or 'contact' in rec.lower() for rec in recommendations)


def run_core_component_tests():
    """Run all core component tests"""
    print("🧪 Running Document Eligibility Agent Core Component Tests")
    print("=" * 70)
    
    test_classes = [
        TestDocumentModels,
        TestEmailProcessor, 
        TestDocumentIntelligence,
        TestSemanticKernelPlugins
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}")
        print("-" * 50)
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        class_passed = 0
        class_failed = 0
        
        for method_name in test_methods:
            try:
                print(f"  Running {method_name}...", end=" ")
                method = getattr(test_instance, method_name)
                
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                
                print("✅ PASSED")
                class_passed += 1
                
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                class_failed += 1
        
        print(f"  Results: {class_passed} passed, {class_failed} failed")
        total_passed += class_passed
        total_failed += class_failed
    
    print("\n" + "=" * 70)
    print(f"📊 Overall Results: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 All core component tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_core_component_tests()
    exit(0 if success else 1)