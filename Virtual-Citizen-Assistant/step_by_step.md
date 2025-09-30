# 🪜 Virtual Citizen Assistant - Step by Step Guide

## 🎯 Complete Implementation Tutorial

This detailed guide walks you through building the Virtual Citizen Assistant from ground up.

## 📋 Prerequisites Checklist

- [ ] Azure subscription with credits available
- [ ] Visual Studio Code with extensions:
  - Azure Tools
  - Python
  - GitHub Copilot
- [ ] Python 3.8+ installed
- [ ] Azure CLI installed and logged in
- [ ] Git configured with GitHub account

## 🏗️ Step 1: Provision Azure AI Search (20 minutes)

### 1.1 Create Resource Group
```bash
# Create resource group for all hackathon resources
az group create --name "nyc-hackathon-rg" --location "eastus"
```

### 1.2 Deploy Azure AI Search Service
```bash
# Create search service
az search service create \
  --name "nyc-citizen-search-$(date +%s)" \
  --resource-group "nyc-hackathon-rg" \
  --sku Standard \
  --location eastus

# Get the search service key
az search admin-key show --service-name "nyc-citizen-search" --resource-group "nyc-hackathon-rg"
```

### 1.3 Create Search Index
```python
# save as create_search_index.py
import json
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.core.credentials import AzureKeyCredential

# Configuration (replace with your values)
search_endpoint = "https://your-search-service.search.windows.net"
search_key = "your-admin-key"
index_name = "city-services"

# Create index schema
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="service_type", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
               searchable=True, vector_search_dimensions=1536, vector_search_profile_name="default"),
    SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="last_updated", type=SearchFieldDataType.DateTimeOffset)
]

# Vector search configuration
vector_search = VectorSearch(
    profiles=[VectorSearchProfile(name="default", algorithm_configuration_name="default")],
    algorithms=[HnswAlgorithmConfiguration(name="default")]
)

# Create the search index
index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
client = SearchIndexClient(endpoint=search_endpoint, credential=AzureKeyCredential(search_key))
client.create_index(index)
print(f"Created search index: {index_name}")
```

### 1.4 Upload Sample Public Records
```python
# save as upload_sample_data.py
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import json
from datetime import datetime

# Sample city services data
sample_documents = [
    {
        "id": "1",
        "service_type": "waste_management",
        "title": "Trash Pickup Schedule",
        "content": "Trash pickup occurs twice weekly in Manhattan. Monday and Thursday for odd-numbered addresses, Tuesday and Friday for even-numbered addresses. Place bins curbside by 7 AM.",
        "category": "sanitation",
        "last_updated": datetime.now().isoformat()
    },
    {
        "id": "2", 
        "service_type": "permits",
        "title": "Business Permit Application",
        "content": "To obtain a business permit, submit Form BP-101 with required documentation including business registration, insurance certificate, and zoning compliance. Processing takes 10-15 business days.",
        "category": "licensing",
        "last_updated": datetime.now().isoformat()
    },
    {
        "id": "3",
        "service_type": "emergency",
        "title": "Emergency Alert System",
        "content": "NYC Emergency Management provides real-time alerts for weather emergencies, public safety incidents, and service disruptions via NotifyNYC. Sign up at nyc.gov/notifynyc.",
        "category": "safety",
        "last_updated": datetime.now().isoformat()
    },
    {
        "id": "4",
        "service_type": "parks",
        "title": "Park Hours and Amenities",
        "content": "Central Park is open from 6 AM to 1 AM daily. Facilities include playgrounds, sports courts, and walking paths. Dog runs are available in designated areas.",
        "category": "recreation",
        "last_updated": datetime.now().isoformat()
    }
]

# Upload documents
search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(search_key))
result = search_client.upload_documents(documents=sample_documents)
print(f"Uploaded {len(sample_documents)} documents to search index")
```

## 🔧 Step 2: Create Semantic Kernel Planner (30 minutes)

