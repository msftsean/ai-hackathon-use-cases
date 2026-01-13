"""Tests for Emergency Response Coordinator."""

import pytest

from src.config import Settings
from src.models import EmergencyType, SeverityLevel
from src.models.emergency_models import EmergencyScenario
from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator


@pytest.fixture
def coordinator():
    """Create coordinator with mock settings."""
    settings = Settings()
    settings.use_mock_services = True
    return EmergencyResponseCoordinator(settings)


@pytest.fixture
def hurricane_scenario():
    """Create a hurricane scenario."""
    return EmergencyScenario(
        incident_type=EmergencyType.HURRICANE,
        severity_level=SeverityLevel.SEVERE,
        location="Manhattan, NYC",
        coordinates=(40.7128, -74.0060),
        affected_area_radius=10.0,
        estimated_population_affected=500000,
        duration_hours=72,
    )


@pytest.fixture
def fire_scenario():
    """Create a fire scenario."""
    return EmergencyScenario(
        incident_type=EmergencyType.FIRE,
        severity_level=SeverityLevel.MODERATE,
        location="Bronx, NYC",
        affected_area_radius=2.0,
        estimated_population_affected=5000,
        duration_hours=8,
    )


class TestEmergencyResponseCoordinator:
    """Tests for EmergencyResponseCoordinator."""

    def test_create_scenario(self, coordinator, hurricane_scenario):
        """Test creating a scenario."""
        created = coordinator.create_scenario(hurricane_scenario)

        assert created.id == hurricane_scenario.id
        assert coordinator.get_scenario(created.id) is not None

    def test_list_scenarios(self, coordinator, hurricane_scenario, fire_scenario):
        """Test listing scenarios."""
        coordinator.create_scenario(hurricane_scenario)
        coordinator.create_scenario(fire_scenario)

        scenarios = coordinator.list_scenarios()
        assert len(scenarios) == 2

    @pytest.mark.asyncio
    async def test_coordinate_response_hurricane(self, coordinator, hurricane_scenario):
        """Test generating response plan for hurricane."""
        coordinator.create_scenario(hurricane_scenario)

        plan = await coordinator.coordinate_response(hurricane_scenario.id)

        assert plan is not None
        assert plan.scenario_id == hurricane_scenario.id
        assert plan.lead_agency == "Office of Emergency Management"
        assert "Fire Department" in str(plan.supporting_agencies)
        assert plan.personnel_count >= 500  # Hurricane requires significant resources
        assert plan.vehicle_count >= 50
        assert len(plan.timeline_milestones) == 5

    @pytest.mark.asyncio
    async def test_coordinate_response_fire(self, coordinator, fire_scenario):
        """Test generating response plan for fire."""
        coordinator.create_scenario(fire_scenario)

        plan = await coordinator.coordinate_response(fire_scenario.id)

        assert plan is not None
        assert "Fire Department" in plan.lead_agency
        assert plan.personnel_count > 0
        assert len(plan.immediate_actions) > 0

    @pytest.mark.asyncio
    async def test_coordinate_response_not_found(self, coordinator):
        """Test that missing scenario raises error."""
        with pytest.raises(ValueError):
            await coordinator.coordinate_response("nonexistent-id")

    def test_determine_lead_agency(self, coordinator):
        """Test lead agency assignment."""
        assert coordinator._determine_lead_agency(EmergencyType.HURRICANE) == "Office of Emergency Management"
        assert "Fire Department" in coordinator._determine_lead_agency(EmergencyType.FIRE)
        assert "Police Department" in coordinator._determine_lead_agency(EmergencyType.TERRORISM)
        assert "Health" in coordinator._determine_lead_agency(EmergencyType.PUBLIC_HEALTH)

    def test_identify_supporting_agencies(self, coordinator):
        """Test supporting agency identification."""
        agencies = coordinator._identify_supporting_agencies(EmergencyType.HURRICANE)

        assert len(agencies) >= 4
        assert any("Fire" in a for a in agencies)
        assert any("Police" in a for a in agencies)

    def test_resource_multipliers(self, coordinator):
        """Test that resource multipliers are defined for all types."""
        for emergency_type in EmergencyType:
            multiplier = coordinator.RESOURCE_MULTIPLIERS.get(emergency_type, 1.0)
            assert multiplier >= 1.0

    @pytest.mark.asyncio
    async def test_plan_has_immediate_actions(self, coordinator, hurricane_scenario):
        """Test that plan includes immediate actions."""
        coordinator.create_scenario(hurricane_scenario)
        plan = await coordinator.coordinate_response(hurricane_scenario.id)

        assert len(plan.immediate_actions) > 0
        # Should include EOC activation
        actions_text = " ".join(plan.immediate_actions).lower()
        assert "emergency operations center" in actions_text or "eoc" in actions_text

    @pytest.mark.asyncio
    async def test_plan_has_timeline(self, coordinator, hurricane_scenario):
        """Test that plan includes timeline milestones."""
        coordinator.create_scenario(hurricane_scenario)
        plan = await coordinator.coordinate_response(hurricane_scenario.id)

        assert len(plan.timeline_milestones) == 5

        # Check milestone structure
        first_milestone = plan.timeline_milestones[0]
        assert "phase" in first_milestone
        assert "action" in first_milestone
        assert "target_time_hours" in first_milestone

    @pytest.mark.asyncio
    async def test_plan_has_weather_assessment(self, coordinator, hurricane_scenario):
        """Test that plan includes weather assessment when coordinates provided."""
        coordinator.create_scenario(hurricane_scenario)
        plan = await coordinator.coordinate_response(hurricane_scenario.id)

        assert plan.weather_risk_assessment is not None
        assert "risk_assessment" in plan.weather_risk_assessment

    @pytest.mark.asyncio
    async def test_plan_has_evacuation_routes(self, coordinator, hurricane_scenario):
        """Test that hurricane plan includes evacuation routes."""
        coordinator.create_scenario(hurricane_scenario)
        plan = await coordinator.coordinate_response(hurricane_scenario.id)

        assert len(plan.evacuation_routes) > 0

    @pytest.mark.asyncio
    async def test_plan_estimated_cost(self, coordinator, hurricane_scenario):
        """Test that plan includes cost estimate."""
        coordinator.create_scenario(hurricane_scenario)
        plan = await coordinator.coordinate_response(hurricane_scenario.id)

        assert plan.estimated_cost is not None
        assert plan.estimated_cost > 0

    @pytest.mark.asyncio
    async def test_plan_processing_time(self, coordinator, hurricane_scenario):
        """Test that processing time is tracked."""
        coordinator.create_scenario(hurricane_scenario)
        plan = await coordinator.coordinate_response(hurricane_scenario.id)

        assert plan.processing_time_ms is not None
        assert plan.processing_time_ms >= 0  # Can be 0 on fast systems
        assert plan.processing_time_ms < 10000  # Should complete in under 10 seconds


