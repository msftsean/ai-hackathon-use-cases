# Emergency Response Agent

Multi-agent AI system for emergency response planning and coordination. Generates coordinated response plans across multiple NY State agencies using weather data integration and resource management.

## Quick Start

### 1. Setup Environment

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

### 2. Run Demo (Mock Mode)

No Azure services required:

```bash
python demo.py
```

### 3. Run Tests

```bash
python -m pytest tests/ -v
```

## Features

- **Emergency Scenario Simulation**: Hurricane, fire, flood, winter storm, public health, earthquake
- **Multi-Agent Orchestration**: Coordinated planning across specialized AI agents
- **Real-time Weather Integration**: NWS API for weather threat assessment
- **Resource Coordination**: Track and allocate resources across agencies
- **Evacuation Planning**: Route optimization with bottleneck analysis
- **Historical Analysis**: Learn from past incident responses

## Emergency Types Supported

| Type | Lead Agency | Key Resources |
|------|-------------|---------------|
| Hurricane | OEM | Evacuation, shelters |
| Fire | FDNY | Firefighters, equipment |
| Flooding | OEM | Pumps, rescue boats |
| Winter Storm | DOT | Plows, salt trucks |
| Public Health | DOH | Healthcare workers, vaccines |
| Earthquake | OEM | Search & rescue teams |
| Infrastructure | Utilities | Emergency generators |

## Project Structure

```
Emergency-Response-Agent/
├── src/
│   ├── agents/          # Specialized AI agents
│   ├── api/             # Flask routes
│   ├── config/          # Settings
│   ├── models/          # Emergency models
│   ├── orchestration/   # Multi-agent coordinator
│   └── services/        # Weather, traffic APIs
├── assets/              # Static resources
├── static/              # Web interface
├── tests/               # Test suite (62 tests)
├── demo.py              # Interactive demo
└── requirements.txt
```

## Multi-Agent Architecture

```
┌─────────────────────────────────────────┐
│           Orchestration Agent           │
│    (Coordinates all response agents)    │
└─────────────────────────────────────────┘
         │           │           │
         ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Weather │ │Resource │ │Logistics│
    │  Agent  │ │  Agent  │ │  Agent  │
    └─────────┘ └─────────┘ └─────────┘
```

## Configuration

For Azure services, create a `.env` file based on `.env.example`:

```env
USE_MOCK_SERVICES=false
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your-key
NWS_API_ENDPOINT=https://api.weather.gov
```

## Coordinated Agencies

- **OEM**: Office of Emergency Management
- **FDNY**: Fire Department
- **NYPD**: Police Department
- **DOT**: Department of Transportation
- **MTA**: Metropolitan Transit Authority
- **DOH**: Department of Health

## Tech Stack

- **Semantic Kernel**: Multi-agent orchestration
- **Azure OpenAI**: Planning and analysis
- **NWS API**: Weather data integration
- **Flask**: Web API framework
- **Pydantic**: Data models

## Hackathon Team

NY State AI Hackathon - January 2026
