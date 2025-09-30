# 🪜 Emergency Response Agent - Step by Step Guide

## 🎯 Complete Implementation Tutorial

This detailed guide walks you through building the Emergency Response Planning Agent with multi-agent orchestration from ground up.

## 📋 Prerequisites Checklist

- [ ] Azure subscription with credits available
- [ ] Visual Studio Code with extensions:
  - Azure Tools
  - Python
  - GitHub Copilot
- [ ] Python 3.8+ installed
- [ ] Azure CLI installed and logged in
- [ ] External API keys:
  - OpenWeatherMap API key
  - Google Maps API key (optional)
- [ ] Git configured with GitHub account

## 🏗️ Step 1: Set Up Historical Data Repository (25 minutes)

### 1.1 Create Azure AI Search for Incident History
```bash
# Create resource group if not exists
az group create --name "nyc-emergency-rg" --location "eastus"

# Create Azure AI Search service
az search service create \
  --name "nyc-emergency-search-$(date +%s)" \
  --resource-group "nyc-emergency-rg" \
  --sku "Standard" \
  --location "eastus"

# Get admin keys
az search admin-key show \
  --service-name "nyc-emergency-search-*" \
  --resource-group "nyc-emergency-rg"
```

### 1.2 Create Historical Incident Index
```python
# save as create_incident_index.py
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.core.credentials import AzureKeyCredential

# Configuration
search_endpoint = "https://your-search-service.search.windows.net"
search_key = "your-admin-key"
index_name = "emergency-incidents"

# Create comprehensive incident schema
fields = [
    SimpleField(name="incident_id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="incident_type", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchableField(name="description", type=SearchFieldDataType.String),
    SimpleField(name="date_occurred", type=SearchFieldDataType.DateTimeOffset, filterable=True),
    SimpleField(name="location", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="severity_level", type=SearchFieldDataType.Int32, filterable=True),
    SearchableField(name="response_actions", type=SearchFieldDataType.String),
    SearchableField(name="resources_deployed", type=SearchFieldDataType.String),
    SearchableField(name="lessons_learned", type=SearchFieldDataType.String),
    SimpleField(name="response_time_minutes", type=SearchFieldDataType.Int32),
    SimpleField(name="effectiveness_score", type=SearchFieldDataType.Double),
    SearchableField(name="agencies_involved", type=SearchFieldDataType.String),
    SimpleField(name="estimated_cost", type=SearchFieldDataType.Double),
    SearchableField(name="weather_conditions", type=SearchFieldDataType.String),
    SimpleField(name="affected_population", type=SearchFieldDataType.Int32)
]

# Create the search index
index = SearchIndex(name=index_name, fields=fields)
client = SearchIndexClient(endpoint=search_endpoint, credential=AzureKeyCredential(search_key))
result = client.create_index(index)
print(f"Created emergency incidents index: {index_name}")
```

