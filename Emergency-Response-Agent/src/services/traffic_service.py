"""Traffic service for evacuation route planning and traffic analysis."""

import random
from typing import Optional

from ..config import logger, Settings
from ..models.emergency_models import TrafficCondition, EvacuationRoute


class TrafficService:
    """Service for traffic conditions and evacuation route planning."""

    # NYC evacuation zones and routes
    NYC_EVACUATION_ZONES = {
        "zone_a": {
            "name": "Zone A - Coastal Areas",
            "areas": ["Lower Manhattan", "Brooklyn Waterfront", "Staten Island Shore"],
            "population": 370000,
        },
        "zone_b": {
            "name": "Zone B - Low-lying Areas",
            "areas": ["South Bronx", "East Harlem", "Coney Island"],
            "population": 200000,
        },
        "zone_c": {
            "name": "Zone C - Elevated Flood Risk",
            "areas": ["Queens Waterfront", "Rockaway Peninsula"],
            "population": 110000,
        },
    }

    NYC_EVACUATION_ROUTES = [
        {
            "route_id": "rt_001",
            "name": "FDR Drive North",
            "start_location": "Lower Manhattan",
            "end_location": "Upper East Side",
            "distance_miles": 8.5,
            "normal_time_minutes": 25,
            "capacity_per_hour": 3500,
        },
        {
            "route_id": "rt_002",
            "name": "West Side Highway North",
            "start_location": "Battery Park",
            "end_location": "George Washington Bridge",
            "distance_miles": 11.2,
            "normal_time_minutes": 30,
            "capacity_per_hour": 4000,
        },
        {
            "route_id": "rt_003",
            "name": "Brooklyn-Queens Expressway",
            "start_location": "Brooklyn Waterfront",
            "end_location": "Long Island Expressway",
            "distance_miles": 15.0,
            "normal_time_minutes": 40,
            "capacity_per_hour": 4500,
        },
        {
            "route_id": "rt_004",
            "name": "Belt Parkway East",
            "start_location": "Coney Island",
            "end_location": "JFK Area",
            "distance_miles": 12.8,
            "normal_time_minutes": 35,
            "capacity_per_hour": 3800,
        },
        {
            "route_id": "rt_005",
            "name": "Bronx River Parkway North",
            "start_location": "South Bronx",
            "end_location": "Westchester Border",
            "distance_miles": 10.5,
            "normal_time_minutes": 28,
            "capacity_per_hour": 3200,
        },
    ]

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize traffic service."""
        self.settings = settings or Settings()

    def get_traffic_conditions(self, route_id: Optional[str] = None) -> list[TrafficCondition]:
        """
        Get current traffic conditions for evacuation routes.

        Args:
            route_id: Specific route ID, or None for all routes

        Returns:
            List of TrafficCondition objects
        """
        conditions = []

        routes = self.NYC_EVACUATION_ROUTES
        if route_id:
            routes = [r for r in routes if r["route_id"] == route_id]

        for route in routes:
            # Generate realistic mock traffic data
            congestion_factor = random.uniform(1.0, 2.5)
            current_speed = route["capacity_per_hour"] / (3600 / route["normal_time_minutes"] * route["distance_miles"]) / congestion_factor

            if congestion_factor < 1.3:
                congestion_level = "light"
            elif congestion_factor < 1.7:
                congestion_level = "moderate"
            elif congestion_factor < 2.2:
                congestion_level = "heavy"
            else:
                congestion_level = "severe"

            # Random incidents
            incidents = []
            if random.random() < 0.2:
                incidents.append(random.choice([
                    "Minor accident - right lane blocked",
                    "Construction - reduced lanes",
                    "Stalled vehicle",
                    "Police activity",
                ]))

            conditions.append(TrafficCondition(
                route_name=route["name"],
                current_speed_mph=round(current_speed * 60, 1),
                free_flow_speed_mph=60.0,
                congestion_level=congestion_level,
                incidents=incidents,
            ))

        return conditions

    def optimize_evacuation_routes(
        self,
        zone: str,
        population: Optional[int] = None
    ) -> list[EvacuationRoute]:
        """
        Get optimized evacuation routes for a zone.

        Args:
            zone: Zone identifier (zone_a, zone_b, zone_c)
            population: Override population estimate

        Returns:
            List of EvacuationRoute objects
        """
        zone_info = self.NYC_EVACUATION_ZONES.get(zone, self.NYC_EVACUATION_ZONES["zone_a"])
        zone_population = population or zone_info["population"]

        # Get current traffic conditions
        traffic = {c.route_name: c for c in self.get_traffic_conditions()}

        routes = []
        for route_data in self.NYC_EVACUATION_ROUTES:
            # Check if route serves this zone
            route_zones = {
                "rt_001": ["zone_a"],
                "rt_002": ["zone_a"],
                "rt_003": ["zone_a", "zone_b"],
                "rt_004": ["zone_b", "zone_c"],
                "rt_005": ["zone_b"],
            }

            if zone not in route_zones.get(route_data["route_id"], []):
                continue

            # Calculate evacuation time with traffic
            traffic_cond = traffic.get(route_data["name"])
            congestion_multiplier = 1.0
            if traffic_cond:
                multipliers = {"light": 1.2, "moderate": 1.5, "heavy": 2.0, "severe": 3.0}
                congestion_multiplier = multipliers.get(traffic_cond.congestion_level, 1.5)

            estimated_time = int(route_data["normal_time_minutes"] * congestion_multiplier)

            # Identify bottlenecks
            bottlenecks = self._analyze_bottlenecks(route_data, traffic_cond)

            # Determine route status
            if traffic_cond and traffic_cond.congestion_level == "severe":
                status = "congested"
            elif traffic_cond and traffic_cond.incidents:
                status = "impacted"
            else:
                status = "available"

            routes.append(EvacuationRoute(
                route_id=route_data["route_id"],
                name=route_data["name"],
                start_location=route_data["start_location"],
                end_location=route_data["end_location"],
                distance_miles=route_data["distance_miles"],
                estimated_time_minutes=estimated_time,
                capacity_per_hour=route_data["capacity_per_hour"],
                current_status=status,
                bottlenecks=bottlenecks,
            ))

        # Sort by estimated time
        routes.sort(key=lambda r: r.estimated_time_minutes)

        return routes

    def _analyze_bottlenecks(
        self,
        route: dict,
        traffic: Optional[TrafficCondition]
    ) -> list[str]:
        """Analyze potential bottlenecks on a route."""
        bottlenecks = []

        # Known bottleneck points
        route_bottlenecks = {
            "rt_001": ["23rd Street entrance", "42nd Street exit", "96th Street merge"],
            "rt_002": ["Holland Tunnel entrance", "Lincoln Tunnel area", "GW Bridge approach"],
            "rt_003": ["Atlantic Avenue junction", "Kosciuszko Bridge", "LIE interchange"],
            "rt_004": ["Sheepshead Bay curve", "Rockaway Parkway exit", "Cross Bay Bridge"],
            "rt_005": ["Bronx Zoo area", "Gun Hill Road exit", "Yonkers border"],
        }

        # Add route-specific bottlenecks based on congestion
        if traffic and traffic.congestion_level in ["heavy", "severe"]:
            potential_bottlenecks = route_bottlenecks.get(route["route_id"], [])
            # Add 1-2 bottlenecks based on severity
            num_bottlenecks = 2 if traffic.congestion_level == "severe" else 1
            bottlenecks.extend(random.sample(
                potential_bottlenecks,
                min(num_bottlenecks, len(potential_bottlenecks))
            ))

        # Add incident-based bottlenecks
        if traffic and traffic.incidents:
            for incident in traffic.incidents:
                bottlenecks.append(f"Incident: {incident}")

        return bottlenecks

    def calculate_evacuation_capacity(
        self,
        zone: str,
        hours: int = 12
    ) -> dict:
        """
        Calculate total evacuation capacity for a zone.

        Args:
            zone: Zone identifier
            hours: Time window for evacuation

        Returns:
            Dictionary with capacity analysis
        """
        routes = self.optimize_evacuation_routes(zone)
        zone_info = self.NYC_EVACUATION_ZONES.get(zone, self.NYC_EVACUATION_ZONES["zone_a"])

        # Sum up capacity from all available routes
        total_capacity = sum(
            r.capacity_per_hour for r in routes
            if r.current_status != "closed"
        )

        # Apply efficiency factor (accounts for realistic throughput)
        efficiency_factor = 0.75  # 75% of theoretical capacity
        effective_capacity = int(total_capacity * efficiency_factor)

        # Calculate time needed to evacuate zone
        population = zone_info["population"]
        hours_needed = population / effective_capacity if effective_capacity > 0 else float("inf")

        return {
            "zone": zone,
            "zone_name": zone_info["name"],
            "population": population,
            "available_routes": len([r for r in routes if r.current_status != "closed"]),
            "theoretical_capacity_per_hour": total_capacity,
            "effective_capacity_per_hour": effective_capacity,
            "total_capacity_in_window": effective_capacity * hours,
            "hours_to_evacuate": round(hours_needed, 1),
            "can_evacuate_in_window": hours_needed <= hours,
            "routes": [
                {
                    "name": r.name,
                    "capacity": r.capacity_per_hour,
                    "status": r.current_status,
                    "time_minutes": r.estimated_time_minutes,
                }
                for r in routes
            ],
        }

    def get_public_transportation_status(self) -> dict:
        """
        Get MTA public transportation status for evacuation support.

        Returns:
            Dictionary with transit status
        """
        # Mock MTA status
        subway_lines = ["1", "2", "3", "4", "5", "6", "7", "A", "C", "E", "B", "D", "F", "M", "N", "Q", "R", "W", "J", "Z", "L", "G", "S"]

        line_statuses = {}
        for line in subway_lines:
            if random.random() < 0.85:
                status = "good_service"
            elif random.random() < 0.7:
                status = "delays"
            else:
                status = "service_change"

            line_statuses[line] = status

        # Bus evacuation support
        bus_capacity = {
            "standard_buses": 150,
            "articulated_buses": 75,
            "total_fleet_capacity": 150 * 40 + 75 * 60,  # passengers per hour
        }

        return {
            "subway": {
                "overall_status": "operational" if sum(1 for s in line_statuses.values() if s == "good_service") > 15 else "degraded",
                "line_status": line_statuses,
                "evacuation_capacity_per_hour": 50000,  # passengers
            },
            "bus": {
                "available_for_evacuation": True,
                "buses_available": bus_capacity["standard_buses"] + bus_capacity["articulated_buses"],
                "capacity_per_hour": bus_capacity["total_fleet_capacity"],
            },
            "ferry": {
                "operational": True,
                "routes_available": ["Staten Island Ferry", "NYC Ferry - East River"],
                "capacity_per_hour": 8000,
            },
        }