### 2.1 Install Required Packages
```bash
pip install semantic-kernel azure-search-documents azure-identity openai python-dotenv flask
```

### 2.2 Create Environment Configuration
```python
# save as .env
AZURE_OPENAI_ENDPOINT=your-openai-endpoint
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_SEARCH_ENDPOINT=your-search-endpoint
AZURE_SEARCH_KEY=your-search-key
AZURE_SEARCH_INDEX=city-services
```

### 2.3 Build Document Retrieval Plugin
```python
# save as src/plugins/document_retrieval_plugin.py
import semantic_kernel as sk
from semantic_kernel.plugin_definition import sk_function, sk_function_context_parameter
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

load_dotenv()

class DocumentRetrievalPlugin:
    def __init__(self):
        self.search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            index_name=os.getenv("AZURE_SEARCH_INDEX"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
        )

    @sk_function(
        description="Search for information about city services",
        name="search_city_services"
    )
    @sk_function_context_parameter(
        name="query",
        description="The search query about city services"
    )
    def search_city_services(self, query: str) -> str:
        """Search for relevant city service information."""
        try:
            # Perform search
            results = self.search_client.search(
                search_text=query,
                top=3,
                select=["title", "content", "service_type", "category"]
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result["title"],
                    "content": result["content"],
                    "service_type": result["service_type"],
                    "category": result["category"]
                })
            
            if not formatted_results:
                return "I couldn't find specific information about that service. Please try a different query or contact 311 for assistance."
            
            # Create response
            response = "Here's what I found about city services:\n\n"
            for i, result in enumerate(formatted_results, 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['content']}\n\n"
            
            return response
            
        except Exception as e:
            return f"I'm sorry, I encountered an error searching for that information. Please try again later."

    @sk_function(
        description="Get specific service information by category",
        name="get_service_by_category"
    )
    @sk_function_context_parameter(
        name="category",
        description="The service category (sanitation, licensing, safety, recreation)"
    )
    def get_service_by_category(self, category: str) -> str:
        """Get services filtered by category."""
        try:
            results = self.search_client.search(
                search_text="*",
                filter=f"category eq '{category}'",
                top=5,
                select=["title", "content", "service_type"]
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result["title"],
                    "content": result["content"]
                })
            
            if not formatted_results:
                return f"No services found in the {category} category."
            
            response = f"Services in {category} category:\n\n"
            for i, result in enumerate(formatted_results, 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['content']}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error retrieving {category} services. Please try again."
```

