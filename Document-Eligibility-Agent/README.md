# 📧 Document Eligibility Processing Agent

## 📋 Overview

Create an intelligent agent that automatically processes emails to identify eligibility-related documents (income statements, medical records, utility bills, etc.), extracts and processes them using AI-powered OCR, and stores the structured data in a database for eligibility determination. This solution dramatically reduces manual processing time for social services departments.

Perfect for hackathon teams looking to build AI solutions that directly impact social services efficiency and citizen experience! This use case combines document intelligence, email automation, and structured data processing.

## 🚀 Quick Start

### Option 1: GitHub Codespaces (Recommended)
1. **Click "Use this template" or "Code" → "Create codespace"**
2. **Wait for environment setup** (automatically installs dependencies)
3. **Configure your API keys** (see Configuration section below)
4. **Run the test script**: `python test_setup.py`
5. **Start processing documents**: `python src/main.py`

### Option 2: Local Development
```bash
git clone <repository-url>
cd Document-Eligibility-Agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python test_setup.py
```

## ⚙️ Configuration

Choose your preferred setup method:

### Method 1: Environment File (.env) - Recommended
```bash
# Create .env file in project root
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_KEY=your_key_here
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_doc_intel_endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_doc_intel_key
AZURE_SQL_CONNECTION_STRING=your_sql_connection_string
MICROSOFT_GRAPH_CLIENT_ID=your_graph_client_id
MICROSOFT_GRAPH_CLIENT_SECRET=your_graph_client_secret
```

### Method 2: Environment Variables
```bash
export AZURE_OPENAI_ENDPOINT="your_endpoint_here"
export AZURE_OPENAI_API_KEY="your_key_here"
export AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="your_doc_intel_endpoint"
export AZURE_DOCUMENT_INTELLIGENCE_KEY="your_doc_intel_key"
export AZURE_SQL_CONNECTION_STRING="your_sql_connection_string"
export MICROSOFT_GRAPH_CLIENT_ID="your_graph_client_id"
export MICROSOFT_GRAPH_CLIENT_SECRET="your_graph_client_secret"
```

### Method 3: Configuration File
Create `config/settings.json`:
```json
{
  "azure_openai": {
    "endpoint": "your_endpoint_here",
    "api_key": "your_key_here"
  },
  "document_intelligence": {
    "endpoint": "your_doc_intel_endpoint",
    "key": "your_doc_intel_key"
  },
  "sql_database": {
    "connection_string": "your_sql_connection_string"
  },
  "microsoft_graph": {
    "client_id": "your_graph_client_id",
    "client_secret": "your_graph_client_secret"
  }
}
```

## 🏗️ Technology Stack

- **Azure AI Document Intelligence**: Advanced OCR and document parsing
- **Microsoft Graph API**: Email processing and attachment handling  
- **Semantic Kernel 1.37.0**: Document classification and data extraction orchestration
- **Azure OpenAI GPT-4**: Natural language processing for data validation
- **Azure SQL Database**: Structured data storage for eligibility records
- **Python 3.8+**: Core development platform
- **FastAPI**: Web API framework for dashboard interface
- **Azure Cognitive Services**: Additional AI capabilities for document analysis

## 🎯 Challenge Goals

- Automatically monitor and parse incoming emails for eligibility documents
- Identify and classify different document types (income proof, medical records, utility bills)
- Extract text and structured data using AI-powered OCR and document intelligence
- Validate and normalize extracted data for consistency
- Store processed information in a structured database
- Generate eligibility assessment reports and recommendations
- Maintain audit trails and compliance with privacy regulations

## 🛠️ Technology Stack

- **Azure AI Foundry**: AI orchestration and workflow management
- **Azure AI Document Intelligence**: Advanced OCR and document parsing
- **Microsoft Graph API**: Email processing and attachment handling
- **Semantic Kernel**: Document classification and data extraction orchestration
- **Azure OpenAI**: Natural language processing for data validation and enhancement
- **Azure SQL Database**: Structured data storage for eligibility records
- **Azure Cognitive Services**: Additional AI capabilities for document analysis
- **Power Platform**: Optional workflow automation and approvals

