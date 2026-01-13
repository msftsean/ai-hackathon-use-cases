"""
Unit tests for Emergency Response Coordinator
Tests the main orchestration and planning functionality.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator
from src.models.emergency_models import (
    EmergencyScenario, EmergencyResponsePlan, EmergencyType, SeverityLevel
)


class TestEmergencyResponseCoordinator:
    """Test EmergencyResponseCoordinator functionality."""
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        coordinator = EmergencyResponseCoordinator()
        
        assert coordinator.kernel is not None
        assert coordinator.weather_service is not None
        assert coordinator.logger is not None
    
    @pytest.mark.asyncio
    async def test_coordinate_response_basic(self, sample_emergency_scenario):
        """Test basic response coordination."""
        coordinator = EmergencyResponseCoordinator()
        
        with patch.object(coordinator, '_perform_scenario_analysis') as mock_analysis, \
             patch.object(coordinator, '_generate_response_plan') as mock_plan, \
             patch.object(coordinator, '_allocate_resources') as mock_resources, \
             patch.object(coordinator, '_create_timeline') as mock_timeline:
            
            mock_analysis.return_value = {"scenario_type": "hurricane", "severity_assessment": {"level": 3}}
            mock_plan.return_value = EmergencyResponsePlan(
                plan_id="test_plan",
                scenario=sample_emergency_scenario,
                lead_agency="Emergency Management",
                activation_time=datetime.now(),
                estimated_duration=timedelta(hours=24)
            )
            
            result = await coordinator.coordinate_response(sample_emergency_scenario)
            
            assert isinstance(result, EmergencyResponsePlan)
            assert result.plan_id == "test_plan"
            mock_analysis.assert_called_once_with(sample_emergency_scenario)
            mock_plan.assert_called_once()
            mock_resources.assert_called_once()
            mock_timeline.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_perform_scenario_analysis_hurricane(self):
        """Test scenario analysis for hurricane."""
        coordinator = EmergencyResponseCoordinator()
        
        hurricane_scenario = EmergencyScenario(
            scenario_id="hurricane_test",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.SEVERE,
            location="Miami, FL",
            affected_area_radius=20.0,
            estimated_population_affected=200000,
            duration_hours=48
        )
        
        analysis = await coordinator._perform_scenario_analysis(hurricane_scenario)
        
        assert analysis["scenario_type"] == "hurricane"
        assert analysis["severity_assessment"]["level"] == 4  # SEVERE
        assert "Large population impact" in analysis["severity_assessment"]["factors"]
        assert "Wide geographic area affected" in analysis["severity_assessment"]["factors"]
        assert analysis["population_impact"]["directly_affected"] == 200000
        assert analysis["population_impact"]["potentially_affected"] == 300000  # 1.5x
        assert "Zone A (Coastal)" in analysis["population_impact"]["evacuation_zones"]
    
    @pytest.mark.asyncio
    async def test_perform_scenario_analysis_fire(self):
        """Test scenario analysis for fire emergency."""
        coordinator = EmergencyResponseCoordinator()
        
        fire_scenario = EmergencyScenario(
            scenario_id="fire_test",
            incident_type=EmergencyType.FIRE,
            severity_level=SeverityLevel.HIGH,
            location="Wildland Area",
            affected_area_radius=5.0,
            estimated_population_affected=5000,
            duration_hours=12
        )
        
        analysis = await coordinator._perform_scenario_analysis(fire_scenario)
        
        assert analysis["scenario_type"] == "fire"
        assert analysis["severity_assessment"]["escalation_potential"] == "high"
        assert "Immediate area" in analysis["population_impact"]["evacuation_zones"]
        assert "Adjacent neighborhoods" in analysis["population_impact"]["evacuation_zones"]
    
    def test_assess_severity_large_population(self):
        """Test severity assessment for large population impact."""
        coordinator = EmergencyResponseCoordinator()
        
        large_scenario = EmergencyScenario(
            scenario_id="large_test",
            incident_type=EmergencyType.FLOOD,
            severity_level=SeverityLevel.MODERATE,
            location="Metro Area",
            affected_area_radius=15.0,
            estimated_population_affected=150000
        )
        
        assessment = coordinator._assess_severity(large_scenario)
        
        assert assessment["level"] == 2  # MODERATE
        assert "Large population impact" in assessment["factors"]
        assert "Wide geographic area affected" in assessment["factors"]
    
    def test_assess_escalation_potential_public_health(self):
        """Test escalation potential assessment for public health emergency."""
        coordinator = EmergencyResponseCoordinator()
        
        health_scenario = EmergencyScenario(
            scenario_id="health_test",
            incident_type=EmergencyType.PUBLIC_HEALTH,
            severity_level=SeverityLevel.MODERATE,
            location="City Center",
            affected_area_radius=3.0,
            estimated_population_affected=10000
        )
        
        escalation = coordinator._assess_escalation_potential(health_scenario)
        assert escalation == "high"
    
    def test_assess_escalation_potential_severe_scenario(self):
        """Test escalation potential for severe scenario."""
        coordinator = EmergencyResponseCoordinator()
        
        severe_scenario = EmergencyScenario(
            scenario_id="severe_test",
            incident_type=EmergencyType.INFRASTRUCTURE_FAILURE,
            severity_level=SeverityLevel.SEVERE,
            location="Industrial District",
            affected_area_radius=8.0,
            estimated_population_affected=25000
        )
        
        escalation = coordinator._assess_escalation_potential(severe_scenario)
        assert escalation == "moderate"
    
    def test_identify_evacuation_zones_hurricane(self):
        """Test evacuation zone identification for hurricane."""
        coordinator = EmergencyResponseCoordinator()
        
        hurricane_scenario = EmergencyScenario(
            scenario_id="hurricane_zones",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.HIGH,
            location="Coastal City",
            affected_area_radius=12.0,
            estimated_population_affected=80000
        )
        
        zones = coordinator._identify_evacuation_zones(hurricane_scenario)
        
        assert "Zone A (Coastal)" in zones
        assert "Zone B (Low-lying areas)" in zones
        assert "Zone C (High-risk flooding)" in zones
    
    def test_identify_evacuation_zones_fire(self):
        """Test evacuation zone identification for fire."""
        coordinator = EmergencyResponseCoordinator()
        
        fire_scenario = EmergencyScenario(
            scenario_id="fire_zones",
            incident_type=EmergencyType.FIRE,
            severity_level=SeverityLevel.HIGH,
            location="Forest Area",
            affected_area_radius=8.0,
            estimated_population_affected=15000
        )
        
        zones = coordinator._identify_evacuation_zones(fire_scenario)
        
        assert "Immediate area" in zones
        assert "Adjacent neighborhoods" in zones
        assert "Smoke-affected areas" in zones
    
    def test_classify_area_type_manhattan(self):
        """Test area type classification for Manhattan."""
        coordinator = EmergencyResponseCoordinator()
        
        area_type = coordinator._classify_area_type("Manhattan, NYC")
        assert area_type == "urban_dense"
        
        area_type = coordinator._classify_area_type("Downtown Manhattan")
        assert area_type == "urban_dense"
    
    def test_classify_area_type_brooklyn(self):
        """Test area type classification for Brooklyn."""
        coordinator = EmergencyResponseCoordinator()
        
        area_type = coordinator._classify_area_type("Brooklyn, NYC")
        assert area_type == "urban_moderate"
        
        area_type = coordinator._classify_area_type("Queens, NYC")
        assert area_type == "urban_moderate"
    
    def test_identify_access_challenges_flood(self):
        """Test access challenge identification for flood."""
        coordinator = EmergencyResponseCoordinator()
        
        flood_scenario = EmergencyScenario(
            scenario_id="flood_access",
            incident_type=EmergencyType.FLOOD,
            severity_level=SeverityLevel.HIGH,
            location="River Valley",
            affected_area_radius=10.0,
            estimated_population_affected=30000
        )
        
        challenges = coordinator._identify_access_challenges(flood_scenario)
        
        assert "Flooded roads" in challenges
        assert "Bridge closures" in challenges
        assert "Underground access limited" in challenges
    
    def test_identify_access_challenges_winter_storm(self):
        """Test access challenge identification for winter storm."""
        coordinator = EmergencyResponseCoordinator()
        
        winter_scenario = EmergencyScenario(
            scenario_id="winter_access",
            incident_type=EmergencyType.WINTER_STORM,
            severity_level=SeverityLevel.MODERATE,
            location="Northern District",
            affected_area_radius=25.0,
            estimated_population_affected=100000
        )
        
        challenges = coordinator._identify_access_challenges(winter_scenario)
        
        assert "Snow-blocked roads" in challenges
        assert "Icy conditions" in challenges
        assert "Limited visibility" in challenges
    
    def test_estimate_resource_requirements_hurricane(self):
        """Test resource requirement estimation for hurricane."""
        coordinator = EmergencyResponseCoordinator()
        
        hurricane_scenario = EmergencyScenario(
            scenario_id="hurricane_resources",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.SEVERE,
            location="Coastal Area",
            affected_area_radius=15.0,
            estimated_population_affected=100000
        )
        
        resources = coordinator._estimate_resource_requirements(hurricane_scenario)
        
        assert resources["personnel"] == 200  # 100 * 2.0 multiplier
        assert resources["vehicles"] == 40    # personnel / 5
        assert resources["medical_units"] == 20  # population / 5000
        assert resources["shelters"] == 100   # population / 1000
        assert resources["communication_units"] == 10  # max(5, personnel / 20)
    
    def test_estimate_resource_requirements_small_incident(self):
        """Test resource requirement estimation for small incident."""
        coordinator = EmergencyResponseCoordinator()
        
        small_scenario = EmergencyScenario(
            scenario_id="small_incident",
            incident_type=EmergencyType.INFRASTRUCTURE_FAILURE,
            severity_level=SeverityLevel.LOW,
            location="Local Area",
            affected_area_radius=2.0,
            estimated_population_affected=500
        )
        
        resources = coordinator._estimate_resource_requirements(small_scenario)
        
        assert resources["personnel"] == 60   # max(50, 500/1000) * 1.2
        assert resources["vehicles"] == 12    # personnel / 5
        assert resources["medical_units"] == 0   # 500 / 5000 = 0
        assert resources["shelters"] == 0     # 500 / 1000 = 0  
        assert resources["communication_units"] == 5  # max(5, personnel / 20)
    
    def test_estimate_timeline_short_duration(self):
        """Test timeline estimation for short duration event."""
        coordinator = EmergencyResponseCoordinator()
        
        short_scenario = EmergencyScenario(
            scenario_id="short_event",
            incident_type=EmergencyType.FIRE,
            severity_level=SeverityLevel.MODERATE,
            location="Industrial Area",
            affected_area_radius=3.0,
            estimated_population_affected=2000,
            duration_hours=6
        )
        
        timeline = coordinator._estimate_timeline(short_scenario)
        
        assert timeline["immediate_response_hours"] == 0  # min(2, 6/12)
        assert timeline["short_term_response_hours"] == 3  # min(12, 6/2)
        assert timeline["total_response_hours"] == 6
        assert timeline["recovery_days"] > 0
    
    def test_estimate_recovery_time_hurricane(self):
        """Test recovery time estimation for hurricane."""
        coordinator = EmergencyResponseCoordinator()
        
        hurricane_scenario = EmergencyScenario(
            scenario_id="hurricane_recovery",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.CATASTROPHIC,
            location="Gulf Coast",
            affected_area_radius=30.0,
            estimated_population_affected=500000
        )
        
        recovery_days = coordinator._estimate_recovery_time(hurricane_scenario)
        
        # Base 30 days * (5/3) severity multiplier = 50 days
        assert recovery_days == 50
    
    def test_estimate_recovery_time_winter_storm(self):
        """Test recovery time estimation for winter storm."""
        coordinator = EmergencyResponseCoordinator()
        
        winter_scenario = EmergencyScenario(
            scenario_id="winter_recovery",
            incident_type=EmergencyType.WINTER_STORM,
            severity_level=SeverityLevel.MODERATE,
            location="Mountain Region",
            affected_area_radius=20.0,
            estimated_population_affected=25000
        )
        
        recovery_days = coordinator._estimate_recovery_time(winter_scenario)
        
        # Base 3 days * (2/3) severity multiplier = 2 days
        assert recovery_days == 2
    
    def test_determine_lead_agency_fire(self):
        """Test lead agency determination for fire."""
        coordinator = EmergencyResponseCoordinator()
        
        fire_scenario = EmergencyScenario(
            scenario_id="fire_lead",
            incident_type=EmergencyType.FIRE,
            severity_level=SeverityLevel.HIGH,
            location="Forest Area",
            affected_area_radius=10.0,
            estimated_population_affected=5000
        )
        
        lead_agency = coordinator._determine_lead_agency(fire_scenario)
        assert lead_agency == "Fire Department"
    
    def test_determine_lead_agency_public_health(self):
        """Test lead agency determination for public health."""
        coordinator = EmergencyResponseCoordinator()
        
        health_scenario = EmergencyScenario(
            scenario_id="health_lead",
            incident_type=EmergencyType.PUBLIC_HEALTH,
            severity_level=SeverityLevel.SEVERE,
            location="Metro Area",
            affected_area_radius=50.0,
            estimated_population_affected=1000000
        )
        
        lead_agency = coordinator._determine_lead_agency(health_scenario)
        assert lead_agency == "Department of Health"
    
    def test_determine_lead_agency_default(self):
        """Test lead agency determination for unknown type."""
        coordinator = EmergencyResponseCoordinator()
        
        unknown_scenario = EmergencyScenario(
            scenario_id="unknown_lead",
            incident_type=EmergencyType.EARTHQUAKE,  # Not in the specific mapping
            severity_level=SeverityLevel.HIGH,
            location="Urban Area",
            affected_area_radius=15.0,
            estimated_population_affected=100000
        )
        
        lead_agency = coordinator._determine_lead_agency(unknown_scenario)
        assert lead_agency == "Office of Emergency Management"
    
    def test_generate_immediate_actions_hurricane(self):
        """Test immediate actions generation for hurricane."""
        coordinator = EmergencyResponseCoordinator()
        
        hurricane_scenario = EmergencyScenario(
            scenario_id="hurricane_actions",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.SEVERE,
            location="Coastal City",
            affected_area_radius=20.0,
            estimated_population_affected=200000
        )
        
        mock_assessment = {"weather_impact": {"impact_level": "high"}}
        
        actions = coordinator._generate_immediate_actions(hurricane_scenario, mock_assessment)
        
        base_actions = [
            "Activate Emergency Operations Center",
            "Deploy first responders to affected area",
            "Establish incident command post",
            "Assess immediate life safety threats"
        ]
        
        hurricane_actions = [
            "Issue evacuation orders for flood-prone areas",
            "Open emergency shelters",
            "Pre-position utility crews"
        ]
        
        for action in base_actions:
            assert action in actions
        
        for action in hurricane_actions:
            assert action in actions
    
    def test_generate_immediate_actions_fire(self):
        """Test immediate actions generation for fire."""
        coordinator = EmergencyResponseCoordinator()
        
        fire_scenario = EmergencyScenario(
            scenario_id="fire_actions",
            incident_type=EmergencyType.FIRE,
            severity_level=SeverityLevel.HIGH,
            location="Wildland Interface",
            affected_area_radius=8.0,
            estimated_population_affected=10000
        )
        
        mock_assessment = {"weather_impact": {"impact_level": "moderate"}}
        
        actions = coordinator._generate_immediate_actions(fire_scenario, mock_assessment)
        
        fire_specific_actions = [
            "Establish fire perimeter",
            "Begin evacuation of immediate area",
            "Deploy fire suppression resources"
        ]
        
        for action in fire_specific_actions:
            assert action in actions
    
    def test_generate_immediate_actions_public_health(self):
        """Test immediate actions generation for public health emergency."""
        coordinator = EmergencyResponseCoordinator()
        
        health_scenario = EmergencyScenario(
            scenario_id="health_actions",
            incident_type=EmergencyType.PUBLIC_HEALTH,
            severity_level=SeverityLevel.SEVERE,
            location="Metro Area",
            affected_area_radius=30.0,
            estimated_population_affected=500000
        )
        
        mock_assessment = {"weather_impact": None}
        
        actions = coordinator._generate_immediate_actions(health_scenario, mock_assessment)
        
        health_specific_actions = [
            "Activate disease surveillance",
            "Implement contact tracing",
            "Coordinate with healthcare facilities"
        ]
        
        for action in health_specific_actions:
            assert action in actions
    
    def test_identify_supporting_agencies_public_health(self):
        """Test supporting agencies identification for public health."""
        coordinator = EmergencyResponseCoordinator()
        
        health_scenario = EmergencyScenario(
            scenario_id="health_agencies",
            incident_type=EmergencyType.PUBLIC_HEALTH,
            severity_level=SeverityLevel.HIGH,
            location="State Wide",
            affected_area_radius=100.0,
            estimated_population_affected=2000000
        )
        
        agencies = coordinator._identify_supporting_agencies(health_scenario)
        
        base_agencies = ["Police Department", "Fire Department", "Emergency Medical Services"]
        health_agencies = ["Department of Health", "Hospitals", "CDC"]
        
        for agency in base_agencies:
            assert agency in agencies
        
        for agency in health_agencies:
            assert agency in agencies
    
    def test_identify_supporting_agencies_hurricane(self):
        """Test supporting agencies identification for hurricane."""
        coordinator = EmergencyResponseCoordinator()
        
        hurricane_scenario = EmergencyScenario(
            scenario_id="hurricane_agencies",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.CATASTROPHIC,
            location="Gulf Coast",
            affected_area_radius=50.0,
            estimated_population_affected=1000000
        )
        
        agencies = coordinator._identify_supporting_agencies(hurricane_scenario)
        
        hurricane_agencies = ["National Weather Service", "Coast Guard", "Red Cross"]
        
        for agency in hurricane_agencies:
            assert agency in agencies
    
    def test_create_communication_plan(self):
        """Test communication plan creation."""
        coordinator = EmergencyResponseCoordinator()
        
        scenario = EmergencyScenario(
            scenario_id="comm_test",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.HIGH,
            location="Test Location",
            affected_area_radius=10.0,
            estimated_population_affected=50000
        )
        
        comm_plan = coordinator._create_communication_plan(scenario)
        
        assert "public_information" in comm_plan
        assert "inter_agency" in comm_plan
        assert "emergency_alerts" in comm_plan
        assert "media_relations" in comm_plan
        
        assert "press briefings" in comm_plan["public_information"]
        assert "radio network" in comm_plan["inter_agency"]
        assert "Emergency Alert System" in comm_plan["emergency_alerts"]
        assert "media liaison" in comm_plan["media_relations"]