### 1.3 Upload Historical Emergency Data
```python
# save as upload_emergency_data.py
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from datetime import datetime, timedelta
import json

# Historical emergency incidents data
historical_incidents = [
    {
        "incident_id": "hurricane_sandy_2012",
        "incident_type": "hurricane",
        "title": "Hurricane Sandy Response",
        "description": "Category 2 hurricane affecting all five boroughs with significant flooding and power outages",
        "date_occurred": "2012-10-29T00:00:00Z",
        "location": "NYC Metro Area",
        "severity_level": 4,
        "response_actions": "Evacuation of Zone A areas, MTA service suspension, emergency shelter activation, National Guard deployment",
        "resources_deployed": "15,000 emergency personnel, 76 emergency shelters, 350 emergency vehicles",
        "lessons_learned": "Better pre-positioning of resources, improved inter-agency communication protocols, enhanced public messaging systems",
        "response_time_minutes": 2880,  # 48 hours prep time
        "effectiveness_score": 7.5,
        "agencies_involved": "FDNY, NYPD, OEM, National Guard, Con Edison, MTA",
        "estimated_cost": 19000000000,  # $19 billion
        "weather_conditions": "90 mph winds, 14 foot storm surge, heavy rain",
        "affected_population": 8400000
    },
    {
        "incident_id": "winter_storm_jonas_2016",
        "incident_type": "winter_storm",
        "title": "Winter Storm Jonas Blizzard Response",
        "description": "Major blizzard bringing 26.8 inches of snow to NYC with travel ban implementation",
        "date_occurred": "2016-01-23T00:00:00Z", 
        "location": "All Five Boroughs",
        "severity_level": 3,
        "response_actions": "Travel ban enforcement, snow removal operations, emergency warming centers, transit service modifications",
        "resources_deployed": "2,500 sanitation workers, 1,200 snow plows, 30 warming centers, 500 salt spreaders",
        "lessons_learned": "Improved snow plow GPS tracking, better coordination with ride-sharing services, enhanced messaging for travel ban",
        "response_time_minutes": 1440,  # 24 hours
        "effectiveness_score": 8.2,
        "agencies_involved": "DSNY, NYPD, FDNY, OEM, MTA, DOT",
        "estimated_cost": 85000000,  # $85 million
        "weather_conditions": "26.8 inch snowfall, 45 mph wind gusts, temperature 18°F",
        "affected_population": 8400000
    },
    {
        "incident_id": "covid19_response_2020",
        "incident_type": "public_health_emergency", 
        "title": "COVID-19 Pandemic Response",
        "description": "Public health emergency response to coronavirus pandemic including lockdowns and healthcare surge",
        "date_occurred": "2020-03-01T00:00:00Z",
        "location": "All Five Boroughs",
        "severity_level": 5,
        "response_actions": "Stay-at-home orders, business closures, field hospital construction, contact tracing program, vaccination distribution",
        "resources_deployed": "15,000 healthcare workers, 5 field hospitals, 3,000 contact tracers, 500 vaccination sites",
        "lessons_learned": "Importance of supply chain resilience, remote work capabilities, digital health systems, community partnerships",
        "response_time_minutes": 10080,  # 7 days initial response
        "effectiveness_score": 6.8,
        "agencies_involved": "DOH, OEM, FDNY, NYPD, HHC, NYC Health + Hospitals",
        "estimated_cost": 4000000000,  # $4 billion
        "weather_conditions": "N/A - Health Emergency",
        "affected_population": 8400000
    },
    {
        "incident_id": "northeast_blackout_2003",
        "incident_type": "infrastructure_failure",
        "title": "Northeast Blackout Power Grid Failure",
        "description": "Widespread power outage affecting 50 million people including 8 million in NYC area",
        "date_occurred": "2003-08-14T16:10:00Z",
        "location": "NYC and Northeast US",
        "severity_level": 4,
        "response_actions": "Emergency generator deployment, traffic control at intersections, emergency shelter opening, communication system backup activation",
        "resources_deployed": "10,000 emergency personnel, 200 emergency generators, 50 emergency shelters, 1,000 traffic control officers",
        "lessons_learned": "Need for backup communication systems, improved generator placement, better inter-utility coordination, enhanced grid monitoring",
        "response_time_minutes": 120,  # 2 hours
        "effectiveness_score": 7.8,
        "agencies_involved": "Con Edison, FDNY, NYPD, OEM, DOT, MTA",
        "estimated_cost": 6000000000,  # $6 billion economic impact
        "weather_conditions": "Hot summer day, 85°F temperature",
        "affected_population": 8400000
    },
    {
        "incident_id": "september_11_2001",
        "incident_type": "terrorist_attack",
        "title": "September 11 World Trade Center Attack Response",
        "description": "Terrorist attack on World Trade Center requiring massive emergency response and evacuation",
        "date_occurred": "2001-09-11T08:46:00Z",
        "location": "Lower Manhattan",
        "severity_level": 5,
        "response_actions": "Evacuation of Lower Manhattan, emergency medical response, search and rescue operations, airspace closure, perimeter establishment",
        "resources_deployed": "35,000 emergency personnel, 500 emergency vehicles, 100 ambulances, National Guard units",
        "lessons_learned": "Importance of interoperable communications, unified command structure, psychological support services, business continuity planning",
        "response_time_minutes": 15,  # Initial response
        "effectiveness_score": 8.5,
        "agencies_involved": "FDNY, NYPD, Port Authority, FBI, National Guard, Coast Guard",
        "estimated_cost": 55000000000,  # $55 billion economic impact
        "weather_conditions": "Clear sky, 72°F temperature",
        "affected_population": 2800000  # Lower Manhattan evacuation
    }
]

# Upload to search index
search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(search_key))
result = search_client.upload_documents(documents=historical_incidents)
print(f"Uploaded {len(historical_incidents)} historical incidents to search index")
```

