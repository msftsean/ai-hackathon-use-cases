"""Weather service for real-time weather data and risk assessment."""

import random
from datetime import datetime
from typing import Optional

import requests

from ..config import logger, Settings
from ..models.emergency_models import WeatherCondition, WeatherRiskAssessment


class WeatherService:
    """Service for fetching weather data and assessing weather-related risks."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize weather service."""
        self.settings = settings or Settings()
        self.api_key = self.settings.openweather_api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_current_conditions(self, lat: float, lon: float) -> WeatherCondition:
        """
        Get current weather conditions for a location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            WeatherCondition with current weather data
        """
        if self.settings.has_openweather_api and not self.settings.use_mock_services:
            try:
                return self._fetch_real_weather(lat, lon)
            except Exception as e:
                logger.warning(f"Failed to fetch real weather, using mock: {e}")

        return self._generate_mock_weather_data(lat, lon)

    def _fetch_real_weather(self, lat: float, lon: float) -> WeatherCondition:
        """Fetch weather from OpenWeatherMap API."""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return WeatherCondition(
            temperature_f=data["main"]["temp"],
            feels_like_f=data["main"]["feels_like"],
            humidity_percent=data["main"]["humidity"],
            wind_speed_mph=data["wind"]["speed"],
            wind_direction=self._degrees_to_cardinal(data["wind"].get("deg", 0)),
            conditions=data["weather"][0]["description"],
            visibility_miles=data.get("visibility", 10000) / 1609.34,
            pressure_hpa=data["main"]["pressure"],
        )

    def _generate_mock_weather_data(self, lat: float, lon: float) -> WeatherCondition:
        """Generate realistic mock weather data."""
        # NYC-based mock data with some randomization
        conditions_options = [
            "clear sky",
            "partly cloudy",
            "scattered clouds",
            "light rain",
            "overcast",
        ]

        return WeatherCondition(
            temperature_f=round(random.uniform(35, 85), 1),
            feels_like_f=round(random.uniform(32, 88), 1),
            humidity_percent=round(random.uniform(30, 80), 0),
            wind_speed_mph=round(random.uniform(5, 25), 1),
            wind_direction=random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            conditions=random.choice(conditions_options),
            visibility_miles=round(random.uniform(5, 10), 1),
            pressure_hpa=round(random.uniform(1010, 1025), 0),
        )

    def get_forecast(self, lat: float, lon: float, hours: int = 24) -> list[WeatherCondition]:
        """
        Get weather forecast for specified hours.

        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours to forecast (max 48)

        Returns:
            List of WeatherCondition objects
        """
        # For mock, generate hourly forecasts
        forecasts = []
        base_weather = self._generate_mock_weather_data(lat, lon)

        for i in range(min(hours, 48)):
            # Add some variation to base weather
            forecast = WeatherCondition(
                temperature_f=base_weather.temperature_f + random.uniform(-5, 5),
                feels_like_f=base_weather.feels_like_f + random.uniform(-5, 5),
                humidity_percent=base_weather.humidity_percent + random.uniform(-10, 10),
                wind_speed_mph=max(0, base_weather.wind_speed_mph + random.uniform(-5, 5)),
                wind_direction=base_weather.wind_direction,
                conditions=base_weather.conditions,
                visibility_miles=base_weather.visibility_miles,
                pressure_hpa=base_weather.pressure_hpa,
            )
            forecasts.append(forecast)

        return forecasts

    def assess_weather_risk(self, weather: WeatherCondition) -> WeatherRiskAssessment:
        """
        Assess weather-related risks for emergency planning.

        Args:
            weather: Current weather conditions

        Returns:
            WeatherRiskAssessment with risk levels and recommendations
        """
        recommendations = []

        # Wind risk assessment
        if weather.wind_speed_mph > 60:
            wind_risk = "critical"
            recommendations.append("Suspend all outdoor operations")
            recommendations.append("Activate high-wind emergency protocols")
        elif weather.wind_speed_mph > 40:
            wind_risk = "high"
            recommendations.append("Secure loose equipment and debris")
            recommendations.append("Consider postponing non-essential outdoor activities")
        elif weather.wind_speed_mph > 20:
            wind_risk = "medium"
            recommendations.append("Monitor wind conditions closely")
        else:
            wind_risk = "low"

        # Temperature risk assessment
        if weather.temperature_f < 20 or weather.temperature_f > 100:
            temp_risk = "critical"
            recommendations.append("Activate extreme temperature protocols")
            recommendations.append("Ensure warming/cooling centers are operational")
        elif weather.temperature_f < 32 or weather.temperature_f > 95:
            temp_risk = "high"
            recommendations.append("Monitor for temperature-related emergencies")
        elif weather.temperature_f < 45 or weather.temperature_f > 85:
            temp_risk = "medium"
        else:
            temp_risk = "low"

        # Precipitation risk (based on conditions)
        precip_conditions = ["rain", "snow", "storm", "drizzle", "thunderstorm"]
        if any(cond in weather.conditions.lower() for cond in precip_conditions):
            if "heavy" in weather.conditions.lower() or "thunderstorm" in weather.conditions.lower():
                precip_risk = "high"
                recommendations.append("Prepare for potential flooding")
            else:
                precip_risk = "medium"
        else:
            precip_risk = "low"

        # Visibility risk
        if weather.visibility_miles < 0.5:
            visibility_risk = "critical"
            recommendations.append("Limit vehicle operations to essential only")
        elif weather.visibility_miles < 1:
            visibility_risk = "high"
            recommendations.append("Use extreme caution for vehicle operations")
        elif weather.visibility_miles < 3:
            visibility_risk = "medium"
        else:
            visibility_risk = "low"

        # Overall risk
        risk_values = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        risks = [wind_risk, temp_risk, precip_risk, visibility_risk]
        max_risk_value = max(risk_values[r] for r in risks)
        risk_mapping = {1: "low", 2: "medium", 3: "high", 4: "critical"}
        overall_risk = risk_mapping[max_risk_value]

        return WeatherRiskAssessment(
            wind_risk=wind_risk,
            temperature_risk=temp_risk,
            precipitation_risk=precip_risk,
            visibility_risk=visibility_risk,
            overall_risk=overall_risk,
            recommendations=recommendations,
        )

    def analyze_weather_impact(
        self, weather: WeatherCondition, emergency_type: str
    ) -> dict:
        """
        Analyze weather impact specific to an emergency type.

        Args:
            weather: Current weather conditions
            emergency_type: Type of emergency

        Returns:
            Dictionary with impact analysis
        """
        risk = self.assess_weather_risk(weather)

        impact = {
            "weather_conditions": {
                "temperature": weather.temperature_f,
                "wind_speed": weather.wind_speed_mph,
                "visibility": weather.visibility_miles,
                "conditions": weather.conditions,
            },
            "risk_assessment": {
                "wind": risk.wind_risk,
                "temperature": risk.temperature_risk,
                "precipitation": risk.precipitation_risk,
                "visibility": risk.visibility_risk,
                "overall": risk.overall_risk,
            },
            "recommendations": risk.recommendations,
            "emergency_specific_factors": [],
        }

        # Emergency-specific weather impacts
        if emergency_type == "hurricane":
            impact["emergency_specific_factors"].extend([
                "High winds will impede rescue operations",
                "Storm surge flooding expected in coastal areas",
                "Power outages likely due to wind damage",
            ])
        elif emergency_type == "fire":
            if weather.wind_speed_mph > 15:
                impact["emergency_specific_factors"].append(
                    f"Wind ({weather.wind_speed_mph} mph) may spread fire rapidly"
                )
            if weather.humidity_percent < 30:
                impact["emergency_specific_factors"].append(
                    "Low humidity increases fire spread risk"
                )
        elif emergency_type == "flood":
            impact["emergency_specific_factors"].extend([
                "Monitor water levels continuously",
                "Prepare for potential road closures",
            ])

        return impact

    @staticmethod
    def _degrees_to_cardinal(degrees: float) -> str:
        """Convert wind direction in degrees to cardinal direction."""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        idx = int((degrees + 11.25) / 22.5) % 16
        return directions[idx]
