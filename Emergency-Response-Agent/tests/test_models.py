"""Tests for Pydantic models."""

import pytest
from datetime import datetime

from src.models import EmergencyType, SeverityLevel
from src.models.emergency_models import (
    EmergencyScenario,
    EmergencyResponsePlan,
    WeatherCondition,
    EvacuationRoute,
    HistoricalIncident,
)


class TestEmergencyScenario:
    """Tests for EmergencyScenario model."""

    def test_create_valid_scenario(self):
        """Test creating a valid scenario."""
        scenario = EmergencyScenario(
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.SEVERE,
            location="Manhattan, NYC",
            affected_area_radius=10.0,
            estimated_population_affected=500000,
            duration_hours=72,
        )

        assert scenario.id is not None
        assert scenario.incident_type == EmergencyType.HURRICANE
        assert scenario.severity_level == SeverityLevel.SEVERE
        assert scenario.estimated_population_affected == 500000

    def test_scenario_with_coordinates(self):
        """Test scenario with coordinates."""
        scenario = EmergencyScenario(
            incident_type=EmergencyType.FLOOD,
            severity_level=SeverityLevel.MODERATE,
            location="Brooklyn",
            coordinates=(40.6782, -73.9442),
            affected_area_radius=5.0,
            estimated_population_affected=100000,
            duration_hours=24,
        )

        assert scenario.coordinates == (40.6782, -73.9442)

    def test_scenario_severity_from_int(self):
        """Test that severity can be provided as int."""
        scenario = EmergencyScenario(
            incident_type="fire",
            severity_level=4,
            location="Bronx",
            affected_area_radius=2.0,
            estimated_population_affected=5000,
            duration_hours=8,
        )

        assert scenario.severity_level == SeverityLevel.SEVERE

    def test_scenario_type_from_string(self):
        """Test that incident_type can be provided as string."""
        scenario = EmergencyScenario(
            incident_type="earthquake",
            severity_level=5,
            location="Queens",
            affected_area_radius=15.0,
            estimated_population_affected=1000000,
            duration_hours=168,
        )

        assert scenario.incident_type == EmergencyType.EARTHQUAKE

    def test_invalid_radius(self):
        """Test that invalid radius raises error."""
        with pytest.raises(Exception):
            EmergencyScenario(
                incident_type=EmergencyType.FIRE,
                severity_level=SeverityLevel.MINOR,
                location="Test",
                affected_area_radius=-1.0,  # Invalid
                estimated_population_affected=100,
                duration_hours=1,
            )

    def test_invalid_population(self):
        """Test that negative population raises error."""
        with pytest.raises(Exception):
            EmergencyScenario(
                incident_type=EmergencyType.FIRE,
                severity_level=SeverityLevel.MINOR,
                location="Test",
                affected_area_radius=1.0,
                estimated_population_affected=-100,  # Invalid
                duration_hours=1,
            )


class TestEmergencyResponsePlan:
    """Tests for EmergencyResponsePlan model."""

    def test_create_valid_plan(self):
        """Test creating a valid response plan."""
        from src.models import ResponsePhase, CoordinationStatus

        plan = EmergencyResponsePlan(
            scenario_id="test-scenario-1",
            lead_agency="Office of Emergency Management",
            supporting_agencies=["FDNY", "NYPD"],
            response_phase=ResponsePhase.PREPARATION,
            coordination_status=CoordinationStatus.ACTIVE,
            personnel_count=500,
            vehicle_count=100,
        )

        assert plan.id is not None
        assert plan.lead_agency == "Office of Emergency Management"
        assert len(plan.supporting_agencies) == 2
        assert plan.personnel_count == 500

    def test_plan_with_resources(self):
        """Test plan with resource allocations."""
        from src.models import ResponsePhase, CoordinationStatus

        resources = [
            {"type": "First Responders", "quantity": 200, "agency": "FDNY"},
            {"type": "Medical Personnel", "quantity": 100, "agency": "EMS"},
        ]

        plan = EmergencyResponsePlan(
            scenario_id="test-scenario-2",
            lead_agency="FDNY",
            supporting_agencies=["NYPD"],
            response_phase=ResponsePhase.RESPONSE,
            coordination_status=CoordinationStatus.ACTIVE,
            personnel_count=300,
            vehicle_count=50,
            resources=resources,
        )

        assert len(plan.resources) == 2
        assert plan.resources[0]["type"] == "First Responders"


class TestWeatherCondition:
    """Tests for WeatherCondition dataclass."""

    def test_create_weather_condition(self):
        """Test creating weather condition."""
        weather = WeatherCondition(
            temperature_f=72.0,
            feels_like_f=74.0,
            humidity_percent=65.0,
            wind_speed_mph=15.0,
            wind_direction="NE",
            conditions="partly cloudy",
            visibility_miles=10.0,
            pressure_hpa=1015.0,
        )

        assert weather.temperature_f == 72.0
        assert weather.wind_speed_mph == 15.0
        assert weather.conditions == "partly cloudy"


class TestEvacuationRoute:
    """Tests for EvacuationRoute dataclass."""

    def test_create_evacuation_route(self):
        """Test creating evacuation route."""
        route = EvacuationRoute(
            route_id="rt_001",
            name="FDR Drive North",
            start_location="Lower Manhattan",
            end_location="Upper East Side",
            distance_miles=8.5,
            estimated_time_minutes=45,
            capacity_per_hour=3500,
            current_status="available",
        )

        assert route.route_id == "rt_001"
        assert route.distance_miles == 8.5
        assert route.capacity_per_hour == 3500


class TestHistoricalIncident:
    """Tests for HistoricalIncident dataclass."""

    def test_create_historical_incident(self):
        """Test creating historical incident."""
        incident = HistoricalIncident(
            id="hist_test",
            incident_type="hurricane",
            severity=4,
            date=datetime(2012, 10, 29),
            location="NYC",
            affected_population=8000000,
            response_time_hours=2.5,
            lessons_learned=["Lesson 1", "Lesson 2"],
            recommendations=["Rec 1"],
            outcome="Significant damage",
        )

        assert incident.id == "hist_test"
        assert incident.severity == 4
        assert len(incident.lessons_learned) == 2
