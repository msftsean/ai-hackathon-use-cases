"""Foundry IQ client for agentic RAG"""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


class FoundryIQKnowledgeBase:
    """Wrapper for Foundry IQ knowledge retrieval"""

    def __init__(self, project_connection_string: str):
        self.client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=project_connection_string
        )

    def query(self, question: str, top_k: int = 5) -> dict:
        """
        Agentic retrieval using Foundry IQ
        - Multi-hop reasoning across documents
        - Citation tracking for government compliance
        """
        agent = self.client.agents.create_agent(
            model="gpt-4o",
            name="constituent-services-agent",
            instructions="""You are a helpful NY State government assistant.
            Always cite your sources. Be accurate and helpful.
            If unsure, say so and direct to official resources.""",
            tools=[{"type": "file_search"}]  # Foundry IQ integration
        )

        thread = self.client.agents.create_thread()
        message = self.client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = self.client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )

        # Get response with citations
        messages = self.client.agents.list_messages(thread_id=thread.id)
        return {
            "answer": messages.data[0].content[0].text.value,
            "citations": self._extract_citations(messages)
        }

    def _extract_citations(self, messages) -> list:
        """Extract source citations for audit trail"""
        citations = []
        for annotation in messages.data[0].content[0].text.annotations:
            if hasattr(annotation, 'file_citation'):
                citations.append({
                    "file_id": annotation.file_citation.file_id,
                    "quote": annotation.file_citation.quote
                })
        return citations


class MockFoundryIQKnowledgeBase:
    """Mock implementation for offline development"""

    def __init__(self, project_connection_string: str = None):
        self.knowledge_base = {
            "snap": {
                "answer": "To apply for SNAP benefits in New York State, you can: 1) Apply online at myBenefits.ny.gov, 2) Visit your local Department of Social Services office, or 3) Call the OTDA Helpline at 1-800-342-3009.",
                "citations": [{"file_id": "snap-guide-2024", "quote": "SNAP applications can be submitted online, in person, or by phone."}]
            },
            "dmv": {
                "answer": "To renew your NY driver's license, you can: 1) Renew online at dmv.ny.gov if eligible, 2) Visit a DMV office with your current license, 3) Renew by mail using form MV-44.",
                "citations": [{"file_id": "dmv-renewal-guide", "quote": "License renewals can be completed online, by mail, or in person."}]
            },
            "unemployment": {
                "answer": "To file for unemployment in NY: 1) Visit labor.ny.gov and create an NY.gov account, 2) File your claim online during your designated day, 3) Certify for benefits weekly.",
                "citations": [{"file_id": "dol-unemployment-guide", "quote": "Unemployment claims must be filed online through the NY.gov portal."}]
            }
        }

    def query(self, question: str, top_k: int = 5) -> dict:
        """Mock query that returns pre-defined responses"""
        question_lower = question.lower()

        if "snap" in question_lower or "food" in question_lower:
            return self.knowledge_base["snap"]
        elif "license" in question_lower or "dmv" in question_lower:
            return self.knowledge_base["dmv"]
        elif "unemployment" in question_lower or "job" in question_lower:
            return self.knowledge_base["unemployment"]
        else:
            return {
                "answer": "I can help you with NY State government services including SNAP benefits, DMV services, and unemployment assistance. What would you like to know?",
                "citations": []
            }
