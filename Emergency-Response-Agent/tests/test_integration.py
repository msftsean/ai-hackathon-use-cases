"""
Integration tests for Emergency Response Agent
Tests the complete system integration and end-to-end functionality.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator
from src.models.emergency_models import (
    EmergencyScenario, EmergencyResponsePlan, EmergencyType, SeverityLevel
)


class TestEmergencyResponseIntegration:
    """Integration tests for complete emergency response system."""
    
    @pytest.mark.asyncio
    async def test_complete_hurricane_response_workflow(self):
        """Test complete hurricane response planning workflow."""
        coordinator = EmergencyResponseCoordinator()
        
        # Create a realistic hurricane scenario
        hurricane_scenario = EmergencyScenario(
            scenario_id="hurricane_integration_test_2025",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.SEVERE,
            location="Miami-Dade County, FL",
            affected_area_radius=25.0,
            estimated_population_affected=350000,
            duration_hours=72,
            special_conditions={
                "storm_surge": "10-15 feet predicted",
                "wind_speed": "90-110 mph sustained",
                "landfall_time": "36 hours"
            }
        )
        
        # Execute complete response coordination
        response_plan = await coordinator.coordinate_response(hurricane_scenario)
        
        # Verify plan structure
        assert isinstance(response_plan, EmergencyResponsePlan)
        assert response_plan.scenario == hurricane_scenario
        assert response_plan.plan_id.startswith("plan_hurricane_integration_test_2025")
        
        # Verify leadership and coordination
        assert response_plan.lead_agency == "Office of Emergency Management"
        assert "Coast Guard" in response_plan.supporting_agencies
        assert "National Weather Service" in response_plan.supporting_agencies
        assert "Red Cross" in response_plan.supporting_agencies
        
        # Verify response actions
        assert len(response_plan.immediate_actions) >= 7  # Base + hurricane specific
        assert "Activate Emergency Operations Center" in response_plan.immediate_actions
        assert "Issue evacuation orders for flood-prone areas" in response_plan.immediate_actions
        assert "Open emergency shelters" in response_plan.immediate_actions
        
        # Verify resource allocation
        assert response_plan.resource_allocation.personnel_deployment["First Responders"] > 0
        assert response_plan.resource_allocation.equipment_requirements["Emergency Vehicles"] > 0
        assert "Emergency Shelters" in response_plan.resource_allocation.facility_assignments
        
        # Verify timeline
        assert len(response_plan.key_milestones) == 5
        assert response_plan.estimated_duration == timedelta(hours=72)
        
        # Verify communication plan
        assert "public_information" in response_plan.communication_plan
        assert "emergency_alerts" in response_plan.communication_plan
    
    @pytest.mark.asyncio
    async def test_complete_public_health_response_workflow(self):
        """Test complete public health emergency response workflow."""
        coordinator = EmergencyResponseCoordinator()
        
        # Create a public health emergency scenario
        health_scenario = EmergencyScenario(
            scenario_id="pandemic_integration_test_2025",
            incident_type=EmergencyType.PUBLIC_HEALTH,
            severity_level=SeverityLevel.CATASTROPHIC,
            location="New York State",
            affected_area_radius=200.0,
            estimated_population_affected=5000000,
            duration_hours=2160,  # 90 days
            special_conditions={
                "pathogen": "Novel respiratory virus",
                "transmission_rate": "R0 = 3.5",
                "case_fatality_rate": "2.1%",
                "hospital_capacity": "Exceeded by 150%"
            }
        )
        
        # Execute complete response coordination
        response_plan = await coordinator.coordinate_response(health_scenario)
        
        # Verify plan structure
        assert isinstance(response_plan, EmergencyResponsePlan)
        assert response_plan.lead_agency == "Department of Health"
        
        # Verify public health specific agencies
        assert "Department of Health" in response_plan.supporting_agencies
        assert "Hospitals" in response_plan.supporting_agencies
        assert "CDC" in response_plan.supporting_agencies
        
        # Verify public health specific actions
        assert "Activate disease surveillance" in response_plan.immediate_actions
        assert "Implement contact tracing" in response_plan.immediate_actions
        assert "Coordinate with healthcare facilities" in response_plan.immediate_actions
        
        # Verify massive resource allocation for catastrophic public health event
        total_personnel = sum(response_plan.resource_allocation.personnel_deployment.values())
        assert total_personnel > 1000  # Large scale response
        
        # Verify extended timeline for public health emergency
        assert response_plan.estimated_duration == timedelta(hours=2160)  # 90 days
    
    @pytest.mark.asyncio
    async def test_complete_fire_response_workflow(self):
        """Test complete fire emergency response workflow."""
        coordinator = EmergencyResponseCoordinator()
        
        # Create a wildfire scenario
        fire_scenario = EmergencyScenario(
            scenario_id="wildfire_integration_test_2025",
            incident_type=EmergencyType.FIRE,
            severity_level=SeverityLevel.HIGH,
            location="Los Angeles County, CA",
            affected_area_radius=12.0,
            estimated_population_affected=75000,
            duration_hours=96,
            special_conditions={
                "fire_type": "Wildland-Urban Interface",
                "weather_conditions": "Red Flag Warning",
                "wind_speed": "45 mph gusts",
                "humidity": "8%"
            }
        )
        
        # Execute complete response coordination
        response_plan = await coordinator.coordinate_response(fire_scenario)
        
        # Verify fire-specific leadership
        assert response_plan.lead_agency == "Fire Department"
        
        # Verify fire-specific actions
        assert "Establish fire perimeter" in response_plan.immediate_actions
        assert "Begin evacuation of immediate area" in response_plan.immediate_actions
        assert "Deploy fire suppression resources" in response_plan.immediate_actions
        
        # Verify evacuation zones appropriate for fire
        # This would be tested through the analysis that feeds into the plan
        # The actual zones are determined in _identify_evacuation_zones
    
    @pytest.mark.asyncio
    async def test_small_scale_incident_response(self):
        """Test response planning for small-scale incident."""
        coordinator = EmergencyResponseCoordinator()
        
        # Create a small infrastructure failure
        small_incident = EmergencyScenario(
            scenario_id="small_incident_test_2025",
            incident_type=EmergencyType.INFRASTRUCTURE_FAILURE,
            severity_level=SeverityLevel.LOW,
            location="Downtown District",
            affected_area_radius=1.5,
            estimated_population_affected=2500,
            duration_hours=8,
            special_conditions={
                "failure_type": "Power grid transformer failure",
                "services_affected": "Electricity to 3 city blocks"
            }
        )
        
        # Execute response coordination
        response_plan = await coordinator.coordinate_response(small_incident)
        
        # Verify appropriate scaling for small incident
        assert response_plan.lead_agency == "Department of Transportation"
        
        # Verify resource allocation is appropriately scaled
        total_personnel = sum(response_plan.resource_allocation.personnel_deployment.values())
        assert total_personnel < 200  # Should be modest for small incident
        
        # Verify shorter timeline
        assert response_plan.estimated_duration == timedelta(hours=8)
    
    @pytest.mark.asyncio
    async def test_multi_hazard_scenario_analysis(self):
        """Test scenario analysis for complex multi-hazard event."""
        coordinator = EmergencyResponseCoordinator()
        
        # Create a complex scenario (hurricane with secondary flooding)
        complex_scenario = EmergencyScenario(
            scenario_id="complex_multi_hazard_2025",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.CATASTROPHIC,
            location="Houston, TX",
            affected_area_radius=40.0,
            estimated_population_affected=800000,
            duration_hours=120,  # 5 days
            special_conditions={
                "primary_hazard": "Category 4 Hurricane",
                "secondary_hazards": "Storm surge, inland flooding, power outages",
                "infrastructure_risk": "Petrochemical facilities",
                "evacuation_routes": "Limited due to flooding"
            }
        )
        
        # Execute scenario analysis
        analysis = await coordinator._perform_scenario_analysis(complex_scenario)
        
        # Verify comprehensive analysis
        assert analysis["scenario_type"] == "hurricane"
        assert analysis["severity_assessment"]["level"] == 5  # CATASTROPHIC
        assert analysis["severity_assessment"]["escalation_potential"] == "moderate"
        
        # Verify population impact analysis
        assert analysis["population_impact"]["directly_affected"] == 800000
        assert analysis["population_impact"]["potentially_affected"] == 1200000  # 1.5x
        assert analysis["population_impact"]["vulnerable_populations"] == 120000  # 15%
        
        # Verify geographic analysis
        assert "natural_barriers" in analysis["geographic_analysis"]
        assert "access_challenges" in analysis["geographic_analysis"]
        
        # Verify resource requirements scaling
        assert analysis["resource_requirements"]["personnel"] >= 1600  # 800 * 2.0 hurricane multiplier
        assert analysis["resource_requirements"]["medical_units"] >= 160  # 800000 / 5000
        assert analysis["resource_requirements"]["shelters"] >= 800  # 800000 / 1000
    
    @pytest.mark.asyncio
    async def test_resource_allocation_integration(self):
        """Test resource allocation for different scenario types."""
        coordinator = EmergencyResponseCoordinator()
        
        scenarios = [
            (EmergencyType.HURRICANE, SeverityLevel.SEVERE, 100000, 2.0),
            (EmergencyType.FIRE, SeverityLevel.HIGH, 25000, 1.8),
            (EmergencyType.PUBLIC_HEALTH, SeverityLevel.CATASTROPHIC, 500000, 1.5),
            (EmergencyType.INFRASTRUCTURE_FAILURE, SeverityLevel.MODERATE, 10000, 1.2)
        ]
        
        for incident_type, severity, population, expected_multiplier in scenarios:
            scenario = EmergencyScenario(
                scenario_id=f"resource_test_{incident_type.value}",
                incident_type=incident_type,
                severity_level=severity,
                location="Test City",
                affected_area_radius=10.0,
                estimated_population_affected=population
            )
            
            response_plan = await coordinator.coordinate_response(scenario)
            
            # Verify resource allocation exists and is reasonable
            assert response_plan.resource_allocation is not None
            
            total_personnel = sum(response_plan.resource_allocation.personnel_deployment.values())
            base_personnel = max(50, population // 1000)
            expected_personnel = int(base_personnel * expected_multiplier)
            
            # Allow for some variance in calculations
            assert abs(total_personnel - expected_personnel) <= 10
    
    @pytest.mark.asyncio
    async def test_timeline_milestone_integration(self):
        """Test timeline and milestone generation integration."""
        coordinator = EmergencyResponseCoordinator()
        
        scenario = EmergencyScenario(
            scenario_id="timeline_test_2025",
            incident_type=EmergencyType.WINTER_STORM,
            severity_level=SeverityLevel.HIGH,
            location="Boston, MA",
            affected_area_radius=15.0,
            estimated_population_affected=120000,
            duration_hours=36
        )
        
        response_plan = await coordinator.coordinate_response(scenario)
        
        # Verify timeline structure
        assert len(response_plan.key_milestones) == 5
        
        # Verify milestone progression
        milestones = response_plan.key_milestones
        for i in range(1, len(milestones)):
            assert milestones[i]["time"] > milestones[i-1]["time"]
        
        # Verify specific milestones exist
        milestone_names = [m["name"] for m in milestones]
        assert "Initial Response Deployed" in milestone_names
        assert "Command Post Established" in milestone_names
        assert "Full Resource Deployment" in milestone_names
        assert "Situation Assessment Complete" in milestone_names
        assert "Response Transition to Recovery" in milestone_names
        
        # Verify timeline spans the scenario duration
        last_milestone = milestones[-1]["time"]
        first_milestone = milestones[0]["time"]
        total_duration = last_milestone - first_milestone
        assert total_duration == response_plan.estimated_duration
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling in integrated workflow."""
        coordinator = EmergencyResponseCoordinator()
        
        # Create scenario with edge case values
        edge_case_scenario = EmergencyScenario(
            scenario_id="edge_case_test",
            incident_type=EmergencyType.EARTHQUAKE,
            severity_level=SeverityLevel.CATASTROPHIC,
            location="",  # Empty location
            affected_area_radius=0.1,  # Very small radius
            estimated_population_affected=0  # No population affected
        )
        
        # Should handle gracefully without crashing
        response_plan = await coordinator.coordinate_response(edge_case_scenario)
        
        # Verify basic plan structure is still created
        assert isinstance(response_plan, EmergencyResponsePlan)
        assert response_plan.scenario == edge_case_scenario
        assert response_plan.lead_agency == "Office of Emergency Management"  # Default
        
        # Verify minimum resource allocation
        total_personnel = sum(response_plan.resource_allocation.personnel_deployment.values())
        assert total_personnel >= 50  # Minimum baseline
    
    @pytest.mark.asyncio
    async def test_concurrent_scenario_processing(self):
        """Test processing multiple scenarios concurrently."""
        coordinator = EmergencyResponseCoordinator()
        
        # Create multiple different scenarios
        scenarios = [
            EmergencyScenario(
                scenario_id="concurrent_fire",
                incident_type=EmergencyType.FIRE,
                severity_level=SeverityLevel.MODERATE,
                location="Forest Area A",
                affected_area_radius=5.0,
                estimated_population_affected=15000
            ),
            EmergencyScenario(
                scenario_id="concurrent_flood",
                incident_type=EmergencyType.FLOOD,
                severity_level=SeverityLevel.HIGH,
                location="River Valley B",
                affected_area_radius=8.0,
                estimated_population_affected=25000
            ),
            EmergencyScenario(
                scenario_id="concurrent_winter",
                incident_type=EmergencyType.WINTER_STORM,
                severity_level=SeverityLevel.SEVERE,
                location="Mountain Region C",
                affected_area_radius=30.0,
                estimated_population_affected=80000
            )
        ]
        
        # Process all scenarios concurrently
        tasks = [coordinator.coordinate_response(scenario) for scenario in scenarios]
        response_plans = await asyncio.gather(*tasks)
        
        # Verify all plans were created successfully
        assert len(response_plans) == 3
        
        # Verify each plan is appropriate for its scenario type
        assert response_plans[0].lead_agency == "Fire Department"  # Fire scenario
        assert response_plans[1].lead_agency == "Office of Emergency Management"  # Flood scenario
        assert response_plans[2].lead_agency == "Office of Emergency Management"  # Winter storm
        
        # Verify scenarios are correctly associated
        assert response_plans[0].scenario.incident_type == EmergencyType.FIRE
        assert response_plans[1].scenario.incident_type == EmergencyType.FLOOD
        assert response_plans[2].scenario.incident_type == EmergencyType.WINTER_STORM