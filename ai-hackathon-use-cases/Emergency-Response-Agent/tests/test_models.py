"""
Unit tests for Emergency Response Models
Tests all data models and their validation logic.
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.models.emergency_models import (
    EmergencyScenario, EmergencyResponsePlan, EmergencyType, SeverityLevel,
    WeatherCondition, TrafficCondition, ResourceAllocation, AgentResponse,
    HistoricalIncident, MultiAgentTask, CoordinationStatus
)


class TestEmergencyScenario:
    """Test EmergencyScenario model."""
    
    def test_valid_scenario_creation(self):
        """Test creating a valid emergency scenario."""
        scenario = EmergencyScenario(
            scenario_id="test_001",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.HIGH,
            location="Test City",
            affected_area_radius=5.0,
            estimated_population_affected=10000
        )
        
        assert scenario.scenario_id == "test_001"
        assert scenario.incident_type == EmergencyType.HURRICANE
        assert scenario.severity_level == SeverityLevel.HIGH
        assert scenario.location == "Test City"
        assert scenario.affected_area_radius == 5.0
        assert scenario.estimated_population_affected == 10000
        assert isinstance(scenario.created_at, datetime)
    
    def test_invalid_radius_validation(self):
        """Test validation of negative radius."""
        with pytest.raises(ValidationError) as exc_info:
            EmergencyScenario(
                scenario_id="test_002",
                incident_type=EmergencyType.FIRE,
                severity_level=SeverityLevel.LOW,
                location="Test Location",
                affected_area_radius=-1.0,  # Invalid negative radius
                estimated_population_affected=1000
            )
        
        assert "Affected area radius must be positive" in str(exc_info.value)
    
    def test_invalid_population_validation(self):
        """Test validation of negative population."""
        with pytest.raises(ValidationError) as exc_info:
            EmergencyScenario(
                scenario_id="test_003",
                incident_type=EmergencyType.FLOOD,
                severity_level=SeverityLevel.MODERATE,
                location="Test Location",
                affected_area_radius=2.0,
                estimated_population_affected=-500  # Invalid negative population
            )
        
        assert "Population affected cannot be negative" in str(exc_info.value)
    
    def test_scenario_with_special_conditions(self):
        """Test scenario with special conditions."""
        special_conditions = {"wind_speed": "85 mph", "storm_surge": "10 feet"}
        
        scenario = EmergencyScenario(
            scenario_id="test_004",
            incident_type=EmergencyType.HURRICANE,
            severity_level=SeverityLevel.SEVERE,
            location="Coastal City",
            affected_area_radius=15.0,
            estimated_population_affected=100000,
            special_conditions=special_conditions
        )
        
        assert scenario.special_conditions == special_conditions
        assert scenario.special_conditions["wind_speed"] == "85 mph"


class TestEmergencyResponsePlan:
    """Test EmergencyResponsePlan model."""
    
    def test_basic_plan_creation(self, sample_emergency_scenario):
        """Test creating a basic response plan."""
        plan = EmergencyResponsePlan(
            plan_id="plan_001",
            scenario=sample_emergency_scenario,
            lead_agency="Emergency Management",
            activation_time=datetime.now(),
            estimated_duration=timedelta(hours=24)
        )
        
        assert plan.plan_id == "plan_001"
        assert plan.scenario == sample_emergency_scenario
        assert plan.lead_agency == "Emergency Management"
        assert isinstance(plan.activation_time, datetime)
        assert plan.estimated_duration == timedelta(hours=24)
        assert isinstance(plan.created_at, datetime)
    
    def test_plan_with_complete_data(self, sample_emergency_scenario):
        """Test creating a complete response plan."""
        resource_allocation = ResourceAllocation(
            personnel_deployment={"Firefighters": 50, "Police": 30},
            equipment_requirements={"Fire Trucks": 10, "Ambulances": 5}
        )
        
        plan = EmergencyResponsePlan(
            plan_id="plan_002",
            scenario=sample_emergency_scenario,
            immediate_actions=["Deploy first responders", "Establish command post"],
            short_term_actions=["Set up shelters", "Coordinate resources"],
            long_term_recovery=["Damage assessment", "Reconstruction planning"],
            resource_allocation=resource_allocation,
            lead_agency="Fire Department",
            supporting_agencies=["Police", "EMS", "Red Cross"],
            communication_plan={"radio": "Channel 5", "public": "Press briefings"},
            activation_time=datetime.now(),
            estimated_duration=timedelta(hours=48),
            success_criteria=["All evacuations completed", "No casualties"],
            risk_factors=["High winds", "Flooding"],
            mitigation_strategies=["Pre-positioned resources", "Early warning"]
        )
        
        assert len(plan.immediate_actions) == 2
        assert len(plan.short_term_actions) == 2
        assert len(plan.long_term_recovery) == 2
        assert plan.resource_allocation.personnel_deployment["Firefighters"] == 50
        assert len(plan.supporting_agencies) == 3
        assert plan.communication_plan["radio"] == "Channel 5"
        assert len(plan.success_criteria) == 2
        assert len(plan.risk_factors) == 2


class TestWeatherCondition:
    """Test WeatherCondition model."""
    
    def test_weather_condition_creation(self):
        """Test creating weather condition."""
        timestamp = datetime.now()
        condition = WeatherCondition(
            temperature=72.5,
            humidity=65,
            wind_speed=12.0,
            wind_direction=180,
            pressure=1013.25,
            visibility=8.5,
            conditions="Partly Cloudy",
            timestamp=timestamp
        )
        
        assert condition.temperature == 72.5
        assert condition.humidity == 65
        assert condition.wind_speed == 12.0
        assert condition.wind_direction == 180
        assert condition.pressure == 1013.25
        assert condition.visibility == 8.5
        assert condition.conditions == "Partly Cloudy"
        assert condition.timestamp == timestamp


class TestTrafficCondition:
    """Test TrafficCondition model."""
    
    def test_traffic_condition_creation(self):
        """Test creating traffic condition."""
        timestamp = datetime.now()
        incidents = ["Accident at Mile 15", "Construction Zone"]
        
        condition = TrafficCondition(
            route_name="Highway 101",
            current_speed=35.0,
            free_flow_speed=65.0,
            congestion_level="heavy",
            travel_time_minutes=45,
            incidents=incidents,
            last_updated=timestamp
        )
        
        assert condition.route_name == "Highway 101"
        assert condition.current_speed == 35.0
        assert condition.free_flow_speed == 65.0
        assert condition.congestion_level == "heavy"
        assert condition.travel_time_minutes == 45
        assert len(condition.incidents) == 2
        assert condition.last_updated == timestamp


class TestResourceAllocation:
    """Test ResourceAllocation model."""
    
    def test_empty_resource_allocation(self):
        """Test creating empty resource allocation."""
        allocation = ResourceAllocation()
        
        assert len(allocation.personnel_deployment) == 0
        assert len(allocation.equipment_requirements) == 0
        assert len(allocation.facility_assignments) == 0
        assert len(allocation.budget_allocation) == 0
    
    def test_populated_resource_allocation(self):
        """Test creating populated resource allocation."""
        allocation = ResourceAllocation(
            personnel_deployment={"Firefighters": 100, "Police": 50, "EMS": 25},
            equipment_requirements={"Fire Trucks": 20, "Ambulances": 10, "Police Cars": 30},
            facility_assignments={"Command Post": "City Hall", "Shelter": "High School"},
            budget_allocation={"Personnel": 500000.0, "Equipment": 200000.0}
        )
        
        assert allocation.personnel_deployment["Firefighters"] == 100
        assert allocation.equipment_requirements["Fire Trucks"] == 20
        assert allocation.facility_assignments["Command Post"] == "City Hall"
        assert allocation.budget_allocation["Personnel"] == 500000.0


class TestAgentResponse:
    """Test AgentResponse model."""
    
    def test_agent_response_creation(self):
        """Test creating agent response."""
        timestamp = datetime.now()
        recommendations = ["Deploy additional units", "Monitor weather conditions"]
        analysis = {"risk_level": "high", "resource_needs": 150}
        
        response = AgentResponse(
            agent_name="Weather Analyst",
            recommendations=recommendations,
            data_analysis=analysis,
            confidence_score=0.85,
            processing_time_seconds=2.5,
            timestamp=timestamp
        )
        
        assert response.agent_name == "Weather Analyst"
        assert len(response.recommendations) == 2
        assert response.data_analysis["risk_level"] == "high"
        assert response.confidence_score == 0.85
        assert response.processing_time_seconds == 2.5
        assert response.timestamp == timestamp


class TestHistoricalIncident:
    """Test HistoricalIncident model."""
    
    def test_historical_incident_creation(self):
        """Test creating historical incident."""
        date_occurred = datetime(2020, 3, 15, 10, 30)
        response_actions = ["Lockdown orders", "Healthcare surge", "Contact tracing"]
        resources = {"Healthcare Workers": 5000, "Testing Sites": 100}
        lessons = ["Importance of early action", "Need for PPE stockpiles"]
        agencies = ["DOH", "Emergency Management", "Police"]
        
        incident = HistoricalIncident(
            incident_id="covid_2020",
            incident_type=EmergencyType.PUBLIC_HEALTH,
            title="COVID-19 Pandemic Response",
            description="Public health emergency response to coronavirus pandemic",
            date_occurred=date_occurred,
            location="Citywide",
            severity_level=SeverityLevel.CATASTROPHIC,
            response_actions=response_actions,
            resources_deployed=resources,
            lessons_learned=lessons,
            response_time_minutes=10080,  # 7 days
            effectiveness_score=7.2,
            agencies_involved=agencies,
            estimated_cost=1000000000.0,
            affected_population=1000000
        )
        
        assert incident.incident_id == "covid_2020"
        assert incident.incident_type == EmergencyType.PUBLIC_HEALTH
        assert incident.date_occurred == date_occurred
        assert incident.severity_level == SeverityLevel.CATASTROPHIC
        assert len(incident.response_actions) == 3
        assert incident.resources_deployed["Healthcare Workers"] == 5000
        assert len(incident.lessons_learned) == 2
        assert incident.effectiveness_score == 7.2
        assert len(incident.agencies_involved) == 3


class TestMultiAgentTask:
    """Test MultiAgentTask model."""
    
    def test_pending_task_creation(self):
        """Test creating a pending multi-agent task."""
        input_data = {"location": "Downtown", "severity": "high"}
        timestamp = datetime.now()
        
        task = MultiAgentTask(
            task_id="task_001",
            task_type="weather_analysis",
            assigned_agent="Weather Analyst",
            input_data=input_data,
            created_at=timestamp
        )
        
        assert task.task_id == "task_001"
        assert task.task_type == "weather_analysis"
        assert task.assigned_agent == "Weather Analyst"
        assert task.input_data == input_data
        assert task.status == CoordinationStatus.PENDING
        assert task.result is None
        assert task.created_at == timestamp
        assert task.completed_at is None
        assert task.error_message is None
    
    def test_completed_task_with_result(self):
        """Test creating a completed task with result."""
        input_data = {"scenario": "hurricane"}
        result = AgentResponse(
            agent_name="Weather Analyst",
            recommendations=["Monitor wind speeds"],
            data_analysis={"wind_speed": 75},
            confidence_score=0.9,
            processing_time_seconds=1.2
        )
        completed_time = datetime.now()
        
        task = MultiAgentTask(
            task_id="task_002",
            task_type="weather_analysis",
            assigned_agent="Weather Analyst",
            input_data=input_data,
            status=CoordinationStatus.COMPLETED,
            result=result,
            completed_at=completed_time
        )
        
        assert task.status == CoordinationStatus.COMPLETED
        assert task.result == result
        assert task.completed_at == completed_time
        assert task.error_message is None
    
    def test_failed_task_with_error(self):
        """Test creating a failed task with error message."""
        task = MultiAgentTask(
            task_id="task_003",
            task_type="traffic_analysis",
            assigned_agent="Traffic Manager",
            input_data={"route": "Main Street"},
            status=CoordinationStatus.FAILED,
            error_message="API connection timeout"
        )
        
        assert task.status == CoordinationStatus.FAILED
        assert task.result is None
        assert task.error_message == "API connection timeout"


class TestEnumValues:
    """Test enum values and functionality."""
    
    def test_emergency_type_values(self):
        """Test EmergencyType enum values."""
        assert EmergencyType.HURRICANE.value == "hurricane"
        assert EmergencyType.FIRE.value == "fire"
        assert EmergencyType.PUBLIC_HEALTH.value == "public_health"
        assert EmergencyType.INFRASTRUCTURE_FAILURE.value == "infrastructure_failure"
    
    def test_severity_level_values(self):
        """Test SeverityLevel enum values."""
        assert SeverityLevel.LOW.value == 1
        assert SeverityLevel.MODERATE.value == 2
        assert SeverityLevel.HIGH.value == 3
        assert SeverityLevel.SEVERE.value == 4
        assert SeverityLevel.CATASTROPHIC.value == 5
    
    def test_coordination_status_values(self):
        """Test CoordinationStatus enum values."""
        assert CoordinationStatus.PENDING.value == "pending"
        assert CoordinationStatus.IN_PROGRESS.value == "in_progress"
        assert CoordinationStatus.COMPLETED.value == "completed"
        assert CoordinationStatus.FAILED.value == "failed"