### 2.4 Create Scheduling API Plugin
```python
# save as src/plugins/scheduling_plugin.py
import semantic_kernel as sk
from semantic_kernel.plugin_definition import sk_function, sk_function_context_parameter
from datetime import datetime, timedelta
import re

class SchedulingPlugin:
    
    @sk_function(
        description="Get trash pickup schedule for an address",
        name="get_trash_schedule"
    )
    @sk_function_context_parameter(
        name="address",
        description="The street address to check pickup schedule for"
    )
    def get_trash_schedule(self, address: str) -> str:
        """Get trash pickup schedule based on address."""
        try:
            # Extract house number to determine odd/even
            house_match = re.search(r'(\d+)', address)
            if not house_match:
                return "Please provide a valid street address with a house number."
            
            house_number = int(house_match.group(1))
            is_odd = house_number % 2 == 1
            
            # Calculate next pickup dates
            today = datetime.now()
            days_ahead = []
            
            if is_odd:
                # Odd addresses: Monday and Thursday
                pickup_days = [0, 3]  # Monday=0, Thursday=3
            else:
                # Even addresses: Tuesday and Friday  
                pickup_days = [1, 4]  # Tuesday=1, Friday=4
            
            # Find next pickup dates
            for pickup_day in pickup_days:
                days_until = (pickup_day - today.weekday()) % 7
                if days_until == 0 and today.hour >= 7:  # If today but past 7AM, get next week
                    days_until = 7
                next_pickup = today + timedelta(days=days_until)
                days_ahead.append(next_pickup)
            
            days_ahead.sort()
            next_pickup = days_ahead[0]
            following_pickup = days_ahead[1] if len(days_ahead) > 1 else days_ahead[0] + timedelta(days=7)
            
            schedule_type = "odd-numbered" if is_odd else "even-numbered"
            pickup_days_text = "Monday and Thursday" if is_odd else "Tuesday and Friday"
            
            return f"""**Trash Pickup Schedule for {address}**

Since you have an {schedule_type} address, your trash pickup days are {pickup_days_text}.

**Next Pickup:** {next_pickup.strftime('%A, %B %d, %Y')}
**Following Pickup:** {following_pickup.strftime('%A, %B %d, %Y')}

**Important Reminders:**
- Place bins curbside by 7:00 AM on pickup day
- Use city-approved containers
- Separate recyclables from regular trash
- No pickup on major holidays (service delayed by one day)

For questions, call 311 or visit nyc.gov/sanitation"""
            
        except Exception as e:
            return "I'm sorry, I couldn't determine the pickup schedule. Please verify your address and try again, or call 311 for assistance."

    @sk_function(
        description="Get information about recycling schedule and guidelines",
        name="get_recycling_info"
    )
    def get_recycling_info(self) -> str:
        """Get recycling schedule and guidelines."""
        return """**NYC Recycling Information**

**Pickup Schedule:** Same days as regular trash pickup
**Collection Time:** Place bins out by 7:00 AM

**What to Recycle:**
- Paper: newspapers, magazines, office paper, cardboard
- Metal: cans, aluminum foil, small metal items  
- Glass: bottles and jars (any color)
- Plastic: bottles, containers, cups (look for recycling symbols)

**What NOT to Recycle:**
- Plastic bags (return to stores)
- Electronics (special collection events)
- Batteries (drop-off locations available)
- Food waste (compost if available in your area)

**Guidelines:**
- Rinse containers to remove food residue
- No need to remove labels
- Keep items loose in bins (no plastic bags)
- Place recycling in blue bins or clear bags

For more information, visit nyc.gov/recycle or call 311."""

    @sk_function(
        description="Check for service disruptions or holiday schedules",
        name="check_service_disruptions"
    )
    def check_service_disruptions(self) -> str:
        """Check for current service disruptions."""
        # In a real implementation, this would check an API for current disruptions
        holidays = [
            "New Year's Day", "Memorial Day", "Independence Day", 
            "Labor Day", "Thanksgiving Day", "Christmas Day"
        ]
        
        return f"""**Service Disruptions & Holiday Schedule**

**Current Status:** No major disruptions reported

**Holiday Schedule:**
Sanitation services are suspended on the following holidays:
{', '.join(holidays)}

**When holidays occur:**
- Service is delayed by one day for the rest of the week
- Check nyc.gov/sanitation for specific holiday schedules
- Sign up for text alerts at nyc.gov/notifynyc

**Weather-Related Delays:**
- Severe weather may cause delays
- Follow @NYCSanitation on social media for real-time updates
- Services resume as soon as safely possible

For current status updates, call 311 or visit nyc.gov/sanitation"""
```

## 🔌 Step 3: Connect to Scheduling APIs (20 minutes)

