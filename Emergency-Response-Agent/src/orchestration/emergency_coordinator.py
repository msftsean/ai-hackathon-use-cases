"""
Emergency Response Coordinator
Main orchestration system for emergency response planning.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function

from ..models.emergency_models import (
    EmergencyScenario, EmergencyResponsePlan, AgentResponse,
    SeverityLevel, EmergencyType, ResourceAllocation
)
from ..services.weather_service import WeatherService


class EmergencyResponseCoordinator:
    """Main coordinator for emergency response planning."""
    
    def __init__(self):
        self.kernel = Kernel()
        self.weather_service = WeatherService()
        self.logger = logging.getLogger(__name__)
        self._setup_kernel_functions()
        
    def _setup_kernel_functions(self):
        """Set up Semantic Kernel functions for emergency planning."""
        # Register this class's methods as kernel functions
        self.kernel.add_function(
            function_name="analyze_scenario",
            plugin_name="emergency_planner",
            function=self._analyze_scenario_kernel
        )
        
    @kernel_function(
        description="Analyze emergency scenario and generate initial assessment",
        name="analyze_scenario"
    )
    async def _analyze_scenario_kernel(self, scenario_data: str) -> str:
        """Kernel function for scenario analysis."""
        try:
            scenario_dict = json.loads(scenario_data)
            scenario = EmergencyScenario(**scenario_dict)
            assessment = await self._perform_scenario_analysis(scenario)
            return json.dumps(assessment, default=str)
        except Exception as e:
            return f"Error analyzing scenario: {str(e)}"
    
    async def coordinate_response(self, scenario: EmergencyScenario) -> EmergencyResponsePlan:
        """Coordinate multi-agent emergency response planning."""
        self.logger.info(f"Starting response coordination for {scenario.scenario_id}")
        
        # Phase 1: Initial assessment
        assessment = await self._perform_scenario_analysis(scenario)
        
        # Phase 2: Generate response plan
        plan = await self._generate_response_plan(scenario, assessment)
        
        # Phase 3: Resource allocation
        await self._allocate_resources(plan)
        
        # Phase 4: Timeline planning
        await self._create_timeline(plan)
        
        self.logger.info(f"Response coordination completed for {scenario.scenario_id}")
        return plan
    
    async def _perform_scenario_analysis(self, scenario: EmergencyScenario) -> Dict:
        """Perform detailed analysis of the emergency scenario."""
        try:
            self.logger.info(f"Analyzing scenario: {scenario.scenario_id}")
            
            # Gather analysis from multiple perspectives
            analysis = {
                "scenario_type": scenario.incident_type.value,
                "severity_assessment": self._assess_severity(scenario),
                "population_impact": self._assess_population_impact(scenario),
                "geographic_analysis": {
                    "natural_barriers": self._identify_natural_barriers(scenario.location),
                    "access_challenges": self._identify_access_challenges(scenario)
                },
                "escalation_potential": self._assess_escalation_potential(scenario),
                "evacuation_zones": self._identify_evacuation_zones(scenario),
                "access_challenges": self._identify_access_challenges(scenario),
                "resource_requirements": self._estimate_resource_requirements(scenario),
                "timeline_estimates": self._estimate_timeline(scenario)
            }
            
            # Get weather analysis if coordinates available
            if hasattr(scenario, 'latitude') and hasattr(scenario, 'longitude'):
                try:
                    async with WeatherService() as weather_service:
                        current_weather = await weather_service.get_current_conditions(
                            scenario.latitude, scenario.longitude
                        )
                        weather_analysis = await weather_service.analyze_weather_impact(
                            scenario.incident_type.value, current_weather
                        )
                        analysis["weather_impact"] = weather_analysis
                except Exception as e:
                    analysis["weather_impact"] = {"error": str(e)}
            
            return analysis
        except Exception as e:
            self.logger.error(f"Error in scenario analysis: {str(e)}")
            # Return a proper dictionary structure even on error
            return {
                "scenario_type": scenario.incident_type.value if scenario else "unknown",
                "error": f"Error analyzing scenario: {str(e)}",
                "severity_assessment": {},
                "population_impact": {},
                "geographic_analysis": {},
                "escalation_potential": {},
                "evacuation_zones": [],
                "access_challenges": [],
                "resource_requirements": {},
                "timeline_estimates": {}
            }
    
    def _assess_severity(self, scenario: EmergencyScenario) -> Dict:
        """Assess scenario severity and impact factors."""
        severity_factors = []
        
        # Population impact factor
        if scenario.estimated_population_affected > 100000:
            severity_factors.append("Large population impact")
        elif scenario.estimated_population_affected > 10000:
            severity_factors.append("Moderate population impact")
        
        # Geographic factor
        if scenario.affected_area_radius > 10:
            severity_factors.append("Wide geographic area affected")
        
        # Emergency type specific factors
        if scenario.incident_type == EmergencyType.HURRICANE:
            severity_factors.append("Hurricane - extended duration impact")
        elif scenario.incident_type == EmergencyType.PUBLIC_HEALTH:
            severity_factors.append("Public health - potential exponential spread")
        
        return {
            "level": scenario.severity_level.value,
            "factors": severity_factors,
            "escalation_potential": self._assess_escalation_potential(scenario)
        }
    
    def _assess_population_impact(self, scenario: EmergencyScenario) -> Dict:
        """Assess population impact and evacuation zones."""
        directly_affected = scenario.estimated_population_affected
        potentially_affected = int(directly_affected * 1.5)  # 1.5x multiplier
        vulnerable_populations = int(directly_affected * 0.15)  # 15% vulnerable
        
        # Generate evacuation zones based on scenario type and location
        evacuation_zones = []
        if scenario.incident_type == EmergencyType.HURRICANE:
            evacuation_zones = ["Zone A (Coastal)", "Zone B (Low-lying areas)"]
        elif scenario.incident_type == EmergencyType.FIRE:
            evacuation_zones = ["Immediate area", "Adjacent neighborhoods"]
        else:
            evacuation_zones = ["Primary zone", "Buffer zone"]
            
        return {
            "directly_affected": directly_affected,
            "potentially_affected": potentially_affected,
            "vulnerable_populations": vulnerable_populations,
            "evacuation_zones": evacuation_zones
        }
    
    def _assess_escalation_potential(self, scenario: EmergencyScenario) -> str:
        """Assess potential for scenario escalation."""
        high_escalation_types = [EmergencyType.PUBLIC_HEALTH, EmergencyType.FIRE]
        
        if scenario.incident_type in high_escalation_types:
            return "high"
        elif scenario.severity_level.value >= 4:
            return "moderate"
        else:
            return "low"
    
    def _calculate_population_impact(self, scenario: EmergencyScenario) -> Dict:
        """Calculate population impact metrics."""
        return {
            "directly_affected": scenario.estimated_population_affected,
            "potentially_affected": int(scenario.estimated_population_affected * 1.5),
            "vulnerable_populations": int(scenario.estimated_population_affected * 0.15),  # 15% vulnerable
            "evacuation_zones": self._identify_evacuation_zones(scenario)
        }
    
    def _identify_evacuation_zones(self, scenario: EmergencyScenario) -> List[str]:
        """Identify evacuation zones based on scenario."""
        zones = []
        
        if scenario.incident_type == EmergencyType.HURRICANE:
            zones = ["Zone A (Coastal)", "Zone B (Low-lying areas)", "Zone C (High-risk flooding)"]
        elif scenario.incident_type == EmergencyType.FIRE:
            zones = ["Immediate area", "Adjacent neighborhoods", "Smoke-affected areas"]
        elif scenario.incident_type == EmergencyType.INFRASTRUCTURE_FAILURE:
            zones = ["Service area affected", "Secondary impact zones"]
        else:
            zones = ["Primary impact area", "Secondary impact area"]
        
        return zones
    
    def _analyze_geographic_factors(self, scenario: EmergencyScenario) -> Dict:
        """Analyze geographic factors affecting response."""
        return {
            "area_type": self._classify_area_type(scenario.location),
            "access_challenges": self._identify_access_challenges(scenario),
            "infrastructure_density": self._assess_infrastructure_density(scenario.location),
            "natural_barriers": self._identify_natural_barriers(scenario.location)
        }
    
    def _classify_area_type(self, location: str) -> str:
        """Classify the area type from location string."""
        location_lower = location.lower()
        if "manhattan" in location_lower or "downtown" in location_lower:
            return "urban_dense"
        elif "brooklyn" in location_lower or "queens" in location_lower:
            return "urban_moderate"
        elif "suburb" in location_lower:
            return "suburban"
        else:
            return "mixed"
    
    def _identify_access_challenges(self, scenario: EmergencyScenario) -> List[str]:
        """Identify access challenges for emergency response."""
        challenges = []
        
        if scenario.incident_type == EmergencyType.FLOOD:
            challenges.extend(["Flooded roads", "Bridge closures", "Underground access limited"])
        elif scenario.incident_type == EmergencyType.WINTER_STORM:
            challenges.extend(["Snow-blocked roads", "Icy conditions", "Limited visibility"])
        elif scenario.incident_type == EmergencyType.FIRE:
            challenges.extend(["Smoke-filled areas", "Heat zones", "Debris blockages"])
        
        return challenges
    
    def _assess_infrastructure_density(self, location: str) -> str:
        """Assess infrastructure density."""
        location_lower = location.lower()
        if "manhattan" in location_lower:
            return "very_high"
        elif any(x in location_lower for x in ["brooklyn", "queens", "bronx"]):
            return "high"
        else:
            return "moderate"
    
    def _identify_natural_barriers(self, location: str) -> List[str]:
        """Identify natural barriers affecting response."""
        barriers = []
        location_lower = location.lower()
        
        if "manhattan" in location_lower:
            barriers.extend(["East River", "Hudson River"])
        elif "brooklyn" in location_lower:
            barriers.extend(["East River", "Gowanus Bay"])
        elif "queens" in location_lower:
            barriers.extend(["East River", "Flushing Bay"])
        
        return barriers
    
    def _estimate_resource_requirements(self, scenario: EmergencyScenario) -> Dict:
        """Estimate resource requirements."""
        base_personnel = max(50, scenario.estimated_population_affected // 1000)
        
        resource_multipliers = {
            EmergencyType.HURRICANE: 2.0,
            EmergencyType.PUBLIC_HEALTH: 1.5,
            EmergencyType.FIRE: 1.8,
            EmergencyType.INFRASTRUCTURE_FAILURE: 1.2,
            EmergencyType.EARTHQUAKE: 1.5
        }
        
        multiplier = resource_multipliers.get(scenario.incident_type, 1.0)
        final_personnel = int(base_personnel * multiplier)
        
        return {
            "personnel": final_personnel,
            "vehicles": int(final_personnel // 5),
            "medical_units": int(scenario.estimated_population_affected // 5000),
            "shelters": int(scenario.estimated_population_affected // 1000),
            "communication_units": max(5, int(final_personnel // 20))
        }
    
    def _estimate_timeline(self, scenario: EmergencyScenario) -> Dict:
        """Estimate response timeline."""
        base_duration = scenario.duration_hours or 24  # Default 24 hours
        
        return {
            "immediate_response_hours": min(2, base_duration // 12),
            "short_term_response_hours": min(12, base_duration // 2),
            "total_response_hours": base_duration,
            "recovery_days": self._estimate_recovery_time(scenario)
        }
    
    def _estimate_recovery_time(self, scenario: EmergencyScenario) -> int:
        """Estimate recovery time in days."""
        recovery_times = {
            EmergencyType.HURRICANE: 30,
            EmergencyType.FIRE: 7,
            EmergencyType.FLOOD: 14,
            EmergencyType.WINTER_STORM: 3,
            EmergencyType.PUBLIC_HEALTH: 90,
            EmergencyType.INFRASTRUCTURE_FAILURE: 5
        }
        
        base_recovery = recovery_times.get(scenario.incident_type, 7)
        severity_multiplier = scenario.severity_level.value / 3
        
        return int(base_recovery * severity_multiplier)
    
    async def _generate_response_plan(self, scenario: EmergencyScenario, assessment: Dict) -> EmergencyResponsePlan:
        """Generate comprehensive response plan."""
        plan = EmergencyResponsePlan(
            plan_id=f"plan_{scenario.scenario_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scenario=scenario,
            lead_agency=self._determine_lead_agency(scenario),
            activation_time=datetime.now(),
            estimated_duration=timedelta(hours=assessment["timeline_estimates"]["total_response_hours"])
        )
        
        # Generate response actions
        plan.immediate_actions = self._generate_immediate_actions(scenario, assessment)
        plan.short_term_actions = self._generate_short_term_actions(scenario, assessment)
        plan.long_term_recovery = self._generate_recovery_actions(scenario, assessment)
        
        # Set supporting agencies
        plan.supporting_agencies = self._identify_supporting_agencies(scenario)
        
        # Create communication plan
        plan.communication_plan = self._create_communication_plan(scenario)
        
        return plan
    
    def _determine_lead_agency(self, scenario: EmergencyScenario) -> str:
        """Determine lead agency based on scenario type."""
        lead_agencies = {
            EmergencyType.FIRE: "Fire Department",
            EmergencyType.PUBLIC_HEALTH: "Department of Health",
            EmergencyType.HURRICANE: "Office of Emergency Management",
            EmergencyType.INFRASTRUCTURE_FAILURE: "Department of Transportation",
            EmergencyType.SECURITY_INCIDENT: "Police Department"
        }
        
        return lead_agencies.get(scenario.incident_type, "Office of Emergency Management")
    
    def _generate_immediate_actions(self, scenario: EmergencyScenario, assessment: Dict) -> List[str]:
        """Generate immediate response actions."""
        actions = [
            "Activate Emergency Operations Center",
            "Deploy first responders to affected area",
            "Establish incident command post",
            "Assess immediate life safety threats"
        ]
        
        if scenario.incident_type == EmergencyType.HURRICANE:
            actions.extend([
                "Issue evacuation orders for flood-prone areas",
                "Open emergency shelters",
                "Pre-position utility crews"
            ])
        elif scenario.incident_type == EmergencyType.FIRE:
            actions.extend([
                "Establish fire perimeter",
                "Begin evacuation of immediate area",
                "Deploy fire suppression resources"
            ])
        elif scenario.incident_type == EmergencyType.PUBLIC_HEALTH:
            actions.extend([
                "Activate disease surveillance",
                "Implement contact tracing",
                "Coordinate with healthcare facilities"
            ])
        
        return actions
    
    def _generate_short_term_actions(self, scenario: EmergencyScenario, assessment: Dict) -> List[str]:
        """Generate short-term response actions."""
        actions = [
            "Establish regular situation briefings",
            "Coordinate resource distribution",
            "Monitor and adjust response strategies"
        ]
        
        # Safely check for weather impact
        if assessment and assessment.get("weather_impact", {}).get("impact_level") == "high":
            actions.append("Monitor weather conditions and adjust operations")
        
        return actions
    
    def _generate_recovery_actions(self, scenario: EmergencyScenario, assessment: Dict) -> List[str]:
        """Generate long-term recovery actions."""
        return [
            "Conduct damage assessment",
            "Coordinate infrastructure repairs",
            "Provide ongoing support to affected populations",
            "Document lessons learned",
            "Update emergency plans based on experience"
        ]
    
    def _identify_supporting_agencies(self, scenario: EmergencyScenario) -> List[str]:
        """Identify supporting agencies."""
        base_agencies = ["Police Department", "Fire Department", "Emergency Medical Services"]
        
        type_specific = {
            EmergencyType.PUBLIC_HEALTH: ["Department of Health", "Hospitals", "CDC"],
            EmergencyType.INFRASTRUCTURE_FAILURE: ["Utility Companies", "Department of Transportation"],
            EmergencyType.HURRICANE: ["National Weather Service", "Coast Guard", "Red Cross"]
        }
        
        agencies = base_agencies + type_specific.get(scenario.incident_type, [])
        return list(set(agencies))  # Remove duplicates
    
    def _create_communication_plan(self, scenario: EmergencyScenario) -> Dict[str, str]:
        """Create communication plan."""
        return {
            "public_information": "Regular press briefings and social media updates",
            "inter_agency": "Secure radio network and incident command system",
            "emergency_alerts": "Emergency Alert System and Wireless Emergency Alerts",
            "media_relations": "Dedicated media liaison and press center"
        }
    
    async def _allocate_resources(self, plan: EmergencyResponsePlan):
        """Allocate resources for the response plan."""
        requirements = self._estimate_resource_requirements(plan.scenario)
        
        # Calculate personnel deployment that adds up to total
        total_personnel = requirements["personnel"]
        first_responders = int(total_personnel * 0.6)  # 60%
        support_staff = int(total_personnel * 0.3)     # 30%
        command_staff = max(5, total_personnel - first_responders - support_staff)  # Remainder
        
        plan.resource_allocation = ResourceAllocation(
            personnel_deployment={
                "First Responders": first_responders,
                "Support Staff": support_staff,
                "Command Staff": command_staff
            },
            equipment_requirements={
                "Emergency Vehicles": requirements["vehicles"],
                "Medical Units": requirements["medical_units"], 
                "Communication Equipment": requirements["communication_units"]
            },
            facility_assignments={
                "Emergency Shelters": f"{requirements['shelters']} facilities",
                "Command Posts": "Primary and backup locations",
                "Medical Facilities": "Hospital and field medical units"
            }
        )
    
    async def _create_timeline(self, plan: EmergencyResponsePlan):
        """Create detailed timeline for response plan."""
        base_time = plan.activation_time
        
        milestones = [
            {"name": "Initial Response Deployed", "time": base_time},
            {"name": "Command Post Established", "time": base_time + timedelta(minutes=30)},
            {"name": "Full Resource Deployment", "time": base_time + timedelta(hours=3)},
            {"name": "Situation Assessment Complete", "time": base_time + timedelta(hours=5)},
            {"name": "Response Transition to Recovery", "time": base_time + plan.estimated_duration}
        ]
        
        plan.key_milestones = milestones