## 🌤️ Step 2: Set Up External API Integrations (20 minutes)

### 2.1 Weather Service Integration
```python
# save as src/services/weather_service.py
import aiohttp
import asyncio
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WeatherCondition:
    temperature: float
    humidity: int
    wind_speed: float
    wind_direction: int
    pressure: float
    visibility: float
    conditions: str
    timestamp: datetime

@dataclass
class WeatherAlert:
    alert_type: str
    severity: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    affected_areas: List[str]

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.alerts_url = "https://api.openweathermap.org/data/3.0"
    
    async def get_current_conditions(self, lat: float, lon: float) -> WeatherCondition:
        """Get current weather conditions for location."""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                return WeatherCondition(
                    temperature=data["main"]["temp"],
                    humidity=data["main"]["humidity"],
                    wind_speed=data["wind"]["speed"],
                    wind_direction=data["wind"]["deg"],
                    pressure=data["main"]["pressure"],
                    visibility=data.get("visibility", 10000) / 1000,  # Convert to miles
                    conditions=data["weather"][0]["description"],
                    timestamp=datetime.now()
                )
    
    async def get_forecast(self, lat: float, lon: float, hours: int = 24) -> List[WeatherCondition]:
        """Get weather forecast for specified hours."""
        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                forecasts = []
                for item in data["list"][:hours//3]:  # 3-hour intervals
                    forecast = WeatherCondition(
                        temperature=item["main"]["temp"],
                        humidity=item["main"]["humidity"],
                        wind_speed=item["wind"]["speed"],
                        wind_direction=item["wind"]["deg"],
                        pressure=item["main"]["pressure"],
                        visibility=item.get("visibility", 10000) / 1000,
                        conditions=item["weather"][0]["description"],
                        timestamp=datetime.fromtimestamp(item["dt"])
                    )
                    forecasts.append(forecast)
                
                return forecasts
    
    async def get_severe_weather_alerts(self, lat: float, lon: float) -> List[WeatherAlert]:
        """Get active severe weather alerts for location."""
        url = f"{self.alerts_url}/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "exclude": "minutely,daily"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    alerts = []
                    if "alerts" in data:
                        for alert_data in data["alerts"]:
                            alert = WeatherAlert(
                                alert_type=alert_data.get("event", "Unknown"),
                                severity="High",  # OpenWeatherMap doesn't provide severity
                                title=alert_data.get("event", "Weather Alert"),
                                description=alert_data.get("description", ""),
                                start_time=datetime.fromtimestamp(alert_data["start"]),
                                end_time=datetime.fromtimestamp(alert_data["end"]),
                                affected_areas=["NYC Metro Area"]  # Simplified
                            )
                            alerts.append(alert)
                    
                    return alerts
        
        except Exception as e:
            print(f"Error fetching weather alerts: {e}")
            return []
    
    def assess_weather_risk(self, conditions: WeatherCondition, forecast: List[WeatherCondition]) -> Dict[str, any]:
        """Assess weather-related risks for emergency planning."""
        risks = {
            "wind_risk": "low",
            "precipitation_risk": "low", 
            "temperature_risk": "low",
            "visibility_risk": "low",
            "overall_risk": "low",
            "recommendations": []
        }
        
        # Wind risk assessment
        max_wind = max([conditions.wind_speed] + [f.wind_speed for f in forecast])
        if max_wind > 40:
            risks["wind_risk"] = "high"
            risks["recommendations"].append("Secure outdoor equipment and signage")
        elif max_wind > 25:
            risks["wind_risk"] = "medium"
        
        # Temperature risk assessment
        min_temp = min([conditions.temperature] + [f.temperature for f in forecast])
        max_temp = max([conditions.temperature] + [f.temperature for f in forecast])
        
        if min_temp < 20:
            risks["temperature_risk"] = "high"
            risks["recommendations"].append("Activate warming centers")
        elif max_temp > 95:
            risks["temperature_risk"] = "high"
            risks["recommendations"].append("Open cooling centers")
        
        # Precipitation risk (based on conditions description)
        precip_conditions = ["rain", "snow", "storm", "thunderstorm", "drizzle"]
        if any(condition in conditions.conditions.lower() for condition in precip_conditions):
            risks["precipitation_risk"] = "medium"
            if "storm" in conditions.conditions.lower() or "thunderstorm" in conditions.conditions.lower():
                risks["precipitation_risk"] = "high"
                risks["recommendations"].append("Monitor for flooding and power outages")
        
        # Overall risk assessment
        high_risks = sum(1 for risk in [risks["wind_risk"], risks["precipitation_risk"], risks["temperature_risk"]] if risk == "high")
        if high_risks >= 2:
            risks["overall_risk"] = "high"
        elif high_risks >= 1:
            risks["overall_risk"] = "medium"
        
        return risks

# NYC coordinates for testing
NYC_COORDINATES = {
    "manhattan": (40.7831, -73.9712),
    "brooklyn": (40.6782, -73.9442),
    "queens": (40.7282, -73.7949),
    "bronx": (40.8448, -73.8648),
    "staten_island": (40.5795, -74.1502)
}
```