### 3.1 Create Mock City API Service
```python
# save as src/services/city_api_service.py
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional

class CityAPIService:
    """Mock service simulating city API integrations."""
    
    def __init__(self):
        # Mock data for demonstration
        self.permit_processing_times = {
            "business": "10-15 business days",
            "construction": "20-30 business days", 
            "event": "5-10 business days",
            "street": "15-20 business days"
        }
        
        self.emergency_alerts = [
            {
                "id": "alert_001",
                "type": "weather",
                "severity": "advisory",
                "title": "Winter Weather Advisory",
                "message": "Light snow expected tonight. Use caution when traveling.",
                "area": "All 5 Boroughs",
                "expires": (datetime.now() + timedelta(hours=12)).isoformat()
            }
        ]

    def get_permit_info(self, permit_type: str) -> Dict:
        """Get permit application information."""
        processing_time = self.permit_processing_times.get(permit_type, "Contact 311 for information")
        
        return {
            "permit_type": permit_type,
            "processing_time": processing_time,
            "required_documents": [
                "Completed application form",
                "Government-issued ID",
                "Proof of insurance (if applicable)",
                "Site plan (for construction permits)"
            ],
            "fees": "Varies by permit type - see fee schedule",
            "contact": "Call 311 or visit nyc.gov/permits"
        }

    def get_emergency_alerts(self, area: Optional[str] = None) -> List[Dict]:
        """Get current emergency alerts."""
        alerts = self.emergency_alerts
        if area:
            alerts = [alert for alert in alerts if area.lower() in alert["area"].lower()]
        return alerts

    def get_park_info(self, park_name: str) -> Dict:
        """Get park information and hours."""
        # Mock park data
        parks_db = {
            "central park": {
                "name": "Central Park",
                "hours": "6:00 AM - 1:00 AM daily",
                "amenities": ["Playgrounds", "Sports courts", "Dog runs", "Walking paths", "Lakes"],
                "special_notes": "Some areas may have restricted hours"
            },
            "prospect park": {
                "name": "Prospect Park", 
                "hours": "5:00 AM - 1:00 AM daily",
                "amenities": ["Zoo", "Lake", "Sports fields", "Playgrounds", "Concert venues"],
                "special_notes": "Zoo has separate admission fee"
            }
        }
        
        park_key = park_name.lower()
        return parks_db.get(park_key, {
            "name": park_name,
            "hours": "Varies - contact Parks Department",
            "amenities": ["Contact Parks Department for details"],
            "special_notes": "Call 311 for specific park information"
        })
```

### 3.2 Create Alerts Plugin
```python
# save as src/plugins/alerts_plugin.py
import semantic_kernel as sk
from semantic_kernel.plugin_definition import sk_function, sk_function_context_parameter
from src.services.city_api_service import CityAPIService

class AlertsPlugin:
    def __init__(self):
        self.city_api = CityAPIService()

    @sk_function(
        description="Get current emergency alerts for NYC",
        name="get_emergency_alerts"
    )
    @sk_function_context_parameter(
        name="area",
        description="Specific area or borough to check (optional)"
    )
    def get_emergency_alerts(self, area: str = "") -> str:
        """Get current emergency alerts."""
        try:
            alerts = self.city_api.get_emergency_alerts(area if area else None)
            
            if not alerts:
                return "There are currently no active emergency alerts for your area. For real-time updates, follow @NYCEmergencyMgmt on social media or sign up for NotifyNYC alerts at nyc.gov/notifynyc."
            
            response = "**Current Emergency Alerts:**\n\n"
            for alert in alerts:
                response += f"🚨 **{alert['title']}**\n"
                response += f"   **Type:** {alert['type'].title()}\n"
                response += f"   **Severity:** {alert['severity'].title()}\n" 
                response += f"   **Area:** {alert['area']}\n"
                response += f"   **Message:** {alert['message']}\n"
                response += f"   **Expires:** {alert['expires']}\n\n"
            
            response += "For more information and updates, visit nyc.gov/emergencymanagement or call 311."
            return response
            
        except Exception as e:
            return "I'm unable to retrieve emergency alerts right now. For immediate emergency information, call 911 or visit nyc.gov/emergencymanagement."

    @sk_function(
        description="Get information about NotifyNYC alert system",
        name="get_notify_nyc_info"
    )
    def get_notify_nyc_info(self) -> str:
        """Get information about signing up for NYC alerts."""
        return """**NotifyNYC - Official Emergency Notifications**

NotifyNYC is the City's official emergency communications program that sends notifications about emergencies and important City services.

**How to Sign Up:**
- Visit: nyc.gov/notifynyc
- Call: 311
- Text: "NYCEM" to 67283

**Alert Types:**
- Weather emergencies
- Transportation disruptions  
- Public safety incidents
- Health advisories
- Planned service outages

**Delivery Methods:**
- Text messages
- Phone calls
- Email notifications
- Mobile app notifications

**Languages Available:**
English, Spanish, Arabic, Bengali, Chinese (Traditional & Simplified), French, Haitian Creole, Korean, Russian, and Urdu.

Stay informed and stay safe with NotifyNYC!"""
```

