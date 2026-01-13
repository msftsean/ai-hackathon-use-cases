#!/usr/bin/env python3
"""
Demo script for Constituent Services Agent.

Demonstrates basic Q&A functionality in mock mode without requiring Azure services.
Run with: python demo.py
"""

import asyncio
import os
import sys

# Ensure mock mode
os.environ["USE_MOCK_SERVICES"] = "true"

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent import ConstituentAgent, MockFoundryIQKnowledgeBase


def print_header():
    """Print demo header."""
    print("\n" + "=" * 70)
    print("  NY State Constituent Services Agent - Demo")
    print("  Mode: MOCK (no Azure services required)")
    print("=" * 70 + "\n")


def print_section(title: str):
    """Print section divider."""
    print("\n" + "-" * 50)
    print(f"  {title}")
    print("-" * 50 + "\n")


async def demo_basic_query():
    """Demonstrate basic Q&A functionality."""
    print_section("Demo 1: Basic SNAP Benefits Query")

    # Initialize agent with mock knowledge base
    kb = MockFoundryIQKnowledgeBase()
    agent = ConstituentAgent(knowledge_base=kb)

    query = "How do I apply for SNAP benefits?"
    print(f"User: {query}\n")

    result = await agent.process_query(query)

    print(f"Agent: {result.response}\n")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Processing time: {result.processing_time_ms}ms")

    if result.citations:
        print(f"\nCitations ({len(result.citations)}):")
        for i, cite in enumerate(result.citations, 1):
            print(f"  [{i}] {cite.title} ({cite.agency})")
            print(f"      {cite.url}")

    if result.disclaimer:
        print(f"\n⚠️  Disclaimer: {result.disclaimer}")


async def demo_dmv_query():
    """Demonstrate DMV services query."""
    print_section("Demo 2: DMV License Renewal Query")

    kb = MockFoundryIQKnowledgeBase()
    agent = ConstituentAgent(knowledge_base=kb)

    query = "How do I renew my driver's license?"
    print(f"User: {query}\n")

    result = await agent.process_query(query)

    print(f"Agent: {result.response}\n")
    print(f"Confidence: {result.confidence:.1%}")

    if result.citations:
        print(f"\nCitations ({len(result.citations)}):")
        for i, cite in enumerate(result.citations, 1):
            print(f"  [{i}] {cite.title} ({cite.agency})")


async def demo_low_confidence():
    """Demonstrate low confidence response with escalation offer."""
    print_section("Demo 3: Low Confidence Query (Escalation)")

    kb = MockFoundryIQKnowledgeBase()
    agent = ConstituentAgent(knowledge_base=kb, confidence_threshold=0.5)

    query = "What is the status of my unemployment claim?"
    print(f"User: {query}\n")

    result = await agent.process_query(query)

    print(f"Agent: {result.response}\n")
    print(f"Confidence: {result.confidence:.1%}")

    if result.should_escalate:
        print("\n🔔 Agent suggests escalation to human agent")

    if result.suggested_actions:
        print("\nSuggested Actions:")
        for action in result.suggested_actions:
            print(f"  - {action['label']} ({action['type']})")


async def demo_eligibility_query():
    """Demonstrate eligibility query with disclaimer."""
    print_section("Demo 4: Benefits Eligibility Query")

    kb = MockFoundryIQKnowledgeBase()
    agent = ConstituentAgent(knowledge_base=kb)

    query = "Am I eligible for Medicaid?"
    print(f"User: {query}\n")

    result = await agent.process_query(query)

    print(f"Agent: {result.response}\n")
    print(f"Confidence: {result.confidence:.1%}")

    if result.disclaimer:
        print(f"\n⚠️  Disclaimer: {result.disclaimer}")


async def demo_interactive():
    """Interactive demo mode."""
    print_section("Interactive Demo")
    print("Type your questions below (or 'quit' to exit)\n")

    kb = MockFoundryIQKnowledgeBase()
    agent = ConstituentAgent(knowledge_base=kb)

    while True:
        try:
            query = input("You: ").strip()
            if not query:
                continue
            if query.lower() in ("quit", "exit", "q"):
                print("\nGoodbye!")
                break

            result = await agent.process_query(query)

            print(f"\nAgent: {result.response}")
            print(f"\n[Confidence: {result.confidence:.1%}]")

            if result.citations:
                print(f"[Sources: {', '.join(c.agency for c in result.citations)}]")

            if result.should_escalate:
                print("[💡 Consider talking to a human agent for more help]")

            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


async def main():
    """Run all demos."""
    print_header()

    # Run automated demos
    await demo_basic_query()
    await demo_dmv_query()
    await demo_low_confidence()
    await demo_eligibility_query()

    # Offer interactive mode
    print("\n" + "=" * 70)
    response = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
    if response in ("y", "yes"):
        await demo_interactive()

    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("  To run the web interface: python -m src.main")
    print("  Then open http://localhost:5000 in your browser")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
