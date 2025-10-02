"""
Unit tests for Weather Service
Tests weather data integration and analysis functionality.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import aiohttp

from src.services.weather_service import WeatherService, WeatherAlert
from src.models.emergency_models import WeatherCondition


class TestWeatherService:
    """Test WeatherService functionality."""
    
    def test_weather_service_initialization(self):
        """Test weather service initialization."""
        service = WeatherService("test_api_key")
        assert service.api_key == "test_api_key"
        assert service.base_url == "https://api.openweathermap.org/data/2.5"
        assert service.session is None
    
    def test_weather_service_no_api_key(self):
        """Test weather service without API key."""
        with patch.dict('os.environ', {}, clear=True):
            service = WeatherService()
            assert service.api_key is None
    
    @pytest.mark.asyncio
    async def test_get_current_conditions_no_api_key(self):
        """Test getting current conditions without API key returns mock data."""
        service = WeatherService()  # No API key
        
        condition = await service.get_current_conditions(40.7128, -74.0060)
        
        assert isinstance(condition, WeatherCondition)
        assert condition.temperature == 72.0
        assert condition.humidity == 65
        assert condition.wind_speed == 8.5
        assert condition.conditions == "Clear"
        assert isinstance(condition.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_get_current_conditions_with_api_success(self):
        """Test getting current conditions with successful API response."""
        mock_response_data = {
            "main": {
                "temp": 75.5,
                "humidity": 68,
                "pressure": 1015.2
            },
            "wind": {
                "speed": 12.3,
                "deg": 225
            },
            "visibility": 8000,
            "weather": [
                {"description": "partly cloudy"}
            ]
        }
        
        service = WeatherService("test_key")
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            condition = await service.get_current_conditions(40.7128, -74.0060)
            
            assert condition.temperature == 75.5
            assert condition.humidity == 68
            assert condition.wind_speed == 12.3
            assert condition.wind_direction == 225
            assert condition.pressure == 1015.2
            assert condition.visibility == 8.0  # Converted from meters to km
            assert condition.conditions == "Partly Cloudy"
    
    @pytest.mark.asyncio
    async def test_get_current_conditions_api_error(self):
        """Test handling API error for current conditions."""
        service = WeatherService("test_key")
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response
            
            condition = await service.get_current_conditions(40.7128, -74.0060)
            
            # Should return mock data on error
            assert isinstance(condition, WeatherCondition)
            assert condition.temperature == 70.0
            assert "API Error" in condition.conditions
    
    @pytest.mark.asyncio
    async def test_get_forecast_no_api_key(self):
        """Test getting forecast without API key returns mock data."""
        service = WeatherService()  # No API key
        
        forecast = await service.get_forecast(40.7128, -74.0060, 12)
        
        assert len(forecast) == 12
        assert isinstance(forecast[0], WeatherCondition)
        assert all(isinstance(item, WeatherCondition) for item in forecast)
        
        # Check that timestamps are progressive
        for i in range(1, len(forecast)):
            assert forecast[i].timestamp > forecast[i-1].timestamp
    
    @pytest.mark.asyncio
    async def test_get_forecast_with_api_success(self):
        """Test getting forecast with successful API response."""
        mock_forecast_item = {
            "main": {
                "temp": 68.2,
                "humidity": 72,
                "pressure": 1012.8
            },
            "wind": {
                "speed": 8.7,
                "deg": 135
            },
            "visibility": 9500,
            "weather": [
                {"description": "light rain"}
            ],
            "dt": int(datetime.now().timestamp())
        }
        
        mock_response_data = {
            "list": [mock_forecast_item] * 8  # 8 items for 24 hours (3-hour intervals)
        }
        
        service = WeatherService("test_key")
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            forecast = await service.get_forecast(40.7128, -74.0060, 24)
            
            assert len(forecast) == 8  # 24 hours / 3 hour intervals
            assert forecast[0].temperature == 68.2
            assert forecast[0].humidity == 72
            assert forecast[0].conditions == "Light Rain"
    
    @pytest.mark.asyncio
    async def test_get_severe_weather_alerts_no_api_key(self):
        """Test getting weather alerts without API key."""
        service = WeatherService()  # No API key
        
        alerts = await service.get_severe_weather_alerts(40.7128, -74.0060)
        
        assert isinstance(alerts, list)
        assert len(alerts) == 0  # No alerts in mock mode by default
    
    @pytest.mark.asyncio
    async def test_get_severe_weather_alerts_high_wind(self):
        """Test weather alerts generation based on conditions."""
        service = WeatherService("test_api_key")  # Provide API key to enable alert generation
        
        # Mock high wind conditions
        with patch.object(service, 'get_current_conditions') as mock_conditions:
            high_wind_condition = WeatherCondition(
                temperature=70.0,
                humidity=60,
                wind_speed=40.0,  # High wind speed triggers alert
                wind_direction=180,
                pressure=1013.0,
                visibility=10.0,
                conditions="Windy",
                timestamp=datetime.now()
            )
            mock_conditions.return_value = high_wind_condition
            
            alerts = await service.get_severe_weather_alerts(40.7128, -74.0060)
            
            assert len(alerts) == 1
            assert alerts[0].alert_type == "High Wind Warning"
            assert alerts[0].severity == "Moderate"
            assert "35+ mph" in alerts[0].description
    
    @pytest.mark.asyncio
    async def test_analyze_weather_impact_hurricane_catastrophic(self):
        """Test weather impact analysis for catastrophic hurricane."""
        service = WeatherService()
        
        hurricane_condition = WeatherCondition(
            temperature=78.0,
            humidity=85,
            wind_speed=85.0,  # Hurricane force winds
            wind_direction=90,
            pressure=950.0,
            visibility=2.0,   # Low visibility
            conditions="Hurricane",
            timestamp=datetime.now()
        )
        
        impact = await service.analyze_weather_impact("hurricane", hurricane_condition)
        
        assert impact["impact_level"] == "catastrophic"
        assert "High winds may down power lines" in impact["risk_factors"]
        assert "Low visibility conditions" in impact["risk_factors"]
        assert "Immediate shelter in place" in impact["recommendations"]
        assert impact["evacuation_difficulty"] == "very difficult"
    
    @pytest.mark.asyncio
    async def test_analyze_weather_impact_winter_storm(self):
        """Test weather impact analysis for winter storm."""
        service = WeatherService()
        
        winter_condition = WeatherCondition(
            temperature=25.0,  # Below freezing
            humidity=90,
            wind_speed=30.0,   # High winds
            wind_direction=315,
            pressure=1008.0,
            visibility=3.0,    # Low visibility due to snow
            conditions="Heavy Snow",
            timestamp=datetime.now()
        )
        
        impact = await service.analyze_weather_impact("winter_storm", winter_condition)
        
        assert impact["impact_level"] == "high"
        assert "High winds may down power lines" in impact["risk_factors"]
        assert "Freezing temperatures" in impact["risk_factors"]
        assert "Low visibility conditions" in impact["risk_factors"]
        assert "Activate warming centers" in impact["recommendations"]
        assert "Pre-position utility crews" in impact["recommendations"]
        assert "Restrict non-essential travel" in impact["recommendations"]
        assert impact["evacuation_difficulty"] == "very difficult"
    
    @pytest.mark.asyncio
    async def test_analyze_weather_impact_heat_wave(self):
        """Test weather impact analysis for extreme heat."""
        service = WeatherService()
        
        heat_condition = WeatherCondition(
            temperature=95.0,  # Extreme heat
            humidity=40,
            wind_speed=5.0,
            wind_direction=180,
            pressure=1018.0,
            visibility=10.0,
            conditions="Clear",
            timestamp=datetime.now()
        )
        
        impact = await service.analyze_weather_impact("heat_emergency", heat_condition)
        
        assert "High heat conditions" in impact["risk_factors"]
        assert "Monitor for heat-related emergencies" in impact["recommendations"]
    
    @pytest.mark.asyncio
    async def test_analyze_weather_impact_normal_conditions(self):
        """Test weather impact analysis for normal conditions."""
        service = WeatherService()
        
        normal_condition = WeatherCondition(
            temperature=72.0,
            humidity=55,
            wind_speed=8.0,
            wind_direction=180,
            pressure=1013.0,
            visibility=10.0,
            conditions="Clear",
            timestamp=datetime.now()
        )
        
        impact = await service.analyze_weather_impact("general", normal_condition)
        
        assert impact["impact_level"] == "low"
        assert len(impact["risk_factors"]) == 0
        assert len(impact["recommendations"]) == 0
        assert impact["evacuation_difficulty"] == "normal"
    
    def test_parse_current_weather(self):
        """Test parsing current weather API response."""
        service = WeatherService("test_key")
        
        api_data = {
            "main": {
                "temp": 73.4,
                "humidity": 67,
                "pressure": 1014.2
            },
            "wind": {
                "speed": 11.5,
                "deg": 210
            },
            "visibility": 7500,
            "weather": [
                {"description": "scattered clouds"}
            ]
        }
        
        condition = service._parse_current_weather(api_data)
        
        assert condition.temperature == 73.4
        assert condition.humidity == 67
        assert condition.wind_speed == 11.5
        assert condition.wind_direction == 210
        assert condition.pressure == 1014.2
        assert condition.visibility == 7.5  # Converted to km
        assert condition.conditions == "Scattered Clouds"
    
    def test_parse_current_weather_missing_wind(self):
        """Test parsing current weather API response with missing wind data."""
        service = WeatherService("test_key")
        
        api_data = {
            "main": {
                "temp": 70.0,
                "humidity": 60,
                "pressure": 1013.0
            },
            # Wind data missing
            "visibility": 10000,
            "weather": [
                {"description": "clear sky"}
            ]
        }
        
        condition = service._parse_current_weather(api_data)
        
        assert condition.temperature == 70.0
        assert condition.wind_speed == 0  # Default value
        assert condition.wind_direction == 0  # Default value
        assert condition.conditions == "Clear Sky"
    
    def test_generate_mock_forecast(self):
        """Test mock forecast generation."""
        service = WeatherService()
        
        forecast = service._generate_mock_forecast(24)
        
        assert len(forecast) == 24
        assert all(isinstance(item, WeatherCondition) for item in forecast)
        
        # Check progressive timestamps
        for i in range(1, len(forecast)):
            assert forecast[i].timestamp > forecast[i-1].timestamp
            time_diff = forecast[i].timestamp - forecast[i-1].timestamp
            # Allow for small microsecond differences in time calculation
            assert abs(time_diff.total_seconds() - 3600) < 1  # Within 1 second of 1 hour
        
        # Check varying conditions
        temperatures = [item.temperature for item in forecast]
        assert len(set(temperatures)) > 1  # Should have varying temperatures
    
    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """Test using WeatherService as async context manager."""
        async with WeatherService() as service:
            assert service.session is not None
            condition = await service.get_current_conditions(40.7128, -74.0060)
            assert isinstance(condition, WeatherCondition)
        
        # Session should be closed after context exit
        # Note: In real usage, session would be closed, but in tests it's mocked


class TestWeatherAlert:
    """Test WeatherAlert functionality."""
    
    def test_weather_alert_creation(self):
        """Test creating a weather alert."""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=6)
        affected_areas = ["Downtown", "Coastal Areas"]
        
        alert = WeatherAlert(
            alert_type="Hurricane Warning",
            severity="Extreme",
            title="Hurricane Warning Issued",
            description="Category 3 hurricane approaching",
            start_time=start_time,
            end_time=end_time,
            affected_areas=affected_areas
        )
        
        assert alert.alert_type == "Hurricane Warning"
        assert alert.severity == "Extreme"
        assert alert.title == "Hurricane Warning Issued"
        assert alert.description == "Category 3 hurricane approaching"
        assert alert.start_time == start_time
        assert alert.end_time == end_time
        assert alert.affected_areas == affected_areas
    
    def test_weather_alert_duration(self):
        """Test weather alert duration calculation."""
        start_time = datetime(2025, 10, 15, 10, 0)
        end_time = datetime(2025, 10, 15, 18, 0)
        
        alert = WeatherAlert(
            alert_type="Thunderstorm Warning",
            severity="Moderate",
            title="Severe Thunderstorm Warning",
            description="Severe thunderstorms with hail expected",
            start_time=start_time,
            end_time=end_time,
            affected_areas=["Metro Area"]
        )
        
        duration = alert.end_time - alert.start_time
        assert duration == timedelta(hours=8)