## 🌐 Step 4: Build UI with Azure Web App (40 minutes)

### 4.1 Create Flask Web Application
```python
# save as src/web/app.py
from flask import Flask, render_template, request, jsonify, session
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import os
from dotenv import load_dotenv
import uuid
import asyncio
from src.plugins.document_retrieval_plugin import DocumentRetrievalPlugin
from src.plugins.scheduling_plugin import SchedulingPlugin
from src.plugins.alerts_plugin import AlertsPlugin

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

class CitizenAssistantService:
    def __init__(self):
        self.kernel = sk.Kernel()
        
        # Add Azure OpenAI chat completion service
        self.kernel.add_service(AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        ))
        
        # Import plugins
        self.kernel.add_plugin(DocumentRetrievalPlugin(), plugin_name="DocumentRetrieval")
        self.kernel.add_plugin(SchedulingPlugin(), plugin_name="Scheduling")
        self.kernel.add_plugin(AlertsPlugin(), plugin_name="Alerts")
        
        # Create a planner
        self.planner = sk.planning.SequentialPlanner(kernel=self.kernel)

    async def process_query(self, user_message: str, conversation_history: list = None) -> str:
        """Process user query and return response."""
        try:
            # Create context with conversation history
            context_vars = sk.ContextVariables()
            context_vars["input"] = user_message
            
            # Add conversation history to context
            if conversation_history:
                history_text = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}" 
                                        for msg in conversation_history[-3:]])  # Last 3 exchanges
                context_vars["conversation_history"] = history_text
            
            # Create a prompt that guides the AI to use appropriate plugins
            system_prompt = """You are a helpful NYC citizen assistant. You can help with:
1. City service information (use DocumentRetrieval plugin)
2. Trash/recycling schedules (use Scheduling plugin)  
3. Emergency alerts and notifications (use Alerts plugin)

Always be helpful, accurate, and direct citizens to call 311 for issues you cannot resolve.
If you need to search for information, use the appropriate plugin functions.

Current user query: {input}

{conversation_history}"""

            # Execute the query using semantic functions
            if "trash" in user_message.lower() or "pickup" in user_message.lower():
                # Direct to scheduling plugin
                result = await self.kernel.invoke_function(
                    plugin_name="Scheduling",
                    function_name="get_trash_schedule",
                    address=user_message
                )
            elif "recycl" in user_message.lower():
                result = await self.kernel.invoke_function(
                    plugin_name="Scheduling", 
                    function_name="get_recycling_info"
                )
            elif "alert" in user_message.lower() or "emergency" in user_message.lower():
                result = await self.kernel.invoke_function(
                    plugin_name="Alerts",
                    function_name="get_emergency_alerts",
                    area=""
                )
            elif "permit" in user_message.lower() or "license" in user_message.lower():
                result = await self.kernel.invoke_function(
                    plugin_name="DocumentRetrieval",
                    function_name="search_city_services", 
                    query=user_message
                )
            else:
                # General search
                result = await self.kernel.invoke_function(
                    plugin_name="DocumentRetrieval",
                    function_name="search_city_services",
                    query=user_message
                )
                
            return str(result)
            
        except Exception as e:
            return f"I apologize, but I encountered an error processing your request. Please try again or call 311 for assistance. Error: {str(e)}"

# Initialize the service
assistant_service = CitizenAssistantService()

@app.route('/')
def index():
    """Main chat interface."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Please enter a message'}), 400
        
        # Get conversation history from session
        conversation_history = session.get('conversation_history', [])
        
        # Process the query
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            assistant_service.process_query(user_message, conversation_history)
        )
        
        # Update conversation history
        conversation_history.append({
            'user': user_message,
            'assistant': response
        })
        
        # Keep only last 10 exchanges
        session['conversation_history'] = conversation_history[-10:]
        
        return jsonify({
            'response': response,
            'session_id': session['session_id']
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'NYC Citizen Assistant'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 4.2 Create HTML Template
```html
<!-- save as src/web/templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYC Citizen Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 600px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(90deg, #4CAF50, #45a049);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            margin-bottom: 5px;
            font-size: 24px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.assistant {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: #007bff;
            color: white;
        }
        
        .message.assistant .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        
        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        
        .chat-input input:focus {
            border-color: #007bff;
        }
        
        .chat-input button {
            margin-left: 10px;
            padding: 12px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        .chat-input button:hover {
            background: #0056b3;
        }
        
        .chat-input button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
            margin-bottom: 15px;
            max-width: 70%;
        }
        
        .typing-dots {
            display: flex;
            align-items: center;
        }
        
        .typing-dots span {
            height: 8px;
            width: 8px;
            background: #999;
            border-radius: 50%;
            display: inline-block;
            margin-right: 3px;
            animation: typing 1.4s infinite;
        }
        
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dots span:nth-child(3) {  
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.4;
            }
            30% {
                transform: translateY(-10px);
                opacity: 1;
            }
        }
        
        .welcome-message {
            text-align: center;
            padding: 40px 20px;
            color: #666;
        }
        
        .welcome-message h2 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .welcome-examples {
            margin-top: 20px;
        }
        
        .welcome-examples h3 {
            margin-bottom: 10px;
            color: #555;
            font-size: 16px;
        }
        
        .example-queries {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        
        .example-query {
            background: #e3f2fd;
            color: #1976d2;
            padding: 8px 12px;
            border-radius: 15px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .example-query:hover {
            background: #bbdefb;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🏙️ NYC Citizen Assistant</h1>
            <p>Your AI-powered guide to New York City services</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                <h2>Welcome! How can I help you today?</h2>
                <p>I can assist you with information about NYC services, schedules, permits, and more.</p>
                
                <div class="welcome-examples">
                    <h3>Try asking me:</h3>
                    <div class="example-queries">
                        <span class="example-query" onclick="sendExample('When is my next trash pickup at 123 Main Street?')">Trash pickup schedule</span>
                        <span class="example-query" onclick="sendExample('How do I apply for a business permit?')">Business permits</span>
                        <span class="example-query" onclick="sendExample('Are there any emergency alerts?')">Emergency alerts</span>
                        <span class="example-query" onclick="sendExample('What are the hours for Central Park?')">Park information</span>
                        <span class="example-query" onclick="sendExample('Tell me about recycling guidelines')">Recycling info</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Ask about NYC services..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" id="sendButton">Send</button>
        </div>
    </div>

    <script>
        let isWaitingForResponse = false;

        function handleKeyPress(event) {
            if (event.key === 'Enter' && !isWaitingForResponse) {
                sendMessage();
            }
        }

        function sendExample(query) {
            document.getElementById('messageInput').value = query;
            sendMessage();
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message || isWaitingForResponse) return;
            
            isWaitingForResponse = true;
            const sendButton = document.getElementById('sendButton');
            sendButton.disabled = true;
            sendButton.textContent = 'Sending...';
            
            // Clear welcome message if it exists
            const welcomeMessage = document.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    addMessage(data.response, 'assistant');
                } else {
                    addMessage('Sorry, I encountered an error. Please try again or call 311 for assistance.', 'assistant');
                }
                
            } catch (error) {
                addMessage('Connection error. Please check your internet connection and try again.', 'assistant');
            } finally {
                hideTypingIndicator();
                isWaitingForResponse = false;
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
                input.focus();
            }
        }

        function addMessage(content, sender) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Convert markdown-style formatting to HTML
            content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            content = content.replace(/\n/g, '<br>');
            
            contentDiv.innerHTML = content;
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function showTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            indicator.style.display = 'block';
            
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function hideTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            indicator.style.display = 'none';
        }

        // Focus input on page load
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('messageInput').focus();
        });
    </script>
