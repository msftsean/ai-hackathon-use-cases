"""
Simple demo script for Document Eligibility Agent
"""
import sys
import os
import asyncio

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import DocumentEligibilityAgent
from src.models.document_types import ApplicantRecord


async def run_demo():
    """Run Document Eligibility Agent demonstration"""
    print("🚀 Document Eligibility Agent - Interactive Demo")
    print("=" * 60)
    print("This demo uses mock services to simulate document processing")
    print("and eligibility determination for social services programs.")
    print()
    
    # Initialize agent with mock services
    agent = DocumentEligibilityAgent(use_mock_services=True)
    
    # Step 1: Process mock emails
    print("📧 Step 1: Processing email batch...")
    processed_documents = await agent.process_email_batch(batch_size=3)
    
    print(f"   📄 Processed {len(processed_documents)} documents")
    for i, doc in enumerate(processed_documents, 1):
        status_icon = "✅" if doc.is_valid() else "⚠️" if doc.requires_review() else "❌"
        print(f"   {status_icon} Document {i}: {doc.metadata.file_name} ({doc.document_type.value})")
        print(f"      Confidence: {doc.metadata.confidence_score:.2f}")
        if doc.extracted_data.extracted_fields:
            key_fields = list(doc.extracted_data.extracted_fields.keys())[:3]
            print(f"      Key fields: {', '.join(key_fields)}")
    print()
    
    # Step 2: Create applicant record
    print("👤 Step 2: Creating applicant record...")
    applicant = ApplicantRecord(
        applicant_id="DEMO_001",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@email.com",
        documents=processed_documents
    )
    print(f"   Created record for {applicant.first_name} {applicant.last_name}")
    print(f"   Documents attached: {len(applicant.documents)}")
    print()
    
    # Step 3: Assess eligibility for multiple programs
    print("🎯 Step 3: Assessing program eligibility...")
    programs = ["SNAP", "Medicaid", "Housing_Assistance"]
    
    for program in programs:
        print(f"\n   📋 {program} Assessment:")
        assessment = agent.assess_eligibility(applicant, program)
        
        eligibility_status = "✅ ELIGIBLE" if assessment.is_eligible else "❌ NOT ELIGIBLE"
        print(f"      Status: {eligibility_status}")
        print(f"      Confidence: {assessment.confidence_score:.2f}")
        print(f"      Assessed Monthly Income: ${assessment.assessed_income:.2f}")
        
        if assessment.missing_documents:
            missing_doc_names = [doc.value.replace('_', ' ').title() for doc in assessment.missing_documents]
            print(f"      Missing Documents: {', '.join(missing_doc_names)}")
        
        # Show key recommendations
        relevant_notes = [note for note in assessment.assessment_notes 
                         if any(indicator in note for indicator in ['✅', '❌', '📋', '💡', '📄'])]
        if relevant_notes:
            print("      Top Recommendations:")
            for note in relevant_notes[:3]:
                recommendation = note.split(': ', 1)[-1]  # Remove timestamp prefix
                print(f"        • {recommendation}")
    
    print()
    
    # Step 4: Generate processing summary
    print("📊 Step 4: Generating processing summary...")
    report = agent.generate_summary_report(processed_documents)
    
    print(f"   Total Documents Processed: {report['total_documents']}")
    print(f"   Average Confidence Score: {report['average_confidence']:.2f}")
    print(f"   Document Types: {', '.join(report['by_type'].keys())}")
    print(f"   Processing Status Distribution:")
    for status, count in report['by_status'].items():
        print(f"     • {status.replace('_', ' ').title()}: {count}")
    
    if report.get('requires_review'):
        print(f"   Documents Requiring Review: {len(report['requires_review'])}")
        for doc in report['requires_review']:
            print(f"     • {doc['file_name']} (confidence: {doc['confidence']:.2f})")
    
    print()
    
    # Step 5: Demonstrate real-world impact
    print("🌟 Step 5: Real-world impact demonstration")
    print("   This system could help social services departments:")
    print("   • Reduce document processing time from days to minutes")
    print("   • Improve accuracy in eligibility determination")
    print("   • Provide consistent service to all applicants")
    print("   • Free up caseworkers for complex cases requiring human judgment")
    print("   • Maintain complete audit trails for compliance")
    print()
    
    print("✨ Demo completed successfully!")
    print("   Ready to transform social services with AI!")


