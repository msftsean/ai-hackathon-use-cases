"""
Emergency Response Models
Defines the core data structures for emergency scenarios and response plans.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, field_validator


class EmergencyType(Enum):
    """Types of emergency scenarios."""
    HURRICANE = "hurricane"
    WINTER_STORM = "winter_storm"
    FLOOD = "flood"
    FIRE = "fire"
    PUBLIC_HEALTH = "public_health"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    SECURITY_INCIDENT = "security_incident"
    EARTHQUAKE = "earthquake"


class SeverityLevel(Enum):
    """Emergency severity levels."""
    LOW = 1
    MODERATE = 2
    HIGH = 3
    SEVERE = 4
    CATASTROPHIC = 5


class ResponsePhase(Enum):
    """Emergency response phases."""
    PREPARATION = "preparation"
    IMMEDIATE_RESPONSE = "immediate_response"
    SHORT_TERM = "short_term"
    LONG_TERM_RECOVERY = "long_term_recovery"


@dataclass
class WeatherCondition:
    """Weather condition data."""
    temperature: float
    humidity: int
    wind_speed: float
    wind_direction: int
    pressure: float
    visibility: float
    conditions: str
    timestamp: datetime


@dataclass
class TrafficCondition:
    """Traffic condition data."""
    route_name: str
    current_speed: float
    free_flow_speed: float
    congestion_level: str
    travel_time_minutes: int
    incidents: List[str]
    last_updated: datetime


@dataclass
class ResourceAllocation:
    """Resource allocation for emergency response."""
    personnel_deployment: Dict[str, int] = field(default_factory=dict)
    equipment_requirements: Dict[str, int] = field(default_factory=dict)
    facility_assignments: Dict[str, str] = field(default_factory=dict)
    budget_allocation: Dict[str, float] = field(default_factory=dict)


class EmergencyScenario(BaseModel):
    """Emergency scenario definition."""
    scenario_id: str
    incident_type: EmergencyType
    severity_level: SeverityLevel
    location: str
    affected_area_radius: float
    estimated_population_affected: int
    duration_hours: Optional[int] = None
    special_conditions: Dict[str, str] = {}
    weather_impact: Optional[WeatherCondition] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @field_validator('affected_area_radius')
    @classmethod
    def validate_radius(cls, v):
        if v <= 0:
            raise ValueError('Affected area radius must be positive')
        return v
    
    @field_validator('estimated_population_affected')
    @classmethod
    def validate_population(cls, v):
        if v < 0:
            raise ValueError('Population affected cannot be negative')
        return v


class EmergencyResponsePlan(BaseModel):
    """Complete emergency response plan."""
    plan_id: str
    scenario: EmergencyScenario
    
    # Response actions by phase
    immediate_actions: List[str] = []
    short_term_actions: List[str] = []
    long_term_recovery: List[str] = []
    
    # Resource allocation
    resource_allocation: ResourceAllocation = field(default_factory=ResourceAllocation)
    
    # Coordination
    lead_agency: str
    supporting_agencies: List[str] = []
    communication_plan: Dict[str, str] = {}
    
    # Timeline
    activation_time: datetime
    estimated_duration: timedelta
    key_milestones: List[Dict[str, datetime]] = []
    
    # Success metrics
    success_criteria: List[str] = []
    performance_indicators: Dict[str, float] = {}
    
    # Risk assessment
    risk_factors: List[str] = []
    mitigation_strategies: List[str] = []
    
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class AgentResponse:
    """Response from a specialized agent."""
    agent_name: str
    recommendations: List[str]
    data_analysis: Dict[str, any]
    confidence_score: float
    processing_time_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HistoricalIncident:
    """Historical emergency incident data."""
    incident_id: str
    incident_type: EmergencyType
    title: str
    description: str
    date_occurred: datetime
    location: str
    severity_level: SeverityLevel
    response_actions: List[str]
    resources_deployed: Dict[str, int]
    lessons_learned: List[str]
    response_time_minutes: int
    effectiveness_score: float
    agencies_involved: List[str]
    estimated_cost: float
    weather_conditions: Optional[str] = None
    affected_population: int = 0


class CoordinationStatus(Enum):
    """Multi-agent coordination status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MultiAgentTask:
    """Task for multi-agent coordination."""
    task_id: str
    task_type: str
    assigned_agent: str
    input_data: Dict[str, any]
    status: CoordinationStatus = CoordinationStatus.PENDING
    result: Optional[AgentResponse] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None