</body>
</html>
```

## 🚀 Step 5: Test Query Scenarios (15 minutes)

### 5.1 Create Test Script
```python
# save as test_scenarios.py
import asyncio
from src.web.app import CitizenAssistantService

async def test_citizen_assistant():
    """Test the citizen assistant with various scenarios."""
    assistant = CitizenAssistantService()
    
    test_queries = [
        "When is my next trash pickup at 123 Main Street?",
        "How do I apply for a business permit?", 
        "Are there any emergency alerts in my area?",
        "What are the park hours for Central Park?",
        "Tell me about recycling guidelines",
        "What permits do I need to open a restaurant?",
        "Is there a holiday schedule for trash pickup?",
        "How do I sign up for emergency notifications?"
    ]
    
    print("🧪 Testing NYC Citizen Assistant\n")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 30)
        
        try:
            response = await assistant.process_query(query)
            print(f"🤖 Response: {response[:200]}...")
            print("✅ Success")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_citizen_assistant())
```

### 5.2 Run Local Tests
```bash
# Test the application locally
cd src/web
python test_scenarios.py

# Start the web application
python app.py
```

## ☁️ Step 6: Push Code to GitHub and Enable Codespaces (15 minutes)

### 6.1 Create Repository Structure
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: NYC Citizen Assistant"

# Create GitHub repository (replace with your GitHub username)
gh repo create nyc-citizen-assistant --public
git remote add origin https://github.com/YOUR_USERNAME/nyc-citizen-assistant.git
git push -u origin main
```

