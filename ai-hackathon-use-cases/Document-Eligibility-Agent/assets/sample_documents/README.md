# Sample Documents for Eligibility Processing Testing

This folder contains sample documents that represent typical eligibility-related documents submitted to social services departments.

## 📄 Document Types Included

### Financial Documents
- **pay_stub_sample.pdf** - Sample pay stub showing income verification
- **tax_return_w2_sample.pdf** - W-2 form for annual income verification
- **bank_statement_sample.pdf** - Bank statement showing assets and account activity
- **unemployment_benefits_sample.pdf** - Unemployment benefit statement

### Identity Documents  
- **drivers_license_sample.jpg** - Sample driver's license for identity verification
- **birth_certificate_sample.pdf** - Birth certificate for age and citizenship verification
- **social_security_card_sample.jpg** - Social Security card sample

### Housing Documents
- **utility_bill_electric_sample.pdf** - Electric utility bill for address verification
- **lease_agreement_sample.pdf** - Rental lease agreement
- **mortgage_statement_sample.pdf** - Mortgage payment statement

### Medical Documents
- **medical_record_sample.pdf** - Sample medical record for disability verification
- **insurance_card_sample.jpg** - Health insurance card sample
- **prescription_list_sample.pdf** - Current prescription medications list

## 🔧 Usage in Testing

These sample documents are designed to test:

1. **Document Classification** - AI agent should correctly identify document types
2. **OCR Accuracy** - Text extraction from various document formats
3. **Data Extraction** - Structured data parsing from unstructured documents
4. **Validation Logic** - Data quality and completeness checks
5. **Eligibility Calculation** - Automated benefit qualification assessment

## 📊 Expected Extraction Results

### Pay Stub Sample:
```json
{
  "employee_name": "John Smith",
  "employer_name": "NYC Department of Education", 
  "gross_pay": 3200.00,
  "net_pay": 2450.00,
  "pay_period": "01/01/2024 - 01/15/2024",
  "year_to_date_gross": 3200.00
}
```

### Utility Bill Sample:
```json
{
  "service_address": "123 Main Street, New York, NY 10001",
  "account_holder": "John Smith",
  "utility_type": "electric",
  "amount_due": 125.50,
  "due_date": "02/15/2024",
  "provider_name": "Con Edison"
}
```

### Driver's License Sample:
```json
{
  "full_name": "John Smith",
  "date_of_birth": "03/15/1985",
  "address": "123 Main Street, New York, NY 10001",
  "license_number": "123456789",
  "expiration_date": "03/15/2027",
  "state_issued": "NY"
}
```

## 🧪 Test Scenarios

### SNAP Benefits Application:
- Documents: pay_stub_sample.pdf, bank_statement_sample.pdf, utility_bill_electric_sample.pdf
- Expected: Income verification, asset check, address confirmation
- Eligibility: Qualified based on income guidelines

### Medicaid Enrollment:
- Documents: medical_record_sample.pdf, insurance_card_sample.jpg, tax_return_w2_sample.pdf
- Expected: Medical need assessment, income verification, current coverage check
- Eligibility: Qualified for supplemental coverage

### Housing Assistance:
- Documents: lease_agreement_sample.pdf, pay_stub_sample.pdf, utility_bill_electric_sample.pdf
- Expected: Housing cost verification, income-to-rent ratio, residency proof
- Eligibility: Qualified for rental assistance program

## 🔒 Privacy Note

All sample documents contain fictional information and are created solely for testing and demonstration purposes. No real personal information is included in these samples.