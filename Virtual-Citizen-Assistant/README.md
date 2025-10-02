# 🤖 AI-Powered Virtual Citizen Assistant

> **🎯 Hackathon Ready!** A complete RAG-powered citizen service chatbot that you can run, test, and extend during the hackathon.

## 📋 Overview

An intelligent conversational AI that helps citizens access public services information through natural language queries. Built with Retrieval-Augmented Generation (RAG), Semantic Kernel, and Azure AI services for accurate, contextual responses about trash pickup, permits, emergency alerts, and more.

**✅ Working Implementation** - Complete RAG system with plugin orchestration

## 🚀 Quick Start for Hackathon

**Get running in 5 minutes!**

### Option 1: Codespaces (Recommended)
1. Open this repository in GitHub Codespaces
2. Navigate to Virtual-Citizen-Assistant: `cd Virtual-Citizen-Assistant`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure API keys (see [Configuration](#configuration))
5. Run the assistant: `python src/main.py`

### Option 2: Local Development
```bash
git clone <repository-url>
cd ai-hackathon-use-cases/Virtual-Citizen-Assistant
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

## 🎯 Hackathon Features

Perfect for extending and customizing during the hackathon:
- **RAG Implementation**: Complete retrieval-augmented generation system
- **Multi-Plugin Architecture**: Easy to add new service plugins
- **Natural Language Processing**: Advanced query understanding and response generation
- **Extensible Design**: Simple to add new city services and data sources
- **Testing Framework**: Validation tools for rapid development

## ⚙️ Configuration

### Required API Keys

Create a `.env` file in the Virtual-Citizen-Assistant directory:

```bash
# Azure OpenAI Configuration (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure AI Search (Required for RAG)
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_ADMIN_KEY=your-search-admin-key
AZURE_SEARCH_INDEX_NAME=citizen-services

# Azure AI Services (Optional - for enhanced processing)
AZURE_AI_TEXT_ANALYTICS_ENDPOINT=https://your-service.cognitiveservices.azure.com/
AZURE_AI_TEXT_ANALYTICS_KEY=your-text-analytics-key
```

### Configuration Options

#### Option 1: .env File (Recommended for Hackathon)
- Create `.env` file in the Virtual-Citizen-Assistant directory
- Add your API keys and endpoints
- Most secure for local development

#### Option 2: Environment Variables
```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key-here"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
```

#### Option 3: Configuration File
Edit `src/config/settings.py` for quick testing

### Getting API Keys

#### Azure OpenAI (Required)
1. Create Azure OpenAI resource in Azure portal
2. Deploy GPT-4 or GPT-3.5-turbo model
3. Copy endpoint, deployment name, and API key

#### Azure AI Search (Required for RAG)
1. Create Azure AI Search resource
2. Create search index for citizen services data
3. Copy service endpoint and admin key

#### Azure AI Services (Optional)
1. Create Text Analytics resource for enhanced language processing
2. Add endpoint and key to configuration

## 🛠️ Technology Stack

- **Semantic Kernel 1.37.0**: Plugin orchestration and conversational flow
- **Azure AI Search**: Vector search and document indexing for RAG
- **Azure OpenAI**: Large language model for natural language understanding
- **Azure AI Services**: Text Analytics for enhanced processing
- **Flask**: Web framework for citizen-facing interface
- **Python 3.9+**: Modern async/await patterns and type hints

## 🏗️ Architecture

```
Citizen Query → Azure Web App → Semantic Kernel Planner
                                      ↓
                            Plugin Orchestration
                           /        |        \
              Document    /    Scheduling   \    Emergency
              Retrieval  /       APIs        \    Alerts
                        ↓                     ↓        ↓
              Azure AI Search    City APIs    Notification
                                              Service
```

## 💡 Key Features

1. **Natural Language Understanding**: Process citizen queries in plain English
2. **Multi-Service Integration**: Connect to various city service APIs
3. **Real-Time Information**: Provide current schedules, alerts, and status updates
4. **Contextual Responses**: Maintain conversation context for follow-up questions
5. **Fallback Handling**: Gracefully handle queries outside the knowledge base

## 📊 Example Interactions

**User**: "When is my next trash pickup?"  
**Assistant**: "Based on your address, your next trash pickup is scheduled for Thursday, October 3rd. Please have your bins out by 7 AM."

**User**: "How do I apply for a business permit?"  
**Assistant**: "To apply for a business permit, you can visit our online portal at city.gov/permits or visit City Hall on weekdays 9 AM-5 PM. You'll need your business plan, zoning approval, and relevant licenses."

## 🧪 Testing

The system includes testing frameworks for validating functionality.

### Running Tests
```bash
# Run plugin tests
python test_plugins.py

# Run setup validation
python test_setup.py

# Test individual components
python -m pytest tests/ -v  # If pytest is configured
```

### Test Components
- **Plugin Testing**: Validate Semantic Kernel plugins
- **Setup Validation**: Verify configuration and API connectivity
- **RAG Testing**: Test retrieval and generation pipeline
- **Integration Testing**: End-to-end conversation flows

### Sample Test Queries
The system can handle various citizen service queries:
- Trash and recycling schedules
- Permit applications and requirements
- Emergency alerts and notifications
- City service hours and locations
- Public transportation information

## 🎯 Hackathon Ideas & Extensions

### Beginner Extensions (30-60 minutes)
1. **New Service Plugin**: Add parking information or library hours
2. **Custom Responses**: Create domain-specific response templates
3. **Simple Web UI**: Build basic HTML interface for queries
4. **Data Import**: Add new city service data to the knowledge base

### Intermediate Extensions (2-4 hours)
1. **Voice Interface**: Add speech-to-text and text-to-speech
2. **Multi-language Support**: Support Spanish, Chinese, or other languages
3. **Location Awareness**: GPS-based service recommendations
4. **Appointment Booking**: Integrate with city appointment systems

### Advanced Extensions (Full Hackathon)
1. **Real-time Integration**: Connect to live city data feeds
2. **Mobile App**: Create React Native or Flutter mobile app
3. **Analytics Dashboard**: Track popular queries and user satisfaction
4. **Personalization**: User accounts with personalized recommendations

### Extension Points in Code
- `src/plugins/`: Add new service-specific plugins
- `src/models/`: Extend data models for new service types
- `src/rag/`: Enhance retrieval and generation components
- `src/ui/`: Build web or mobile user interfaces

## 🚀 Getting Started Guide

### Step 1: Environment Setup
```bash
cd Virtual-Citizen-Assistant
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure API Keys
```bash
# Create .env file
touch .env  # Or create manually
# Edit .env with your API keys
code .env  # Or use any text editor
```

### Step 3: Test Installation
```bash
# Run setup validation
python test_setup.py
```

### Step 4: Run Example Conversations
```bash
# Start the interactive assistant
python src/main.py

# Or run specific test scenarios
python test_plugins.py
```

### Step 5: Start Building!
- Check `src/examples/` for usage patterns
- Review `assets/` for sample data and configurations
- Explore `src/plugins/` for extension points

## 📊 RAG (Retrieval-Augmented Generation) Features

### Document Retrieval
- **Vector Search**: Semantic similarity search using Azure AI Search
- **Keyword Search**: Traditional text-based search for specific terms
- **Hybrid Search**: Combines vector and keyword search for best results
- **Contextual Filtering**: Filter results by service type, location, or date

### Knowledge Base
- **City Services**: Comprehensive database of municipal services
- **Procedures**: Step-by-step guides for common citizen tasks
- **Contact Information**: Department contacts and service hours
- **Forms and Documents**: Links to required forms and applications

### Response Generation
- **Contextual Answers**: Responses based on retrieved documents
- **Multi-turn Conversations**: Maintain context across conversation
- **Fallback Handling**: Graceful responses for unknown queries
- **Source Attribution**: Reference original documents in responses

## 🆘 Troubleshooting

### Common Issues

#### "No API key found"
- **Solution**: Verify `.env` file exists and contains correct keys
- **Check**: File is in correct directory (Virtual-Citizen-Assistant/)

#### "Search index not found"
- **Solution**: Create Azure AI Search index with sample data
- **Check**: Verify search service endpoint and admin key

#### "Module not found" errors
- **Solution**: Ensure virtual environment is activated
- **Check**: Run `pip list` to verify installed packages

#### RAG not returning results
- **Solution**: Check search index has data and is properly configured
- **Check**: Test search queries directly in Azure portal

### Getting Help
1. **Test Setup**: Run `test_setup.py` to verify configuration
2. **Plugin Tests**: Run `test_plugins.py` to check functionality
3. **Review Logs**: Check console output for detailed error messages
4. **Sample Queries**: Start with simple queries to test basic functionality

## 📈 Real-World Applications

### Municipal Use Cases
- **Citizen Service Centers**: Replace phone-based inquiries
- **City Websites**: Intelligent search and assistance
- **Mobile Apps**: On-the-go citizen services
- **Call Center Support**: AI-assisted customer service

### Service Categories
- **Waste Management**: Collection schedules and recycling info
- **Permits and Licenses**: Application processes and requirements
- **Transportation**: Public transit and parking information
- **Emergency Services**: Alert systems and emergency procedures
- **Recreation**: Parks, events, and community programs

### Benefits
- **24/7 Availability**: Always-on citizen assistance
- **Consistent Information**: Accurate, up-to-date responses
- **Reduced Wait Times**: Instant answers to common questions
- **Multi-language Support**: Serve diverse communities
- **Cost Effective**: Reduce staff workload for routine inquiries

## 📚 Additional Resources

- **Semantic Kernel Documentation**: [Microsoft Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/)
- **Azure AI Search**: [Vector Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- **RAG Best Practices**: [Retrieval-Augmented Generation Guide](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/use-your-data)
- **Citizen Service Design**: [Digital Government Guidelines](https://digital.gov/)

---

**Ready to transform citizen services with AI? Start building and make government more accessible! 🤖🏛️**  
**Assistant**: "To apply for a business permit, you'll need to submit Form BP-101 along with the required documents. You can apply online at nyc.gov/permits or visit the Business Services office at..."

**User**: "Are there any current emergency alerts in my area?"  
**Assistant**: "There are currently no active emergency alerts for your zip code. For real-time updates, you can also follow @NYCEmergencyMgmt on social media."

## 🚀 Success Metrics

- **Accuracy**: >90% correct responses for supported query types
- **Response Time**: <3 seconds average response time
- **User Satisfaction**: Intuitive conversation flow and helpful responses
- **Coverage**: Handle at least 80% of common citizen service queries

## 📂 Project Structure

```
Virtual-Citizen-Assistant/
├── src/
│   ├── plugins/
│   │   ├── document_retrieval_plugin.py
│   │   ├── scheduling_plugin.py
│   │   └── alerts_plugin.py
│   ├── models/
│   │   └── citizen_query.py
│   ├── services/
│   │   ├── semantic_kernel_service.py
│   │   └── search_service.py
│   ├── web/
│   │   ├── app.py
│   │   ├── templates/
│   │   └── static/
│   └── config/
│       └── settings.py
├── assets/
│   ├── sample_data/
│   ├── architecture_diagrams/
│   └── screenshots/
├── README.md
├── execution_script.md
├── step_by_step.md
└── requirements.txt
```

## 🎯 Learning Objectives

By completing this use case, you'll learn:
- How to implement RAG patterns with Azure AI Search
- Semantic Kernel plugin development and orchestration  
- Integration patterns for multiple city service APIs
- Deployment strategies for citizen-facing AI applications
- Best practices for conversational AI user experience

## 🏁 Next Steps

1. Review the [execution_script.md](./execution_script.md) for implementation roadmap
2. Follow the detailed [step_by_step.md](./step_by_step.md) guide
3. Explore the sample code in the `src/` directory
4. Use the assets in `assets/` for testing and demonstration

Let's build an AI assistant that makes civic services more accessible! 🌟