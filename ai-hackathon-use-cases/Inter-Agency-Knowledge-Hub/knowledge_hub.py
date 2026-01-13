"""Inter-Agency Knowledge Hub using Foundry IQ"""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from typing import Optional


class InterAgencyKnowledgeHub:
    """Cross-agency document search with permission-aware responses"""

    AGENCIES = {
        "DMV": "Department of Motor Vehicles",
        "DOL": "Department of Labor",
        "OTDA": "Office of Temporary and Disability Assistance",
        "DOH": "Department of Health",
        "OGS": "Office of General Services"
    }

    def __init__(self, project_connection_string: str):
        self.client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=project_connection_string
        )

    def search(
        self,
        query: str,
        user_permissions: list[str],
        agencies: Optional[list[str]] = None,
        top_k: int = 10
    ) -> dict:
        """
        Search across agency knowledge bases with permission filtering

        Args:
            query: User search query
            user_permissions: List of agency codes user can access
            agencies: Optional filter to specific agencies
            top_k: Number of results to return
        """
        # Filter to permitted agencies
        target_agencies = agencies or list(self.AGENCIES.keys())
        permitted_agencies = [a for a in target_agencies if a in user_permissions]

        if not permitted_agencies:
            return {
                "results": [],
                "message": "You do not have permission to access any of the requested agencies."
            }

        agent = self.client.agents.create_agent(
            model="gpt-4o",
            name="inter-agency-knowledge-hub",
            instructions=f"""You are an inter-agency knowledge assistant for NY State.
            Search across these agencies: {', '.join(permitted_agencies)}
            Always cite your sources with agency and document references.
            If information spans multiple agencies, highlight the cross-references.
            Be accurate and helpful. If unsure, direct to official resources.""",
            tools=[{"type": "file_search"}]
        )

        thread = self.client.agents.create_thread()
        self.client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=f"Search for: {query}"
        )

        self.client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )

        messages = self.client.agents.list_messages(thread_id=thread.id)

        return {
            "query": query,
            "permitted_agencies": permitted_agencies,
            "answer": messages.data[0].content[0].text.value,
            "citations": self._extract_citations(messages),
            "cross_references": self._find_cross_references(messages)
        }

    def _extract_citations(self, messages) -> list:
        """Extract source citations with agency attribution"""
        citations = []
        for annotation in messages.data[0].content[0].text.annotations:
            if hasattr(annotation, 'file_citation'):
                citations.append({
                    "file_id": annotation.file_citation.file_id,
                    "quote": annotation.file_citation.quote,
                    "agency": self._detect_agency(annotation.file_citation.file_id)
                })
        return citations

    def _detect_agency(self, file_id: str) -> str:
        """Detect agency from file ID pattern"""
        file_id_upper = file_id.upper()
        for agency_code in self.AGENCIES:
            if agency_code in file_id_upper:
                return agency_code
        return "UNKNOWN"

    def _find_cross_references(self, messages) -> list:
        """Identify cross-agency references in the response"""
        cross_refs = []
        response_text = messages.data[0].content[0].text.value

        agencies_mentioned = []
        for agency_code, agency_name in self.AGENCIES.items():
            if agency_code in response_text or agency_name in response_text:
                agencies_mentioned.append(agency_code)

        if len(agencies_mentioned) > 1:
            cross_refs.append({
                "type": "multi_agency",
                "agencies": agencies_mentioned,
                "note": "Response references multiple agencies"
            })

        return cross_refs


class MockInterAgencyKnowledgeHub:
    """Mock implementation for offline development"""

    AGENCIES = {
        "DMV": "Department of Motor Vehicles",
        "DOL": "Department of Labor",
        "OTDA": "Office of Temporary and Disability Assistance",
        "DOH": "Department of Health",
        "OGS": "Office of General Services"
    }

    MOCK_KNOWLEDGE = {
        "DMV": {
            "license": "NY driver's licenses can be renewed online at dmv.ny.gov. You need your current license number and may need to pass a vision test.",
            "registration": "Vehicle registration can be renewed online or at any DMV office. You'll need your registration documents and proof of insurance."
        },
        "DOL": {
            "unemployment": "File for unemployment benefits at labor.ny.gov. You must have earned wages in NY and be actively seeking work.",
            "workers_comp": "Report workplace injuries to your employer immediately. File a claim with the Workers' Compensation Board within 2 years."
        },
        "OTDA": {
            "snap": "Apply for SNAP at myBenefits.ny.gov or at your local social services office. Eligibility is based on income and household size.",
            "medicaid": "Medicaid applications can be submitted through NY State of Health or your local social services office."
        },
        "DOH": {
            "vital_records": "Birth, death, and marriage certificates can be ordered from the DOH Vital Records office or online.",
            "immunization": "Immunization records are maintained by healthcare providers and can be accessed through the NY Immunization Information System."
        },
        "OGS": {
            "procurement": "State agencies must follow OGS procurement guidelines. Check the NYS Contract Reporter for current opportunities.",
            "facilities": "State facility requests should be submitted through OGS Building Services."
        }
    }

    def __init__(self, project_connection_string: str = None):
        pass

    def search(
        self,
        query: str,
        user_permissions: list[str],
        agencies: Optional[list[str]] = None,
        top_k: int = 10
    ) -> dict:
        """Mock search with permission filtering"""
        target_agencies = agencies or list(self.AGENCIES.keys())
        permitted_agencies = [a for a in target_agencies if a in user_permissions]

        if not permitted_agencies:
            return {
                "results": [],
                "message": "You do not have permission to access any of the requested agencies."
            }

        # Find relevant content
        results = []
        query_lower = query.lower()

        for agency in permitted_agencies:
            agency_content = self.MOCK_KNOWLEDGE.get(agency, {})
            for topic, content in agency_content.items():
                if topic in query_lower or any(word in content.lower() for word in query_lower.split()):
                    results.append({
                        "agency": agency,
                        "topic": topic,
                        "content": content
                    })

        # Build response
        if results:
            answer = "\n\n".join([
                f"**{r['agency']} - {r['topic'].title()}**: {r['content']}"
                for r in results[:top_k]
            ])
            citations = [
                {"file_id": f"{r['agency']}-{r['topic']}-guide", "quote": r['content'][:100], "agency": r['agency']}
                for r in results[:top_k]
            ]
        else:
            answer = "No specific results found. Please try a different search query or contact the relevant agency directly."
            citations = []

        # Check for cross-references
        agencies_in_results = list(set(r['agency'] for r in results))
        cross_references = []
        if len(agencies_in_results) > 1:
            cross_references.append({
                "type": "multi_agency",
                "agencies": agencies_in_results,
                "note": "Response references multiple agencies"
            })

        return {
            "query": query,
            "permitted_agencies": permitted_agencies,
            "answer": answer,
            "citations": citations,
            "cross_references": cross_references
        }
