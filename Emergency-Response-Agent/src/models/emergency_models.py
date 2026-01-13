"""Pydantic models for emergency response planning."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from . import EmergencyType, SeverityLevel, ResponsePhase, CoordinationStatus, RiskLevel


class EmergencyScenario(BaseModel):
    """Model for emergency scenario input."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    incident_type: EmergencyType
    severity_level: SeverityLevel
    location: str
    coordinates: Optional[tuple[float, float]] = None
    affected_area_radius: float = Field(gt=0, description="Radius in miles")
    estimated_population_affected: int = Field(ge=0)
    duration_hours: int = Field(gt=0)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("severity_level", mode="before")
    @classmethod
    def validate_severity(cls, v):
        """Convert integer severity to enum."""
        if isinstance(v, int):
            return SeverityLevel(v)
        return v

    @field_validator("incident_type", mode="before")
    @classmethod
    def validate_incident_type(cls, v):
        """Convert string to enum."""
        if isinstance(v, str):
            return EmergencyType(v.lower())
        return v


@dataclass
class ResourceAllocation:
    """Resource allocation for emergency response."""

    resource_type: str
    quantity: int
    unit: str
    assigned_agency: str
    status: str = "available"
    notes: str = ""


@dataclass
class TimelineMilestone:
    """Timeline milestone for response plan."""

    phase: str
    action: str
    target_time_hours: float
    responsible_agency: str
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"


class EmergencyResponsePlan(BaseModel):
    """Comprehensive emergency response plan."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    lead_agency: str
    supporting_agencies: list[str]
    response_phase: ResponsePhase
    coordination_status: CoordinationStatus

    # Resource allocations
    personnel_count: int = Field(ge=0)
    vehicle_count: int = Field(ge=0)
    equipment_list: list[str] = Field(default_factory=list)
    resources: list[dict] = Field(default_factory=list)

    # Timeline
    timeline_milestones: list[dict] = Field(default_factory=list)

    # Actions
    immediate_actions: list[str] = Field(default_factory=list)
    short_term_actions: list[str] = Field(default_factory=list)
    recovery_actions: list[str] = Field(default_factory=list)

    # Metadata
    estimated_cost: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[int] = None

    # Weather and environmental factors
    weather_risk_assessment: Optional[dict] = None
    evacuation_routes: list[dict] = Field(default_factory=list)


@dataclass
class WeatherCondition:
    """Weather condition data."""

    temperature_f: float
    feels_like_f: float
    humidity_percent: float
    wind_speed_mph: float
    wind_direction: str
    conditions: str
    visibility_miles: float
    pressure_hpa: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WeatherRiskAssessment:
    """Weather risk assessment for emergency planning."""

    wind_risk: str  # low, medium, high, critical
    temperature_risk: str
    precipitation_risk: str
    visibility_risk: str
    overall_risk: str
    recommendations: list[str] = field(default_factory=list)


@dataclass
class TrafficCondition:
    """Traffic condition for a route."""

    route_name: str
    current_speed_mph: float
    free_flow_speed_mph: float
    congestion_level: str  # light, moderate, heavy, severe
    incidents: list[str] = field(default_factory=list)


@dataclass
class EvacuationRoute:
    """Evacuation route information."""

    route_id: str
    name: str
    start_location: str
    end_location: str
    distance_miles: float
    estimated_time_minutes: int
    capacity_per_hour: int
    current_status: str
    bottlenecks: list[str] = field(default_factory=list)


@dataclass
class HistoricalIncident:
    """Historical incident record."""

    id: str
    incident_type: str
    severity: int
    date: datetime
    location: str
    affected_population: int
    response_time_hours: float
    lessons_learned: list[str]
    recommendations: list[str]
    outcome: str


@dataclass
class AgentResponse:
    """Response from an individual agent."""

    agent_name: str
    task_id: str
    result: dict
    confidence: float
    processing_time_ms: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MultiAgentTask:
    """Task for multi-agent coordination."""

    task_id: str
    task_type: str
    description: str
    assigned_agents: list[str]
    priority: int
    status: str = "pending"
    results: list[AgentResponse] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


__all__ = [
    "EmergencyScenario",
    "EmergencyResponsePlan",
    "ResourceAllocation",
    "TimelineMilestone",
    "WeatherCondition",
    "WeatherRiskAssessment",
    "TrafficCondition",
    "EvacuationRoute",
    "HistoricalIncident",
    "AgentResponse",
    "MultiAgentTask",
]
