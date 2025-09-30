# 🎬 Document Eligibility Agent - Execution Script

## 🎯 Quick Start Implementation Guide

This execution script provides a streamlined roadmap to build your Document Eligibility Processing Agent from start to finish.

## ⏱️ Timeline: 6-8 Hours

### Phase 1: Infrastructure Setup (1.5 hours)
```bash
# 1. Create Azure AI Document Intelligence service
az cognitiveservices account create --name "nyc-doc-intelligence" \
  --resource-group "nyc-hackathon-rg" --kind FormRecognizer --sku S0 --location eastus

# 2. Create Azure SQL Database for eligibility records
az sql server create --name "nyc-eligibility-server" --resource-group "nyc-hackathon-rg" \
  --location eastus --admin-user sqladmin --admin-password "SecurePass123!"

az sql db create --resource-group "nyc-hackathon-rg" --server "nyc-eligibility-server" \
  --name "eligibility_db" --service-objective Basic

# 3. Set up Microsoft Graph API permissions for email access
# Register app in Azure AD with Mail.Read permissions
az ad app create --display-name "Document Eligibility Agent"
```

### Phase 2: Email Processing Setup (1.5 hours)
```python
# 4. Configure Microsoft Graph client for email monitoring:
#    - OAuth authentication setup
#    - Email inbox monitoring
#    - Attachment extraction and filtering
#    - Document type identification

# 5. Implement email processing pipeline:
#    - Real-time email monitoring
#    - Attachment download and storage
#    - Initial document classification
#    - Queue management for processing
```

### Phase 3: Document Intelligence Integration (2 hours)
```python
# 6. Build AI-powered OCR processing:
#    - Azure AI Document Intelligence integration
#    - Custom model training for eligibility documents
#    - Text extraction and structure recognition
#    - Data validation and quality checks

# 7. Create document type processors:
#    - Income document parser (pay stubs, tax returns)
#    - Identity document parser (ID, SSN, birth certificates)  
#    - Housing document parser (leases, utility bills)
#    - Medical document parser (records, insurance cards)
```

### Phase 4: Semantic Kernel Orchestration (1.5 hours)
```python
# 8. Use Semantic Kernel to orchestrate document processing:
#    - DocumentClassificationPlugin
#    - DataExtractionPlugin
#    - EligibilityCalculationPlugin
#    - ValidationPlugin

# 9. Integrate Azure OpenAI for:
#    - Natural language processing of extracted text
#    - Data validation and error correction
#    - Eligibility rule interpretation
#    - Report generation
```

### Phase 5: Database & Web Interface (1.5 hours)
```python
# 10. Create database schema and data access layer
# 11. Build case worker dashboard for review and approvals
# 12. Implement audit trail and compliance reporting
# 13. Test end-to-end processing workflow
```

## 🔧 Key Implementation Steps

### Step 1: Microsoft Graph Email Integration
```python
# Configure Graph API client
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

class EmailMonitorService:
    def __init__(self, tenant_id, client_id, client_secret):
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id, 
            client_secret=client_secret
        )
        self.client = GraphServiceClient(
            credentials=self.credential,
            scopes=['https://graph.microsoft.com/.default']
        )
    
    async def monitor_eligibility_emails(self):
        # Monitor inbox for eligibility-related emails
        messages = await self.client.me.messages.get()
        return self.filter_eligibility_emails(messages)
```

### Step 2: Document Intelligence Service
```python
# Azure AI Document Intelligence integration
from azure.ai.formrecognizer import DocumentAnalysisClient

class DocumentIntelligenceService:
    def __init__(self, endpoint, key):
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
    
    async def analyze_document(self, document_bytes, document_type):
        # Use appropriate model based on document type
        if document_type == "income_statement":
            model_id = "prebuilt-receipt"  # Or custom trained model
        elif document_type == "identity_document":
            model_id = "prebuilt-idDocument"
        else:
            model_id = "prebuilt-document"
        
        poller = await self.client.begin_analyze_document(
            model_id=model_id,
            document=document_bytes
        )
        result = await poller.result()
        return self.extract_structured_data(result)
```

### Step 3: Database Schema Design
```sql
-- Core eligibility database schema
CREATE TABLE Applicants (
    applicant_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    first_name NVARCHAR(100) NOT NULL,
    last_name NVARCHAR(100) NOT NULL,
    ssn NVARCHAR(11),
    date_of_birth DATE,
    address NVARCHAR(500),
    phone NVARCHAR(20),
    email NVARCHAR(100),
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE Documents (
    document_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    applicant_id UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Applicants(applicant_id),
    document_type NVARCHAR(50) NOT NULL,
    original_filename NVARCHAR(255),
    file_path NVARCHAR(500),
    processing_status NVARCHAR(20) DEFAULT 'pending',
    extracted_data NVARCHAR(MAX), -- JSON format
    confidence_score DECIMAL(3,2),
    processed_date DATETIME2,
    created_date DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE EligibilityAssessments (
    assessment_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    applicant_id UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Applicants(applicant_id),
    program_type NVARCHAR(50) NOT NULL,
    eligibility_status NVARCHAR(20),
    monthly_income DECIMAL(10,2),
    household_size INT,
    assets_value DECIMAL(12,2),
    recommendation NVARCHAR(MAX),
    case_worker_id NVARCHAR(100),
    assessment_date DATETIME2 DEFAULT GETDATE()
);
```

