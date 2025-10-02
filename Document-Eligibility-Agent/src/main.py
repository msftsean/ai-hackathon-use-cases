"""
Main application for Document Eligibility Processing Agent
"""
import os
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from .services.email_processor import EmailProcessorService, MockEmailProcessorService
from .services.document_intelligence import DocumentIntelligenceService, MockDocumentIntelligenceService
from .plugins.document_processing_plugins import (
    DocumentClassificationPlugin, 
    DataExtractionPlugin,
    EligibilityCalculationPlugin
)
from .models.document_types import (
    DocumentType, ProcessedDocument, ApplicantRecord, 
    EligibilityAssessment, ProcessingStatus
)


class DocumentEligibilityAgent:
    """Main agent for processing eligibility documents"""
    
    def __init__(self, use_mock_services: bool = False):
        """
        Initialize the Document Eligibility Agent
        
        Args:
            use_mock_services: Whether to use mock services for testing
        """
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        if use_mock_services:
            self.email_service = MockEmailProcessorService()
            self.doc_intelligence = MockDocumentIntelligenceService()
        else:
            self.email_service = EmailProcessorService()
            self.doc_intelligence = DocumentIntelligenceService()
        
        # Initialize Semantic Kernel plugins
        self.classification_plugin = DocumentClassificationPlugin()
        self.extraction_plugin = DataExtractionPlugin()
        self.eligibility_plugin = EligibilityCalculationPlugin()
        
        self.logger.info("Document Eligibility Agent initialized")
    
    async def process_email_batch(self, user_id: str = 'me', batch_size: int = 5) -> List[ProcessedDocument]:
        """
        Process a batch of emails and extract eligibility documents
        
        Args:
            user_id: Email user ID to process
            batch_size: Number of emails to process
            
        Returns:
            List of processed documents
        """
        try:
            self.logger.info(f"Processing email batch for user: {user_id}")
            
            # Get document metadata from emails
            document_metadata_list = await self.email_service.process_email_batch(user_id, batch_size)
            
            processed_documents = []
            for metadata in document_metadata_list:
                try:
                    # Download document content
                    content = await self.email_service.download_attachment(
                        user_id, metadata.email_id, metadata.document_id
                    )
                    
                    if content:
                        # Process the document
                        processed_doc = await self.process_single_document(metadata, content)
                        processed_documents.append(processed_doc)
                        
                except Exception as e:
                    self.logger.error(f"Error processing document {metadata.document_id}: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully processed {len(processed_documents)} documents")
            return processed_documents
            
        except Exception as e:
            self.logger.error(f"Error processing email batch: {str(e)}")
            return []
    
    async def process_single_document(self, metadata, content: bytes) -> ProcessedDocument:
        """
        Process a single document through the complete pipeline
        
        Args:
            metadata: Document metadata
            content: Document content as bytes
            
        Returns:
            Processed document with extracted data
        """
        try:
            self.logger.info(f"Processing document: {metadata.file_name}")
            
            # Step 1: Classify document type
            initial_classification = self.email_service.classify_document_type(metadata.file_name)
            
            # Step 2: Extract data using Document Intelligence
            extracted_data = await self.doc_intelligence.analyze_document(content, initial_classification)
            
            # Step 3: Validate and enhance classification using Semantic Kernel
            if extracted_data.extracted_fields:
                enhanced_classification = self.classification_plugin.classify_document_type(
                    metadata.file_name,
                    extracted_data.get_field("full_text", "")
                )
                
                # Update document type if enhanced classification is more confident
                if enhanced_classification != DocumentType.UNKNOWN.value:
                    extracted_data.document_type = DocumentType(enhanced_classification)
            
            # Step 4: Validate extraction quality
            validation_result = self.extraction_plugin.validate_extraction_quality(
                extracted_data.extracted_fields
            )
            
            # Step 5: Determine processing status
            status = ProcessingStatus.COMPLETED
            confidence_score = validation_result.get('quality_score', 0.0)
            
            if confidence_score < 0.6:
                status = ProcessingStatus.REQUIRES_REVIEW
            elif len(extracted_data.validation_errors) > 0:
                status = ProcessingStatus.FAILED
            
            # Update metadata with confidence score
            metadata.confidence_score = confidence_score
            
            # Create processed document
            processed_doc = ProcessedDocument(
                metadata=metadata,
                document_type=extracted_data.document_type,
                extracted_data=extracted_data,
                status=status,
                processing_timestamp=datetime.now()
            )
            
            # Add processing notes
            if validation_result.get('issues'):
                processed_doc.review_notes.extend(validation_result['issues'])
            
            self.logger.info(f"Document processed successfully: {metadata.file_name} ({status.value})")
            return processed_doc
            
        except Exception as e:
            self.logger.error(f"Error processing document {metadata.file_name}: {str(e)}")
            
            # Create failed processing result
            processed_doc = ProcessedDocument(
                metadata=metadata,
                document_type=DocumentType.UNKNOWN,
                extracted_data=extracted_data if 'extracted_data' in locals() else None,
                status=ProcessingStatus.FAILED,
                processing_timestamp=datetime.now()
            )
            processed_doc.review_notes.append(f"Processing failed: {str(e)}")
            return processed_doc
    
    def assess_eligibility(
        self, 
        applicant_record: ApplicantRecord, 
        program_name: str = 'SNAP'
    ) -> EligibilityAssessment:
        """
        Assess eligibility for a benefit program based on processed documents
        
        Args:
            applicant_record: Complete applicant record with documents
            program_name: Name of benefit program to assess
            
        Returns:
            Eligibility assessment result
        """
        try:
            self.logger.info(f"Assessing {program_name} eligibility for {applicant_record.applicant_id}")
            
            # Extract key information from documents
            monthly_income = 0.0
            household_size = 1
            available_document_types = []
            
            for doc in applicant_record.documents:
                if doc.status == ProcessingStatus.COMPLETED:
                    available_document_types.append(doc.document_type.value)
                    
                    # Extract income information
                    if doc.document_type == DocumentType.INCOME_VERIFICATION:
                        income_amount = doc.extracted_data.get_field("income_amount", 0)
                        if income_amount:
                            try:
                                monthly_income = float(str(income_amount).replace('$', '').replace(',', ''))
                            except (ValueError, TypeError):
                                pass
            
            # Calculate eligibility using Semantic Kernel plugin
            assessment_result = self.eligibility_plugin.calculate_eligibility(
                program_name=program_name,
                monthly_income=monthly_income,
                household_size=household_size,
                available_documents=available_document_types
            )
            
            # Create eligibility assessment
            assessment = EligibilityAssessment(
                applicant_id=applicant_record.applicant_id,
                program_name=program_name,
                is_eligible=assessment_result.get('eligible', False),
                confidence_score=assessment_result.get('confidence', 0.0),
                assessed_income=monthly_income,
                household_size=household_size,
                missing_documents=[
                    DocumentType(doc) for doc in assessment_result.get('missing_documents', [])
                ],
                assessment_timestamp=datetime.now()
            )
            
            # Add assessment notes
            if assessment_result.get('reason'):
                assessment.add_note(assessment_result['reason'])
            
            # Generate recommendations
            recommendations = self.eligibility_plugin.generate_recommendations(
                assessment_result,
                {
                    'applicant_id': applicant_record.applicant_id,
                    'monthly_income': monthly_income,
                    'available_documents': available_document_types
                }
            )
            
            for recommendation in recommendations:
                assessment.add_note(recommendation)
            
            self.logger.info(f"Eligibility assessment completed: {assessment.is_eligible}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing eligibility: {str(e)}")
            
            # Return failed assessment
            return EligibilityAssessment(
                applicant_id=applicant_record.applicant_id,
                program_name=program_name,
                is_eligible=False,
                confidence_score=0.0,
                assessed_income=0.0,
                household_size=1,
                assessment_timestamp=datetime.now()
            )
    
    def generate_summary_report(self, processed_documents: List[ProcessedDocument]) -> Dict[str, Any]:
        """
        Generate summary report of processed documents
        
        Args:
            processed_documents: List of processed documents
            
        Returns:
            Summary report with statistics and insights
        """
        try:
            report = {
                'total_documents': len(processed_documents),
                'by_status': {},
                'by_type': {},
                'average_confidence': 0.0,
                'requires_review': [],
                'processing_errors': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # Calculate statistics
            total_confidence = 0.0
            for doc in processed_documents:
                # Status breakdown
                status = doc.status.value
                report['by_status'][status] = report['by_status'].get(status, 0) + 1
                
                # Type breakdown
                doc_type = doc.document_type.value
                report['by_type'][doc_type] = report['by_type'].get(doc_type, 0) + 1
                
                # Confidence tracking
                total_confidence += doc.metadata.confidence_score
                
                # Documents requiring review
                if doc.requires_review():
                    report['requires_review'].append({
                        'document_id': doc.metadata.document_id,
                        'file_name': doc.metadata.file_name,
                        'confidence': doc.metadata.confidence_score,
                        'issues': doc.review_notes
                    })
                
                # Processing errors
                if doc.status == ProcessingStatus.FAILED:
                    report['processing_errors'].append({
                        'document_id': doc.metadata.document_id,
                        'file_name': doc.metadata.file_name,
                        'errors': doc.review_notes
                    })
            
            if processed_documents:
                report['average_confidence'] = total_confidence / len(processed_documents)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


async def main():
    """Main function for running the Document Eligibility Agent"""
    
    # Initialize agent with mock services for demonstration
    agent = DocumentEligibilityAgent(use_mock_services=True)
    
    print("🚀 Document Eligibility Agent - Demo Mode")
    print("=" * 50)
    
    # Process email batch
    print("📧 Processing email batch...")
    processed_documents = await agent.process_email_batch()
    
    # Generate summary report
    print("\n📊 Generating summary report...")
    report = agent.generate_summary_report(processed_documents)
    
    print(f"\n📋 Processing Summary:")
    print(f"Total Documents: {report['total_documents']}")
    print(f"Average Confidence: {report['average_confidence']:.2f}")
    print(f"By Status: {report['by_status']}")
    print(f"By Type: {report['by_type']}")
    
    if report['requires_review']:
        print(f"\n⚠️  Documents Requiring Review: {len(report['requires_review'])}")
        for doc in report['requires_review']:
            print(f"  • {doc['file_name']} (confidence: {doc['confidence']:.2f})")
    
    # Create sample applicant record and assess eligibility
    if processed_documents:
        print("\n🎯 Assessing SNAP Eligibility...")
        applicant = ApplicantRecord(
            applicant_id="APP_001",
            first_name="John",
            last_name="Doe",
            email="john.doe@email.com",
            documents=processed_documents
        )
        
        assessment = agent.assess_eligibility(applicant, "SNAP")
        
        print(f"Eligibility Result: {'✅ ELIGIBLE' if assessment.is_eligible else '❌ NOT ELIGIBLE'}")
        print(f"Confidence: {assessment.confidence_score:.2f}")
        print(f"Assessed Income: ${assessment.assessed_income:.2f}")
        
        if assessment.missing_documents:
            print(f"Missing Documents: {[doc.value for doc in assessment.missing_documents]}")
        
        print("\nRecommendations:")
        for note in assessment.assessment_notes[-5:]:  # Show last 5 notes
            if note.startswith(('✅', '❌', '📋', '💡', '📄', '📞', '🌐')):
                print(f"  {note.split(': ', 1)[-1]}")
    
    print("\n✨ Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())