## 🏗️ Architecture

```
Email Inbox → Graph API → Document Classification → AI Document Intelligence
     ↓                                                         ↓
Attachment                                              Text Extraction
Extraction                                                     ↓
     ↓                                                Data Validation
Semantic Kernel                                              ↓
Orchestration                                        Database Storage
     ↓                                                       ↓
Document Type → OCR Processing → Data Extraction → Eligibility
Classification                                       Assessment
```

## 💡 Key Features

1. **Intelligent Email Processing**: Automatically identify eligibility-related emails and attachments
2. **Document Classification**: Use AI to categorize documents by type and purpose
3. **Advanced OCR**: Extract text from images, PDFs, and scanned documents
4. **Data Structuring**: Convert unstructured document content into structured database records
5. **Validation & Quality Control**: Verify extracted data accuracy and completeness
6. **Eligibility Assessment**: Generate preliminary eligibility recommendations
7. **Audit & Compliance**: Maintain complete processing history and data lineage

## 📊 Document Types Supported

### Financial Documents:
- **Pay Stubs**: Income verification, employment status
- **Tax Returns**: Annual income, dependents, filing status
- **Bank Statements**: Asset verification, transaction history
- **Benefit Statements**: Social Security, unemployment, disability payments

### Identity & Personal Documents:
- **Driver's License**: Identity verification, address confirmation
- **Birth Certificates**: Age verification, dependent relationships
- **Social Security Cards**: SSN verification, citizenship status
- **Passport/ID Cards**: Identity and residency verification

### Household & Living Situation:
- **Utility Bills**: Address verification, household composition
- **Rent/Mortgage Statements**: Housing costs, residency proof
- **Lease Agreements**: Rental obligations, authorized occupants
- **Property Tax Bills**: Homeownership verification, property value

### Medical & Healthcare:
- **Medical Records**: Disability documentation, treatment history
- **Insurance Cards**: Coverage verification, medical needs
- **Prescription Records**: Medical expenses, ongoing treatments
- **Doctor's Notes**: Disability assessments, work restrictions

## 🚀 Success Metrics

- **Processing Speed**: Reduce document processing time from hours to minutes
- **Accuracy**: 95%+ accuracy in data extraction and classification
- **Volume Handling**: Process 1000+ documents per day automatically
- **Error Reduction**: 80%+ reduction in manual data entry errors
- **Compliance**: 100% audit trail maintenance and privacy protection
- **User Satisfaction**: Streamlined workflow for case workers

## 📂 Project Structure

```
Document-Eligibility-Agent/
├── src/
│   ├── agents/
│   │   ├── email_monitor_agent.py
│   │   ├── document_classifier_agent.py
│   │   ├── ocr_processor_agent.py
│   │   └── eligibility_assessor_agent.py
│   ├── services/
│   │   ├── graph_email_service.py
│   │   ├── document_intelligence_service.py
│   │   ├── database_service.py
│   │   └── validation_service.py
│   ├── models/
│   │   ├── document_types.py
│   │   ├── applicant_record.py
│   │   └── eligibility_assessment.py
│   ├── processors/
│   │   ├── income_document_processor.py
│   │   ├── identity_document_processor.py
│   │   ├── housing_document_processor.py
│   │   └── medical_document_processor.py
│   ├── plugins/
│   │   ├── document_classification_plugin.py
│   │   ├── data_extraction_plugin.py
│   │   └── eligibility_calculation_plugin.py
│   └── web/
│       ├── dashboard.py
│       ├── case_worker_interface.py
│       ├── templates/
│       └── static/
├── assets/
│   ├── sample_documents/
│   ├── classification_models/
│   ├── validation_rules/
│   └── database_schemas/
├── README.md
├── execution_script.md
├── step_by_step.md
└── requirements.txt
```

## 🎯 Learning Objectives

By completing this use case, you'll learn:
- Email automation and attachment processing with Microsoft Graph
- Advanced document intelligence and OCR capabilities
- Multi-modal AI agent orchestration with Semantic Kernel
- Database design for structured eligibility data
- Data validation and quality assurance in AI systems
- Compliance and audit trail maintenance
- Privacy-preserving document processing workflows

