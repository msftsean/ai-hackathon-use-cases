"""Data models for Emergency Response Agent."""

from enum import Enum


class EmergencyType(str, Enum):
    """Types of emergencies the system can handle."""

    HURRICANE = "hurricane"
    FIRE = "fire"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    CHEMICAL_SPILL = "chemical_spill"
    PUBLIC_HEALTH = "public_health"
    TERRORISM = "terrorism"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"


class SeverityLevel(int, Enum):
    """Severity levels for emergencies (1-5 scale)."""

    MINIMAL = 1
    MINOR = 2
    MODERATE = 3
    SEVERE = 4
    CATASTROPHIC = 5


class ResponsePhase(str, Enum):
    """Phases of emergency response."""

    PREPARATION = "preparation"
    RESPONSE = "response"
    RECOVERY = "recovery"
    MITIGATION = "mitigation"


class CoordinationStatus(str, Enum):
    """Status of multi-agency coordination."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"


class ResourceType(str, Enum):
    """Types of resources for emergency response."""

    PERSONNEL = "personnel"
    VEHICLES = "vehicles"
    EQUIPMENT = "equipment"
    SUPPLIES = "supplies"
    SHELTER = "shelter"


class RiskLevel(str, Enum):
    """Risk level assessment."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


__all__ = [
    "EmergencyType",
    "SeverityLevel",
    "ResponsePhase",
    "CoordinationStatus",
    "ResourceType",
    "RiskLevel",
]