class TestResourceCalculation:
    """Tests for resource calculation logic."""

    @pytest.mark.asyncio
    async def test_hurricane_resources(self, coordinator, hurricane_scenario):
        """Test resource calculation for hurricane."""
        coordinator.create_scenario(hurricane_scenario)
        plan = await coordinator.coordinate_response(hurricane_scenario.id)

        # Hurricane with 500k population, severity 4 should have significant resources
        assert plan.personnel_count >= 500
        assert plan.vehicle_count >= 50
        assert "Pumps" in plan.equipment_list or "Boats" in plan.equipment_list

    @pytest.mark.asyncio
    async def test_fire_resources(self, coordinator, fire_scenario):
        """Test resource calculation for fire."""
        coordinator.create_scenario(fire_scenario)
        plan = await coordinator.coordinate_response(fire_scenario.id)

        # Fire with 5k population, severity 3
        assert plan.personnel_count > 0
        assert "Fire hoses" in plan.equipment_list or "Breathing apparatus" in plan.equipment_list

    @pytest.mark.asyncio
    async def test_severity_affects_resources(self, coordinator):
        """Test that higher severity means more resources."""
        low_scenario = EmergencyScenario(
            incident_type=EmergencyType.FLOOD,
            severity_level=SeverityLevel.MINOR,
            location="Test",
            affected_area_radius=5.0,
            estimated_population_affected=10000,
            duration_hours=24,
        )

        high_scenario = EmergencyScenario(
            incident_type=EmergencyType.FLOOD,
            severity_level=SeverityLevel.CATASTROPHIC,
            location="Test",
            affected_area_radius=5.0,
            estimated_population_affected=10000,
            duration_hours=24,
        )

        coordinator.create_scenario(low_scenario)
        coordinator.create_scenario(high_scenario)

        low_plan = await coordinator.coordinate_response(low_scenario.id)
        high_plan = await coordinator.coordinate_response(high_scenario.id)

        assert high_plan.personnel_count > low_plan.personnel_count
        assert high_plan.vehicle_count > low_plan.vehicle_count