## 🔒 Privacy & Compliance Considerations

### Data Protection:
- **Encryption**: All documents encrypted at rest and in transit
- **Access Control**: Role-based access to sensitive information
- **Data Retention**: Automated deletion based on policy requirements
- **Audit Logging**: Complete activity tracking for compliance

### Regulatory Compliance:
- **HIPAA**: Medical document handling and privacy protection
- **FERPA**: Educational record protection (if applicable)
- **State Privacy Laws**: Compliance with local data protection regulations
- **Social Services Regulations**: Adherence to eligibility determination requirements

## 🌟 Use Case Scenarios

### Scenario 1: SNAP Benefits Application
- **Input**: Email with pay stubs, bank statements, utility bills
- **Processing**: Document classification, income extraction, household verification
- **Output**: Structured eligibility data with preliminary assessment

### Scenario 2: Medicaid Enrollment
- **Input**: Medical records, insurance information, income documentation
- **Processing**: Medical need assessment, financial qualification, coverage verification
- **Output**: Eligibility recommendation with required additional documentation

### Scenario 3: Housing Assistance Application
- **Input**: Lease agreements, income verification, household composition documents
- **Processing**: Housing cost analysis, income-to-rent ratios, family size verification
- **Output**: Housing assistance eligibility determination with benefit calculations

## 🧪 Testing

### Running Tests
```bash
# Test document processing pipeline
python test_document_processing.py

# Test email integration
python test_email_processor.py

# Validate API connections
python test_setup.py

# Test individual processors
python -m pytest tests/ -v  # If pytest is configured
```

### Test Data
Use sample documents in `assets/sample_documents/`:
- Income verification (pay stubs, tax returns)
- Medical records and insurance documents
- Utility bills and housing documentation
- Identity and citizenship documents

### Validation Tests
- **Document Classification**: Verify correct document type identification
- **Data Extraction**: Test OCR accuracy and structured data extraction
- **Database Integration**: Validate data storage and retrieval
- **Email Processing**: Test attachment handling and processing

## 🎯 Hackathon Ideas & Extensions

### Beginner Extensions (30-60 minutes)
1. **New Document Type**: Add support for school enrollment documents
2. **Simple Dashboard**: Create basic HTML interface to view processed cases
3. **Email Templates**: Build automated response templates for applicants
4. **Data Export**: Add CSV/Excel export functionality for case workers

### Intermediate Extensions (2-4 hours)
1. **Multi-language Support**: Process documents in Spanish, Vietnamese, etc.
2. **Mobile Upload**: Create mobile app for document submission
3. **Fraud Detection**: Implement basic document authenticity checks
4. **Workflow Automation**: Add approval workflows for case workers

### Advanced Extensions (Full Hackathon)
1. **Real-time Dashboard**: Live processing status and analytics
2. **Machine Learning Models**: Custom document classification models
3. **Integration Platform**: Connect to existing social services systems
4. **Blockchain Verification**: Immutable audit trail for processed documents

### Extension Points in Code
- `src/processors/`: Add new document type processors
- `src/plugins/`: Extend Semantic Kernel functionality
- `src/services/`: Add new AI service integrations
- `src/web/`: Build web interfaces and dashboards

## 🚀 Getting Started Guide

### Step 1: Environment Setup
```bash
cd Document-Eligibility-Agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Azure Services Setup
1. **Create Azure AI Document Intelligence resource**
2. **Set up Azure OpenAI service**
3. **Configure Azure SQL Database**
4. **Register Microsoft Graph application**

### Step 3: Configuration
```bash
# Create configuration file
cp config/settings.template.json config/settings.json
# Edit with your API keys and endpoints
code config/settings.json
```

### Step 4: Test Setup
```bash
# Validate all connections
python test_setup.py

# Process sample documents
python test_document_processing.py
```

### Step 5: Start Processing!
```bash
# Run the main application
python src/main.py

