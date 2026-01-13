# Quickstart: Emergency Response Planning Agent

**Feature**: 003-emergency-response-agent
**Time to Complete**: ~10 minutes

## Prerequisites

- Python 3.11+
- pip or uv package manager

## Setup

### 1. Create Project Directory

```bash
cd c:/Users/segayle/repos/hackathon/newyork
mkdir Emergency-Response-Agent
cd Emergency-Response-Agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings (optional - works with defaults)
```

Required only if using real APIs:
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key (optional, has mock fallback)
- `AZURE_OPENAI_KEY`: Azure OpenAI key (optional for basic demo)

## Run the Demo

### Option 1: Interactive Demo

```bash
python demo.py
```

Expected output:
```
============================================================
Emergency Response Planning Agent - Demo
NY State AI Hackathon
============================================================

[OK] Components initialized

Demo 1: Hurricane Scenario
--------------------------
Creating scenario: Category 4 Hurricane - Manhattan
  Type: hurricane
  Severity: 4 (Severe)
  Population: 500,000
  Duration: 72 hours

Generating response plan...
  [OK] Plan generated in 0.8s
  Lead Agency: Office of Emergency Management
  Supporting: Fire Department, Police Department, Red Cross
  Personnel: 1,000 total
  Timeline: 5 milestones

Demo 2: Weather Integration
---------------------------
Fetching weather for NYC (40.7128, -74.0060)...
  Temperature: 72°F
  Wind: 15 mph
  Conditions: Clear

Weather Risk Assessment:
  Wind Risk: low
  Temperature Risk: low
  Overall Risk: low

Demo 3: Evacuation Planning
---------------------------
Zone A Evacuation Routes:
  Route 1: Lower Manhattan to Midtown (3.5 mi, 45 min)
  Route 2: Brooklyn Waterfront to Central Brooklyn (8.2 mi, 65 min)

Capacity Analysis:
  Total: 8,250 people/hour
  Zone A evacuation: 77.6 hours

============================================================
DEMO COMPLETE
============================================================
```

### Option 2: Web API

```bash
python -m src.main
```

Then access:
- API: http://localhost:5002/api/v1
- Health: http://localhost:5002/api/v1/health

### Option 3: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific category
pytest tests/test_models.py -v

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

## Quick API Examples

### Create Scenario

```bash
curl -X POST http://localhost:5002/api/v1/scenarios \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "hurricane",
    "severity_level": 4,
    "location": "Manhattan, NYC",
    "affected_area_radius": 10.0,
    "estimated_population_affected": 500000,
    "duration_hours": 72
  }'
```

### Generate Response Plan

```bash
curl -X POST http://localhost:5002/api/v1/scenarios/{scenario_id}/plan
```

### Get Weather

```bash
curl "http://localhost:5002/api/v1/weather/current?lat=40.7128&lon=-74.0060"
```

### Search Historical Incidents

```bash
curl "http://localhost:5002/api/v1/historical/search?q=hurricane&severity_min=4"
```

## Project Structure

```
Emergency-Response-Agent/
├── src/
│   ├── main.py              # Flask app entry
│   ├── config/settings.py   # Configuration
│   ├── models/              # Pydantic models
│   ├── services/            # Weather, traffic, search
│   ├── orchestration/       # Response coordinator
│   └── api/routes.py        # API endpoints
├── tests/                   # Test suite
├── demo.py                  # Interactive demo
├── requirements.txt         # Dependencies
└── .env.example             # Environment template
```

## Common Issues

### Weather API Returns Mock Data

This is expected if `OPENWEATHER_API_KEY` is not set. The system gracefully falls back to mock data.

### Import Errors

Ensure you're in the project directory and virtual environment is activated:
```bash
cd Emergency-Response-Agent
venv\Scripts\activate  # Windows
```

### Port Already in Use

Change the port:
```bash
FLASK_PORT=5003 python -m src.main
```

## Next Steps

1. **Customize Scenarios**: Edit `src/orchestration/emergency_coordinator.py` to add new emergency types
2. **Add Agencies**: Extend lead/supporting agency mappings
3. **Integrate Real APIs**: Add your API keys to `.env`
4. **Build Dashboard**: Create web UI using `static/` directory
5. **Add Historical Data**: Populate Azure AI Search with real incidents
