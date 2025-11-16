#!/usr/bin/env python3
"""
Master Orchestrator - Main Entry Point

This is the main entry point for the Master Orchestrator system.
Provides CLI interface and interactive chat mode.

Author: AI Research Team
Date: November 2025
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
import argparse
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator.master_orchestrator import MasterOrchestrator, WorkflowRequest, WorkflowType
from src.orchestrator.chat_interface import ChatInterface
from src.config.config_manager import get_config
from src.utils.logger import LoggerFactory, get_logger
from src.utils.anthropic_client import AnthropicIntelligence


def setup_environment():
    """Setup environment and verify configuration."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  ERROR: ANTHROPIC_API_KEY not found!")
        print("\nPlease set your Anthropic API key:")
        print("  1. Copy .env.template to .env")
        print("  2. Edit .env and add your API key")
        print("  3. Or export it: export ANTHROPIC_API_KEY=your_key_here\n")
        sys.exit(1)

    return api_key


def print_banner():
    """Print system banner."""
    banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║              🎯 MASTER ORCHESTRATOR SYSTEM v1.0.0 🎯              ║
║                                                                    ║
║         Viral YouTube Synthesis - Central Coordination            ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def interactive_mode():
    """Run interactive chat mode."""
    api_key = setup_environment()
    print_banner()

    print("Initializing Master Orchestrator...")
    print("-" * 70)

    # Setup logging
    config = get_config()
    LoggerFactory.configure(
        log_dir=config.system.logs_dir,
        log_level=config.system.log_level
    )

    # Initialize orchestrator
    orchestrator = MasterOrchestrator()

    # Initialize chat interface
    ai = AnthropicIntelligence(api_key=api_key)
    chat = ChatInterface(ai)

    # Start session
    session = chat.start_session()

    print("\n✓ System initialized successfully!")
    print("-" * 70)
    print(session.messages[0].content)
    print("-" * 70)
    print("\nℹ️  Commands:")
    print("  - Type your request naturally")
    print("  - Type 'status' to see system status")
    print("  - Type 'exit' or 'quit' to exit")
    print("  - Type 'help' for assistance")
    print("-" * 70)

    # Interactive loop
    while True:
        try:
            user_input = input("\n🎯 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Shutting down Master Orchestrator...")
                print("   Total requests processed:", orchestrator.total_requests_processed)
                print("   Goodbye!\n")
                break

            if user_input.lower() == 'status':
                status = orchestrator.get_system_status()
                print("\n📊 System Status:")
                print(f"   • Total Requests: {status['total_requests']}")
                print(f"   • Active Workflows: {status['active_workflows']}")
                print(f"   • Completed Workflows: {status['completed_workflows']}")
                print(f"   • Registered Gatekeepers:")
                for name, registered in status['registered_gatekeepers'].items():
                    symbol = "✓" if registered else "✗"
                    print(f"     {symbol} {name.capitalize()}")
                print(f"   • Vector DB Items: {status['vector_db_stats'].get('total_strategies', 0)}")
                print(f"   • AI Tokens Used: {status['ai_token_usage'].get('total_tokens', 0):,}")
                continue

            # Process message
            print("\n🤖 Assistant: ", end="", flush=True)
            response = chat.process_message(user_input)

            print(response['message'])

            # Show action if not just help/explain
            if response['action'] not in ['help', 'explain', 'clarify']:
                print(f"\n   Action: {response['action']}")

                if response.get('parameters'):
                    print("   Parameters:")
                    for key, value in response['parameters'].items():
                        print(f"     • {key}: {value}")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Shutting down...\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("   Please try again or type 'help' for assistance.\n")


