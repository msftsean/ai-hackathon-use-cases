"""Integration tests for Emergency Response Agent."""

import pytest
from flask import Flask

from src.config import Settings
from src.main import create_app
from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator


@pytest.fixture
def app():
    """Create Flask app for testing."""
    settings = Settings()
    settings.use_mock_services = True
    return create_app(settings)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"

    def test_readiness_check(self, client):
        """Test readiness endpoint."""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ready"


class TestScenarioEndpoints:
    """Test scenario management endpoints."""

    def test_create_scenario(self, client):
        """Test creating a scenario via API."""
        response = client.post("/api/v1/scenarios", json={
            "incident_type": "hurricane",
            "severity_level": 4,
            "location": "Manhattan, NYC",
            "affected_area_radius": 10.0,
            "estimated_population_affected": 500000,
            "duration_hours": 72,
        })

        assert response.status_code == 201
        data = response.get_json()
        assert "id" in data
        assert data["incident_type"] == "hurricane"
        assert data["severity_level"] == 4

    def test_create_scenario_invalid(self, client):
        """Test creating scenario with invalid data."""
        response = client.post("/api/v1/scenarios", json={
            "incident_type": "invalid_type",
            "severity_level": 4,
            "location": "Test",
        })

        assert response.status_code == 400

    def test_list_scenarios(self, client):
        """Test listing scenarios."""
        # Create a scenario first
        client.post("/api/v1/scenarios", json={
            "incident_type": "fire",
            "severity_level": 3,
            "location": "Bronx",
            "affected_area_radius": 2.0,
            "estimated_population_affected": 5000,
            "duration_hours": 8,
        })

        response = client.get("/api/v1/scenarios")

        assert response.status_code == 200
        data = response.get_json()
        assert "scenarios" in data
        assert len(data["scenarios"]) >= 1

    def test_get_scenario(self, client):
        """Test getting a specific scenario."""
        # Create scenario
        create_response = client.post("/api/v1/scenarios", json={
            "incident_type": "flood",
            "severity_level": 3,
            "location": "Queens",
            "affected_area_radius": 5.0,
            "estimated_population_affected": 100000,
            "duration_hours": 24,
        })
        scenario_id = create_response.get_json()["id"]

        # Get scenario
        response = client.get(f"/api/v1/scenarios/{scenario_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == scenario_id
        assert data["incident_type"] == "flood"

    def test_get_scenario_not_found(self, client):
        """Test getting nonexistent scenario."""
        response = client.get("/api/v1/scenarios/nonexistent-id")

        assert response.status_code == 404


class TestPlanGeneration:
    """Test response plan generation endpoints."""

    def test_generate_plan(self, client):
        """Test generating a response plan."""
        # Create scenario
        create_response = client.post("/api/v1/scenarios", json={
            "incident_type": "hurricane",
            "severity_level": 4,
            "location": "Manhattan",
            "coordinates": [40.7128, -74.0060],
            "affected_area_radius": 10.0,
            "estimated_population_affected": 500000,
            "duration_hours": 72,
        })
        scenario_id = create_response.get_json()["id"]

        # Generate plan
        response = client.post(f"/api/v1/scenarios/{scenario_id}/plan")

        assert response.status_code == 201
        data = response.get_json()
        assert "id" in data
        assert data["scenario_id"] == scenario_id
        assert data["lead_agency"] is not None
        assert len(data["supporting_agencies"]) > 0
        assert data["personnel_count"] > 0

    def test_generate_plan_not_found(self, client):
        """Test generating plan for nonexistent scenario."""
        response = client.post("/api/v1/scenarios/nonexistent/plan")

        assert response.status_code == 404


class TestWeatherEndpoints:
    """Test weather-related endpoints."""

    def test_get_current_weather(self, client):
        """Test getting current weather."""
        response = client.get("/api/v1/weather/current?lat=40.7128&lon=-74.0060")

        assert response.status_code == 200
        data = response.get_json()
        assert "temperature_f" in data
        assert "wind_speed_mph" in data
        assert "conditions" in data

    def test_get_weather_missing_params(self, client):
        """Test weather endpoint without required params."""
        response = client.get("/api/v1/weather/current")

        assert response.status_code == 400

    def test_get_forecast(self, client):
        """Test getting weather forecast."""
        response = client.get("/api/v1/weather/forecast?lat=40.7128&lon=-74.0060&hours=12")

        assert response.status_code == 200
        data = response.get_json()
        assert "forecasts" in data
        assert data["hours"] == 12

    def test_assess_weather_risk(self, client):
        """Test weather risk assessment."""
        response = client.post("/api/v1/weather/risk", json={
            "lat": 40.7128,
            "lon": -74.0060,
        })

        assert response.status_code == 200
        data = response.get_json()
        assert "risk_assessment" in data
        assert "overall_risk" in data["risk_assessment"]


class TestEvacuationEndpoints:
    """Test evacuation-related endpoints."""

    def test_get_evacuation_routes(self, client):
        """Test getting evacuation routes."""
        response = client.get("/api/v1/evacuation/routes?zone=zone_a")

        assert response.status_code == 200
        data = response.get_json()
        assert "routes" in data
        assert len(data["routes"]) > 0

    def test_calculate_capacity(self, client):
        """Test evacuation capacity calculation."""
        response = client.post("/api/v1/evacuation/capacity", json={
            "zone": "zone_a",
            "hours": 12,
        })

        assert response.status_code == 200
        data = response.get_json()
        assert "population" in data
        assert "effective_capacity_per_hour" in data
        assert "hours_to_evacuate" in data

    def test_get_traffic_conditions(self, client):
        """Test getting traffic conditions."""
        response = client.get("/api/v1/traffic/conditions")

        assert response.status_code == 200
        data = response.get_json()
        assert "conditions" in data


class TestHistoricalEndpoints:
    """Test historical incident endpoints."""

    def test_search_historical(self, client):
        """Test searching historical incidents."""
        response = client.get("/api/v1/historical/search?q=hurricane")

        assert response.status_code == 200
        data = response.get_json()
        assert "results" in data

    def test_search_historical_with_filters(self, client):
        """Test searching with filters."""
        response = client.get("/api/v1/historical/search?type=hurricane&severity_min=4")

        assert response.status_code == 200
        data = response.get_json()
        # All results should be hurricanes with severity >= 4
        for result in data["results"]:
            assert result["incident_type"] == "hurricane"
            assert result["severity"] >= 4

    def test_get_historical_statistics(self, client):
        """Test getting historical statistics."""
        response = client.get("/api/v1/historical/statistics")

        assert response.status_code == 200
        data = response.get_json()
        assert "total_incidents" in data
        assert "by_type" in data


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_emergency_workflow(self, client):
        """Test complete emergency planning workflow."""
        # 1. Create scenario
        create_response = client.post("/api/v1/scenarios", json={
            "incident_type": "fire",
            "severity_level": 3,
            "location": "Brooklyn, NYC",
            "coordinates": [40.6782, -73.9442],
            "affected_area_radius": 2.0,
            "estimated_population_affected": 10000,
            "duration_hours": 8,
        })
        assert create_response.status_code == 201
        scenario_id = create_response.get_json()["id"]

        # 2. Get weather for location
        weather_response = client.get("/api/v1/weather/current?lat=40.6782&lon=-73.9442")
        assert weather_response.status_code == 200

        # 3. Generate response plan
        plan_response = client.post(f"/api/v1/scenarios/{scenario_id}/plan")
        assert plan_response.status_code == 201
        plan = plan_response.get_json()

        # 4. Verify plan contents
        assert "Fire Department" in plan["lead_agency"]
        assert plan["personnel_count"] > 0
        assert len(plan["immediate_actions"]) > 0
        assert len(plan["timeline_milestones"]) == 5

        # 5. Check historical incidents
        historical_response = client.get("/api/v1/historical/search?type=fire")
        assert historical_response.status_code == 200