### 2.2 Traffic and Transportation Service
```python
# save as src/services/traffic_service.py
import aiohttp
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class TrafficCondition:
    route_name: str
    current_speed: float
    free_flow_speed: float
    congestion_level: str  # "free_flow", "moderate", "heavy", "severe"
    travel_time_minutes: int
    incidents: List[str]
    last_updated: datetime

@dataclass
class EvacuationRoute:
    route_id: str
    origin: str
    destination: str
    distance_miles: float 
    estimated_time_minutes: int
    capacity_vehicles_per_hour: int
    current_usage_percent: float
    alternate_routes: List[str]
    bottlenecks: List[str]

class TrafficService:
    def __init__(self, google_maps_api_key: Optional[str] = None):
        self.google_maps_api_key = google_maps_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
        # NYC major routes and their normal capacities
        self.major_routes = {
            "FDR_Drive": {"capacity": 4000, "bottlenecks": ["Brooklyn Bridge", "Williamsburg Bridge"]},
            "West_Side_Highway": {"capacity": 3500, "bottlenecks": ["Lincoln Tunnel", "Holland Tunnel"]},
            "BQE": {"capacity": 5000, "bottlenecks": ["Kosciuszko Bridge", "Gowanus Expressway"]},
            "LIE": {"capacity": 6000, "bottlenecks": ["Midtown Tunnel", "Queens Boulevard"]},
            "Major_Deegan": {"capacity": 4500, "bottlenecks": ["RFK Bridge", "GW Bridge"]},
            "Cross_Bronx": {"capacity": 5500, "bottlenecks": ["GW Bridge", "Bruckner Interchange"]}
        }
    
    async def get_traffic_conditions(self, routes: List[str] = None) -> List[TrafficCondition]:
        """Get current traffic conditions for major NYC routes."""
        if routes is None:
            routes = list(self.major_routes.keys())
        
        conditions = []
        
        # Mock implementation - in production, integrate with Google Traffic API or NYC DOT
        for route in routes:
            # Simulate realistic traffic conditions
            import random
            base_speed = random.uniform(25, 45)  # Base highway speed
            congestion_factor = random.uniform(0.3, 1.0)
            current_speed = base_speed * congestion_factor
            
            if congestion_factor > 0.8:
                congestion_level = "free_flow"
            elif congestion_factor > 0.6:
                congestion_level = "moderate"
            elif congestion_factor > 0.3:
                congestion_level = "heavy"
            else:
                congestion_level = "severe"
            
            # Estimate travel time (assuming 10-mile average route)
            travel_time = int((10 / current_speed) * 60)
            
            condition = TrafficCondition(
                route_name=route,
                current_speed=current_speed,
                free_flow_speed=base_speed,
                congestion_level=congestion_level,
                travel_time_minutes=travel_time,
                incidents=[] if congestion_factor > 0.7 else ["Construction", "Disabled Vehicle"],
                last_updated=datetime.now()
            )\n            conditions.append(condition)\n        \n        return conditions\n    \n    async def optimize_evacuation_routes(self, evacuation_zones: List[str], shelters: List[str]) -> List[EvacuationRoute]:\n        \"\"\"Optimize evacuation routes from zones to shelters.\"\"\"\n        routes = []\n        \n        # Pre-defined evacuation routes for NYC\n        predefined_routes = [\n            {\n                \"route_id\": \"ZONE_A_TO_MANHATTAN_SHELTERS\",\n                \"origin\": \"Lower Manhattan (Zone A)\",\n                \"destination\": \"Midtown Manhattan Shelters\",\n                \"distance_miles\": 3.5,\n                \"estimated_time_minutes\": 45,\n                \"capacity_vehicles_per_hour\": 2000,\n                \"current_usage_percent\": 0.0,\n                \"alternate_routes\": [\"FDR_Drive\", \"West_Side_Highway\"],\n                \"bottlenecks\": [\"Brooklyn Bridge Access\", \"FDR Drive Merge\"]\n            },\n            {\n                \"route_id\": \"BROOKLYN_WATERFRONT_TO_INLAND\",\n                \"origin\": \"Brooklyn Waterfront\",\n                \"destination\": \"Central Brooklyn Shelters\",\n                \"distance_miles\": 8.2,\n                \"estimated_time_minutes\": 65,\n                \"capacity_vehicles_per_hour\": 1800,\n                \"current_usage_percent\": 0.0,\n                \"alternate_routes\": [\"BQE\", \"Atlantic Avenue\"],\n                \"bottlenecks\": [\"Gowanus Expressway\", \"Atlantic Terminal Area\"]\n            },\n            {\n                \"route_id\": \"QUEENS_COASTAL_TO_INLAND\",\n                \"origin\": \"Queens Coastal Areas\",\n                \"destination\": \"Central Queens Shelters\",\n                \"distance_miles\": 12.1,\n                \"estimated_time_minutes\": 85,\n                \"capacity_vehicles_per_hour\": 1500,\n                \"current_usage_percent\": 0.0,\n                \"alternate_routes\": [\"LIE\", \"Northern Boulevard\"],\n                \"bottlenecks\": [\"LIE Entrance Ramps\", \"Queens Boulevard\"]\n            }\n        ]\n        \n        for route_data in predefined_routes:\n            route = EvacuationRoute(\n                route_id=route_data[\"route_id\"],\n                origin=route_data[\"origin\"],\n                destination=route_data[\"destination\"],\n                distance_miles=route_data[\"distance_miles\"],\n                estimated_time_minutes=route_data[\"estimated_time_minutes\"],\n                capacity_vehicles_per_hour=route_data[\"capacity_vehicles_per_hour\"],\n                current_usage_percent=route_data[\"current_usage_percent\"],\n                alternate_routes=route_data[\"alternate_routes\"],\n                bottlenecks=route_data[\"bottlenecks\"]\n            )\n            routes.append(route)\n        \n        return routes\n    \n    async def get_public_transportation_status(self) -> Dict[str, any]:\n        \"\"\"Get current MTA service status.\"\"\"\n        # Mock MTA service status - in production, integrate with MTA APIs\n        return {\n            \"subway\": {\n                \"operational_lines\": [\"4\", \"5\", \"6\", \"N\", \"Q\", \"R\", \"W\"],\n                \"suspended_lines\": [\"1\", \"2\", \"3\"],  # Lower Manhattan evacuation\n                \"service_changes\": {\n                    \"express_service_suspended\": True,\n                    \"increased_frequency\": [\"4\", \"5\", \"6\"],\n                    \"extended_hours\": True\n                }\n            },\n            \"buses\": {\n                \"additional_routes\": [\"M15\", \"M20\", \"B63\"],\n                \"evacuation_shuttles\": {\n                    \"active\": True,\n                    \"routes\": [\n                        \"Lower Manhattan to Midtown\",\n                        \"Brooklyn Waterfront to Central Brooklyn\"\n                    ]\n                }\n            },\n            \"ferries\": {\n                \"suspended\": True,\n                \"reason\": \"High winds and storm surge\"\n            },\n            \"last_updated\": datetime.now().isoformat()\n        }\n    \n    def calculate_evacuation_capacity(self, routes: List[EvacuationRoute]) -> Dict[str, int]:\n        \"\"\"Calculate total evacuation capacity and timeline.\"\"\"\n        total_capacity_per_hour = sum(route.capacity_vehicles_per_hour for route in routes)\n        \n        # Assume average 1.5 people per vehicle during evacuation\n        people_per_hour = total_capacity_per_hour * 1.5\n        \n        # NYC evacuation zone populations (simplified)\n        zone_populations = {\n            \"Zone_A\": 640000,  # Approximately 640k in Zone A\n            \"Zone_B\": 1200000,  # Approximately 1.2M in Zone B\n            \"Zone_C\": 1800000   # Approximately 1.8M in Zone C\n        }\n        \n        evacuation_times = {}\n        for zone, population in zone_populations.items():\n            hours_needed = population / people_per_hour\n            evacuation_times[zone] = {\n                \"population\": population,\n                \"hours_to_evacuate\": round(hours_needed, 1),\n                \"recommended_start_time\": f\"{int(hours_needed) + 12} hours before landfall\"\n            }\n        \n        return {\n            \"total_hourly_capacity\": int(people_per_hour),\n            \"evacuation_times\": evacuation_times,\n            \"bottleneck_analysis\": self._analyze_bottlenecks(routes)\n        }\n    \n    def _analyze_bottlenecks(self, routes: List[EvacuationRoute]) -> List[Dict[str, any]]:\n        \"\"\"Analyze potential bottlenecks in evacuation routes.\"\"\"\n        bottleneck_analysis = []\n        \n        # Collect all bottlenecks from routes\n        all_bottlenecks = {}\n        for route in routes:\n            for bottleneck in route.bottlenecks:\n                if bottleneck not in all_bottlenecks:\n                    all_bottlenecks[bottleneck] = {\n                        \"name\": bottleneck,\n                        \"affected_routes\": [],\n                        \"severity\": \"medium\"\n                    }\n                all_bottlenecks[bottleneck][\"affected_routes\"].append(route.route_id)\n        \n        # Assess severity based on number of affected routes\n        for bottleneck_name, bottleneck_data in all_bottlenecks.items():\n            affected_count = len(bottleneck_data[\"affected_routes\"])\n            if affected_count >= 3:\n                bottleneck_data[\"severity\"] = \"high\"\n            elif affected_count >= 2:\n                bottleneck_data[\"severity\"] = \"medium\"\n            else:\n                bottleneck_data[\"severity\"] = \"low\"\n            \n            bottleneck_analysis.append(bottleneck_data)\n        \n        return sorted(bottleneck_analysis, key=lambda x: len(x[\"affected_routes\"]), reverse=True)"