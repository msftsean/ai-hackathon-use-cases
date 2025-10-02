"""
Integration tests for Document Eligibility Agent
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.main import DocumentEligibilityAgent
from src.models.document_types import (
    DocumentType, ProcessingStatus, ApplicantRecord, EligibilityAssessment
)


class TestDocumentEligibilityAgentIntegration:
    """Integration tests for the complete Document Eligibility Agent system"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.agent = DocumentEligibilityAgent(use_mock_services=True)
    
    @pytest.mark.asyncio
    async def test_complete_email_processing_workflow(self):
        """Test complete workflow from email to processed documents"""
        # Process email batch
        processed_documents = await self.agent.process_email_batch(batch_size=3)
        
        # Verify documents were processed
        assert len(processed_documents) > 0
        
        for doc in processed_documents:
            # Check document structure
            assert doc.metadata is not None
            assert doc.document_type is not None
            assert doc.extracted_data is not None
            assert doc.status in [ProcessingStatus.COMPLETED, ProcessingStatus.REQUIRES_REVIEW, ProcessingStatus.FAILED]
            
            # Check processing timestamp
            assert doc.processing_timestamp is not None
            assert doc.processing_timestamp <= datetime.now()
            
            # If document was successfully processed, check extracted data
            if doc.status == ProcessingStatus.COMPLETED:
                assert len(doc.extracted_data.extracted_fields) > 0
                assert doc.metadata.confidence_score > 0.0
    
    @pytest.mark.asyncio
    async def test_document_type_classification_workflow(self):
        """Test document type classification through complete workflow"""
        processed_documents = await self.agent.process_email_batch(batch_size=5)
        
        # Check that different document types are classified correctly
        document_types_found = set()
        for doc in processed_documents:
            document_types_found.add(doc.document_type)
        
        # Should have at least a few different document types from mock data
        assert len(document_types_found) > 1
        assert DocumentType.UNKNOWN not in document_types_found  # Mock should classify correctly
    
    def test_eligibility_assessment_workflow(self):
        """Test complete eligibility assessment workflow"""
        # Create sample applicant with processed documents
        applicant = ApplicantRecord(
            applicant_id="INT_TEST_001",
            first_name="Integration",
            last_name="Test",
            email="integration@test.com"
        )
        
        # Add mock processed documents
        income_doc = self._create_mock_income_document()
        identity_doc = self._create_mock_identity_document()
        utility_doc = self._create_mock_utility_document()
        
        applicant.add_document(income_doc)
        applicant.add_document(identity_doc)
        applicant.add_document(utility_doc)
        
        # Test SNAP eligibility assessment
        snap_assessment = self.agent.assess_eligibility(applicant, "SNAP")
        
        assert isinstance(snap_assessment, EligibilityAssessment)
        assert snap_assessment.applicant_id == applicant.applicant_id
        assert snap_assessment.program_name == "SNAP"
        assert snap_assessment.confidence_score > 0.0
        assert snap_assessment.assessment_timestamp is not None
        
        # Should be eligible with mock income data
        assert snap_assessment.is_eligible is True
        assert len(snap_assessment.missing_documents) == 0
        
        # Test Medicaid eligibility assessment
        medicaid_assessment = self.agent.assess_eligibility(applicant, "Medicaid")
        assert medicaid_assessment.program_name == "Medicaid"
    
    def test_summary_report_generation(self):
        """Test summary report generation with processed documents"""
        # Create mix of processed documents with different statuses
        processed_documents = [
            self._create_mock_income_document(),
            self._create_mock_identity_document(),
            self._create_mock_utility_document(),
            self._create_mock_failed_document()
        ]
        
        # Generate summary report
        report = self.agent.generate_summary_report(processed_documents)
        
        # Verify report structure
        assert 'total_documents' in report
        assert 'by_status' in report
        assert 'by_type' in report
        assert 'average_confidence' in report
        assert 'requires_review' in report
        assert 'processing_errors' in report
        assert 'timestamp' in report
        
        # Verify report accuracy
        assert report['total_documents'] == len(processed_documents)
        assert report['average_confidence'] >= 0.0
        assert report['average_confidence'] <= 1.0
        
        # Should have at least one failed document
        assert ProcessingStatus.FAILED.value in report['by_status']
        assert len(report['processing_errors']) > 0
    
    @pytest.mark.asyncio
    async def test_end_to_end_eligibility_workflow(self):
        """Test complete end-to-end workflow from email to eligibility decision"""
        # Step 1: Process emails and documents
        processed_documents = await self.agent.process_email_batch(batch_size=3)
        assert len(processed_documents) > 0
        
        # Step 2: Create applicant record
        applicant = ApplicantRecord(
            applicant_id="E2E_TEST_001",
            first_name="End-to-End",
            last_name="Test",
            email="e2e@test.com",
            documents=processed_documents
        )
        
        # Step 3: Assess eligibility for multiple programs
        programs = ["SNAP", "Medicaid", "Housing_Assistance"]
        assessments = []
        
        for program in programs:
            assessment = self.agent.assess_eligibility(applicant, program)
            assessments.append(assessment)
            
            # Verify assessment structure
            assert assessment.applicant_id == applicant.applicant_id
            assert assessment.program_name == program
            assert assessment.confidence_score >= 0.0
            assert len(assessment.assessment_notes) > 0
        
        # Step 4: Generate summary report
        report = self.agent.generate_summary_report(processed_documents)
        
        # Verify complete workflow results
        assert len(assessments) == len(programs)
        assert report['total_documents'] == len(processed_documents)
        
        # At least some assessments should be completed successfully
        successful_assessments = [a for a in assessments if a.confidence_score > 0.5]
        assert len(successful_assessments) > 0
    
    def test_error_handling_integration(self):
        """Test error handling throughout the system"""
        # Test with invalid program name
        applicant = ApplicantRecord(
            applicant_id="ERROR_TEST_001",
            first_name="Error",
            last_name="Test",
            email="error@test.com"
        )
        
        assessment = self.agent.assess_eligibility(applicant, "INVALID_PROGRAM")
        assert assessment.is_eligible is False
        assert assessment.confidence_score == 0.0
        assert "unknown program" in assessment.assessment_notes[0].lower()
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent document processing"""
        # Process multiple batches concurrently
        tasks = [
            self.agent.process_email_batch(batch_size=2),
            self.agent.process_email_batch(batch_size=2)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Both batches should complete successfully
        assert len(results) == 2
        assert all(len(batch) > 0 for batch in results)
        
        # Documents should be processed independently
        all_docs = results[0] + results[1]
        doc_ids = [doc.metadata.document_id for doc in all_docs]
        assert len(doc_ids) == len(set(doc_ids))  # All unique IDs
    
    def test_data_persistence_simulation(self):
        """Test data structures for persistence readiness"""
        # Create complete applicant record
        applicant = ApplicantRecord(
            applicant_id="PERSIST_TEST_001",
            first_name="Persistence",
            last_name="Test",
            email="persist@test.com"
        )
        
        # Add documents and assessments
        applicant.add_document(self._create_mock_income_document())
        
        assessment = self.agent.assess_eligibility(applicant, "SNAP")
        applicant.eligibility_assessments.append(assessment)
        
        # Verify all data is serializable (important for database persistence)
        import json
        
        # Test serialization of key components
        try:
            # Metadata serialization
            metadata_dict = {
                'document_id': applicant.documents[0].metadata.document_id,
                'file_name': applicant.documents[0].metadata.file_name,
                'confidence_score': applicant.documents[0].metadata.confidence_score
            }
            json.dumps(metadata_dict)
            
            # Assessment serialization
            assessment_dict = {
                'applicant_id': assessment.applicant_id,
                'program_name': assessment.program_name,
                'is_eligible': assessment.is_eligible,
                'confidence_score': assessment.confidence_score,
                'assessed_income': assessment.assessed_income
            }
            json.dumps(assessment_dict)
            
        except TypeError as e:
            pytest.fail(f"Data structures are not serializable: {e}")
    
    def _create_mock_income_document(self):
        """Create a mock income verification document"""
        from src.models.document_types import DocumentMetadata, ExtractedData, ProcessedDocument
        
        metadata = DocumentMetadata(
            document_id="mock_income_001",
            file_name="pay_stub.pdf",
            file_size=2048,
            mime_type="application/pdf",
            upload_timestamp=datetime.now(),
            confidence_score=0.92
        )
        
        extracted_data = ExtractedData(document_type=DocumentType.INCOME_VERIFICATION)
        extracted_data.add_field("income_amount", 3500.0, 0.95)
        extracted_data.add_field("employee_name", "Test User", 0.88)
        extracted_data.add_field("pay_period", "Monthly", 0.85)
        
        return ProcessedDocument(
            metadata=metadata,
            document_type=DocumentType.INCOME_VERIFICATION,
            extracted_data=extracted_data,
            status=ProcessingStatus.COMPLETED
        )
    
    def _create_mock_identity_document(self):
        """Create a mock identity document"""
        from src.models.document_types import DocumentMetadata, ExtractedData, ProcessedDocument
        
        metadata = DocumentMetadata(
            document_id="mock_identity_001",
            file_name="drivers_license.jpg",
            file_size=1536,
            mime_type="image/jpeg",
            upload_timestamp=datetime.now(),
            confidence_score=0.89
        )
        
        extracted_data = ExtractedData(document_type=DocumentType.IDENTITY_DOCUMENT)
        extracted_data.add_field("full_name", "Test User", 0.94)
        extracted_data.add_field("address", "123 Test St, Test City, TS 12345", 0.87)
        
        return ProcessedDocument(
            metadata=metadata,
            document_type=DocumentType.IDENTITY_DOCUMENT,
            extracted_data=extracted_data,
            status=ProcessingStatus.COMPLETED
        )
    
    def _create_mock_utility_document(self):
        """Create a mock utility bill document"""
        from src.models.document_types import DocumentMetadata, ExtractedData, ProcessedDocument
        
        metadata = DocumentMetadata(
            document_id="mock_utility_001",
            file_name="electric_bill.pdf",
            file_size=1024,
            mime_type="application/pdf",
            upload_timestamp=datetime.now(),
            confidence_score=0.91
        )
        
        extracted_data = ExtractedData(document_type=DocumentType.UTILITY_BILL)
        extracted_data.add_field("service_address", "123 Test St, Test City, TS 12345", 0.93)
        extracted_data.add_field("amount_due", 125.50, 0.96)
        
        return ProcessedDocument(
            metadata=metadata,
            document_type=DocumentType.UTILITY_BILL,
            extracted_data=extracted_data,
            status=ProcessingStatus.COMPLETED
        )
    
    def _create_mock_failed_document(self):
        """Create a mock failed document for testing error scenarios"""
        from src.models.document_types import DocumentMetadata, ExtractedData, ProcessedDocument
        
        metadata = DocumentMetadata(
            document_id="mock_failed_001",
            file_name="corrupted_file.pdf",
            file_size=0,
            mime_type="application/pdf",
            upload_timestamp=datetime.now(),
            confidence_score=0.0
        )
        
        extracted_data = ExtractedData(document_type=DocumentType.UNKNOWN)
        extracted_data.validation_errors.append("File could not be processed")
        
        doc = ProcessedDocument(
            metadata=metadata,
            document_type=DocumentType.UNKNOWN,
            extracted_data=extracted_data,
            status=ProcessingStatus.FAILED
        )
        doc.review_notes.append("Processing failed due to file corruption")
        
        return doc


def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Document Eligibility Agent Integration Tests")
    print("=" * 70)
    
    test_class = TestDocumentEligibilityAgentIntegration()
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            print(f"Running {method_name}...", end=" ")
            
            # Setup test instance
            test_instance = TestDocumentEligibilityAgentIntegration()
            test_instance.setup_method()
            
            method = getattr(test_instance, method_name)
            
            if asyncio.iscoroutinefunction(method):
                asyncio.run(method())
            else:
                method()
            
            print("✅ PASSED")
            passed += 1
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed! System integration is working correctly.")
        return True
    else:
        print("⚠️  Some integration tests failed. Please check system integration.")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)