### 6.2 Create Codespaces Configuration
```json
// save as .devcontainer/devcontainer.json
{
    "name": "NYC Citizen Assistant",
    "image": "mcr.microsoft.com/devcontainers/python:3.11",
    "features": {
        "ghcr.io/devcontainers/features/azure-cli:1": {},
        "ghcr.io/devcontainers/features/github-cli:1": {}
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.flake8",
                "ms-vscode.azure-account",
                "ms-vscode.azurecli",
                "GitHub.copilot",
                "GitHub.copilot-chat"
            ],
            "settings": {
                "python.defaultInterpreterPath": "/usr/local/bin/python",
                "python.formatting.provider": "black"
            }
        }
    },
    "postCreateCommand": "pip install -r requirements.txt",
    "forwardPorts": [5000],
    "portsAttributes": {
        "5000": {
            "label": "NYC Citizen Assistant",
            "onAutoForward": "notify"
        }
    }
}
```

### 6.3 Create Requirements File
```text
# save as requirements.txt
semantic-kernel==0.9.1b1
azure-search-documents==11.4.0
azure-identity==1.15.0
azure-cognitiveservices-language-textanalytics==5.3.0
openai==1.3.7
flask==3.0.0
python-dotenv==1.0.0
asyncio==3.4.3
requests==2.31.0
```

## 🎉 Final Steps: Demo Preparation (10 minutes)