def execute_workflow_from_args(args):
    """Execute workflow from command line arguments."""
    api_key = setup_environment()
    print_banner()

    print("Initializing Master Orchestrator...")
    orchestrator = MasterOrchestrator()
    print("✓ System initialized\n")

    # Determine workflow type
    if args.workflow == "full":
        workflow_type = WorkflowType.FULL_PIPELINE
    elif args.workflow == "research":
        workflow_type = WorkflowType.RESEARCH_ONLY
    elif args.workflow == "viral":
        workflow_type = WorkflowType.VIRAL_ANALYSIS
    elif args.workflow == "content":
        workflow_type = WorkflowType.CONTENT_GENERATION
    else:
        print(f"❌ Unknown workflow type: {args.workflow}")
        sys.exit(1)

    # Check if gatekeepers are registered
    status = orchestrator.get_system_status()
    registered = status['registered_gatekeepers']

    if workflow_type == WorkflowType.FULL_PIPELINE:
        if not all(registered.values()):
            print("⚠️  WARNING: Not all gatekeepers are registered!")
            print("   Registered gatekeepers:")
            for name, reg in registered.items():
                print(f"     {'✓' if reg else '✗'} {name}")
            print("\n   You need to register gatekeepers before running workflows.")
            print("   See examples/mock_gatekeeper_example.py for how to do this.\n")
            sys.exit(1)

    # Create request
    request = WorkflowRequest(
        workflow_type=workflow_type,
        topic=args.topic,
        parameters={
            "target_audience": args.audience or "general audience",
            "duration_minutes": args.duration or 15
        }
    )

    print(f"Executing workflow: {workflow_type.value}")
    print(f"Topic: {args.topic}")
    print(f"Audience: {request.parameters['target_audience']}")
    print(f"Duration: {request.parameters['duration_minutes']} minutes")
    print("-" * 70)

    # Execute workflow
    try:
        result = orchestrator.execute_workflow(request)

        print(f"\n✓ Workflow completed!")
        print(f"   Status: {result.status.value}")

        if result.quality_metrics:
            print(f"\n   Quality Metrics:")
            for stage, metrics in result.quality_metrics.items():
                symbol = "✓" if metrics.passes_threshold else "✗"
                print(f"     {symbol} {stage}: {metrics.overall_score}/10")

        if result.outputs:
            print(f"\n   Outputs generated:")
            for key in result.outputs.keys():
                print(f"     • {key}")

        print(f"\n   Check outputs/ directory for detailed results")

    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")
        sys.exit(1)


def show_status():
    """Show system status."""
    setup_environment()
    print_banner()

    orchestrator = MasterOrchestrator()

    status = orchestrator.get_system_status()

    print("📊 SYSTEM STATUS")
    print("=" * 70)
    print(f"\nInitialized: {status['initialized']}")
    print(f"Total Requests Processed: {status['total_requests']}")
    print(f"Active Workflows: {status['active_workflows']}")
    print(f"Completed Workflows: {status['completed_workflows']}")

    print(f"\n🔧 Configuration:")
    print(f"   • Modular Mode: {status['config']['modular_mode']}")
    print(f"   • Learning Enabled: {status['config']['learning_enabled']}")
    print(f"   • Log Level: {status['config']['log_level']}")

    print(f"\n🎯 Registered Gatekeepers:")
    for name, registered in status['registered_gatekeepers'].items():
        symbol = "✓" if registered else "✗"
        status_text = "Registered" if registered else "Not Registered"
        print(f"   {symbol} {name.capitalize()}: {status_text}")

    print(f"\n📊 Vector Database:")
    db_stats = status['vector_db_stats']
    print(f"   • Total Strategies: {db_stats.get('total_strategies', 0)}")
    print(f"   • Total Patterns: {db_stats.get('total_patterns', 0)}")
    if 'tier_distribution' in db_stats and db_stats['tier_distribution']:
        print(f"   • Tier Distribution:")
        for tier, count in db_stats['tier_distribution'].items():
            print(f"     - {tier}: {count}")

    print(f"\n🤖 AI Usage:")
    ai_usage = status['ai_token_usage']
    print(f"   • Total Tokens: {ai_usage.get('total_tokens', 0):,}")
    print(f"   • Estimated Cost: ${ai_usage.get('estimated_cost_usd', 0):.4f}")

    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Master Orchestrator - Viral YouTube Synthesis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chat mode
  python main.py --interactive

  # Execute full pipeline
  python main.py --workflow full --topic "AI Ethics" --audience "academics"

  # Research only
  python main.py --workflow research --topic "Quantum Computing"

  # Show system status
  python main.py --status

For more information, see MASTER_ORCHESTRATOR_README.md
        """
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive chat mode"
    )

    parser.add_argument(
        "--workflow", "-w",
        choices=["full", "research", "viral", "content"],
        help="Workflow type to execute"
    )

    parser.add_argument(
        "--topic", "-t",
        help="Topic for the workflow"
    )

    parser.add_argument(
        "--audience", "-a",
        help="Target audience"
    )

    parser.add_argument(
        "--duration", "-d",
        type=int,
        help="Video duration in minutes"
    )

    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Show system status"
    )

    args = parser.parse_args()

    # Determine mode
    if args.status:
        show_status()
    elif args.interactive:
        interactive_mode()
    elif args.workflow:
        if not args.topic:
            print("❌ Error: --topic is required for workflow execution")
            sys.exit(1)
        execute_workflow_from_args(args)
    else:
        # Default to interactive mode
        print("No mode specified. Starting interactive mode...")
        print("(Use --help to see all options)\n")
        interactive_mode()


if __name__ == "__main__":
    main()
