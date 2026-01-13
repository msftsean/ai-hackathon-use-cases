# Data Model: Emergency Response Planning Agent

**Feature**: 003-emergency-response-agent
**Date**: 2026-01-12

## Entity Overview

```
┌─────────────────────┐     creates    ┌─────────────────────────┐
│  EmergencyScenario  │───────────────▶│  EmergencyResponsePlan  │
└─────────────────────┘                └─────────────────────────┘
         │                                        │
         │ includes                               │ contains
         ▼                                        ▼
┌─────────────────────┐                ┌─────────────────────────┐
│  WeatherCondition   │                │   ResourceAllocation    │
└─────────────────────┘                └─────────────────────────┘
                                                  │
┌─────────────────────┐                           │ references
│  EvacuationRoute    │◀──────────────────────────┘
└─────────────────────┘
                                       ┌─────────────────────────┐
┌─────────────────────┐     informs    │   HistoricalIncident    │
│  TrafficCondition   │───────────────▶└─────────────────────────┘
└─────────────────────┘
```

## Enumerations

### EmergencyType

| Value | Description |
|-------|-------------|
| `HURRICANE` | Tropical storm/hurricane events |
| `WINTER_STORM` | Blizzards, ice storms, extreme cold |
| `FLOOD` | River flooding, flash floods, coastal surge |
| `FIRE` | Wildfires, structural fires, industrial fires |
| `PUBLIC_HEALTH` | Disease outbreaks, pandemics, contamination |
| `INFRASTRUCTURE_FAILURE` | Power outages, water main breaks, bridge failures |
| `SECURITY_INCIDENT` | Terrorism, civil unrest, active threats |
| `EARTHQUAKE` | Seismic events and aftershocks |

### SeverityLevel

| Value | Level | Description |
|-------|-------|-------------|
| `LOW` | 1 | Minor impact, local response sufficient |
| `MODERATE` | 2 | Moderate impact, multi-agency coordination needed |
| `HIGH` | 3 | Significant impact, city-wide awareness |
| `SEVERE` | 4 | Major emergency, potential evacuation |
| `CATASTROPHIC` | 5 | Catastrophic, maximum resource mobilization |

### ResponsePhase

| Value | Description |
|-------|-------------|
| `PREPARATION` | Pre-event preparation and staging |
| `IMMEDIATE_RESPONSE` | First 2 hours of active response |
| `SHORT_TERM` | Hours 2-12 of response operations |
| `LONG_TERM_RECOVERY` | Days to weeks post-event |

### CoordinationStatus

| Value | Description |
|-------|-------------|
| `PENDING` | Task created, not started |
| `IN_PROGRESS` | Task actively being processed |
| `COMPLETED` | Task finished successfully |
| `FAILED` | Task failed with error |

## Core Entities

### EmergencyScenario

Represents a potential or active emergency event.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `scenario_id` | string | Yes | Non-empty | Unique identifier |
| `incident_type` | EmergencyType | Yes | Valid enum | Type of emergency |
| `severity_level` | SeverityLevel | Yes | Valid enum | Severity 1-5 |
| `location` | string | Yes | Non-empty | Geographic location description |
| `affected_area_radius` | float | Yes | > 0 | Radius in miles |
| `estimated_population_affected` | int | Yes | >= 0 | Population count |
| `duration_hours` | int | No | > 0 if set | Expected duration |
| `special_conditions` | dict[str, str] | No | - | Additional parameters |
| `weather_impact` | WeatherCondition | No | - | Current weather data |
| `latitude` | float | No | -90 to 90 | Location latitude |
| `longitude` | float | No | -180 to 180 | Location longitude |
| `created_at` | datetime | Auto | - | Creation timestamp |

**Validation Rules**:
- `affected_area_radius` must be positive
- `estimated_population_affected` cannot be negative
- `scenario_id` must be unique within system

### EmergencyResponsePlan

