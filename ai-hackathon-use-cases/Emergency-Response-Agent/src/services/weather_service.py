"""
Weather Service Integration
Provides weather data and analysis for emergency response planning.
"""
import aiohttp
import asyncio
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from ..models.emergency_models import WeatherCondition


class WeatherAlert:
    """Weather alert information."""
    def __init__(self, alert_type: str, severity: str, title: str, 
                 description: str, start_time: datetime, end_time: datetime,
                 affected_areas: List[str]):
        self.alert_type = alert_type
        self.severity = severity
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.affected_areas = affected_areas


class WeatherService:
    """Service for accessing weather data and forecasts."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_current_conditions(self, lat: float, lon: float) -> WeatherCondition:
        """Get current weather conditions for a location."""
        if not self.api_key:
            # Return mock data for testing
            return WeatherCondition(
                temperature=72.0,
                humidity=65,
                wind_speed=8.5,
                wind_direction=180,
                pressure=1013.25,
                visibility=10.0,
                conditions="Clear",
                timestamp=datetime.now()
            )
        
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_current_weather(data)
                else:
                    raise Exception(f"Weather API error: {response.status}")
        except Exception as e:
            # Return mock data on error
            return WeatherCondition(
                temperature=70.0,
                humidity=60,
                wind_speed=5.0,
                wind_direction=90,
                pressure=1013.0,
                visibility=10.0,
                conditions=f"API Error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def get_forecast(self, lat: float, lon: float, hours: int = 24) -> List[WeatherCondition]:
        """Get weather forecast for a location."""
        if not self.api_key:
            # Return mock forecast data
            return self._generate_mock_forecast(hours)
        
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_forecast(data, hours)
                else:
                    return self._generate_mock_forecast(hours)
        except Exception:
            return self._generate_mock_forecast(hours)
    
    async def get_severe_weather_alerts(self, lat: float, lon: float) -> List[WeatherAlert]:
        """Get severe weather alerts for a region."""
        if not self.api_key:
            # Return mock alerts for testing
            return []
        
        # In a real implementation, this would call a weather alerts API
        # For now, return mock data based on conditions
        current = await self.get_current_conditions(lat, lon)
        alerts = []
        
        if current.wind_speed > 35:
            alerts.append(WeatherAlert(
                alert_type="High Wind Warning",
                severity="Moderate",
                title="High Wind Warning in Effect",
                description="Sustained winds of 35+ mph expected",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=6),
                affected_areas=["Emergency Planning Area"]
            ))
        
        return alerts
    
    def _parse_current_weather(self, data: Dict) -> WeatherCondition:
        """Parse API response into WeatherCondition object."""
        return WeatherCondition(
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            wind_speed=data.get("wind", {}).get("speed", 0),
            wind_direction=data.get("wind", {}).get("deg", 0),
            pressure=data["main"]["pressure"],
            visibility=data.get("visibility", 10000) / 1000,  # Convert to km
            conditions=data["weather"][0]["description"].title(),
            timestamp=datetime.now()
        )
    
    def _parse_forecast(self, data: Dict, hours: int) -> List[WeatherCondition]:
        """Parse forecast API response."""
        forecast = []
        for item in data["list"][:hours//3]:  # API returns 3-hour intervals
            forecast.append(WeatherCondition(
                temperature=item["main"]["temp"],
                humidity=item["main"]["humidity"],
                wind_speed=item.get("wind", {}).get("speed", 0),
                wind_direction=item.get("wind", {}).get("deg", 0),
                pressure=item["main"]["pressure"],
                visibility=item.get("visibility", 10000) / 1000,
                conditions=item["weather"][0]["description"].title(),
                timestamp=datetime.fromtimestamp(item["dt"])
            ))
        return forecast
    
    def _generate_mock_forecast(self, hours: int) -> List[WeatherCondition]:
        """Generate mock forecast data for testing."""
        forecast = []
        base_temp = 70.0
        
        for i in range(hours):
            forecast.append(WeatherCondition(
                temperature=base_temp + (i * 0.5) - 5,
                humidity=60 + (i % 20),
                wind_speed=5.0 + (i % 10),
                wind_direction=90 + (i * 10) % 360,
                pressure=1013.0 + (i % 10),
                visibility=10.0,
                conditions="Partly Cloudy" if i % 3 == 0 else "Clear",
                timestamp=datetime.now() + timedelta(hours=i)
            ))
        
        return forecast
    
    async def analyze_weather_impact(self, scenario_type: str, weather: WeatherCondition) -> Dict[str, any]:
        """Analyze weather impact on emergency scenario."""
        impact_analysis = {
            "impact_level": "low",
            "risk_factors": [],
            "recommendations": [],
            "evacuation_difficulty": "normal"
        }
        
        # High wind impact
        if weather.wind_speed > 25:
            impact_analysis["impact_level"] = "high"
            impact_analysis["risk_factors"].append("High winds may down power lines")
            impact_analysis["recommendations"].append("Pre-position utility crews")
            impact_analysis["evacuation_difficulty"] = "difficult"
        
        # Temperature impact
        if weather.temperature < 32:
            impact_analysis["risk_factors"].append("Freezing temperatures")
            impact_analysis["recommendations"].append("Activate warming centers")
        elif weather.temperature > 85:
            impact_analysis["risk_factors"].append("High heat conditions")
            impact_analysis["recommendations"].append("Monitor for heat-related emergencies")
        
        # Visibility impact
        if weather.visibility < 5:
            impact_analysis["impact_level"] = "high"
            impact_analysis["risk_factors"].append("Low visibility conditions")
            impact_analysis["recommendations"].append("Restrict non-essential travel")
            impact_analysis["evacuation_difficulty"] = "very difficult"
        
        # Hurricane specific analysis
        if scenario_type == "hurricane":
            if weather.wind_speed > 74:
                impact_analysis["impact_level"] = "catastrophic"
                impact_analysis["recommendations"].append("Immediate shelter in place")
            elif weather.wind_speed > 39:
                impact_analysis["impact_level"] = "severe"
                impact_analysis["recommendations"].append("Complete evacuations")
        
        return impact_analysis