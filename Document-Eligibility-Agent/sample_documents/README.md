# Sample Documents

This directory contains sample documents for testing the Document Eligibility Agent.

## Available Samples

### W-2 Tax Form (w2_sample.pdf)
- Employer: ACME Corporation
- Tax Year: 2025
- Wages: $52,500.00
- Federal Tax Withheld: $7,875.00
- Employee SSN: XXX-XX-1234 (masked)

### Pay Stub (paystub_sample.pdf)
- Employer: ACME Corporation
- Employee: John Doe
- Pay Period: 12/01/2025 - 12/15/2025
- Pay Date: 12/20/2025
- Gross Pay: $2,187.50
- Net Pay: $1,750.00

### Utility Bill (utility_bill_sample.pdf)
- Provider: Con Edison
- Service Address: 123 Main St, Albany, NY 12207
- Bill Date: 12/15/2025
- Amount Due: $145.67
- Account Number: ****5678 (masked)

## Using Sample Documents

These documents are used by the mock extraction service to demonstrate the
document processing pipeline without requiring Azure Document Intelligence.

To test with these samples:

1. Start the application in mock mode:
   ```bash
   export USE_MOCK_SERVICES=true
   python demo.py
   ```

2. Upload a sample document via the web interface at http://localhost:5001

3. Observe the extracted fields and confidence scores

## Creating Your Own Test Documents

For testing with real Azure Document Intelligence:

1. Create PDF documents with realistic data
2. Ensure documents are high quality (300+ DPI if scanned)
3. Use standard document formats
4. Test with both clean and challenging documents (rotated, low quality, etc.)

## Note

These are placeholder descriptions. In a real deployment, actual PDF files
would be placed here for testing purposes.