Comprehensive response plan generated from a scenario.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan_id` | string | Yes | Unique identifier (format: `plan_{scenario_id}_{timestamp}`) |
| `scenario` | EmergencyScenario | Yes | Source scenario |
| `immediate_actions` | list[str] | Yes | Actions for first 2 hours |
| `short_term_actions` | list[str] | Yes | Actions for hours 2-12 |
| `long_term_recovery` | list[str] | Yes | Recovery phase actions |
| `resource_allocation` | ResourceAllocation | Yes | Resource deployment |
| `lead_agency` | string | Yes | Primary responsible agency |
| `supporting_agencies` | list[str] | Yes | Supporting organizations |
| `communication_plan` | dict[str, str] | Yes | Communication channels |
| `activation_time` | datetime | Yes | Plan activation timestamp |
| `estimated_duration` | timedelta | Yes | Expected response duration |
| `key_milestones` | list[dict] | Yes | 5+ timeline milestones |
| `success_criteria` | list[str] | No | Success metrics |
| `performance_indicators` | dict[str, float] | No | KPIs |
| `risk_factors` | list[str] | No | Identified risks |
| `mitigation_strategies` | list[str] | No | Risk mitigations |
| `created_at` | datetime | Auto | Creation timestamp |
| `last_updated` | datetime | Auto | Last modification |

### ResourceAllocation

Resource deployment details for a response plan.

| Field | Type | Description |
|-------|------|-------------|
| `personnel_deployment` | dict[str, int] | Role -> count mapping |
| `equipment_requirements` | dict[str, int] | Equipment type -> count |
| `facility_assignments` | dict[str, str] | Facility type -> description |
| `budget_allocation` | dict[str, float] | Category -> budget amount |

**Default Personnel Categories**:
- First Responders (60%)
- Support Staff (30%)
- Command Staff (10%)

**Default Equipment Categories**:
- Emergency Vehicles
- Medical Units
- Communication Equipment

### WeatherCondition

Weather data for a specific location and time.

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `temperature` | float | °F | Current temperature |
| `humidity` | int | % | Relative humidity |
| `wind_speed` | float | mph | Wind speed |
| `wind_direction` | int | degrees | Wind direction (0-360) |
| `pressure` | float | hPa | Atmospheric pressure |
| `visibility` | float | miles | Visibility distance |
| `conditions` | string | - | Text description |
| `timestamp` | datetime | - | Observation time |

### TrafficCondition

Traffic data for a specific route.

| Field | Type | Description |
|-------|------|-------------|
| `route_name` | string | Route identifier |
| `current_speed` | float | Current average speed (mph) |
| `free_flow_speed` | float | Optimal speed (mph) |
| `congestion_level` | string | free_flow/moderate/heavy/severe |
| `travel_time_minutes` | int | Estimated travel time |
| `incidents` | list[str] | Active incidents |
| `last_updated` | datetime | Data timestamp |

### EvacuationRoute

Evacuation route from origin to destination.

| Field | Type | Description |
|-------|------|-------------|
| `route_id` | string | Unique identifier |
| `origin` | string | Starting location/zone |
| `destination` | string | Shelter/safe area |
| `distance_miles` | float | Route distance |
| `estimated_time_minutes` | int | Travel time estimate |
| `capacity_vehicles_per_hour` | int | Route throughput |
| `current_usage_percent` | float | Current utilization |
| `alternate_routes` | list[str] | Backup routes |
| `bottlenecks` | list[str] | Congestion points |

### HistoricalIncident

Record of past emergency events for learning.

| Field | Type | Description |
|-------|------|-------------|
| `incident_id` | string | Unique identifier |
| `incident_type` | EmergencyType | Type of emergency |
| `title` | string | Short title |
| `description` | string | Full description |
| `date_occurred` | datetime | Event date |
| `location` | string | Geographic location |
| `severity_level` | SeverityLevel | Severity at time |
| `response_actions` | list[str] | Actions taken |
| `resources_deployed` | dict[str, int] | Resources used |
| `lessons_learned` | list[str] | Key learnings |
| `response_time_minutes` | int | Initial response time |
| `effectiveness_score` | float | 0-10 rating |
| `agencies_involved` | list[str] | Participating agencies |
| `estimated_cost` | float | Total cost |
| `weather_conditions` | string | Weather at time |
| `affected_population` | int | People affected |

### AgentResponse

Response from a specialized analysis agent.

| Field | Type | Description |
|-------|------|-------------|
| `agent_name` | string | Agent identifier |
| `recommendations` | list[str] | Suggested actions |
| `data_analysis` | dict[str, any] | Analysis results |
| `confidence_score` | float | 0-1 confidence |
| `processing_time_seconds` | float | Execution time |
| `timestamp` | datetime | Response time |

### MultiAgentTask

Task for multi-agent coordination tracking.

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Unique identifier |
| `task_type` | string | Type of analysis task |
| `assigned_agent` | string | Agent handling task |
| `input_data` | dict[str, any] | Task input |
| `status` | CoordinationStatus | Current status |
| `result` | AgentResponse | Task result (if completed) |
| `created_at` | datetime | Creation time |
| `completed_at` | datetime | Completion time |
| `error_message` | string | Error (if failed) |

## State Transitions

### Scenario Lifecycle

```
Created → Analyzing → Plan Generated → Active → Recovery → Closed
                          ↓
                       [Error] → Failed
```

### Task Lifecycle

```
PENDING → IN_PROGRESS → COMPLETED
              ↓
           FAILED
```

## Indexes and Queries

### Primary Queries

1. **Get scenario by ID**: `scenario_id` (exact match)
2. **Get plan by scenario**: `scenario.scenario_id` (exact match)
3. **Search historical incidents**: Full-text on `title`, `description`, `lessons_learned`
4. **Filter by type**: `incident_type` (enum filter)
5. **Filter by severity**: `severity_level` (numeric range)
6. **Filter by date**: `date_occurred` (date range)

### Secondary Indexes

- `HistoricalIncident.incident_type` for filtering
- `HistoricalIncident.severity_level` for filtering
- `HistoricalIncident.date_occurred` for sorting/filtering
- `EmergencyScenario.created_at` for recent scenarios
