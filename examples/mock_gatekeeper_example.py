"""
Mock Gatekeeper Example

Demonstrates how to create and register mock gatekeepers
for testing and development.

Author: AI Research Team
Date: November 2025
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator.master_orchestrator import MasterOrchestrator, WorkflowRequest, WorkflowType
from interfaces.gatekeeper_interface import (
    BaseGatekeeper,
    GatekeeperResult,
    GatekeeperStatus,
    QualityMetrics
)
from utils.logger import get_logger


class MockResearchGatekeeper(BaseGatekeeper):
    """Mock research gatekeeper for demonstration."""

    def process(self, input_data: Dict[str, Any]) -> GatekeeperResult:
        """Process research request."""
        topic = input_data.get("topic", "Unknown")

        self.logger.info(f"Mock Research: Processing topic '{topic}'")

        # Simulate research output
        output = {
            "topic": topic,
            "research_summary": f"Mock research findings about {topic}",
            "papers_analyzed": 50,
            "key_insights": [
                f"Insight 1 about {topic}",
                f"Insight 2 about {topic}",
                f"Insight 3 about {topic}"
            ],
            "citations": ["Source 1", "Source 2", "Source 3"]
        }

        # Create quality metrics
        quality_metrics = QualityMetrics(
            overall_score=8.5,
            criterion_scores={
                "academic_rigor": 8.5,
                "source_diversity": 9.0,
                "novelty": 8.0
            },
            strengths=["Comprehensive coverage", "High-quality sources"],
            weaknesses=["Could include more recent papers"],
            recommendations=["Add 2024-2025 papers"],
            passes_threshold=True,
            threshold_value=8.0
        )

        return GatekeeperResult(
            status=GatekeeperStatus.COMPLETED,
            output=output,
            quality_metrics=quality_metrics
        )

    def validate_quality(self, output: Dict[str, Any]) -> QualityMetrics:
        """Validate output quality."""
        return QualityMetrics(
            overall_score=8.5,
            passes_threshold=True,
            threshold_value=8.0
        )

    def iterate(
        self,
        previous_output: Dict[str, Any],
        quality_metrics: QualityMetrics
    ) -> GatekeeperResult:
        """Improve output."""
        self.logger.info("Mock Research: Iterating to improve quality")
        # Return improved version
        return self.process({"topic": previous_output.get("topic", "Unknown")})


class MockViralGatekeeper(BaseGatekeeper):
    """Mock viral analyser gatekeeper for demonstration."""

    def process(self, input_data: Dict[str, Any]) -> GatekeeperResult:
        """Process viral analysis request."""
        topic = input_data.get("topic", "Unknown")

        self.logger.info(f"Mock Viral Analysis: Creating strategy for '{topic}'")

        output = {
            "topic": topic,
            "hooks": [
                f"Hook 1: What if I told you {topic} could change everything?",
                f"Hook 2: The shocking truth about {topic}",
                f"Hook 3: Why experts are terrified of {topic}"
            ],
            "psychology_triggers": [
                "curiosity_gap",
                "social_proof",
                "authority",
                "novelty"
            ],
            "viral_score": 9.2,
            "retention_strategy": "Place hooks at 0s, 2min, 4min, 6min"
        }

        quality_metrics = QualityMetrics(
            overall_score=9.2,
            criterion_scores={
                "hook_quality": 9.5,
                "trigger_effectiveness": 9.0,
                "viral_potential": 9.2
            },
            strengths=["Strong hooks", "Multiple psychology triggers"],
            weaknesses=["Could add more variety"],
            recommendations=["Test A/B variations"],
            passes_threshold=True,
            threshold_value=9.0
        )

        return GatekeeperResult(
            status=GatekeeperStatus.COMPLETED,
            output=output,
            quality_metrics=quality_metrics
        )

    def validate_quality(self, output: Dict[str, Any]) -> QualityMetrics:
        """Validate quality."""
        return QualityMetrics(
            overall_score=9.2,
            passes_threshold=True,
            threshold_value=9.0
        )

    def iterate(
        self,
        previous_output: Dict[str, Any],
        quality_metrics: QualityMetrics
    ) -> GatekeeperResult:
        """Improve output."""
        return self.process({"topic": previous_output.get("topic", "Unknown")})


class MockContentGatekeeper(BaseGatekeeper):
    """Mock content synthesis gatekeeper for demonstration."""

    def process(self, input_data: Dict[str, Any]) -> GatekeeperResult:
        """Process content generation request."""
        research = input_data.get("research", {})
        viral_strategy = input_data.get("viral_strategy", {})

        topic = research.get("topic", "Unknown")

        self.logger.info(f"Mock Content: Generating script for '{topic}'")

        output = {
            "script": f"[OPENING HOOK]\n{viral_strategy.get('hooks', [''])[0]}\n\n"
                     f"[INTRODUCTION]\nWelcome to our deep dive into {topic}...\n\n"
                     f"[MAIN CONTENT]\n{research.get('research_summary', '')}\n\n"
                     f"[CONCLUSION]\nThat's our exploration of {topic}!",
            "scenes": [
                {"time": "0:00", "description": "Opening hook with dramatic visuals"},
                {"time": "0:15", "description": "Introduction with presenter"},
                {"time": "1:00", "description": "Main content with infographics"}
            ],
            "production_notes": {
                "duration": "15 minutes",
                "b_roll_needed": ["Stock footage", "Animations"],
                "music_style": "Dramatic orchestral"
            },
            "word_count": 2500
        }

        quality_metrics = QualityMetrics(
            overall_score=9.3,
            criterion_scores={
                "script_quality": 9.5,
                "visual_quality": 9.0,
                "production_feasibility": 9.5
            },
            strengths=["Clear structure", "Engaging narrative"],
            weaknesses=["Could add more examples"],
            recommendations=["Include case studies"],
            passes_threshold=True,
            threshold_value=9.0
        )

        return GatekeeperResult(
            status=GatekeeperStatus.COMPLETED,
            output=output,
            quality_metrics=quality_metrics
        )

    def validate_quality(self, output: Dict[str, Any]) -> QualityMetrics:
        """Validate quality."""
        return QualityMetrics(
            overall_score=9.3,
            passes_threshold=True,
            threshold_value=9.0
        )

    def iterate(
        self,
        previous_output: Dict[str, Any],
        quality_metrics: QualityMetrics
    ) -> GatekeeperResult:
        """Improve output."""
        return self.process({})


def main():
    """Run mock gatekeeper example."""
    print("="*70)
    print("Master Orchestrator - Mock Gatekeeper Example")
    print("="*70)

    # Initialize orchestrator
    print("\n1. Initializing Master Orchestrator...")
    orchestrator = MasterOrchestrator()

    # Create mock gatekeepers
    print("\n2. Creating and registering mock gatekeepers...")
    logger = get_logger("mock_gatekeepers")

    research_gk = MockResearchGatekeeper({"max_iterations": 5}, logger)
    viral_gk = MockViralGatekeeper({"max_iterations": 5}, logger)
    content_gk = MockContentGatekeeper({"max_iterations": 5}, logger)

    # Register gatekeepers
    orchestrator.register_gatekeeper("research", research_gk)
    orchestrator.register_gatekeeper("viral", viral_gk)
    orchestrator.register_gatekeeper("content", content_gk)

    print("   ✓ Research Gatekeeper registered")
    print("   ✓ Viral Analyser Gatekeeper registered")
    print("   ✓ Content Synthesis Gatekeeper registered")

    # Execute full pipeline
    print("\n3. Executing full pipeline workflow...")
    print("   Topic: 'The Future of Artificial Intelligence'")

    request = WorkflowRequest(
        workflow_type=WorkflowType.FULL_PIPELINE,
        topic="The Future of Artificial Intelligence",
        parameters={
            "target_audience": "tech enthusiasts",
            "duration_minutes": 15
        }
    )

    result = orchestrator.execute_workflow(request)

    # Display results
    print("\n4. Workflow Results:")
    print(f"   Status: {result.status.value}")
    print(f"\n   Quality Metrics:")
    for stage, metrics in result.quality_metrics.items():
        print(f"     • {stage.capitalize()}: {metrics.overall_score}/10 "
              f"({'✓ PASS' if metrics.passes_threshold else '✗ FAIL'})")

    print(f"\n   Iteration History:")
    for item in result.iteration_history:
        print(f"     • {item['stage']}: {item['iterations']} iteration(s), "
              f"quality: {item['quality']}/10")

    print(f"\n   Outputs Generated:")
    for key in result.outputs.keys():
        print(f"     • {key}")

    # Show sample output
    print("\n5. Sample Output (Research):")
    research_output = result.outputs.get("research", {})
    print(f"   Topic: {research_output.get('topic')}")
    print(f"   Papers Analyzed: {research_output.get('papers_analyzed')}")
    print(f"   Key Insights:")
    for insight in research_output.get("key_insights", [])[:2]:
        print(f"     • {insight}")

    print("\n" + "="*70)
    print("Example completed successfully!")
    print("="*70)
    print("\nOutputs saved to: outputs/")
    print("Logs saved to: logs/")


if __name__ == "__main__":
    main()
