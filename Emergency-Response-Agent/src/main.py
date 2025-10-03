"""
Emergency Response Agent - Main Application
Demonstrates the emergency response planning system.
"""
import asyncio
import json
import sys
import os
from datetime import datetime
import requests

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.emergency_models import EmergencyScenario, EmergencyType, SeverityLevel
from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator
user_location = input("Enter your location (city, state): ")


def get_direct_geocoding_results(location: str) -> str:
    """Construct the OpenWeatherMap direct geocoding URL for a location."""
    base_url = os.getenv("OPENWEATHERMAP_DIRECT_GEOCODING_URL")
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    url = f"{base_url}{location}&limit=1&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if not data:
        raise ValueError("No geocoding results found.")
    return data[0]  # The first result

lat_geocoding_url = get_direct_geocoding_results(user_location)
lat_geocoding_url["lat"]
lon_geocoding_url["lon"]

def get_current_conditions_url(lat: float, lon: float) -> str:
    """Construct the OpenWeatherMap current conditions URL for a location."""
    base_url = os.getenv("OPENWEATHERMAP_CURRENT_CONDITIONS_URL")
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    return f"{base_url}lat={lat_geocoding_url['lat']}&lon={lon_geocoding_url['lon']}&appid={api_key}"

async def main():
    """Main demonstration of emergency response planning."""
    print("🚨 Emergency Response Planning Agent Demo")
    print("=" * 50)
    
    # Create coordinator
    coordinator = EmergencyResponseCoordinator()
    
    # Create sample emergency scenario
    hurricane_scenario = EmergencyScenario(
        scenario_id="hurricane_test_2025",
        incident_type=EmergencyType.HURRICANE,
        severity_level=SeverityLevel.SEVERE,
        location=get_current_conditions_url(lat_geocoding_url['lat'], lon_geocoding_url['lon']),
        affected_area_radius=15.0,
        estimated_population_affected=500000,
        duration_hours=48,
        special_conditions={
            "storm_surge": "8-12 feet expected",
            "wind_speed": "85-95 mph sustained"
        }
    )

    tsunami_scenario = EmergencyScenario(
        scenario_id="tsunami_test_2025",
        incident_type=EmergencyType.TSUNAMI,
        severity_level=SeverityLevel.SEVERE,
        location=os.getenv(f"OPENWEATHERMAP_DIRECT_GEOCODING_URL{user_location}"),
        affected_area_radius=10.0,
        estimated_population_affected=200000,
        duration_hours=72,
        special_conditions={
            "wave_height": "30-50 feet expected",
            "evacuation_order": "Mandatory for coastal areas"
        }
    )




    print(f"📋 Scenario: {hurricane_scenario.scenario_id}")
    print(f"🌀 Type: {hurricane_scenario.incident_type.value}")
    print(f"📍 Location: {hurricane_scenario.location}")
    print(f"👥 Population Affected: {hurricane_scenario.estimated_population_affected:,}")
    print(f"⚠️ Severity: Level {hurricane_scenario.severity_level.value}")
    print()
    
    print("🔄 Generating Emergency Response Plan...")
    
    try:
        # Generate response plan
        response_plan = await coordinator.coordinate_response(hurricane_scenario)
        
        print("✅ Emergency Response Plan Generated!")
        print("=" * 50)
        
        print(f"📋 Plan ID: {response_plan.plan_id}")
        print(f"🏢 Lead Agency: {response_plan.lead_agency}")
        print(f"⏰ Activation Time: {response_plan.activation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Estimated Duration: {response_plan.estimated_duration}")
        print()
        
        print("🚨 Immediate Actions:")
        for i, action in enumerate(response_plan.immediate_actions, 1):
            print(f"  {i}. {action}")
        print()
        
        print("📊 Resource Allocation:")
        if response_plan.resource_allocation.personnel_deployment:
            print("  Personnel:")
            for role, count in response_plan.resource_allocation.personnel_deployment.items():
                print(f"    • {role}: {count}")
        
        if response_plan.resource_allocation.equipment_requirements:
            print("  Equipment:")
            for equipment, count in response_plan.resource_allocation.equipment_requirements.items():
                print(f"    • {equipment}: {count}")
        print()
        
        print("🤝 Supporting Agencies:")
        for agency in response_plan.supporting_agencies:
            print(f"  • {agency}")
        print()
        
        print("📅 Key Milestones:")
        for milestone in response_plan.key_milestones:
            print(f"  • {milestone['name']}: {milestone['time'].strftime('%H:%M')}")
        
    except Exception as e:
        print(f"❌ Error generating response plan: {e}")
    
    print("\n🎯 Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())