### Step 4: Semantic Kernel Plugin Framework
```python
import semantic_kernel as sk
from semantic_kernel.plugin_definition import sk_function

class DocumentClassificationPlugin:
    @sk_function(description="Classify uploaded document by type and purpose")
    def classify_document(self, document_content: str, filename: str) -> str:
        # AI-powered document classification
        pass

class DataExtractionPlugin:
    @sk_function(description="Extract structured data from classified documents")
    def extract_eligibility_data(self, document_content: str, document_type: str) -> str:
        # Structured data extraction based on document type
        pass

class EligibilityCalculationPlugin:
    @sk_function(description="Calculate eligibility based on extracted data")
    def calculate_eligibility(self, applicant_data: str, program_requirements: str) -> str:
        # Eligibility determination logic
        pass
```

## 📊 Data Processing Workflow

### Document Type Classification:
1. **Email Attachment Analysis**: Identify potential eligibility documents
2. **Initial Classification**: Categorize by document type (income, identity, housing, medical)
3. **Confidence Scoring**: Assess classification accuracy
4. **Human Review Queue**: Flag uncertain classifications for manual review

### Data Extraction Pipeline:
1. **OCR Processing**: Extract text using Azure AI Document Intelligence
2. **Structure Recognition**: Identify key fields and data points
3. **Data Validation**: Verify extracted information accuracy
4. **Normalization**: Standardize data formats and values
5. **Database Storage**: Save structured data with audit trail

## 🧪 Testing Scenarios

### Scenario 1: SNAP Application Processing
```python
test_documents = [
    "pay_stub_jan_2024.pdf",
    "bank_statement_checking.pdf", 
    "utility_bill_electric.pdf",
    "drivers_license_scan.jpg"
]

expected_extraction = {
    "monthly_income": 3200.00,
    "bank_balance": 1250.00,
    "address_verified": True,
    "identity_confirmed": True
}
```

### Scenario 2: Medicaid Enrollment
```python
test_documents = [
    "medical_records_2024.pdf",
    "insurance_card_current.jpg",
    "prescription_list.pdf",
    "income_tax_return_2023.pdf"
]

expected_extraction = {
    "medical_conditions": ["diabetes", "hypertension"],
    "current_insurance": "employer_plan",
    "annual_income": 28000.00,
    "medical_expenses": 4500.00
}
```

## 🚀 Deployment Checklist

- [ ] Azure AI Document Intelligence service configured with custom models
- [ ] Microsoft Graph API permissions granted for email access
- [ ] Azure SQL Database created with eligibility schema
- [ ] Semantic Kernel plugins implemented and tested
- [ ] Document classification models trained and validated
- [ ] Data extraction accuracy verified (>95% target)
- [ ] Case worker dashboard deployed and accessible
- [ ] Audit trail and compliance reporting functional
- [ ] End-to-end processing workflow tested

## 📈 Success Metrics

- **Email Processing**: 100% of eligibility emails automatically detected
- **Document Classification**: 95%+ accuracy in document type identification
- **OCR Accuracy**: 98%+ text extraction accuracy across document types
- **Processing Speed**: <5 minutes average per document
- **Data Quality**: 95%+ accuracy in extracted structured data
- **Throughput**: Process 500+ documents per day per instance

## 🛟 Troubleshooting Quick Fixes

### Common Issues:
1. **Graph API Authentication**: Verify app registration and permissions
2. **OCR Quality**: Check document image quality and resolution
3. **Classification Errors**: Retrain models with additional samples
4. **Database Connection**: Validate connection strings and firewall rules

### Debug Commands:
```bash
# Test Graph API connection
python test_graph_connection.py

# Validate Document Intelligence service
python test_document_analysis.py sample_pay_stub.pdf

# Check database connectivity
python test_database_connection.py

# Run end-to-end processing test
python test_full_pipeline.py
```

## 🎯 Demo Flow (8 minutes)

### Setup (1 minute)
- Show case worker dashboard
- Display pending email queue
- Demonstrate document types supported

### Live Processing Demo (5 minutes)
1. **Email Receipt** (1 minute)
   - Receive email with eligibility documents
   - Show automatic detection and queuing

2. **Document Processing** (2 minutes)
   - Demonstrate OCR and data extraction
   - Show structured data output
   - Highlight confidence scores and validation

3. **Eligibility Assessment** (2 minutes)
   - Show preliminary eligibility calculation
   - Display case worker review interface
   - Demonstrate approval workflow

### Technical Architecture (2 minutes)
- **Multi-Agent Orchestration**: Document classification and processing agents
- **AI Integration**: Document Intelligence, OpenAI, and Semantic Kernel
- **Data Pipeline**: Email → OCR → Validation → Database → Assessment

Ready to build your document eligibility agent? Follow the [step_by_step.md](./step_by_step.md) for detailed implementation! 📧