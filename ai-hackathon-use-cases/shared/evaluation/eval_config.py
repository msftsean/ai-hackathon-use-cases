"""Azure AI Evaluation configuration for NY State hackathon"""
from azure.ai.evaluation import (
    evaluate,
    ContentSafetyEvaluator,
    GroundednessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator
)


class HackathonEvaluator:
    """Responsible AI evaluation suite for government use cases"""

    def __init__(self, azure_ai_project: dict):
        self.project = azure_ai_project
        self.evaluators = {
            "safety": ContentSafetyEvaluator(azure_ai_project=azure_ai_project),
            "groundedness": GroundednessEvaluator(model_config=azure_ai_project),
            "relevance": RelevanceEvaluator(model_config=azure_ai_project),
            "coherence": CoherenceEvaluator(model_config=azure_ai_project),
            "fluency": FluencyEvaluator(model_config=azure_ai_project)
        }

    def evaluate_response(self, query: str, response: str, context: str = None):
        """Evaluate a single response for responsible AI compliance"""
        data = {
            "query": query,
            "response": response,
            "context": context or ""
        }
        return evaluate(data=data, evaluators=self.evaluators)

    def batch_evaluate(self, test_file: str):
        """Evaluate batch of test cases from JSONL file"""
        return evaluate(data=test_file, evaluators=self.evaluators)


def create_evaluator(
    subscription_id: str,
    resource_group: str,
    project_name: str
) -> HackathonEvaluator:
    """Factory function to create a HackathonEvaluator with Azure AI project config"""
    azure_ai_project = {
        "subscription_id": subscription_id,
        "resource_group_name": resource_group,
        "project_name": project_name
    }
    return HackathonEvaluator(azure_ai_project)


if __name__ == "__main__":
    # Example usage with mock data
    print("Azure AI Evaluation Framework for NY State Hackathon")
    print("=" * 50)
    print("\nTo use this evaluator, set up your Azure AI project:")
    print("""
    from eval_config import create_evaluator

    evaluator = create_evaluator(
        subscription_id="your-subscription-id",
        resource_group="your-resource-group",
        project_name="your-project-name"
    )

    results = evaluator.evaluate_response(
        query="How do I apply for SNAP benefits?",
        response="To apply for SNAP benefits in NY State...",
        context="Official SNAP documentation..."
    )
    """)
