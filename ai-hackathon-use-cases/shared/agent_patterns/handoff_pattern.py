"""Handoff pattern for citizen inquiry routing"""
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.agents.orchestration import HandoffOrchestration


async def create_citizen_router(kernel: Kernel) -> HandoffOrchestration:
    """
    Dynamic routing: triage → specialist
    Routes based on inquiry type (benefits, permits, complaints, etc.)

    Use Case: NY State constituent services where different inquiries
    need to be routed to specialized agents based on topic.
    """
    triage_agent = ChatCompletionAgent(
        kernel=kernel,
        name="TriageAgent",
        instructions="""You are the Triage Agent for NY State citizen services.
        Your job is to:
        1. Understand the citizen's inquiry
        2. Classify it into one of these categories:
           - BENEFITS: SNAP, Medicaid, unemployment, disability assistance
           - PERMITS: building permits, business licenses, event permits
           - COMPLAINTS: service issues, feedback, accessibility concerns
           - GENERAL: all other inquiries
        3. Hand off to the appropriate specialist agent

        Be empathetic and efficient. Citizens should feel heard and helped.
        If an inquiry spans multiple categories, route to the primary concern first."""
    )

    benefits_agent = ChatCompletionAgent(
        kernel=kernel,
        name="BenefitsAgent",
        instructions="""You are the Benefits Specialist Agent for NY State.
        You handle inquiries about:
        - SNAP (food assistance)
        - Medicaid
        - Unemployment insurance
        - Disability assistance
        - Cash assistance (TANF)

        Provide accurate information about:
        - Eligibility requirements
        - Application processes
        - Required documents
        - Office locations and hours
        - Appeal processes

        Always cite official sources (myBenefits.ny.gov, labor.ny.gov).
        If you're unsure, direct citizens to the appropriate agency."""
    )

    permits_agent = ChatCompletionAgent(
        kernel=kernel,
        name="PermitsAgent",
        instructions="""You are the Permits Specialist Agent for NY State.
        You handle inquiries about:
        - Building permits
        - Business licenses
        - Event permits
        - Professional licenses
        - Vehicle registrations

        Provide accurate information about:
        - Permit types and requirements
        - Application processes
        - Fees and timelines
        - Required inspections
        - Renewal procedures

        Always cite official sources (dmv.ny.gov, dos.ny.gov).
        Complex permit questions should be referred to local agencies."""
    )

    complaints_agent = ChatCompletionAgent(
        kernel=kernel,
        name="ComplaintsAgent",
        instructions="""You are the Complaints Specialist Agent for NY State.
        You handle:
        - Service quality concerns
        - Accessibility issues
        - Wait time complaints
        - Staff conduct issues
        - General feedback

        Your approach:
        - Acknowledge the citizen's concern
        - Gather relevant details
        - Explain the complaint process
        - Provide expected timelines
        - Offer alternative solutions when possible

        All complaints are logged for quality improvement.
        Escalate serious issues to human supervisors."""
    )

    general_agent = ChatCompletionAgent(
        kernel=kernel,
        name="GeneralAgent",
        instructions="""You are the General Inquiry Agent for NY State.
        You handle questions that don't fit other categories:
        - State agency contact information
        - General government information
        - Website navigation help
        - Process explanations
        - Referrals to appropriate agencies

        Be helpful and patient. If you can't answer directly,
        provide the best resource or contact for assistance."""
    )

    # Create handoff orchestration with triage and specialists
    orchestration = HandoffOrchestration(
        triage=triage_agent,
        specialists={
            "benefits_agent": benefits_agent,
            "permits_agent": permits_agent,
            "complaints_agent": complaints_agent,
            "general_agent": general_agent
        }
    )

    return orchestration


async def route_citizen_inquiry(
    kernel: Kernel,
    inquiry: str,
    citizen_context: dict = None
) -> dict:
    """
    Route a citizen inquiry to the appropriate specialist

    Args:
        kernel: Configured Semantic Kernel instance
        inquiry: The citizen's question or concern
        citizen_context: Optional context (language preference, history, etc.)

    Returns:
        Response with routing information and specialist answer
    """
    router = await create_citizen_router(kernel)

    # Add context if provided
    full_inquiry = inquiry
    if citizen_context:
        context_str = f"Context: {citizen_context}\n\nInquiry: {inquiry}"
        full_inquiry = context_str

    result = await router.invoke(full_inquiry)

    return {
        "inquiry": inquiry,
        "routed_to": result.specialist_name,
        "response": result.response,
        "suggested_resources": result.resources if hasattr(result, 'resources') else []
    }


# Mock implementation for offline development
class MockHandoffOrchestration:
    """Mock handoff orchestration for testing without Azure"""

    CATEGORY_KEYWORDS = {
        "benefits_agent": ["snap", "medicaid", "unemployment", "benefits", "food", "assistance", "welfare"],
        "permits_agent": ["permit", "license", "registration", "dmv", "building", "business"],
        "complaints_agent": ["complaint", "problem", "issue", "feedback", "concern", "terrible", "bad"],
        "general_agent": []  # Default
    }

    MOCK_RESPONSES = {
        "benefits_agent": "I can help with benefits questions. For SNAP, visit myBenefits.ny.gov or call 1-800-342-3009. For unemployment, visit labor.ny.gov. What specific information do you need?",
        "permits_agent": "I can help with permits and licenses. For DMV services, visit dmv.ny.gov. For business licenses, contact your local government or visit dos.ny.gov. What type of permit are you looking for?",
        "complaints_agent": "I'm sorry to hear you're having an issue. Your feedback is important to us. Could you please describe the problem in detail so I can help resolve it or escalate to the appropriate department?",
        "general_agent": "I'm here to help with NY State government services. I can provide information about various agencies, programs, and processes. What would you like to know?"
    }

    def __init__(self, triage=None, specialists=None):
        pass

    async def invoke(self, inquiry: str) -> 'MockResult':
        """Route inquiry to appropriate mock specialist"""
        inquiry_lower = inquiry.lower()

        # Determine category based on keywords
        selected_agent = "general_agent"
        for agent, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in inquiry_lower for kw in keywords):
                selected_agent = agent
                break

        return MockResult(
            specialist_name=selected_agent,
            response=self.MOCK_RESPONSES[selected_agent]
        )


class MockResult:
    """Mock result object"""
    def __init__(self, specialist_name: str, response: str):
        self.specialist_name = specialist_name
        self.response = response


if __name__ == "__main__":
    print("Handoff Agent Pattern for Citizen Inquiry Routing")
    print("=" * 50)
    print()
    print("This pattern implements dynamic routing where a triage agent")
    print("classifies inquiries and hands off to specialist agents.")
    print()
    print("Agents:")
    print("  TriageAgent → classifies and routes")
    print("  ├── BenefitsAgent (SNAP, Medicaid, unemployment)")
    print("  ├── PermitsAgent (building, business, licenses)")
    print("  ├── ComplaintsAgent (service issues, feedback)")
    print("  └── GeneralAgent (all other inquiries)")
    print()
    print("Use Case: Constituent services where different topics")
    print("require specialized knowledge and responses.")
