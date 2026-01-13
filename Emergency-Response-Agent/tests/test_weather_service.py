"""Tests for Weather Service."""

import pytest

from src.config import Settings
from src.services.weather_service import WeatherService
from src.models.emergency_models import WeatherCondition


@pytest.fixture
def weather_service():
    """Create weather service with mock settings."""
    settings = Settings()
    settings.use_mock_services = True
    return WeatherService(settings)


class TestWeatherService:
    """Tests for WeatherService."""

    def test_get_current_conditions(self, weather_service):
        """Test getting current weather conditions."""
        weather = weather_service.get_current_conditions(40.7128, -74.0060)

        assert isinstance(weather, WeatherCondition)
        assert -50 <= weather.temperature_f <= 120
        assert 0 <= weather.humidity_percent <= 100
        assert weather.wind_speed_mph >= 0

    def test_get_forecast(self, weather_service):
        """Test getting weather forecast."""
        forecasts = weather_service.get_forecast(40.7128, -74.0060, hours=24)

        assert len(forecasts) == 24
        for forecast in forecasts:
            assert isinstance(forecast, WeatherCondition)

    def test_assess_weather_risk_low(self, weather_service):
        """Test risk assessment for calm weather."""
        weather = WeatherCondition(
            temperature_f=72.0,
            feels_like_f=72.0,
            humidity_percent=50.0,
            wind_speed_mph=10.0,
            wind_direction="N",
            conditions="clear sky",
            visibility_miles=10.0,
            pressure_hpa=1015.0,
        )

        risk = weather_service.assess_weather_risk(weather)

        assert risk.wind_risk == "low"
        assert risk.temperature_risk == "low"
        assert risk.overall_risk == "low"

    def test_assess_weather_risk_high_wind(self, weather_service):
        """Test risk assessment for high winds."""
        weather = WeatherCondition(
            temperature_f=72.0,
            feels_like_f=72.0,
            humidity_percent=50.0,
            wind_speed_mph=45.0,  # High wind
            wind_direction="N",
            conditions="clear sky",
            visibility_miles=10.0,
            pressure_hpa=1015.0,
        )

        risk = weather_service.assess_weather_risk(weather)

        assert risk.wind_risk == "high"
        assert risk.overall_risk == "high"
        # Check for high wind recommendations (secure equipment, postpone activities)
        assert len(risk.recommendations) > 0
        assert any("secure" in rec.lower() or "outdoor" in rec.lower() for rec in risk.recommendations)

    def test_assess_weather_risk_extreme_cold(self, weather_service):
        """Test risk assessment for extreme cold."""
        weather = WeatherCondition(
            temperature_f=10.0,  # Extreme cold
            feels_like_f=5.0,
            humidity_percent=50.0,
            wind_speed_mph=5.0,
            wind_direction="N",
            conditions="clear sky",
            visibility_miles=10.0,
            pressure_hpa=1015.0,
        )

        risk = weather_service.assess_weather_risk(weather)

        assert risk.temperature_risk in ["high", "critical"]

    def test_assess_weather_risk_extreme_heat(self, weather_service):
        """Test risk assessment for extreme heat."""
        weather = WeatherCondition(
            temperature_f=105.0,  # Extreme heat
            feels_like_f=110.0,
            humidity_percent=80.0,
            wind_speed_mph=5.0,
            wind_direction="S",
            conditions="hazy",
            visibility_miles=8.0,
            pressure_hpa=1010.0,
        )

        risk = weather_service.assess_weather_risk(weather)

        assert risk.temperature_risk == "critical"
        assert "extreme temperature" in risk.recommendations[0].lower() or "warming" in " ".join(risk.recommendations).lower() or "cooling" in " ".join(risk.recommendations).lower()

    def test_assess_weather_risk_low_visibility(self, weather_service):
        """Test risk assessment for low visibility."""
        weather = WeatherCondition(
            temperature_f=72.0,
            feels_like_f=72.0,
            humidity_percent=90.0,
            wind_speed_mph=5.0,
            wind_direction="N",
            conditions="fog",
            visibility_miles=0.3,  # Very low
            pressure_hpa=1015.0,
        )

        risk = weather_service.assess_weather_risk(weather)

        assert risk.visibility_risk == "critical"

    def test_analyze_weather_impact_hurricane(self, weather_service):
        """Test weather impact analysis for hurricane."""
        weather = WeatherCondition(
            temperature_f=75.0,
            feels_like_f=78.0,
            humidity_percent=85.0,
            wind_speed_mph=35.0,
            wind_direction="NE",
            conditions="rain",
            visibility_miles=5.0,
            pressure_hpa=1000.0,
        )

        impact = weather_service.analyze_weather_impact(weather, "hurricane")

        assert "weather_conditions" in impact
        assert "risk_assessment" in impact
        assert "emergency_specific_factors" in impact
        assert len(impact["emergency_specific_factors"]) > 0

    def test_analyze_weather_impact_fire(self, weather_service):
        """Test weather impact analysis for fire."""
        weather = WeatherCondition(
            temperature_f=95.0,
            feels_like_f=100.0,
            humidity_percent=15.0,  # Low humidity
            wind_speed_mph=20.0,  # Moderate wind
            wind_direction="W",
            conditions="clear",
            visibility_miles=10.0,
            pressure_hpa=1015.0,
        )

        impact = weather_service.analyze_weather_impact(weather, "fire")

        assert len(impact["emergency_specific_factors"]) > 0
        # Should mention wind and/or humidity
        factors_text = " ".join(impact["emergency_specific_factors"]).lower()
        assert "wind" in factors_text or "humidity" in factors_text

    def test_degrees_to_cardinal(self, weather_service):
        """Test wind direction conversion."""
        assert weather_service._degrees_to_cardinal(0) == "N"
        assert weather_service._degrees_to_cardinal(90) == "E"
        assert weather_service._degrees_to_cardinal(180) == "S"
        assert weather_service._degrees_to_cardinal(270) == "W"
        assert weather_service._degrees_to_cardinal(45) == "NE"
