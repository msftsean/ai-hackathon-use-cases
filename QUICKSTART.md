# NY State AI Hackathon - Spec Files Quick Reference

## 📁 Spec Files Overview

| Spec File | Use Case | Primary Tech | Hackathon Focus |
|-----------|----------|--------------|-----------------|
| `constituent-services-agent.spec.md` | Citizen Q&A chatbot | Foundry IQ + Translator | Multi-language RAG |
| `document-eligibility-agent.spec.md` | Document processing | Doc Intelligence + Graph | OCR + extraction |
| `policy-compliance-checker.spec.md` | Compliance review | Azure OpenAI + rules engine | Document analysis |
| `emergency-response-agent.spec.md` | Multi-agent coordination | Agent Framework | Agent orchestration |
| `inter-agency-knowledge-hub.spec.md` | Cross-agency search | Foundry IQ + SharePoint | Permission-aware RAG |

---

## 🚀 Using Specs with GitHub Copilot

### Step 1: Open Spec in VS Code/Codespaces
```bash
cd ai-hackathon-use-cases
code specs/[your-chosen-spec].spec.md
```

### Step 2: Generate Implementation Plan
In Copilot Chat, use:
```
/speckit.plan

We're building this for the NY State AI Hackathon using:
- Python 3.11 with Semantic Kernel 1.45+
- Azure AI Foundry (Foundry IQ for RAG)
- Azure OpenAI GPT-4o
- Entra ID authentication
- GCC-compliant Azure services only

Focus on the Day 1 Deliverables section for MVP scope.
```

### Step 3: Break Into Tasks
```
/speckit.tasks

Create tasks for Day 1 deliverables only. Each task should be completable in 1-2 hours.
```

### Step 4: Implement
```
/speckit.implement

Start with task 1. Use Azure AI Foundry SDK patterns.
```

---

## 🎯 Hackathon Day 1 Priority Tasks by Use Case

### Constituent Services Agent
1. Set up Foundry IQ knowledge base with sample NY State content
2. Implement basic Q&A endpoint with citation return
3. Add Azure Translator for language detection
4. Create simple Streamlit/Gradio chat interface

### Document Eligibility Agent  
1. Set up Azure Document Intelligence client
2. Implement email attachment extraction (mock or Graph API)
3. Create extraction pipeline for W-2 and pay stub
4. Build simple review queue interface

### Policy Compliance Checker
1. Define 3 rule sets in JSON/YAML format
2. Implement document upload and text extraction
3. Create rule matching engine with Azure OpenAI
4. Display results with severity ranking

### Emergency Response Agent
1. Set up NWS API integration for weather data
2. Create Weather Agent with threat assessment prompt
3. Implement basic resource tracking data model
4. Build orchestrator connecting agents

### Inter-Agency Knowledge Hub
1. Create Foundry IQ knowledge base
2. Connect to 2-3 sample SharePoint document libraries
3. Implement permission-aware search (Entra ID groups)
4. Build search interface with citation display

---

## 📋 Key Azure Services by Use Case

```
┌─────────────────────────────────────────────────────────────────┐
│                    All Use Cases                                 │
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

┌──────────────────┬──────────────────┐
│ Emergency Resp   │ Knowledge Hub    │
├──────────────────┼──────────────────┤
│ Agent Framework  │ Foundry IQ       │
│ Azure Maps       │ SharePoint API   │
│ Comm Services    │ Microsoft Graph  │
└──────────────────┴──────────────────┘
```

---

## 🔧 Common Patterns

### Foundry IQ Setup (Constituent Services, Knowledge Hub)
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["AZURE_AI_PROJECT_CONNECTION"]
)

# Create agent with file search (Foundry IQ)
agent = client.agents.create_agent(
    model="gpt-4o",
    name="nys-assistant",
    instructions="You are a helpful NY State government assistant...",
    tools=[{"type": "file_search"}]
)
```

### Document Intelligence (Document Eligibility)
```python
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

client = DocumentIntelligenceClient(
    endpoint=os.environ["DOC_INTEL_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["DOC_INTEL_KEY"])
)

poller = client.begin_analyze_document(
    "prebuilt-document",  # or prebuilt-tax.us.w2
    document=document_bytes
)
result = poller.result()
```

### Multi-Agent Orchestration (Emergency Response)
```python
from semantic_kernel.agents.orchestration import SequentialOrchestration
from semantic_kernel.agents import ChatCompletionAgent

weather_agent = ChatCompletionAgent(kernel=kernel, name="WeatherAgent", ...)
resource_agent = ChatCompletionAgent(kernel=kernel, name="ResourceAgent", ...)

orchestration = SequentialOrchestration(
    members=[weather_agent, resource_agent]
)
```

---

## ✅ Spec Validation Checklist

Before starting implementation, verify your chosen spec:

- [ ] Read through all User Stories - do they make sense for hackathon?
- [ ] Check Day 1 Deliverables - are they achievable in 4-5 hours?
- [ ] Review Dependencies - do you have access to required services?
- [ ] Understand Success Criteria - can you demo these metrics?
- [ ] Note Out of Scope - don't accidentally build excluded features

---

## 🏆 Demo Success Tips

1. **Working > Perfect**: Get basic flow working first, polish later
2. **Use Mock Data**: If API isn't ready, mock it - judges care about the concept
3. **Prepare Fallbacks**: Have screenshots ready if live demo fails
4. **Tell a Story**: Frame demo around constituent/user benefit, not tech
5. **Show Citations**: Government AI must show sources - make this visible
6. **Human-in-the-Loop**: Demonstrate where humans approve/override AI

---

## 📚 Additional Resources

- [Azure AI Foundry Docs](https://learn.microsoft.com/azure/ai-foundry/)
- [Semantic Kernel Agents](https://learn.microsoft.com/semantic-kernel/agents/)
- [Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [NY State ITS AI Policy](https://its.ny.gov/ai)