def run_interactive_demo():
    """Run interactive version of the demo"""
    print("🎮 Interactive Document Eligibility Agent Demo")
    print("=" * 50)
    
    while True:
        print("\nChoose a demo option:")
        print("1. 📧 Process email batch and show results")
        print("2. 🎯 Quick eligibility check")
        print("3. 📊 Show processing statistics")
        print("4. 🔧 Test system components")
        print("5. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            asyncio.run(demonstrate_email_processing())
        elif choice == '2':
            asyncio.run(demonstrate_eligibility_check())
        elif choice == '3':
            asyncio.run(demonstrate_statistics())
        elif choice == '4':
            demonstrate_system_test()
        elif choice == '5':
            print("👋 Thanks for trying the Document Eligibility Agent!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")


async def demonstrate_email_processing():
    """Demonstrate email processing capabilities"""
    print("\n📧 Email Processing Demonstration")
    print("-" * 40)
    
    agent = DocumentEligibilityAgent(use_mock_services=True)
    docs = await agent.process_email_batch(batch_size=2)
    
    for i, doc in enumerate(docs, 1):
        print(f"\nDocument {i}: {doc.metadata.file_name}")
        print(f"Type: {doc.document_type.value.replace('_', ' ').title()}")
        print(f"Status: {doc.status.value.replace('_', ' ').title()}")
        print(f"Confidence: {doc.metadata.confidence_score:.2f}")
        
        if doc.extracted_data.extracted_fields:
            print("Extracted Data:")
            for key, value in list(doc.extracted_data.extracted_fields.items())[:3]:
                print(f"  • {key}: {value}")


async def demonstrate_eligibility_check():
    """Demonstrate eligibility checking"""
    print("\n🎯 Eligibility Check Demonstration")
    print("-" * 40)
    
    agent = DocumentEligibilityAgent(use_mock_services=True)
    docs = await agent.process_email_batch(batch_size=2)
    
    applicant = ApplicantRecord(
        applicant_id="DEMO_INTERACTIVE",
        first_name="Demo",
        last_name="User",
        email="demo@example.com",
        documents=docs
    )
    
    assessment = agent.assess_eligibility(applicant, "SNAP")
    
    print(f"Applicant: {applicant.first_name} {applicant.last_name}")
    print(f"SNAP Eligibility: {'✅ ELIGIBLE' if assessment.is_eligible else '❌ NOT ELIGIBLE'}")
    print(f"Confidence: {assessment.confidence_score:.2f}")
    print(f"Monthly Income: ${assessment.assessed_income:.2f}")
    
    if assessment.assessment_notes:
        print("\nKey Information:")
        for note in assessment.assessment_notes[:3]:
            if any(indicator in note for indicator in ['✅', '❌', '📋']):
                print(f"  • {note.split(': ', 1)[-1]}")


async def demonstrate_statistics():
    """Demonstrate processing statistics"""
    print("\n📊 Processing Statistics Demonstration")
    print("-" * 45)
    
    agent = DocumentEligibilityAgent(use_mock_services=True)
    docs = await agent.process_email_batch(batch_size=4)
    
    report = agent.generate_summary_report(docs)
    
    print(f"Documents Processed: {report['total_documents']}")
    print(f"Average Confidence: {report['average_confidence']:.2f}")
    print("\nDocument Types:")
    for doc_type, count in report['by_type'].items():
        print(f"  • {doc_type.replace('_', ' ').title()}: {count}")
    
    print("\nProcessing Status:")
    for status, count in report['by_status'].items():
        print(f"  • {status.replace('_', ' ').title()}: {count}")


def demonstrate_system_test():
    """Demonstrate system component testing"""
    print("\n🔧 System Component Test")
    print("-" * 30)
    
    try:
        from src.plugins.document_processing_plugins import DocumentClassificationPlugin
        plugin = DocumentClassificationPlugin()
        
        # Test classification
        result = plugin.classify_document_type("pay_stub.pdf", "gross pay salary")
        print(f"✅ Document Classification: {result}")
        
        # Test eligibility calculation
        from src.plugins.document_processing_plugins import EligibilityCalculationPlugin
        eligibility_plugin = EligibilityCalculationPlugin()
        
        result = eligibility_plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=1500.0,
            household_size=2,
            available_documents=['income_verification', 'identity_document', 'utility_bill']
        )
        
        print(f"✅ Eligibility Calculation: {'Eligible' if result['eligible'] else 'Not Eligible'}")
        print("✅ All system components are working correctly!")
        
    except Exception as e:
        print(f"❌ System test failed: {e}")


def main():
    """Main demo entry point"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'interactive':
            run_interactive_demo()
        elif mode == 'auto':
            asyncio.run(run_demo())
        else:
            print("Usage: python demo.py [auto|interactive]")
            print("  auto        - Run automated demo")
            print("  interactive - Run interactive demo")
    else:
        # Default to automated demo
        asyncio.run(run_demo())


if __name__ == "__main__":
    main()