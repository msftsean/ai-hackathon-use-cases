"""
Emergency Response Agent - Evaluation Configuration
Evaluates multi-agent coordination and recommendation quality
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.eval_base import HackathonEvaluator, EvalConfig, get_azure_ai_project


class EmergencyResponseEvaluator(HackathonEvaluator):
    """
    Extended evaluator for Emergency Response Agent.
    Focuses on recommendation safety and coordination accuracy.
    """
    
    PASS_THRESHOLDS = {
        "groundedness": 4.0,
        "relevance": 4.5,  # Critical for emergency response
        "coherence": 4.0,
        "fluency": 3.5
    }
    
    def evaluate_recommendation_safety(
        self, 
        test_case: dict, 
        recommendation: str
    ) -> dict:
        """
        Evaluate that recommendations prioritize safety.
        
        Args:
            test_case: Dict with scenario details
            recommendation: System's recommendation
        
        Returns:
            Dict with safety evaluation results
        """
        safety_violations = []
        
        # Check for required safety elements
        scenario_type = test_case.get("scenario_type", "")
        
        if scenario_type == "evacuation":
            required = ["shelter", "route", "timeline"]
            for req in required:
                if req.lower() not in recommendation.lower():
                    safety_violations.append(f"Missing {req} in evacuation recommendation")
        
        if scenario_type == "severe_weather":
            if "monitor" not in recommendation.lower() and "update" not in recommendation.lower():
                safety_violations.append("No mention of monitoring/updates for evolving situation")
        
        # Check for dangerous over-confidence
        uncertainty_markers = ["may", "could", "recommend", "suggest", "consider"]
        if not any(m in recommendation.lower() for m in uncertainty_markers):
            safety_violations.append("Recommendation lacks appropriate uncertainty language")
        
        return {
            "passed": len(safety_violations) == 0,
            "violations": safety_violations
        }
    
    def evaluate_resource_allocation(
        self, 
        test_case: dict, 
        allocation: dict
    ) -> dict:
        """
        Evaluate resource allocation reasonableness.
        
        Args:
            test_case: Dict with available resources and constraints
            allocation: Proposed resource allocation
        
        Returns:
            Dict with allocation evaluation
        """
        available = test_case.get("available_resources", {})
        constraints = test_case.get("constraints", {})
        
        issues = []
        
        # Check for over-allocation
        for resource_type, allocated in allocation.items():
            available_qty = available.get(resource_type, 0)
            if allocated > available_qty:
                issues.append(f"Over-allocated {resource_type}: {allocated} > {available_qty}")
        
        # Check constraint violations
        for constraint, limit in constraints.items():
            if constraint in allocation and allocation[constraint] > limit:
                issues.append(f"Constraint violated: {constraint} exceeds {limit}")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }


def run_evaluation(system_fn: callable = None):
    """Run full evaluation suite for Emergency Response Agent."""
    config = EvalConfig(
        use_case="emergency-response",
        azure_ai_project=get_azure_ai_project(),
        test_cases_path=str(Path(__file__).parent / "test_cases.jsonl")
    )
    
    evaluator = EmergencyResponseEvaluator(config)
    
    if system_fn is None:
        def mock_system(query):
            return (
                "Based on current weather data, I recommend pre-positioning resources. Consider activating shelters if conditions worsen.",
                "Weather advisory context..."
            )
        system_fn = mock_system
    
    return evaluator.run_batch_evaluation(system_fn)


if __name__ == "__main__":
    print("Running Emergency Response Agent Evaluation...")
    results = run_evaluation()
    print(f"\nPass Rate: {results['summary']['pass_rate']}")
