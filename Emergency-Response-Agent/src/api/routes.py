"""Flask API routes for Emergency Response Agent."""

import asyncio
from functools import wraps

from flask import Blueprint, jsonify, request

from ..config import logger
from ..models.emergency_models import EmergencyScenario
from ..orchestration.emergency_coordinator import EmergencyResponseCoordinator
from ..services.weather_service import WeatherService
from ..services.traffic_service import TrafficService
from ..services.search_service import SearchService


def async_route(f):
    """Decorator to run async functions in Flask routes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


def create_api_blueprint(coordinator: EmergencyResponseCoordinator) -> Blueprint:
    """
    Create Flask Blueprint with all API routes.

    Args:
        coordinator: EmergencyResponseCoordinator instance

    Returns:
        Flask Blueprint
    """
    api = Blueprint("api", __name__, url_prefix="/api/v1")

    weather_service = coordinator.weather_service
    traffic_service = coordinator.traffic_service
    search_service = coordinator.search_service

    # Health check endpoints
    @api.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "Emergency Response Agent",
            "version": "0.1.0",
        })

    @api.route("/health/ready", methods=["GET"])
    def readiness_check():
        """Readiness check endpoint."""
        return jsonify({
            "status": "ready",
            "services": {
                "coordinator": "operational",
                "weather": "operational",
                "traffic": "operational",
                "search": "operational",
            },
        })

    # Scenario endpoints
    @api.route("/scenarios", methods=["POST"])
    def create_scenario():
        """Create a new emergency scenario."""
        try:
            data = request.get_json()
            scenario = EmergencyScenario(**data)
            created = coordinator.create_scenario(scenario)
            return jsonify({
                "id": created.id,
                "incident_type": created.incident_type.value,
                "severity_level": created.severity_level.value,
                "location": created.location,
                "created_at": created.created_at.isoformat(),
            }), 201
        except Exception as e:
            logger.error(f"Error creating scenario: {e}")
            return jsonify({"error": str(e)}), 400

    @api.route("/scenarios", methods=["GET"])
    def list_scenarios():
        """List all scenarios."""
        scenarios = coordinator.list_scenarios()
        return jsonify({
            "scenarios": [
                {
                    "id": s.id,
                    "incident_type": s.incident_type.value,
                    "severity_level": s.severity_level.value,
                    "location": s.location,
                    "created_at": s.created_at.isoformat(),
                }
                for s in scenarios
            ],
            "total": len(scenarios),
        })

    @api.route("/scenarios/<scenario_id>", methods=["GET"])
    def get_scenario(scenario_id):
        """Get a specific scenario."""
        scenario = coordinator.get_scenario(scenario_id)
        if not scenario:
            return jsonify({"error": "Scenario not found"}), 404

        return jsonify({
            "id": scenario.id,
            "incident_type": scenario.incident_type.value,
            "severity_level": scenario.severity_level.value,
            "location": scenario.location,
            "coordinates": scenario.coordinates,
            "affected_area_radius": scenario.affected_area_radius,
            "estimated_population_affected": scenario.estimated_population_affected,
            "duration_hours": scenario.duration_hours,
            "description": scenario.description,
            "created_at": scenario.created_at.isoformat(),
        })

    @api.route("/scenarios/<scenario_id>/plan", methods=["POST"])
    @async_route
    async def generate_plan(scenario_id):
        """Generate a response plan for a scenario."""
        try:
            plan = await coordinator.coordinate_response(scenario_id)
            return jsonify({
                "id": plan.id,
                "scenario_id": plan.scenario_id,
                "lead_agency": plan.lead_agency,
                "supporting_agencies": plan.supporting_agencies,
                "response_phase": plan.response_phase.value,
                "coordination_status": plan.coordination_status.value,
                "personnel_count": plan.personnel_count,
                "vehicle_count": plan.vehicle_count,
                "equipment_list": plan.equipment_list,
                "timeline_milestones": plan.timeline_milestones,
                "immediate_actions": plan.immediate_actions,
                "short_term_actions": plan.short_term_actions,
                "recovery_actions": plan.recovery_actions,
                "estimated_cost": plan.estimated_cost,
                "weather_risk_assessment": plan.weather_risk_assessment,
                "evacuation_routes": plan.evacuation_routes,
                "processing_time_ms": plan.processing_time_ms,
                "generated_at": plan.generated_at.isoformat(),
            }), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            return jsonify({"error": str(e)}), 500

    @api.route("/plans/<plan_id>", methods=["GET"])
    def get_plan(plan_id):
        """Get a specific response plan."""
        plan = coordinator.get_plan(plan_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404

        return jsonify({
            "id": plan.id,
            "scenario_id": plan.scenario_id,
            "lead_agency": plan.lead_agency,
            "supporting_agencies": plan.supporting_agencies,
            "response_phase": plan.response_phase.value,
            "personnel_count": plan.personnel_count,
            "vehicle_count": plan.vehicle_count,
            "timeline_milestones": plan.timeline_milestones,
            "immediate_actions": plan.immediate_actions,
            "estimated_cost": plan.estimated_cost,
            "generated_at": plan.generated_at.isoformat(),
        })

    # Weather endpoints
    @api.route("/weather/current", methods=["GET"])
    def get_weather():
        """Get current weather conditions."""
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)

        if lat is None or lon is None:
            return jsonify({"error": "lat and lon parameters required"}), 400

        weather = weather_service.get_current_conditions(lat, lon)
        return jsonify({
            "temperature_f": weather.temperature_f,
            "feels_like_f": weather.feels_like_f,
            "humidity_percent": weather.humidity_percent,
            "wind_speed_mph": weather.wind_speed_mph,
            "wind_direction": weather.wind_direction,
            "conditions": weather.conditions,
            "visibility_miles": weather.visibility_miles,
            "timestamp": weather.timestamp.isoformat(),
        })

    @api.route("/weather/forecast", methods=["GET"])
    def get_forecast():
        """Get weather forecast."""
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)
        hours = request.args.get("hours", default=24, type=int)

        if lat is None or lon is None:
            return jsonify({"error": "lat and lon parameters required"}), 400

        forecasts = weather_service.get_forecast(lat, lon, hours)
        return jsonify({
            "location": {"lat": lat, "lon": lon},
            "hours": len(forecasts),
            "forecasts": [
                {
                    "temperature_f": f.temperature_f,
                    "wind_speed_mph": f.wind_speed_mph,
                    "conditions": f.conditions,
                }
                for f in forecasts
            ],
        })

    @api.route("/weather/risk", methods=["POST"])
    def assess_weather_risk():
        """Assess weather risk for emergency planning."""
        data = request.get_json()
        lat = data.get("lat")
        lon = data.get("lon")

        if lat is None or lon is None:
            return jsonify({"error": "lat and lon required in request body"}), 400

        weather = weather_service.get_current_conditions(lat, lon)
        risk = weather_service.assess_weather_risk(weather)

        return jsonify({
            "current_conditions": {
                "temperature_f": weather.temperature_f,
                "wind_speed_mph": weather.wind_speed_mph,
                "conditions": weather.conditions,
            },
            "risk_assessment": {
                "wind_risk": risk.wind_risk,
                "temperature_risk": risk.temperature_risk,
                "precipitation_risk": risk.precipitation_risk,
                "visibility_risk": risk.visibility_risk,
                "overall_risk": risk.overall_risk,
            },
            "recommendations": risk.recommendations,
        })

    # Evacuation endpoints
    @api.route("/evacuation/routes", methods=["GET"])
    def get_evacuation_routes():
        """Get evacuation routes for a zone."""
        zone = request.args.get("zone", default="zone_a")
        routes = traffic_service.optimize_evacuation_routes(zone)

        return jsonify({
            "zone": zone,
            "routes": [
                {
                    "route_id": r.route_id,
                    "name": r.name,
                    "start_location": r.start_location,
                    "end_location": r.end_location,
                    "distance_miles": r.distance_miles,
                    "estimated_time_minutes": r.estimated_time_minutes,
                    "capacity_per_hour": r.capacity_per_hour,
                    "status": r.current_status,
                    "bottlenecks": r.bottlenecks,
                }
                for r in routes
            ],
        })

    @api.route("/evacuation/capacity", methods=["POST"])
    def calculate_capacity():
        """Calculate evacuation capacity for a zone."""
        data = request.get_json()
        zone = data.get("zone", "zone_a")
        hours = data.get("hours", 12)

        capacity = traffic_service.calculate_evacuation_capacity(zone, hours)
        return jsonify(capacity)

    @api.route("/traffic/conditions", methods=["GET"])
    def get_traffic():
        """Get current traffic conditions."""
        route_id = request.args.get("route_id")
        conditions = traffic_service.get_traffic_conditions(route_id)

        return jsonify({
            "conditions": [
                {
                    "route_name": c.route_name,
                    "current_speed_mph": c.current_speed_mph,
                    "congestion_level": c.congestion_level,
                    "incidents": c.incidents,
                }
                for c in conditions
            ],
        })

    @api.route("/traffic/transit", methods=["GET"])
    def get_transit():
        """Get public transportation status."""
        status = traffic_service.get_public_transportation_status()
        return jsonify(status)

    # Historical incident endpoints
    @api.route("/historical/search", methods=["GET"])
    def search_historical():
        """Search historical incidents."""
        query = request.args.get("q")
        incident_type = request.args.get("type")
        severity_min = request.args.get("severity_min", type=int)
        severity_max = request.args.get("severity_max", type=int)
        limit = request.args.get("limit", default=10, type=int)

        incidents = search_service.search_historical_incidents(
            query=query,
            incident_type=incident_type,
            severity_min=severity_min,
            severity_max=severity_max,
            limit=limit,
        )

        return jsonify({
            "query": query,
            "results": [
                {
                    "id": i.id,
                    "incident_type": i.incident_type,
                    "severity": i.severity,
                    "date": i.date.isoformat(),
                    "location": i.location,
                    "affected_population": i.affected_population,
                    "lessons_learned": i.lessons_learned,
                    "outcome": i.outcome,
                }
                for i in incidents
            ],
            "total": len(incidents),
        })

    @api.route("/historical/<incident_id>", methods=["GET"])
    def get_historical_incident(incident_id):
        """Get a specific historical incident."""
        incident = search_service.get_incident_by_id(incident_id)
        if not incident:
            return jsonify({"error": "Incident not found"}), 404

        return jsonify({
            "id": incident.id,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "date": incident.date.isoformat(),
            "location": incident.location,
            "affected_population": incident.affected_population,
            "response_time_hours": incident.response_time_hours,
            "lessons_learned": incident.lessons_learned,
            "recommendations": incident.recommendations,
            "outcome": incident.outcome,
        })

    @api.route("/historical/statistics", methods=["GET"])
    def get_statistics():
        """Get historical incident statistics."""
        stats = search_service.get_statistics()
        return jsonify(stats)

    return api