# Or start the web dashboard
python src/web/dashboard.py
```

### Step 6: Process Test Documents
- Upload documents via web interface
- Send test emails with attachments
- Monitor processing in dashboard
- Review extracted data and eligibility assessments

## 📊 Document Processing Features

### Supported Document Types
- **Income Verification**: Pay stubs, tax returns, bank statements
- **Medical Records**: Insurance cards, medical bills, treatment records
- **Housing Documentation**: Lease agreements, utility bills, mortgage statements
- **Identity Documents**: Driver's licenses, social security cards, birth certificates
- **Educational Records**: Transcripts, enrollment verification, student aid documents

### AI Processing Pipeline
1. **Email Monitoring**: Automatic attachment detection and download
2. **Document Classification**: Identify document type using AI models
3. **OCR Processing**: Extract text and structured data using Azure AI
4. **Data Validation**: Verify and normalize extracted information
5. **Eligibility Assessment**: Calculate benefit eligibility based on rules
6. **Database Storage**: Store structured data with audit trail

### Quality Assurance
- **Confidence Scoring**: AI confidence levels for extracted data
- **Human Review Queue**: Flag uncertain extractions for manual review
- **Data Validation Rules**: Business logic validation for extracted data
- **Error Handling**: Graceful handling of processing failures

## 🆘 Troubleshooting

### Common Issues

#### "Document Intelligence service not found"
- **Solution**: Verify Azure Document Intelligence endpoint and key
- **Check**: Ensure service is deployed in correct Azure region

#### "Graph API authentication failed"
- **Solution**: Check Microsoft Graph app registration and permissions
- **Check**: Verify client ID and secret in configuration

#### "SQL connection failed"
- **Solution**: Validate Azure SQL connection string and firewall rules
- **Check**: Ensure database exists and user has proper permissions

#### "Email processing not working"
- **Solution**: Check Graph API permissions for email access
- **Check**: Verify mailbox permissions and OAuth scopes

### Performance Optimization
- **Batch Processing**: Process multiple documents simultaneously
- **Caching**: Cache frequently accessed data and models
- **Async Processing**: Use background tasks for long-running operations
- **Database Indexing**: Optimize database queries for large datasets

### Getting Help
1. **Run Diagnostics**: Use `test_setup.py` to verify all services
2. **Check Logs**: Review application logs for detailed error information
3. **Sample Documents**: Start with provided sample documents for testing
4. **API Testing**: Test individual services (Document Intelligence, Graph API) separately

## 📈 Real-World Applications

### Social Services Use Cases
- **SNAP Benefits**: Automated income and household verification for food assistance
- **Medicaid Enrollment**: Medical document processing for healthcare coverage
- **Housing Assistance**: Rent and income verification for housing programs
- **Disability Services**: Medical record processing for disability determination
- **Child Care Assistance**: Income and employment verification for childcare subsidies

### Government Benefits
- **Unemployment Insurance**: Employment and wage verification
- **Senior Services**: Age and income verification for senior programs
- **Veterans Benefits**: Military service and disability documentation
- **Emergency Assistance**: Rapid processing for crisis situations

### Efficiency Gains
- **Processing Time**: Reduce document processing from days to minutes
- **Accuracy**: Minimize human error in data entry and calculation
- **Cost Savings**: Reduce manual labor costs for case workers
- **Citizen Experience**: Faster benefit determination and approval
- **Audit Compliance**: Automated audit trails and compliance reporting

## 🏁 Next Steps

1. **Review Architecture**: Check [execution_script.md](./execution_script.md) for implementation details
2. **Follow Guide**: Use [step_by_step.md](./step_by_step.md) for detailed setup
3. **Explore Code**: Examine `src/` directory for implementation examples
4. **Test with Samples**: Use `assets/` for sample documents and configurations
5. **Build Extensions**: Start with beginner hackathon ideas and expand
6. **Deploy Solution**: Consider Azure deployment options for production use

## 📚 Additional Resources

- **Azure Document Intelligence**: [AI Document Processing](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- **Microsoft Graph**: [Email and Calendar APIs](https://learn.microsoft.com/en-us/graph/)
- **Semantic Kernel**: [AI Orchestration Framework](https://learn.microsoft.com/en-us/semantic-kernel/)
- **Social Services Tech**: [Government Digital Services](https://digital.gov/)

---

**Ready to revolutionize social services with AI? Start building and make government benefits more accessible! �📋**