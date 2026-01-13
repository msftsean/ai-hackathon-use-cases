# 🏛️ NY State AI Hackathon - AI Accelerators for Government Services

[![Accelerators](https://img.shields.io/badge/Accelerators-6-blue.svg)](#-the-6-ai-accelerators)
[![Tests](https://img.shields.io/badge/Tests-265%20Passing-brightgreen.svg)](#-testing--evaluation)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](https://python.org)
[![.NET 9](https://img.shields.io/badge/.NET-9.0-512BD4.svg)](https://dotnet.microsoft.com)
[![Semantic Kernel](https://img.shields.io/badge/Semantic%20Kernel-1.37%2B-orange.svg)](https://docs.microsoft.com/semantic-kernel)

**Hackathon**: NY State AI Hackathon for Public Sector
**Event Date**: January 13-14, 2026
**Location**: SUNY ETEC Albany

---

## 📋 Executive Summary

### What Are Accelerators?

**Accelerators** are a Microsoft term for **complete, working applications** that serve as production-ready starting points for your own solutions. Rather than building from scratch, accelerators let you:

- ✅ **Learn faster** - See real-world implementations of AI patterns and best practices
- ✅ **Build securely** - Start with security, compliance, and responsible AI already built in
- ✅ **Ship sooner** - Extend working code instead of writing boilerplate from zero
- ✅ **Reduce risk** - Leverage tested, validated architectures designed for government use

Think of accelerators as **fully-functional blueprints** - they work out of the box, but are designed for you to customize and extend for your specific agency needs.

### This Repository

This repository contains **6 AI accelerators** designed to transform how NY State government agencies serve constituents. Each accelerator is a complete application built with Microsoft Azure AI services and the Semantic Kernel framework, demonstrating practical AI solutions for:

| Challenge | Accelerator Solution |
|-----------|---------------------|
| 📞 Citizens can't find answers | AI chatbot with citations |
| 📄 Document processing backlogs | Automated OCR & validation |
| 🚨 Emergency coordination gaps | Multi-agent planning system |
| 📋 Policy compliance burden | Automated document review |
| 🔍 Siloed agency knowledge | Cross-agency secure search |
| 🏙️ NYC citizen services | RAG-powered .NET chatbot |

All accelerators comply with NY State's **LOADinG Act** and **RAISE Act** requirements for transparent, accountable AI in government.

---

## 📊 Revision Matrix

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| **2.1.0** | Jan 12, 2026 | Added .NET Virtual Citizen Assistant, 265 tests | ✅ Current |
| 2.0.0 | Jan 12, 2026 | Production release with 5 accelerators | ✅ Stable |
| 1.5.0 | Jan 10, 2026 | Added Inter-Agency Knowledge Hub accelerator | ✅ Stable |
| 1.4.0 | Jan 9, 2026 | Added Policy Compliance Checker accelerator | ✅ Stable |
| 1.3.0 | Jan 8, 2026 | Added Emergency Response Agent accelerator | ✅ Stable |
| 1.2.0 | Jan 7, 2026 | Added Document Eligibility Agent accelerator | ✅ Stable |
| 1.1.0 | Jan 6, 2026 | Added Constituent Services Agent accelerator | ✅ Stable |
| 1.0.0 | Jan 5, 2026 | Initial repository setup with shared infrastructure | ✅ Stable |

---

## 🚀 The 6 AI Accelerators

### 1️⃣ Constituent Services Agent
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](./Constituent-Services-Agent/)
[![Tests](https://img.shields.io/badge/Tests-43%20Passing-brightgreen.svg)](./Constituent-Services-Agent/)
[![Demo](https://img.shields.io/badge/Demo-5%20min-blue.svg)](./Constituent-Services-Agent/)

**🎯 Purpose**: AI-powered chatbot answering citizen questions about NY State services

**✨ Key Features**:
- 💬 Natural language Q&A about SNAP benefits, driver's licenses, unemployment, Medicaid
- 📚 Citation-backed responses with source documents
- 📊 Confidence scoring and human escalation when uncertain
- 🌍 Multi-language support (English, Spanish, Chinese, Arabic, Russian, Korean, Haitian Creole, Bengali)
- ♿ WCAG 2.1 AA accessible web interface

**🛠️ Tech Stack**: Azure AI Foundry + Foundry IQ + Semantic Kernel + Flask

**▶️ Demo Command**:
```bash
cd Constituent-Services-Agent
pip install -r requirements.txt
python demo.py
```

**💡 Sample Queries**:
- "How do I apply for SNAP benefits?"
- "How do I renew my driver's license?"
- "Am I eligible for Medicaid?"

---

### 2️⃣ Document Eligibility Agent
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](./Document-Eligibility-Agent/)
[![Tests](https://img.shields.io/badge/Tests-86%20Passing-brightgreen.svg)](./Document-Eligibility-Agent/)
[![Demo](https://img.shields.io/badge/Demo-5%20min-blue.svg)](./Document-Eligibility-Agent/)

**🎯 Purpose**: Automated processing of eligibility documents (W-2s, pay stubs, utility bills)

**✨ Key Features**:
- 📧 Email inbox monitoring for document submissions
- 🔍 OCR and intelligent data extraction using Azure Document Intelligence
- 📊 Confidence scoring for all extracted fields
- 🔒 PII detection and automatic masking
- ✅ Validation rules (document age, completeness)
- 📋 Case routing and workload distribution

**🛠️ Tech Stack**: Azure Document Intelligence + Microsoft Graph + Semantic Kernel + Flask

**▶️ Demo Command**:
```bash
cd Document-Eligibility-Agent
pip install -r requirements.txt
python demo.py
```

**📄 Supported Document Types**:
| Document | Fields Extracted |
|----------|-----------------|
| W-2 Forms | Wages, employer, tax year |
| Pay Stubs | Gross pay, period, date |
| Utility Bills | Provider, address, date |
| Bank Statements | Institution, balance |
| Driver's Licenses | Name, DOB, expiration |
| Birth Certificates | Name, DOB, parents |
| Lease Agreements | Landlord, address, rent |

---

### 3️⃣ Emergency Response Agent
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](./Emergency-Response-Agent/)
[![Tests](https://img.shields.io/badge/Tests-62%20Passing-brightgreen.svg)](./Emergency-Response-Agent/)
[![Multi-Agent](https://img.shields.io/badge/Pattern-Multi--Agent-purple.svg)](./Emergency-Response-Agent/)

**🎯 Purpose**: Multi-agent system for emergency response planning and coordination

**✨ Key Features**:
- 🌀 Emergency scenario simulation (hurricane, fire, flood, winter storm, public health, earthquake)
- 🌤️ Real-time weather integration
- 🏛️ Multi-agency resource coordination (FDNY, NYPD, OEM, DOT, MTA)
- 🚗 Evacuation route planning with bottleneck analysis
- 📜 Historical incident analysis for lessons learned
- ⏱️ Response plans with timeline milestones

**🛠️ Tech Stack**: Semantic Kernel + Azure AI Foundry + Weather APIs + Multi-Agent Orchestration

**🚨 Supported Emergency Types**:
| Type | Lead Agency | Key Resources |
|------|-------------|---------------|
| 🌀 Hurricane | OEM | Evacuation, shelters |
| 🔥 Fire | FDNY | Firefighters, equipment |
| 🌊 Flooding | OEM | Pumps, rescue boats |
| ❄️ Winter Storm | DOT | Plows, salt trucks |
| 🏥 Public Health | DOH | Healthcare workers, vaccines |
| 🏚️ Earthquake | OEM | Search & rescue teams |
| ⚡ Infrastructure | Utilities | Emergency generators |

---

### 4️⃣ Policy Compliance Checker
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](./Policy-Compliance-Checker/)
[![Tests](https://img.shields.io/badge/Tests-14%20Passing-brightgreen.svg)](./Policy-Compliance-Checker/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-orange.svg)](./Policy-Compliance-Checker/)

**🎯 Purpose**: Automated review of policy documents against compliance rules

**✨ Key Features**:
- 📄 Document parsing (PDF, DOCX, Markdown)
- 🔍 Rule-based compliance checking with regex patterns
- ⚠️ Severity categorization (Critical, High, Medium, Low)
- 📊 Compliance scoring (0-100)
- 🤖 AI-powered analysis with Azure OpenAI
- 💡 Detailed recommendations for each violation
- 🔄 Version comparison for policy changes

**🛠️ Tech Stack**: Azure AI Foundry + Semantic Kernel + Document AI

**▶️ Demo Command**:
```bash
cd Policy-Compliance-Checker
pip install -r requirements.txt
python demo.py
```

**📋 Compliance Categories**:
| Category | Description | Examples |
|----------|-------------|----------|
| Data Privacy | PII handling rules | Encryption, retention |
| Accessibility | WCAG compliance | Alt text, contrast |
| Security | Security standards | Authentication, logging |
| Documentation | Policy requirements | Version control, approval |

---

### 5️⃣ Inter-Agency Knowledge Hub
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](./Inter-Agency-Knowledge-Hub/)
[![Tests](https://img.shields.io/badge/Tests-38%20Passing-brightgreen.svg)](./Inter-Agency-Knowledge-Hub/)
[![Cross-Agency](https://img.shields.io/badge/Search-Cross--Agency-purple.svg)](./Inter-Agency-Knowledge-Hub/)

**🎯 Purpose**: Cross-agency document search with permission-aware results

**✨ Key Features**:
- 🔍 Unified search across 5+ agency knowledge bases (DMV, DOL, OTDA, DOH, OGS)
- 🔐 Entra ID authentication with role-based access
- 🛡️ Permission-aware result filtering
- 📚 Citation tracking for LOADinG Act compliance
- 🔗 Cross-agency policy cross-references
- 👤 Human-in-the-loop for complex queries
- 📋 7-year audit log retention

**🛠️ Tech Stack**: Microsoft Foundry + Foundry IQ + Azure AI Search + Entra ID

**▶️ Demo Command**:
```bash
cd Inter-Agency-Knowledge-Hub
pip install -r requirements.txt
python demo.py
```

**🏛️ Supported Agencies**:
| Agency | Domain | Documents |
|--------|--------|-----------|
| DMV | Transportation | Licensing, registration |
| DOL | Labor | Employment, wages |
| OTDA | Social Services | Benefits, assistance |
| DOH | Health | Public health, regulations |
| OGS | General Services | Procurement, facilities |

---

### 6️⃣ Virtual Citizen Assistant (.NET)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](./DotNet-Virtual-Citizen-Assistant/)
[![Tests](https://img.shields.io/badge/Tests-22%20Passing-brightgreen.svg)](./DotNet-Virtual-Citizen-Assistant/)
[![.NET 9](https://img.shields.io/badge/.NET-9.0-512BD4.svg)](./DotNet-Virtual-Citizen-Assistant/)

**🎯 Purpose**: RAG-powered AI assistant for NYC government services built with .NET

**✨ Key Features**:
- 💬 AI chat assistant with source citations
- 🔍 Semantic, keyword, and hybrid search modes
- 📂 Category browser with visual grid layout
- 📄 Document details with print and share
- 🛠️ Data upload utility for Azure AI Search
- 🎨 Bootstrap 5.3 responsive UI

**🛠️ Tech Stack**: .NET 9 + ASP.NET Core MVC + Semantic Kernel 1.65 + Azure AI Search + Azure OpenAI

**▶️ Demo Command**:
```bash
cd DotNet-Virtual-Citizen-Assistant
dotnet restore
dotnet run --project VirtualCitizenAgent
```

**💡 Sample Features**:
- Chat with AI about NYC services
- Search documents semantically
- Browse by service category

---

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     🖥️ Frontend Layer                           │
│   Flask Web UI  │  REST APIs  │  WCAG 2.1 AA Accessible        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  🤖 AI Orchestration Layer                      │
│   Semantic Kernel  │  Foundry IQ  │  Multi-Agent Patterns      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ☁️ Azure AI Services                          │
│  Azure OpenAI GPT-4o  │  Document Intelligence  │  AI Search   │
│  Microsoft Graph      │  Translator            │  Entra ID     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      💾 Data Layer                              │
│   SQLite/Azure SQL  │  Blob Storage  │  Vector DBs             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Compliance & Responsible AI

### 📜 NY LOADinG Act Compliance
- ✅ All AI decisions are logged with rationale
- ✅ Human-in-the-loop for benefits determinations
- ✅ Transparent citation of data sources
- ✅ Bias testing across demographic groups

### 📋 NY RAISE Act Requirements
- ✅ AI assistance clearly disclosed to users
- ✅ Accountability measures for automated decisions
- ✅ Regular auditing and evaluation frameworks
- ✅ Azure AI Evaluation integration for red-teaming

### 🔒 Security & Privacy
- 🏛️ Azure GCC (Government Community Cloud) compatible
- 🔐 PII detection and automatic masking
- 👤 Role-based access control via Entra ID
- 🔒 Encrypted data at rest and in transit
- 🗑️ 30-day conversation data purge policy

---

## 📁 Project Structure

```
newyork/
├── 📂 Constituent-Services-Agent/     # 💬 Citizen Q&A chatbot
│   ├── src/
│   │   ├── agent/                     # AI agent components
│   │   ├── api/                       # Flask routes
│   │   ├── models/                    # Data models
│   │   └── services/                  # Knowledge service
│   ├── demo.py                        # Interactive demo
│   └── requirements.txt
│
├── 📂 Document-Eligibility-Agent/     # 📄 Document processing
│   ├── src/
│   │   ├── agent/                     # Processing agents
│   │   ├── api/                       # REST endpoints
│   │   ├── models/                    # Document models
│   │   └── services/                  # OCR, email, storage
│   ├── demo.py
│   └── sample_documents/
│
├── 📂 Emergency-Response-Agent/       # 🚨 Emergency planning
│   ├── src/
│   │   ├── models/                    # Emergency models
│   │   ├── orchestration/             # Multi-agent coordinator
│   │   └── services/                  # Weather, traffic APIs
│   └── requirements.txt
│
├── 📂 Policy-Compliance-Checker/      # 📋 Compliance checking
│   ├── src/
│   │   ├── models/                    # Compliance models
│   │   ├── services/                  # Rule engine, parsing
│   │   └── api/                       # Flask routes
│   └── requirements.txt
│
├── 📂 Inter-Agency-Knowledge-Hub/     # 🔍 Cross-agency search
│   ├── src/
│   │   ├── models/                    # Search models
│   │   ├── services/                  # Search, auth services
│   │   └── api/                       # Flask routes
│   └── requirements.txt
│
├── 📂 DotNet-Virtual-Citizen-Assistant/  # 🏙️ NYC .NET chatbot
│   ├── VirtualCitizenAgent/           # Main web application
│   │   ├── Controllers/               # MVC and API controllers
│   │   ├── Services/                  # Business logic
│   │   ├── Plugins/                   # Semantic Kernel plugins
│   │   └── Views/                     # Razor views
│   ├── VirtualCitizenAgent.Tests/     # xUnit tests
│   └── AzureSearchUploader/           # Data upload utility
│
├── 📂 docs/                             # 📖 Documentation
│   ├── QUICKSTART.md                    # Quick start guide
│   ├── EVAL_GUIDE.md                    # Evaluation guide
│   └── SPEC_TEMPLATE.md                 # Specification template
│
├── 📂 evaluation/                       # 🧪 AI evaluation framework
│   ├── eval_config.py                   # Evaluation configuration
│   ├── run_evals.py                     # Run evaluations
│   ├── red_team.yaml                    # Red team test config
│   └── test_cases.jsonl                 # Test cases
│
└── 📂 specs/                            # 📋 Feature specifications
    ├── 001-constituent-services-agent/
    ├── 002-document-eligibility-agent/
    ├── 003-emergency-response-agent/
    ├── 004-policy-compliance-checker/
    └── 005-inter-agency-knowledge-hub/
```

---

## ⚡ Quick Start (Any Accelerator)

```bash
# 1️⃣ Clone and navigate
cd newyork

# 2️⃣ Choose an accelerator
cd Constituent-Services-Agent  # or any other accelerator

# 3️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 4️⃣ Install dependencies
pip install -r requirements.txt

# 5️⃣ Run demo (mock mode - no Azure required)
python demo.py

# 6️⃣ Run web interface
python -m src.main
```

> 💡 **Mock Mode**: All accelerators work without Azure services using mock data for offline development. No API keys required to get started!

---

## 🔧 Key Technologies

| Technology | Purpose | Badge |
|------------|---------|-------|
| **Azure AI Foundry** | AI development platform | ![Azure](https://img.shields.io/badge/Azure-AI%20Foundry-0078D4.svg) |
| **Foundry IQ** | Intelligent document retrieval | ![Foundry IQ](https://img.shields.io/badge/Foundry-IQ-blue.svg) |
| **Semantic Kernel** | AI orchestration framework | ![SK](https://img.shields.io/badge/Semantic%20Kernel-1.45%2B-orange.svg) |
| **Azure OpenAI GPT-4o** | Language model for Q&A | ![OpenAI](https://img.shields.io/badge/GPT-4o-green.svg) |
| **Azure Document Intelligence** | OCR and document parsing | ![Doc Intel](https://img.shields.io/badge/Document-Intelligence-blue.svg) |
| **Azure AI Search** | Vector search with security filters | ![Search](https://img.shields.io/badge/AI-Search-purple.svg) |
| **Microsoft Graph** | Email and document access | ![Graph](https://img.shields.io/badge/Microsoft-Graph-blue.svg) |
| **Entra ID** | Authentication and authorization | ![Entra](https://img.shields.io/badge/Entra-ID-0078D4.svg) |
| **Flask** | Web framework for APIs | ![Flask](https://img.shields.io/badge/Flask-2.0%2B-black.svg) |
| **Pydantic** | Data validation | ![Pydantic](https://img.shields.io/badge/Pydantic-2.0-red.svg) |

---

## 🧪 Testing & Evaluation

### ✅ Test Coverage
| Accelerator | Tests | Status |
|-------------|-------|--------|
| Constituent Services Agent | 43 | ✅ All Passing |
| Document Eligibility Agent | 86 | ✅ All Passing |
| Emergency Response Agent | 62 | ✅ All Passing |
| Policy Compliance Checker | 14 | ✅ All Passing |
| Inter-Agency Knowledge Hub | 38 | ✅ All Passing |
| Virtual Citizen Assistant (.NET) | 22 | ✅ All Passing |
| **Total** | **265** | ✅ **Production Ready** |

### 🤖 AI Evaluation Framework
- **Quality Evaluators**: Groundedness, Relevance, Coherence, Fluency
- **Safety Evaluators**: Content safety, PII detection
- **Red Team Tests**: Jailbreak, PII extraction, authority spoofing, hallucination

```bash
# Run tests for Python accelerators
cd [Accelerator-Directory]
python -m pytest tests/ -v

# Run tests for .NET accelerator
cd DotNet-Virtual-Citizen-Assistant
dotnet test

# Run AI evaluations
python -m shared.evaluation.eval_config
```

---

## 📈 Success Metrics

| Accelerator | Key Metric | Target | Status |
|-------------|-----------|--------|--------|
| 💬 Constituent Services | Response time | < 5 seconds | ✅ |
| 💬 Constituent Services | Citation accuracy | > 95% | ✅ |
| 📄 Document Eligibility | Processing time | < 2 minutes | ✅ |
| 📄 Document Eligibility | Extraction accuracy | > 95% | ✅ |
| 🚨 Emergency Response | Plan generation | < 5 seconds | ✅ |
| 📋 Policy Compliance | Analysis time | < 30 seconds | ✅ |
| 🔍 Knowledge Hub | Search response | < 3 seconds | ✅ |

---

## 🎯 Hackathon Impact

### 👥 For Citizens
- ⚡ **Faster answers**: Get information about government services instantly
- 🌍 **Accessible**: Multi-language support, WCAG 2.1 AA compliant
- 📚 **Transparent**: See sources for all information provided

### 👔 For Agency Staff
- 📉 **Reduced workload**: AI handles routine inquiries, staff focus on complex cases
- ⏱️ **Faster processing**: Documents processed in minutes, not hours
- 🤝 **Better coordination**: Cross-agency visibility and emergency planning

### 🏛️ For Government
- ✅ **Compliance**: Built-in LOADinG Act and RAISE Act compliance
- 📈 **Scalability**: Handles high volumes during crises
- 📋 **Accountability**: Complete audit trails for all AI decisions

---

## 🤝 Collaboration & Access

### Getting Access to This Repository

**For Microsoft Enterprise Users**: If you have a Microsoft enterprise account and are having trouble accessing this repository, please see our detailed [Collaboration Guide](./COLLABORATION.md) for step-by-step instructions.

**Quick Access Steps**:
1. Ensure your GitHub account has 2FA enabled
2. Link your Microsoft enterprise email to your GitHub account
3. Request access from the repository owner (@msftsean)
4. For detailed instructions, see [COLLABORATION.md](./COLLABORATION.md)

### Contributing

We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) for:
- Code standards and best practices
- Pull request process
- Testing requirements
- Security considerations

**Quick Start for Contributors**:
```bash
# Fork and clone the repository
git clone https://github.com/msftsean/ai-hackathon-use-cases.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and run tests
pytest tests/ -v  # Python projects
dotnet test       # .NET project

# Submit a pull request
```

---

## 👥 Team

**NY State AI Hackathon - January 2026**

Built for NY State government agencies to demonstrate how AI can improve constituent services while maintaining transparency, accountability, and security.

---

## 📚 Additional Resources

- 🚀 [Quick Start Guide](./docs/QUICKSTART.md)
- 🤝 [Collaboration Guide](./COLLABORATION.md) - **For Microsoft enterprise users**
- 📝 [Contributing Guidelines](./CONTRIBUTING.md)
- 📋 [Feature Specifications](./specs/)
- 🧪 [Evaluation Framework](./evaluation/)
- 📖 [Evaluation Guide](./docs/EVAL_GUIDE.md)
- 🔗 [Azure AI Foundry Documentation](https://docs.microsoft.com/azure/ai-foundry)
- 🔗 [Semantic Kernel Documentation](https://docs.microsoft.com/semantic-kernel)
- 🔗 [Microsoft Accelerators](https://github.com/microsoft/solution-accelerators)

---

<p align="center">
  <b>🏛️ Shaping the Future of Responsible AI in New York State 🗽</b>
</p>
