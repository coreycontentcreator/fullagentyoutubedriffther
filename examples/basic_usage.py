"""
Basic Usage Example - Master Orchestrator

This example demonstrates basic usage of the Master Orchestrator
for generating viral YouTube content.

Author: AI Research Team
Date: November 2025
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator.master_orchestrator import MasterOrchestrator, WorkflowRequest, WorkflowType
from config.config_manager import ConfigurationManager


def main():
    """Run basic orchestrator example."""
    print("="*70)
    print("Master Orchestrator - Basic Usage Example")
    print("="*70)

    # Initialize the orchestrator
    print("\n1. Initializing Master Orchestrator...")
    orchestrator = MasterOrchestrator()

    # Show system status
    print("\n2. System Status:")
    status = orchestrator.get_system_status()
    print(f"   - Initialized: {status['initialized']}")
    print(f"   - Modular Mode: {status['config']['modular_mode']}")
    print(f"   - Learning Enabled: {status['config']['learning_enabled']}")
    print(f"   - Registered Gatekeepers:")
    for name, registered in status['registered_gatekeepers'].items():
        print(f"     • {name.capitalize()}: {'✓' if registered else '✗ (not registered)'}")

    # Example 1: Chat interaction
    print("\n3. Chat Interaction Example:")
    print("   User: 'What can you do?'")
    response = orchestrator.process_chat_request("What can you do?")
    print(f"   Assistant: {response.get('response', '')[:200]}...")

    # Example 2: System help
    print("\n4. Getting Help:")
    print("   User: 'Help me get started'")
    response = orchestrator.process_chat_request("Help me get started")
    print(f"   Commands available: {len(response.get('commands', {}))}")

    # Note about gatekeeper registration
    print("\n" + "="*70)
    print("NOTE: To execute full workflows, you need to register gatekeepers:")
    print("="*70)
    print("""
# Example of registering gatekeepers (when implemented):

from research_gatekeeper import ResearchGatekeeper
from viral_analyser_gatekeeper import ViralAnalyserGatekeeper
from content_synthesis_gatekeeper import ContentSynthesisGatekeeper

# Create gatekeeper instances
research_gk = ResearchGatekeeper(config, logger)
viral_gk = ViralAnalyserGatekeeper(config, logger)
content_gk = ContentSynthesisGatekeeper(config, logger)

# Register with orchestrator
orchestrator.register_gatekeeper("research", research_gk)
orchestrator.register_gatekeeper("viral", viral_gk)
orchestrator.register_gatekeeper("content", content_gk)

# Now you can execute full workflows:
request = WorkflowRequest(
    workflow_type=WorkflowType.FULL_PIPELINE,
    topic="The Future of Artificial Intelligence",
    parameters={
        "target_audience": "tech enthusiasts",
        "duration_minutes": 20
    }
)

result = orchestrator.execute_workflow(request)
print(f"Workflow completed with quality: {result.quality_metrics}")
""")

    print("\n" + "="*70)
    print("Example completed!")
    print("="*70)


if __name__ == "__main__":
    main()
