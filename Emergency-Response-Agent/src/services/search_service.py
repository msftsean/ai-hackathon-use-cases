"""Search service for historical incident analysis."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import logger, Settings
from ..models.emergency_models import HistoricalIncident


class SearchService:
    """Service for searching and analyzing historical incidents."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize search service."""
        self.settings = settings or Settings()
        self.incidents: dict[str, HistoricalIncident] = {}
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample historical incident data."""
        # Default sample incidents
        sample_incidents = [
            HistoricalIncident(
                id="hist_001",
                incident_type="hurricane",
                severity=4,
                date=datetime(2012, 10, 29),
                location="New York City",
                affected_population=8400000,
                response_time_hours=2.5,
                lessons_learned=[
                    "Pre-positioned emergency supplies were critical",
                    "Evacuation orders should be issued 48+ hours in advance",
                    "Hospital evacuation requires specialized planning",
                    "Fuel supply chains need backup plans",
                ],
                recommendations=[
                    "Establish regional fuel reserves",
                    "Improve hospital backup power systems",
                    "Create shelter-in-place guidance for high-rises",
                ],
                outcome="Major flooding, 43 deaths in NYC, $19B damage",
            ),
            HistoricalIncident(
                id="hist_002",
                incident_type="blackout",
                severity=3,
                date=datetime(2003, 8, 14),
                location="Northeast US",
                affected_population=55000000,
                response_time_hours=1.0,
                lessons_learned=[
                    "Grid interdependencies need better monitoring",
                    "Traffic management was a major challenge",
                    "Communication systems need backup power",
                ],
                recommendations=[
                    "Invest in grid modernization",
                    "Establish manual traffic control protocols",
                    "Ensure cell tower backup generators",
                ],
                outcome="55 million affected, $6B economic loss, 11 deaths",
            ),
            HistoricalIncident(
                id="hist_003",
                incident_type="public_health",
                severity=5,
                date=datetime(2020, 3, 1),
                location="New York City",
                affected_population=8400000,
                response_time_hours=168.0,  # ~1 week for full response
                lessons_learned=[
                    "PPE stockpiles were insufficient",
                    "Hospital surge capacity needs improvement",
                    "Remote work infrastructure proved critical",
                    "Contact tracing requires massive workforce",
                ],
                recommendations=[
                    "Maintain 90-day PPE stockpile",
                    "Develop field hospital deployment plans",
                    "Establish testing infrastructure framework",
                ],
                outcome="Major pandemic response, 30,000+ deaths in NYC",
            ),
            HistoricalIncident(
                id="hist_004",
                incident_type="fire",
                severity=4,
                date=datetime(2017, 12, 28),
                location="Bronx, NYC",
                affected_population=200,
                response_time_hours=0.1,
                lessons_learned=[
                    "Space heater safety education is critical",
                    "High-rise fires require specialized response",
                    "Smoke spread faster than fire",
                ],
                recommendations=[
                    "Increase fire safety inspections in winter",
                    "Distribute smoke detectors to vulnerable populations",
                ],
                outcome="12 deaths, 200+ displaced",
            ),
            HistoricalIncident(
                id="hist_005",
                incident_type="flood",
                severity=3,
                date=datetime(2021, 9, 1),
                location="NYC Metropolitan Area",
                affected_population=500000,
                response_time_hours=0.5,
                lessons_learned=[
                    "Basement apartments are high risk during flash floods",
                    "Subway flooding requires rapid response",
                    "Storm drains need proactive clearing",
                ],
                recommendations=[
                    "Improve basement apartment regulations",
                    "Install flood sensors in subway system",
                    "Create rapid storm drain clearing protocols",
                ],
                outcome="13 deaths from basement flooding, major transit disruption",
            ),
            HistoricalIncident(
                id="hist_006",
                incident_type="terrorism",
                severity=5,
                date=datetime(2001, 9, 11),
                location="Lower Manhattan, NYC",
                affected_population=500000,
                response_time_hours=0.25,
                lessons_learned=[
                    "First responder communication was fragmented",
                    "Building evacuation protocols needed improvement",
                    "Dust and debris created long-term health issues",
                ],
                recommendations=[
                    "Unify first responder radio systems",
                    "Establish comprehensive evacuation training",
                    "Provide respiratory protection for first responders",
                ],
                outcome="2,977 deaths, massive economic impact",
            ),
        ]

        for incident in sample_incidents:
            self.incidents[incident.id] = incident

        logger.info(f"Loaded {len(self.incidents)} historical incidents")

    def search_historical_incidents(
        self,
        query: Optional[str] = None,
        incident_type: Optional[str] = None,
        severity_min: Optional[int] = None,
        severity_max: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 10,
    ) -> list[HistoricalIncident]:
        """
        Search historical incidents with filters.

        Args:
            query: Text search in incident details
            incident_type: Filter by incident type
            severity_min: Minimum severity level
            severity_max: Maximum severity level
            date_from: Start date filter
            date_to: End date filter
            limit: Maximum results to return

        Returns:
            List of matching HistoricalIncident objects
        """
        results = list(self.incidents.values())

        # Apply filters
        if incident_type:
            results = [i for i in results if i.incident_type.lower() == incident_type.lower()]

        if severity_min is not None:
            results = [i for i in results if i.severity >= severity_min]

        if severity_max is not None:
            results = [i for i in results if i.severity <= severity_max]

        if date_from:
            results = [i for i in results if i.date >= date_from]

        if date_to:
            results = [i for i in results if i.date <= date_to]

        if query:
            query_lower = query.lower()
            results = [
                i for i in results
                if query_lower in i.location.lower()
                or query_lower in i.incident_type.lower()
                or query_lower in i.outcome.lower()
                or any(query_lower in lesson.lower() for lesson in i.lessons_learned)
            ]

        # Sort by date (most recent first)
        results.sort(key=lambda x: x.date, reverse=True)

        return results[:limit]

    def get_incident_by_id(self, incident_id: str) -> Optional[HistoricalIncident]:
        """
        Get a specific historical incident by ID.

        Args:
            incident_id: Incident ID

        Returns:
            HistoricalIncident if found, None otherwise
        """
        return self.incidents.get(incident_id)

    def add_incident(self, incident: HistoricalIncident) -> bool:
        """
        Add a new historical incident to the database.

        Args:
            incident: HistoricalIncident to add

        Returns:
            True if added successfully
        """
        if incident.id in self.incidents:
            logger.warning(f"Incident {incident.id} already exists")
            return False

        self.incidents[incident.id] = incident
        logger.info(f"Added incident {incident.id}: {incident.incident_type}")
        return True

    def get_lessons_for_emergency_type(self, emergency_type: str) -> dict:
        """
        Get aggregated lessons learned for a specific emergency type.

        Args:
            emergency_type: Type of emergency

        Returns:
            Dictionary with lessons and recommendations
        """
        incidents = self.search_historical_incidents(
            incident_type=emergency_type,
            limit=100
        )

        all_lessons = []
        all_recommendations = []

        for incident in incidents:
            all_lessons.extend(incident.lessons_learned)
            all_recommendations.extend(incident.recommendations)

        # Deduplicate while preserving order
        unique_lessons = list(dict.fromkeys(all_lessons))
        unique_recommendations = list(dict.fromkeys(all_recommendations))

        return {
            "emergency_type": emergency_type,
            "incidents_analyzed": len(incidents),
            "lessons_learned": unique_lessons,
            "recommendations": unique_recommendations,
            "average_response_time_hours": (
                sum(i.response_time_hours for i in incidents) / len(incidents)
                if incidents else 0
            ),
            "severity_range": {
                "min": min((i.severity for i in incidents), default=0),
                "max": max((i.severity for i in incidents), default=0),
            },
        }

    def get_statistics(self) -> dict:
        """Get statistics about historical incidents."""
        incidents = list(self.incidents.values())

        if not incidents:
            return {"total_incidents": 0}

        types_count = {}
        for incident in incidents:
            types_count[incident.incident_type] = types_count.get(incident.incident_type, 0) + 1

        return {
            "total_incidents": len(incidents),
            "by_type": types_count,
            "date_range": {
                "earliest": min(i.date for i in incidents).isoformat(),
                "latest": max(i.date for i in incidents).isoformat(),
            },
            "severity_distribution": {
                str(i): len([inc for inc in incidents if inc.severity == i])
                for i in range(1, 6)
            },
            "total_affected_population": sum(i.affected_population for i in incidents),
        }
