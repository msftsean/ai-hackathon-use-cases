#!/usr/bin/env python3
"""Interactive demonstration script for Emergency Response Agent."""

import asyncio
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, ".")

from src.config import Settings, logger
from src.models import EmergencyType, SeverityLevel
from src.models.emergency_models import EmergencyScenario
from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator
from src.services.weather_service import WeatherService
from src.services.traffic_service import TrafficService
from src.services.search_service import SearchService


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f" {text}")
    print("=" * 60)


def print_section(text: str):
    """Print a section header."""
    print(f"\n{text}")
    print("-" * len(text))


async def run_demo():
    """Run the interactive demonstration."""
    print_header("Emergency Response Planning Agent - Demo")
    print("NY State AI Hackathon")

    # Initialize components
    settings = Settings()
    settings.use_mock_services = True  # Use mock for demo

    coordinator = EmergencyResponseCoordinator(settings)
    weather_service = coordinator.weather_service
    traffic_service = coordinator.traffic_service
    search_service = coordinator.search_service

    print("\n[OK] Components initialized")

    # Demo 1: Hurricane Scenario
    print_section("Demo 1: Hurricane Scenario")

    scenario = EmergencyScenario(
        incident_type=EmergencyType.HURRICANE,
        severity_level=SeverityLevel.SEVERE,
        location="Manhattan, NYC",
        coordinates=(40.7128, -74.0060),
        affected_area_radius=10.0,
        estimated_population_affected=500000,
        duration_hours=72,
        description="Category 4 Hurricane approaching NYC metropolitan area",
    )

    print(f"Creating scenario: Category 4 Hurricane - Manhattan")
    print(f"  Type: {scenario.incident_type.value}")
    print(f"  Severity: {scenario.severity_level.value} (Severe)")
    print(f"  Population: {scenario.estimated_population_affected:,}")
    print(f"  Duration: {scenario.duration_hours} hours")

    # Create and generate plan
    created = coordinator.create_scenario(scenario)
    print("\nGenerating response plan...")

    import time
    start = time.time()
    plan = await coordinator.coordinate_response(created.id)
    elapsed = time.time() - start

    print(f"  [OK] Plan generated in {elapsed:.1f}s")
    print(f"  Lead Agency: {plan.lead_agency}")
    print(f"  Supporting: {', '.join(plan.supporting_agencies[:4])}")
    print(f"  Personnel: {plan.personnel_count:,} total")
    print(f"  Vehicles: {plan.vehicle_count:,}")
    print(f"  Timeline: {len(plan.timeline_milestones)} milestones")
    print(f"  Estimated Cost: ${plan.estimated_cost:,.2f}")

    # Show immediate actions
    print("\nImmediate Actions:")
    for action in plan.immediate_actions[:5]:
        print(f"  - {action}")

    # Demo 2: Weather Integration
    print_section("Demo 2: Weather Integration")

    lat, lon = 40.7128, -74.0060
    print(f"Fetching weather for NYC ({lat}, {lon})...")

    weather = weather_service.get_current_conditions(lat, lon)
    print(f"  Temperature: {weather.temperature_f:.0f}°F")
    print(f"  Wind: {weather.wind_speed_mph:.0f} mph {weather.wind_direction}")
    print(f"  Conditions: {weather.conditions}")
    print(f"  Humidity: {weather.humidity_percent:.0f}%")

    risk = weather_service.assess_weather_risk(weather)
    print("\nWeather Risk Assessment:")
    print(f"  Wind Risk: {risk.wind_risk}")
    print(f"  Temperature Risk: {risk.temperature_risk}")
    print(f"  Precipitation Risk: {risk.precipitation_risk}")
    print(f"  Overall Risk: {risk.overall_risk}")

    if risk.recommendations:
        print("\nRecommendations:")
        for rec in risk.recommendations[:3]:
            print(f"  - {rec}")

    # Demo 3: Evacuation Planning
    print_section("Demo 3: Evacuation Planning")

    routes = traffic_service.optimize_evacuation_routes("zone_a")
    print("Zone A Evacuation Routes:")
    for route in routes[:3]:
        status_icon = "[OK]" if route.current_status == "available" else "[!]"
        print(f"  {status_icon} {route.name}")
        print(f"      {route.start_location} -> {route.end_location}")
        print(f"      Distance: {route.distance_miles:.1f} mi, Time: {route.estimated_time_minutes} min")

    capacity = traffic_service.calculate_evacuation_capacity("zone_a", hours=12)
    print("\nEvacuation Capacity Analysis:")
    print(f"  Zone Population: {capacity['population']:,}")
    print(f"  Available Routes: {capacity['available_routes']}")
    print(f"  Capacity/Hour: {capacity['effective_capacity_per_hour']:,} people")
    print(f"  Hours to Evacuate: {capacity['hours_to_evacuate']:.1f}")
    can_evac = "Yes" if capacity['can_evacuate_in_window'] else "No"
    print(f"  Can Evacuate in 12 hours: {can_evac}")

    # Demo 4: Historical Analysis
    print_section("Demo 4: Historical Analysis")

    incidents = search_service.search_historical_incidents(
        incident_type="hurricane",
        limit=3
    )

    print(f"Found {len(incidents)} historical hurricane incidents:")
    for incident in incidents:
        print(f"\n  [{incident.id}] {incident.date.strftime('%Y-%m-%d')}")
        print(f"    Location: {incident.location}")
        print(f"    Severity: {incident.severity}/5")
        print(f"    Affected: {incident.affected_population:,} people")
        print(f"    Key Lesson: {incident.lessons_learned[0][:60]}...")

    # Demo 5: Multi-Agency Coordination
    print_section("Demo 5: Agency Resource Summary")

    print(f"\nResponse Plan Resource Allocation:")
    print(f"{'Resource Type':<25} {'Quantity':>10} {'Agency':<30}")
    print("-" * 70)

    for resource in plan.resources[:6]:
        print(f"{resource['type']:<25} {resource['quantity']:>10} {resource['agency']:<30}")

    # Summary
    print_header("DEMO COMPLETE")
    print("\nThe Emergency Response Agent can:")
    print("  1. Create and analyze emergency scenarios")
    print("  2. Generate comprehensive response plans")
    print("  3. Integrate real-time weather data")
    print("  4. Plan evacuation routes with capacity analysis")
    print("  5. Learn from historical incidents")
    print("  6. Coordinate multi-agency responses")

    print("\nTo run the API server:")
    print("  python -m src.main")
    print("\nAPI will be available at http://localhost:5002/api/v1")


def main():
    """Entry point for demo."""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
