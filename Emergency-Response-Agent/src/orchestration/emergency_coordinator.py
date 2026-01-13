"""Emergency Response Coordinator - Multi-agent orchestration for emergency planning."""

import time
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..config import logger, Settings
from ..models import EmergencyType, SeverityLevel, ResponsePhase, CoordinationStatus
from ..models.emergency_models import (
    EmergencyScenario,
    EmergencyResponsePlan,
    TimelineMilestone,
    ResourceAllocation,
)
from ..services.weather_service import WeatherService
from ..services.traffic_service import TrafficService
from ..services.search_service import SearchService


class EmergencyResponseCoordinator:
    """
    Coordinates emergency response planning using multiple specialized services.

    This coordinator:
    - Analyzes emergency scenarios
    - Determines lead and supporting agencies
    - Calculates resource requirements
    - Generates comprehensive response plans
    - Integrates weather and traffic data
    """

    # Agency mappings by emergency type
    LEAD_AGENCIES = {
        EmergencyType.HURRICANE: "Office of Emergency Management",
        EmergencyType.FIRE: "Fire Department (FDNY)",
        EmergencyType.FLOOD: "Office of Emergency Management",
        EmergencyType.EARTHQUAKE: "Office of Emergency Management",
        EmergencyType.CHEMICAL_SPILL: "Fire Department (FDNY) - HazMat",
        EmergencyType.PUBLIC_HEALTH: "Department of Health",
        EmergencyType.TERRORISM: "Police Department (NYPD)",
        EmergencyType.INFRASTRUCTURE_FAILURE: "Office of Emergency Management",
    }

    SUPPORTING_AGENCIES = {
        EmergencyType.HURRICANE: [
            "Fire Department (FDNY)",
            "Police Department (NYPD)",
            "Department of Transportation",
            "Department of Buildings",
            "American Red Cross",
            "National Guard",
        ],
        EmergencyType.FIRE: [
            "Police Department (NYPD)",
            "Emergency Medical Services",
            "Department of Buildings",
            "American Red Cross",
        ],
        EmergencyType.FLOOD: [
            "Fire Department (FDNY)",
            "Police Department (NYPD)",
            "Department of Environmental Protection",
            "Department of Transportation",
            "American Red Cross",
        ],
        EmergencyType.EARTHQUAKE: [
            "Fire Department (FDNY)",
            "Police Department (NYPD)",
            "Department of Buildings",
            "Utilities (Con Edison)",
            "American Red Cross",
            "National Guard",
        ],
        EmergencyType.CHEMICAL_SPILL: [
            "Police Department (NYPD)",
            "Department of Environmental Protection",
            "Department of Health",
            "Emergency Medical Services",
        ],
        EmergencyType.PUBLIC_HEALTH: [
            "Emergency Medical Services",
            "Office of Emergency Management",
            "Hospitals Network",
            "Department of Education",
        ],
        EmergencyType.TERRORISM: [
            "Fire Department (FDNY)",
            "FBI",
            "Office of Emergency Management",
            "Emergency Medical Services",
            "National Guard",
        ],
        EmergencyType.INFRASTRUCTURE_FAILURE: [
            "Utilities (Con Edison)",
            "Department of Transportation",
            "Police Department (NYPD)",
            "Fire Department (FDNY)",
        ],
    }

    # Resource multipliers by emergency type
    RESOURCE_MULTIPLIERS = {
        EmergencyType.HURRICANE: 2.0,
        EmergencyType.FIRE: 1.8,
        EmergencyType.FLOOD: 1.5,
        EmergencyType.EARTHQUAKE: 2.5,
        EmergencyType.CHEMICAL_SPILL: 1.2,
        EmergencyType.PUBLIC_HEALTH: 1.0,
        EmergencyType.TERRORISM: 2.0,
        EmergencyType.INFRASTRUCTURE_FAILURE: 1.3,
    }

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize coordinator with services."""
        self.settings = settings or Settings()
        self.weather_service = WeatherService(self.settings)
        self.traffic_service = TrafficService(self.settings)
        self.search_service = SearchService(self.settings)

        # In-memory scenario storage
        self.scenarios: dict[str, EmergencyScenario] = {}
        self.plans: dict[str, EmergencyResponsePlan] = {}

    def create_scenario(self, scenario: EmergencyScenario) -> EmergencyScenario:
        """
        Create and store a new emergency scenario.

        Args:
            scenario: EmergencyScenario to create

        Returns:
            Created scenario with ID
        """
        self.scenarios[scenario.id] = scenario
        logger.info(f"Created scenario {scenario.id}: {scenario.incident_type.value}")
        return scenario

    def get_scenario(self, scenario_id: str) -> Optional[EmergencyScenario]:
        """Get a scenario by ID."""
        return self.scenarios.get(scenario_id)

    def list_scenarios(self) -> list[EmergencyScenario]:
        """List all scenarios."""
        return list(self.scenarios.values())

    async def coordinate_response(self, scenario_id: str) -> EmergencyResponsePlan:
        """
        Coordinate a full emergency response plan for a scenario.

        Args:
            scenario_id: ID of the scenario to plan for

        Returns:
            Complete EmergencyResponsePlan
        """
        start_time = time.time()

        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        logger.info(f"Coordinating response for scenario {scenario_id}")

        # Step 1: Perform scenario analysis
        analysis = self._perform_scenario_analysis(scenario)

        # Step 2: Determine agencies
        lead_agency = self._determine_lead_agency(scenario.incident_type)
        supporting_agencies = self._identify_supporting_agencies(scenario.incident_type)

        # Step 3: Calculate resources
        resources = self._estimate_resource_requirements(scenario)

        # Step 4: Generate timeline
        timeline = self._create_timeline(scenario)

        # Step 5: Generate actions
        immediate_actions = self._generate_immediate_actions(scenario)
        short_term_actions = self._generate_short_term_actions(scenario)
        recovery_actions = self._generate_recovery_actions(scenario)

        # Step 6: Get weather impact if coordinates available
        weather_assessment = None
        if scenario.coordinates:
            weather = self.weather_service.get_current_conditions(
                scenario.coordinates[0], scenario.coordinates[1]
            )
            weather_assessment = self.weather_service.analyze_weather_impact(
                weather, scenario.incident_type.value
            )

        # Step 7: Get evacuation routes if applicable
        evacuation_routes = []
        if scenario.incident_type in [EmergencyType.HURRICANE, EmergencyType.FLOOD, EmergencyType.FIRE]:
            routes = self.traffic_service.optimize_evacuation_routes("zone_a")
            evacuation_routes = [
                {
                    "route_id": r.route_id,
                    "name": r.name,
                    "distance_miles": r.distance_miles,
                    "time_minutes": r.estimated_time_minutes,
                    "status": r.current_status,
                }
                for r in routes
            ]

        # Build the response plan
        processing_time = int((time.time() - start_time) * 1000)

        plan = EmergencyResponsePlan(
            scenario_id=scenario_id,
            lead_agency=lead_agency,
            supporting_agencies=supporting_agencies,
            response_phase=ResponsePhase.PREPARATION,
            coordination_status=CoordinationStatus.ACTIVE,
            personnel_count=resources["personnel"],
            vehicle_count=resources["vehicles"],
            equipment_list=resources["equipment"],
            resources=resources["detailed"],
            timeline_milestones=[vars(m) for m in timeline],
            immediate_actions=immediate_actions,
            short_term_actions=short_term_actions,
            recovery_actions=recovery_actions,
            estimated_cost=self._estimate_cost(resources, scenario),
            weather_risk_assessment=weather_assessment,
            evacuation_routes=evacuation_routes,
            processing_time_ms=processing_time,
        )

        self.plans[plan.id] = plan
        logger.info(f"Generated plan {plan.id} in {processing_time}ms")

        return plan

    def _perform_scenario_analysis(self, scenario: EmergencyScenario) -> dict:
        """Analyze the scenario and assess impact."""
        population_impact = self._assess_population_impact(scenario)

        # Get historical lessons
        historical = self.search_service.get_lessons_for_emergency_type(
            scenario.incident_type.value
        )

        return {
            "severity_assessment": {
                "level": scenario.severity_level.value,
                "description": self._get_severity_description(scenario.severity_level),
            },
            "population_impact": population_impact,
            "historical_context": {
                "similar_incidents": historical["incidents_analyzed"],
                "avg_response_time": historical["average_response_time_hours"],
            },
            "key_lessons": historical["lessons_learned"][:5],
        }

    def _assess_population_impact(self, scenario: EmergencyScenario) -> dict:
        """Assess population impact based on scenario parameters."""
        population = scenario.estimated_population_affected

        # Calculate impact zones
        inner_zone = int(population * 0.3)  # 30% in immediate danger
        middle_zone = int(population * 0.5)  # 50% affected
        outer_zone = int(population * 0.2)  # 20% marginally affected

        # Estimate vulnerable populations (typically ~20% of affected)
        elderly = int(population * 0.15)
        children = int(population * 0.18)
        medical_needs = int(population * 0.05)

        return {
            "total_affected": population,
            "impact_zones": {
                "immediate_danger": inner_zone,
                "significantly_affected": middle_zone,
                "marginally_affected": outer_zone,
            },
            "vulnerable_populations": {
                "elderly_65_plus": elderly,
                "children_under_18": children,
                "special_medical_needs": medical_needs,
            },
            "shelter_needs": int(inner_zone * 0.8),  # 80% of immediate zone may need shelter
        }

    def _estimate_resource_requirements(self, scenario: EmergencyScenario) -> dict:
        """Estimate resources needed based on scenario."""
        population = scenario.estimated_population_affected
        severity = scenario.severity_level.value
        multiplier = self.RESOURCE_MULTIPLIERS.get(scenario.incident_type, 1.5)

        # Base calculations
        base_personnel = max(100, population // 1000)
        base_vehicles = max(20, population // 5000)

        # Apply severity and type multipliers
        personnel = int(base_personnel * severity * multiplier)
        vehicles = int(base_vehicles * severity * multiplier * 0.5)

        # Equipment by emergency type
        equipment = self._get_equipment_for_type(scenario.incident_type)

        # Detailed resource breakdown
        detailed = [
            {
                "type": "First Responders",
                "quantity": int(personnel * 0.4),
                "unit": "personnel",
                "agency": self._determine_lead_agency(scenario.incident_type),
            },
            {
                "type": "Medical Personnel",
                "quantity": int(personnel * 0.2),
                "unit": "personnel",
                "agency": "Emergency Medical Services",
            },
            {
                "type": "Support Staff",
                "quantity": int(personnel * 0.4),
                "unit": "personnel",
                "agency": "Multiple Agencies",
            },
            {
                "type": "Emergency Vehicles",
                "quantity": int(vehicles * 0.5),
                "unit": "vehicles",
                "agency": self._determine_lead_agency(scenario.incident_type),
            },
            {
                "type": "Transport Vehicles",
                "quantity": int(vehicles * 0.3),
                "unit": "vehicles",
                "agency": "Department of Transportation",
            },
            {
                "type": "Support Vehicles",
                "quantity": int(vehicles * 0.2),
                "unit": "vehicles",
                "agency": "Multiple Agencies",
            },
        ]

        return {
            "personnel": personnel,
            "vehicles": vehicles,
            "equipment": equipment,
            "detailed": detailed,
        }

    def _get_equipment_for_type(self, emergency_type: EmergencyType) -> list[str]:
        """Get equipment list based on emergency type."""
        common = ["Communication radios", "First aid kits", "Generators", "Lighting equipment"]

        type_specific = {
            EmergencyType.HURRICANE: [
                "Pumps", "Chainsaws", "Tarps", "Sandbags", "Boats",
            ],
            EmergencyType.FIRE: [
                "Fire hoses", "Breathing apparatus", "Thermal cameras", "Foam systems",
            ],
            EmergencyType.FLOOD: [
                "Pumps", "Boats", "Life jackets", "Sandbags", "Water barriers",
            ],
            EmergencyType.EARTHQUAKE: [
                "Heavy rescue equipment", "Search dogs", "Concrete cutters", "Jacks",
            ],
            EmergencyType.CHEMICAL_SPILL: [
                "HazMat suits", "Decontamination equipment", "Air monitors", "Containment booms",
            ],
            EmergencyType.PUBLIC_HEALTH: [
                "PPE", "Testing equipment", "Ventilators", "Medical supplies",
            ],
            EmergencyType.TERRORISM: [
                "Bomb disposal equipment", "Tactical gear", "Drones", "Detection equipment",
            ],
            EmergencyType.INFRASTRUCTURE_FAILURE: [
                "Heavy machinery", "Repair equipment", "Temporary structures", "Power units",
            ],
        }

        return common + type_specific.get(emergency_type, [])

    def _determine_lead_agency(self, emergency_type: EmergencyType) -> str:
        """Determine the lead agency for an emergency type."""
        return self.LEAD_AGENCIES.get(emergency_type, "Office of Emergency Management")

    def _identify_supporting_agencies(self, emergency_type: EmergencyType) -> list[str]:
        """Identify supporting agencies for an emergency type."""
        return self.SUPPORTING_AGENCIES.get(emergency_type, [
            "Fire Department (FDNY)",
            "Police Department (NYPD)",
            "Emergency Medical Services",
        ])

    def _create_timeline(self, scenario: EmergencyScenario) -> list[TimelineMilestone]:
        """Create response timeline with milestones."""
        duration = scenario.duration_hours

        milestones = [
            TimelineMilestone(
                phase="Immediate Response",
                action="Activate Emergency Operations Center and deploy first responders",
                target_time_hours=0.5,
                responsible_agency=self._determine_lead_agency(scenario.incident_type),
            ),
            TimelineMilestone(
                phase="Assessment",
                action="Complete initial damage assessment and resource survey",
                target_time_hours=2.0,
                responsible_agency="All responding agencies",
                dependencies=["Immediate Response"],
            ),
            TimelineMilestone(
                phase="Stabilization",
                action="Establish staging areas and begin rescue operations",
                target_time_hours=4.0,
                responsible_agency=self._determine_lead_agency(scenario.incident_type),
                dependencies=["Assessment"],
            ),
            TimelineMilestone(
                phase="Operations",
                action="Full-scale response operations and evacuations if needed",
                target_time_hours=min(12.0, duration * 0.25),
                responsible_agency="Unified Command",
                dependencies=["Stabilization"],
            ),
            TimelineMilestone(
                phase="Transition to Recovery",
                action="Begin transition from response to recovery phase",
                target_time_hours=min(duration * 0.75, 72.0),
                responsible_agency="Office of Emergency Management",
                dependencies=["Operations"],
            ),
        ]

        return milestones

    def _generate_immediate_actions(self, scenario: EmergencyScenario) -> list[str]:
        """Generate immediate action items."""
        common_actions = [
            "Activate Emergency Operations Center (EOC)",
            "Issue public safety alerts via Notify NYC",
            "Deploy first responder units to affected area",
            "Establish incident command structure",
            "Begin preliminary damage assessment",
        ]

        type_specific = {
            EmergencyType.HURRICANE: [
                "Issue evacuation orders for coastal zones",
                "Open emergency shelters",
                "Pre-position search and rescue teams",
            ],
            EmergencyType.FIRE: [
                "Establish fire perimeter and evacuation zone",
                "Request mutual aid if needed",
                "Coordinate utility shutoffs",
            ],
            EmergencyType.FLOOD: [
                "Close flooded roadways",
                "Deploy pumping equipment",
                "Issue shelter-in-place or evacuation orders",
            ],
            EmergencyType.EARTHQUAKE: [
                "Check structural integrity of critical buildings",
                "Deploy urban search and rescue teams",
                "Inspect utilities for damage",
            ],
            EmergencyType.CHEMICAL_SPILL: [
                "Establish exclusion zone",
                "Identify substance and hazards",
                "Begin decontamination procedures",
            ],
            EmergencyType.PUBLIC_HEALTH: [
                "Activate health emergency protocols",
                "Coordinate with hospitals",
                "Begin contact tracing if applicable",
            ],
            EmergencyType.TERRORISM: [
                "Secure perimeter and crime scene",
                "Coordinate with federal agencies",
                "Implement security protocols citywide",
            ],
            EmergencyType.INFRASTRUCTURE_FAILURE: [
                "Identify failure extent",
                "Coordinate with utility providers",
                "Implement traffic management",
            ],
        }

        return common_actions + type_specific.get(scenario.incident_type, [])

    def _generate_short_term_actions(self, scenario: EmergencyScenario) -> list[str]:
        """Generate short-term (12-72 hour) action items."""
        return [
            "Sustain emergency operations",
            "Provide shelter and supplies to displaced residents",
            "Continue search and rescue operations",
            "Coordinate with state and federal agencies for additional resources",
            "Establish disaster assistance centers",
            "Begin infrastructure damage assessment",
            "Coordinate debris removal operations",
            "Provide regular public updates",
        ]

    def _generate_recovery_actions(self, scenario: EmergencyScenario) -> list[str]:
        """Generate recovery phase action items."""
        return [
            "Transition to recovery operations",
            "Process disaster assistance applications",
            "Support infrastructure restoration",
            "Coordinate with insurance and FEMA",
            "Conduct after-action review",
            "Document lessons learned",
            "Begin community rebuilding support",
            "Address long-term housing needs",
        ]

    def _estimate_cost(self, resources: dict, scenario: EmergencyScenario) -> float:
        """Estimate response cost."""
        # Rough cost estimates
        personnel_cost = resources["personnel"] * 500 * (scenario.duration_hours / 8)  # $500/shift
        vehicle_cost = resources["vehicles"] * 200 * scenario.duration_hours  # $200/hour
        equipment_cost = len(resources["equipment"]) * 5000  # $5000 avg per equipment type
        overhead = (personnel_cost + vehicle_cost + equipment_cost) * 0.2  # 20% overhead

        return round(personnel_cost + vehicle_cost + equipment_cost + overhead, 2)

    def _get_severity_description(self, severity: SeverityLevel) -> str:
        """Get human-readable severity description."""
        descriptions = {
            SeverityLevel.MINIMAL: "Minimal impact - localized incident",
            SeverityLevel.MINOR: "Minor impact - limited area affected",
            SeverityLevel.MODERATE: "Moderate impact - significant resources needed",
            SeverityLevel.SEVERE: "Severe impact - major emergency declaration likely",
            SeverityLevel.CATASTROPHIC: "Catastrophic - citywide emergency, maximum response",
        }
        return descriptions.get(severity, "Unknown severity level")

    def get_plan(self, plan_id: str) -> Optional[EmergencyResponsePlan]:
        """Get a response plan by ID."""
        return self.plans.get(plan_id)

    def list_plans(self) -> list[EmergencyResponsePlan]:
        """List all response plans."""
        return list(self.plans.values())
