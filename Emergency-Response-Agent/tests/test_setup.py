"""Setup and infrastructure tests."""

import pytest


def test_imports():
    """Test that all modules can be imported."""
    from src.config import Settings, logger
    from src.models import EmergencyType, SeverityLevel, ResponsePhase
    from src.models.emergency_models import EmergencyScenario, EmergencyResponsePlan
    from src.services.weather_service import WeatherService
    from src.services.traffic_service import TrafficService
    from src.services.search_service import SearchService
    from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator

    assert Settings is not None
    assert logger is not None
    assert EmergencyType is not None
    assert EmergencyScenario is not None


def test_settings_defaults():
    """Test that settings have sensible defaults."""
    from src.config import Settings

    settings = Settings()

    assert settings.flask_port == 5002
    assert settings.use_mock_services is True
    assert settings.log_level == "INFO"


def test_emergency_types():
    """Test that all emergency types are defined."""
    from src.models import EmergencyType

    types = list(EmergencyType)
    assert len(types) == 8
    assert EmergencyType.HURRICANE in types
    assert EmergencyType.FIRE in types
    assert EmergencyType.FLOOD in types


def test_severity_levels():
    """Test severity level values."""
    from src.models import SeverityLevel

    assert SeverityLevel.MINIMAL.value == 1
    assert SeverityLevel.CATASTROPHIC.value == 5
    assert len(list(SeverityLevel)) == 5
