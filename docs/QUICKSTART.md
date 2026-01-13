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

## 🔧 Configuring Azure OpenAI (Optional)

All accelerators work in mock mode by default. To connect real Azure OpenAI services, follow these steps.

### Step 1: Get Your Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your **Azure OpenAI** resource
3. Click **Keys and Endpoint** in the left menu
4. Copy:
   - **Endpoint**: `https://your-resource-name.openai.azure.com`
   - **Key 1** or **Key 2**: Your API key

5. Click **Model deployments** → **Manage Deployments** in Azure AI Studio
6. Note your **Deployment name** (e.g., `gpt-4`, `gpt-4o`, `gpt-35-turbo`)

### Step 2: Configure Python Projects (Accelerators 1-5)

Create a `.env` file in the accelerator directory:

```env
# Required for all Python accelerators
USE_MOCK_SERVICES=false
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Additional keys by accelerator:

# Document Eligibility Agent (Accelerator 2)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-doc-intel.cognitiveservices.azure.com
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key

# Inter-Agency Knowledge Hub (Accelerator 5)
AZURE_AI_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_AI_SEARCH_KEY=your-key
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

### Step 3: Configure .NET Project (Accelerator 6)

**Option A: Edit appsettings.json**

Edit `VirtualCitizenAgent/appsettings.json`:

```json
{
  "SearchConfiguration": {
    "UseMockService": false,
    "Endpoint": "https://your-search.search.windows.net",
    "IndexName": "citizen-services",
    "ApiKey": "your-search-api-key"
  },
  "OpenAI": {
    "UseMockService": false,
    "Endpoint": "https://your-resource-name.openai.azure.com",
    "ApiKey": "your-openai-api-key",
    "DeploymentName": "gpt-4o"
  }
}
```

**Option B: Use Environment Variables**

```bash
# Windows PowerShell
$env:OpenAI__Endpoint = "https://your-resource-name.openai.azure.com"
$env:OpenAI__ApiKey = "your-api-key"
$env:OpenAI__DeploymentName = "gpt-4o"
$env:OpenAI__UseMockService = "false"

# Mac/Linux
export OpenAI__Endpoint="https://your-resource-name.openai.azure.com"
export OpenAI__ApiKey="your-api-key"
export OpenAI__DeploymentName="gpt-4o"
export OpenAI__UseMockService="false"
```

### Supported Azure OpenAI Models

| Model | Deployment Name | Best For |
|-------|-----------------|----------|
| GPT-4o | `gpt-4o` | Best quality, multimodal |
| GPT-4 | `gpt-4` | High quality reasoning |
| GPT-4 Turbo | `gpt-4-turbo` | Fast, large context |
| GPT-3.5 Turbo | `gpt-35-turbo` | Cost-effective |

> **Note**: Use the deployment name you created in Azure AI Studio, not the model name.

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

- [Main README](../README.md) - Full documentation
- [Evaluation Guide](./EVAL_GUIDE.md) - AI evaluation framework
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-foundry/)
- [Semantic Kernel](https://learn.microsoft.com/semantic-kernel/)
- [Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [NY State ITS AI Policy](https://its.ny.gov/ai)

---

**NY State AI Hackathon - January 2026**