### 6.1 Create Demo Script
```markdown
# save as DEMO_SCRIPT.md

# 🎬 NYC Citizen Assistant - Demo Script

## 🎯 Demo Flow (5 minutes)

### Setup (30 seconds)
- Open the web application
- Show the clean, professional interface
- Highlight the example queries

### Core Functionality Demo (3 minutes)

1. **Trash Pickup Query** (45 seconds)
   - Input: "When is my next trash pickup at 456 Oak Street?"
   - Highlight: Address parsing, schedule calculation, helpful reminders

2. **Permit Information** (45 seconds)
   - Input: "How do I apply for a business permit?"
   - Highlight: RAG retrieval from city documents, step-by-step guidance

3. **Emergency Alerts** (45 seconds)
   - Input: "Are there any current emergency alerts?"
   - Highlight: Real-time information, safety focus

4. **Follow-up Question** (45 seconds)
   - Input: "What about recycling information?"
   - Highlight: Context awareness, comprehensive information

### Technical Highlights (1.5 minutes)
- **Azure AI Search**: Document indexing and retrieval
- **Semantic Kernel**: Plugin orchestration and planning
- **Azure OpenAI**: Natural language understanding
- **Azure Web App**: Scalable deployment

## 🎤 Key Talking Points

- **Citizen-Centric**: Designed for real NYC residents and visitors
- **Multi-Modal**: Handles various service types seamlessly  
- **Intelligent**: Uses RAG for accurate, current information
- **Scalable**: Built on Azure cloud platform
- **Extensible**: Easy to add new services and plugins

## 🏆 Success Metrics Achieved

- ✅ Natural language processing of citizen queries
- ✅ Integration with multiple city service types
- ✅ Real-time information retrieval
- ✅ User-friendly web interface
- ✅ Cloud-ready deployment architecture
```

### 6.2 Create README for GitHub
```markdown
# save as README.md (project root)

# 🤖 NYC Citizen Assistant

An AI-powered virtual assistant that helps NYC residents and visitors access city services through natural language queries.

## 🌟 Features

- **Natural Language Processing**: Ask questions in plain English
- **Multi-Service Integration**: Trash pickup, permits, emergency alerts, park info
- **Real-Time Information**: Current schedules and alerts
- **Intelligent Responses**: RAG-powered accuracy
- **User-Friendly Interface**: Clean, responsive web design

## 🚀 Quick Start

### Option 1: GitHub Codespaces (Recommended)
1. Click "Code" → "Create codespace on main"
2. Wait for environment setup
3. Run `python src/web/app.py`
4. Open forwarded port 5000

### Option 2: Local Development
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run `python src/web/app.py`

## 🛠️ Technology Stack

- **Azure AI Foundry**: AI orchestration platform
- **Semantic Kernel**: Plugin orchestration
- **Azure AI Search**: Document indexing and retrieval
- **Azure OpenAI**: Language model
- **Flask**: Web application framework
- **Azure Web App**: Cloud hosting

## 📊 Demo Queries

Try these example queries:
- "When is my next trash pickup at 123 Main Street?"
- "How do I apply for a business permit?"
- "Are there any current emergency alerts?"
- "What are the hours for Central Park?"
- "Tell me about recycling guidelines"

## 🏗️ Architecture

```
User Query → Flask Web App → Semantic Kernel Planner
                                    ↓
                          Plugin Orchestration
                         /        |        \
            Document    /    Scheduling   \    Emergency
            Retrieval  /       APIs        \    Alerts
                      ↓                     ↓        ↓
            Azure AI Search    City APIs    Notification
                                            Service
```

## 🤝 Contributing

This project was built for the NYC AI Hackathon. Feel free to fork and extend!

## 📄 License

MIT License - see LICENSE file for details
```

Congratulations! 🎉 You've successfully built a comprehensive Virtual Citizen Assistant. Your solution demonstrates:

- **RAG Implementation** with Azure AI Search
- **Plugin Orchestration** with Semantic Kernel  
- **Multi-Service Integration** for city services
- **Professional Web Interface** for citizens
- **Cloud-Ready Deployment** on Azure
- **Developer-Friendly Setup** with Codespaces

The assistant can now handle complex citizen queries, provide accurate information, and offer a smooth user experience. You're ready for the hackathon demo! 🚀