#!/usr/bin/env python3
"""
Document Eligibility Agent - Demo Script

Demonstrates the document processing pipeline in mock mode.
Run with: python demo.py
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set mock mode
os.environ["USE_MOCK_SERVICES"] = "true"


async def main():
    """Run the demo."""
    print("=" * 60)
    print("Document Eligibility Agent - Demo")
    print("NY State AI Hackathon")
    print("=" * 60)
    print()

    # Import after setting env
    from src.agent.document_processor import DocumentProcessor
    from src.agent.extraction_agent import ExtractionAgent
    from src.agent.validation_agent import ValidationAgent
    from src.models import DocumentStatus, DocumentType

    # Initialize components
    print("Initializing components...")
    processor = DocumentProcessor()
    extraction_agent = ExtractionAgent()
    validation_agent = ValidationAgent()
    print("  [OK] DocumentProcessor initialized")
    print("  [OK] ExtractionAgent initialized")
    print("  [OK] ValidationAgent initialized")
    print()

    # Demo 1: Email Polling
    print("-" * 60)
    print("DEMO 1: Email Inbox Polling")
    print("-" * 60)
    print()

    print("Polling email inbox for new document submissions...")
    documents = await processor.poll_email_inbox()
    print(f"  Found {len(documents)} documents in inbox")
    print()

    for doc in documents:
        print(f"  Document: {doc.id}")
        print(f"    Case ID: {doc.case_id}")
        print(f"    Type: {doc.document_type.value}")
        print(f"    Source: {doc.source.value}")
        print(f"    Filename: {doc.filename}")
        print(f"    Status: {doc.status.value}")
        print(f"    Duplicate: {doc.is_duplicate}")
        print()

    # Demo 2: Document Processing
    print("-" * 60)
    print("DEMO 2: Document Processing Pipeline")
    print("-" * 60)
    print()

    if documents:
        doc = documents[0]
        print(f"Processing document: {doc.id}")
        print(f"  Document type: {doc.document_type.value}")
        print()

        # Run processing
        processed_doc = await processor.process_document(str(doc.id))
        print(f"  [OK] Processing complete")
        print(f"    Status: {processed_doc.status.value}")
        print(f"    Overall Confidence: {processed_doc.overall_confidence:.2%}")
        print(f"    Page Count: {processed_doc.page_count}")
        print()

        # Show extractions
        extractions = processor.get_extractions(str(doc.id))
        print(f"  Extracted {len(extractions)} fields:")
        print()

        for ext in extractions:
            confidence_icon = "[OK]" if ext.confidence >= 0.85 else "[WARN]" if ext.confidence >= 0.7 else "[LOW]"
            pii_marker = " [PII]" if ext.is_pii else ""
            value_display = ext.get_display_value(include_pii=False) if ext.is_pii else ext.field_value

            print(f"    {confidence_icon} {ext.field_name}: {value_display}")
            print(f"       Confidence: {ext.confidence:.2%}{pii_marker}")

        print()

    # Demo 3: Validation
    print("-" * 60)
    print("DEMO 3: Document Validation")
    print("-" * 60)
    print()

    if documents:
        doc = documents[0]
        extractions = processor.get_extractions(str(doc.id))

        print(f"Validating document: {doc.id}")
        print(f"  Document type: {doc.document_type.value}")
        print()

        # Run validation
        overall_status, results = await validation_agent.validate_document(
            document_type=doc.document_type,
            extractions=extractions,
            case_data={
                "applicant_name": "John Doe",
                "address": "123 Main St, Albany, NY 12207",
            },
        )

        print(f"  Overall Status: {overall_status.value}")
        print(f"  Validation Results:")
        print()

        for result in results:
            status_icon = "[PASS]" if result.status.value == "passed" else "[WARN]" if result.status.value == "warning" else "[FAIL]"
            print(f"    {status_icon} {result.rule_name}: {result.status.value}")
            if result.message:
                print(f"       {result.message}")

        print()

    # Demo 4: Manual Upload Simulation
    print("-" * 60)
    print("DEMO 4: Manual Document Upload")
    print("-" * 60)
    print()

    print("Simulating manual document upload...")

    # Create a mock document directly
    from src.models.document import Document
    from src.models import DocumentSource, DocumentPriority

    manual_doc = Document(
        case_id="CASE-99999",
        document_type=DocumentType.W2,
        source=DocumentSource.UPLOAD,
        filename="manual_w2.pdf",
        file_size_bytes=2048,
        mime_type="application/pdf",
        priority=DocumentPriority.EXPEDITED,
    )

    # Store it
    processor._documents[str(manual_doc.id)] = manual_doc

    # Upload content to storage
    mock_content = b"Mock W-2 document content for manual upload test"
    blob_url = await processor._storage.upload_document(
        case_id=manual_doc.case_id,
        document_id=manual_doc.id,
        file_content=mock_content,
        filename=manual_doc.filename,
        content_type=manual_doc.mime_type,
    )
    manual_doc.blob_url = blob_url
    manual_doc.content_hash = processor._storage.compute_hash(mock_content)

    print(f"  [OK] Document created: {manual_doc.id}")
    print(f"    Case ID: {manual_doc.case_id}")
    print(f"    Type: {manual_doc.document_type.value}")
    print(f"    Priority: {manual_doc.priority.value}")
    print(f"    Status: {manual_doc.status.value}")
    print()

    # Process it
    print("Processing uploaded document...")
    processed = await processor.process_document(str(manual_doc.id))
    print(f"  [OK] Processing complete")
    print(f"    Status: {processed.status.value}")
    print(f"    Confidence: {processed.overall_confidence:.2%}")
    print()

    # Demo 5: Queue Statistics
    print("-" * 60)
    print("DEMO 5: Queue Statistics")
    print("-" * 60)
    print()

    all_docs = processor.get_all_documents()
    print(f"Total documents in queue: {len(all_docs)}")
    print()

    # Count by status
    status_counts = {}
    for doc in all_docs:
        status = doc.status.value
        status_counts[status] = status_counts.get(status, 0) + 1

    print("By Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print()

    # Count by type
    type_counts = {}
    for doc in all_docs:
        doc_type = doc.document_type.value
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

    print("By Type:")
    for doc_type, count in sorted(type_counts.items()):
        print(f"  {doc_type}: {count}")
    print()

    # Count by category
    category_counts = {}
    for doc in all_docs:
        category = processor.categorize_document(doc)
        category_counts[category] = category_counts.get(category, 0) + 1

    print("By Category:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")
    print()

    # Summary
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("The Document Eligibility Agent successfully demonstrated:")
    print("  [OK] Email inbox polling and attachment extraction")
    print("  [OK] Document type classification")
    print("  [OK] OCR and data extraction with confidence scoring")
    print("  [OK] PII detection and masking")
    print("  [OK] Document validation rules")
    print("  [OK] Manual document upload")
    print("  [OK] Queue management")
    print()
    print("To run the web interface:")
    print("  python -m src.main")
    print()
    print("Then open http://localhost:5001 in your browser.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
