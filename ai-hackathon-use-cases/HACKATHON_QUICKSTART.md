# NY State AI Hackathon Quick Start

Welcome to the NY State AI Hackathon for Public Sector! This guide will get you up and running in 5 minutes.

## 5-Minute Setup

### 1. Clone and Branch
```bash
git clone https://github.com/msftsean/ai-hackathon-use-cases
cd ai-hackathon-use-cases
git checkout nys-hackathon-jan-2026
```

### 2. Choose Your Use Case

| Use Case | Best For | Complexity | Time to Demo |
|----------|----------|------------|--------------|
| Constituent-Services-Agent | Chatbots, Q&A, Multi-language | Beginner | 5 min |
| Document-Eligibility-Agent | Document processing, OCR | Intermediate | 5 min |
| Policy-Compliance-Checker | Compliance review, Analysis | Intermediate | 5 min |
| Emergency-Response-Agent | Multi-agent orchestration | Advanced | 5 min |
| Inter-Agency-Knowledge-Hub | Cross-agency search, Security | Advanced | 10 min |
| DotNet-Virtual-Citizen-Assistant | .NET development, Web apps | Intermediate | 5 min |

### 3. Run Demo

```bash
cd [UseCase-Name]/
pip install -r requirements.txt
python demo.py
```

All use cases include mock services - no API keys required to start!

### 4. Build Your Extension

Use GitHub Copilot Agent Mode with Spec Kit:

1. Open spec file: `specs/[your-feature].spec.md`
2. `/speckit.plan` - Generate implementation plan
3. `/speckit.tasks` - Break into tasks
4. `/speckit.implement` - Build it

## Environment Setup

### Python Setup (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### .NET Setup (for DotNet-Virtual-Citizen-Assistant)
```bash
cd DotNet-Virtual-Citizen-Assistant
dotnet restore
dotnet run
```

## Azure Configuration (Optional)

For live Azure services, set these environment variables:

```bash
# Azure AI Project
export AZURE_AI_PROJECT_CONNECTION_STRING="your-connection-string"

# Azure OpenAI
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com"
export AZURE_OPENAI_KEY="your-key"

# Azure AI Search
export AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net"
export AZURE_SEARCH_KEY="your-key"

# Azure Translator (for multi-language)
export AZURE_TRANSLATOR_KEY="your-key"
export AZURE_TRANSLATOR_ENDPOINT="https://api.cognitive.microsofttranslator.com"

# Entra ID (for permission filtering)
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
```

## Quick Wins for Each Use Case

### Constituent-Services-Agent
- Add a new agency's FAQ to the knowledge base
- Add support for a new language
- Create a web interface for the chatbot

### Document-Eligibility-Agent
- Add a new document type recognition
- Build a status dashboard
- Add email notification for status updates

### Policy-Compliance-Checker
- Add new compliance rules for a specific regulation
- Create a compliance score visualization
- Add report export functionality

### Emergency-Response-Agent
- Add a new emergency type (flood, fire, etc.)
- Integrate weather API data
- Build a resource allocation dashboard

### Inter-Agency-Knowledge-Hub
- Add sample documents for a new agency
- Create search analytics dashboard
- Build a document comparison tool

## Hackathon Success Tips

1. **Start with working demo, then extend** - All use cases work out of the box
2. **Use Foundry IQ for RAG** - No need to build custom retrieval pipelines
3. **Run evals early** - `python -m pytest tests/ -v`
4. **Commit after every working feature** - Don't lose your progress
5. **Use mock services for development** - Switch to Azure when ready
6. **Document AI decisions** - Required for LOADinG Act compliance

## Testing Your Code

```bash
# Run all tests for a use case
cd [UseCase-Name]/
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_specific.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## AI Evaluation

Run responsible AI evaluations on your responses:

```bash
# Using Azure AI Evaluation
python -c "
from shared.evaluation import create_evaluator

evaluator = create_evaluator(
    subscription_id='your-sub',
    resource_group='your-rg',
    project_name='your-project'
)

results = evaluator.evaluate_response(
    query='How do I apply for SNAP?',
    response='Your response here',
    context='Source context'
)
print(results)
"

# Using promptfoo for red teaming
cd shared/evaluation
npx promptfoo eval -c red_team_config.yaml
```

## Getting Help

- **Technical Issues**: Check the README in each use case folder
- **Azure Questions**: Ask hackathon mentors
- **GitHub Copilot**: Use `/help` in Copilot Chat
- **Sample Data**: See `sample_data/nys_agencies/` for reference data

## Presentation Tips

1. **Tell a story** - Start with the problem, show the solution
2. **Live demo** - Show it working, not just slides
3. **Show the AI** - Highlight where AI adds value
4. **Address compliance** - Mention LOADinG Act, human-in-the-loop
5. **Be honest about limitations** - Judges appreciate transparency

## Deliverables Checklist

Before presenting, ensure you have:

- [ ] Working demo that runs without errors
- [ ] Clear explanation of what your extension does
- [ ] Documentation of AI decision points
- [ ] Test cases that pass
- [ ] Source citations for any AI responses
- [ ] Human-in-the-loop for citizen-affecting decisions

Good luck and happy hacking!
