# NY State AI Hackathon - Quick Start Guide

Get any accelerator running in 5 minutes. All accelerators include mock mode for offline development - no Azure services required to get started.

## 🚀 Quick Start (Any Accelerator)

### Python Accelerators (1-5)

```bash
# 1. Navigate to accelerator
cd [Accelerator-Directory]

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
venv\Scripts\activate
# OR Mac/Linux: source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run demo (mock mode)
python demo.py

# 6. Run web interface
python -m src.main
```

### .NET Accelerator (6)

```bash
# 1. Navigate to accelerator
cd DotNet-Virtual-Citizen-Assistant

# 2. Restore packages
dotnet restore

# 3. Run (mock mode)
dotnet run --project VirtualCitizenAgent

# Open http://localhost:5000
```

---

## 📁 The 6 Accelerators

| # | Accelerator | Directory | Tests | Demo |
|---|-------------|-----------|-------|------|
| 1 | Constituent Services Agent | `Constituent-Services-Agent/` | 43 | `python demo.py` |
| 2 | Document Eligibility Agent | `Document-Eligibility-Agent/` | 86 | `python demo.py` |
| 3 | Emergency Response Agent | `Emergency-Response-Agent/` | 62 | `python demo.py` |
| 4 | Policy Compliance Checker | `Policy-Compliance-Checker/` | 14 | `python demo.py` |
| 5 | Inter-Agency Knowledge Hub | `Inter-Agency-Knowledge-Hub/` | 38 | `python demo.py` |
| 6 | Virtual Citizen Assistant | `DotNet-Virtual-Citizen-Assistant/` | 22 | `dotnet run` |

**Total: 265 tests passing**

---

## 🧪 Running Tests

### Python Projects

```bash
cd [Accelerator-Directory]
python -m pytest tests/ -v
```

### .NET Project

```bash
cd DotNet-Virtual-Citizen-Assistant
dotnet test
```

---

## 🔧 Configuring Azure Services (Optional)

All accelerators work in mock mode by default. To connect real Azure services:

### Python Projects

Create a `.env` file based on `.env.example`:

```env
USE_MOCK_SERVICES=false
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your-key
# Additional service-specific keys...
```

### .NET Project

Edit `VirtualCitizenAgent/appsettings.json`:

```json
{
  "SearchConfiguration": {
    "UseMockService": false,
    "Endpoint": "https://your-search.search.windows.net",
    "ApiKey": "your-key"
  },
  "OpenAI": {
    "UseMockService": false,
    "Endpoint": "https://your-openai.openai.azure.com",
    "ApiKey": "your-key"
  }
}
```

---

## 🎯 Accelerator Use Cases

### 1. Constituent Services Agent
**What it does**: AI chatbot answering citizen questions about NY State services
**Try**: "How do I apply for SNAP benefits?" / "How do I renew my driver's license?"

### 2. Document Eligibility Agent
**What it does**: Processes eligibility documents (W-2s, pay stubs, utility bills)
**Try**: Upload sample documents from `sample_documents/`

### 3. Emergency Response Agent
**What it does**: Multi-agent planning for emergency response coordination
**Try**: Simulate a hurricane or winter storm scenario

### 4. Policy Compliance Checker
**What it does**: Analyzes policy documents for compliance violations
**Try**: Upload a sample policy document for analysis

### 5. Inter-Agency Knowledge Hub
**What it does**: Cross-agency search with permission-aware results
**Try**: Search across DMV, DOL, OTDA knowledge bases

### 6. Virtual Citizen Assistant (.NET)
**What it does**: RAG-powered chatbot for NYC government services
**Try**: Ask about housing, transportation, or city services

---

## 📋 Key Azure Services by Accelerator

```
┌─────────────────────────────────────────────────────────────────┐
│                    Common Services (All)                        │
├─────────────────────────────────────────────────────────────────┤
│  Azure AI Foundry  │  Entra ID  │  Azure OpenAI  │  Key Vault   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│ Constituent Svc  │ Document Elig    │ Policy Checker   │
├──────────────────┼──────────────────┼──────────────────┤
│ Foundry IQ       │ Doc Intelligence │ Azure OpenAI     │
│ Azure Translator │ Microsoft Graph  │ Blob Storage     │
│ Azure AI Search  │ Blob Storage     │ Azure AI Search  │
└──────────────────┴──────────────────┴──────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│ Emergency Resp   │ Knowledge Hub    │ Virtual Citizen  │
├──────────────────┼──────────────────┼──────────────────┤
│ Multi-Agent SK   │ Foundry IQ       │ Semantic Kernel  │
│ Weather APIs     │ Azure AI Search  │ Azure AI Search  │
│ Azure Maps       │ Microsoft Graph  │ Azure OpenAI     │
└──────────────────┴──────────────────┴──────────────────┘
```

---

## 🏆 Demo Tips

1. **Mock Mode First**: All accelerators work without Azure - start there
2. **Run Tests**: Verify everything works with `pytest tests/ -v` or `dotnet test`
3. **Use Sample Data**: Each accelerator includes test data
4. **Show Citations**: Government AI must show sources - this is built-in
5. **Human-in-the-Loop**: Demonstrate escalation and approval workflows

---

## 📚 Additional Resources

- [Main README](./README.md) - Full documentation
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-foundry/)
- [Semantic Kernel](https://learn.microsoft.com/semantic-kernel/)
- [Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [NY State ITS AI Policy](https://its.ny.gov/ai)

---

**NY State AI Hackathon - January 2026**
