"""Test configuration and fixtures."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_emergency_scenario():
    """Create a sample emergency scenario for testing."""
    from src.models.emergency_models import EmergencyScenario, EmergencyType, SeverityLevel
    
    return EmergencyScenario(
        scenario_id="test_scenario_001",
        incident_type=EmergencyType.HURRICANE,
        severity_level=SeverityLevel.HIGH,
        location="Test City",
        affected_area_radius=10.0,
        estimated_population_affected=50000,
        duration_hours=24
    )

@pytest.fixture
def mock_weather_service():
    """Mock weather service for testing."""
    from src.models.emergency_models import WeatherCondition
    from datetime import datetime
    
    mock_service = AsyncMock()
    mock_condition = WeatherCondition(
        temperature=75.0,
        humidity=60,
        wind_speed=15.0,
        wind_direction=180,
        pressure=1013.25,
        visibility=10.0,
        conditions="Partly Cloudy",
        timestamp=datetime.now()
    )
    
    mock_service.get_current_conditions.return_value = mock_condition
    mock_service.get_forecast.return_value = [mock_condition] * 24
    mock_service.get_severe_weather_alerts.return_value = []
    mock_service.analyze_weather_impact.return_value = {
        "impact_level": "moderate",
        "risk_factors": ["Moderate winds"],
        "recommendations": ["Monitor conditions"],
        "evacuation_difficulty": "normal"
    }
    
    return mock_service