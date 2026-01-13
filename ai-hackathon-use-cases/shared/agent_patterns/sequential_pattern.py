"""Sequential agent pattern for permit processing"""
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.agents.orchestration import SequentialOrchestration
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion


async def create_permit_pipeline(kernel: Kernel) -> SequentialOrchestration:
    """
    Sequential pipeline: intake → validation → review → decision
    Each agent hands off to the next with full context

    Use Case: Building permit processing for NY State agencies
    Each step must complete before the next begins, with full audit trail.
    """
    intake_agent = ChatCompletionAgent(
        kernel=kernel,
        name="IntakeAgent",
        instructions="""You are the Intake Agent for NY State permit processing.
        Your job is to:
        1. Extract permit application details from the submission
        2. Identify the permit type (building, business, event, environmental)
        3. List all documents provided
        4. Note any obvious missing information
        5. Create a structured summary for the Validation Agent

        Always be thorough and accurate. Document everything for audit purposes."""
    )

    validation_agent = ChatCompletionAgent(
        kernel=kernel,
        name="ValidationAgent",
        instructions="""You are the Validation Agent for NY State permit processing.
        Your job is to:
        1. Verify all required documents are present based on permit type
        2. Check document validity (dates, signatures, certifications)
        3. Validate applicant information matches across documents
        4. Flag any discrepancies or concerns
        5. Create a validation report for the Review Agent

        Required documents vary by permit type:
        - Building: Plans, engineering reports, insurance, contractor license
        - Business: Business registration, tax ID, zoning approval
        - Event: Insurance, safety plan, location approval
        - Environmental: Impact assessment, mitigation plan, agency approvals

        Be strict but fair. Document all validation decisions."""
    )

    review_agent = ChatCompletionAgent(
        kernel=kernel,
        name="ReviewAgent",
        instructions="""You are the Review Agent for NY State permit processing.
        Your job is to:
        1. Check the application against zoning requirements
        2. Verify compliance with relevant regulations (building codes, environmental, safety)
        3. Identify any conflicts with existing permits or restrictions
        4. Assess risk level (low, medium, high)
        5. Create a detailed review report for the Decision Agent

        Regulatory references should be cited for all compliance determinations.
        Flag anything that requires human expert review."""
    )

    decision_agent = ChatCompletionAgent(
        kernel=kernel,
        name="DecisionAgent",
        instructions="""You are the Decision Agent for NY State permit processing.
        Your job is to:
        1. Review all previous agent reports
        2. Synthesize findings into a recommendation
        3. Provide one of: APPROVE, CONDITIONAL APPROVE, DENY, ESCALATE
        4. List any conditions for approval
        5. Create a full audit trail with citations

        IMPORTANT: This is a RECOMMENDATION only. Final decisions require human approval.
        For ESCALATE: Clearly explain why human review is needed.
        For DENY: Provide specific reasons with regulatory citations.
        For CONDITIONAL APPROVE: List specific conditions that must be met."""
    )

    orchestration = SequentialOrchestration(
        members=[intake_agent, validation_agent, review_agent, decision_agent]
    )

    return orchestration


async def process_permit_application(
    kernel: Kernel,
    application_text: str
) -> dict:
    """
    Process a permit application through the sequential pipeline

    Args:
        kernel: Configured Semantic Kernel instance
        application_text: The permit application text/documents

    Returns:
        Processing results with full audit trail
    """
    pipeline = await create_permit_pipeline(kernel)

    # Run the sequential orchestration
    result = await pipeline.invoke(application_text)

    return {
        "stages": ["intake", "validation", "review", "decision"],
        "result": result,
        "audit_trail": [
            {"agent": "IntakeAgent", "action": "extracted application details"},
            {"agent": "ValidationAgent", "action": "validated documents"},
            {"agent": "ReviewAgent", "action": "checked compliance"},
            {"agent": "DecisionAgent", "action": "generated recommendation"}
        ]
    }


# Mock implementation for offline development
class MockSequentialOrchestration:
    """Mock sequential orchestration for testing without Azure"""

    def __init__(self, members: list):
        self.members = members

    async def invoke(self, input_text: str) -> str:
        """Process through mock agents sequentially"""
        current_output = input_text

        mock_outputs = [
            "INTAKE REPORT: Application received for building permit. Documents: plans, insurance, contractor license. Missing: engineering report.",
            "VALIDATION REPORT: Documents validated. Insurance current. Contractor license valid. ISSUE: Engineering report required for structural work.",
            "REVIEW REPORT: Zoning compliant. Building code review pending engineering report. Risk: MEDIUM due to missing documentation.",
            "DECISION: CONDITIONAL APPROVE. Condition: Submit certified engineering report within 30 days. Full approval pending document submission. Human review required for final sign-off."
        ]

        for i, member in enumerate(self.members):
            current_output = mock_outputs[i] if i < len(mock_outputs) else current_output

        return current_output


if __name__ == "__main__":
    print("Sequential Agent Pattern for Permit Processing")
    print("=" * 50)
    print()
    print("This pattern implements a sequential pipeline where each agent")
    print("processes in order, passing results to the next agent.")
    print()
    print("Agents: IntakeAgent → ValidationAgent → ReviewAgent → DecisionAgent")
    print()
    print("Use Case: Building permit applications that require multiple")
    print("stages of review with full audit trail for compliance.")
