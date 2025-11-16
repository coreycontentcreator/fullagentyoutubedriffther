"""
Viral Analysis System - Main Entry Point
World-class viral content analysis with Anthropic AI
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from chat.chat_interface import ChatInterface
from viral_analysis.viral_analyser_gatekeeper import ViralAnalyserGatekeeper
from config.config_manager import get_config_manager


def run_interactive_mode():
    """Run interactive chat interface"""
    chat = ChatInterface()
    chat.start()


def run_analysis(topic: str, duration: int = 15, audience: str = "general"):
    """Run single analysis from command line"""
    gatekeeper = ViralAnalyserGatekeeper()

    print(f"\n🎯 Running viral analysis for: {topic}\n")

    result = gatekeeper.analyze_content(
        topic=topic,
        target_audience=audience,
        video_duration_minutes=duration,
        content_type="documentary"
    )

    # Print summary
    print("\n" + "="*80)
    print("📊 ANALYSIS SUMMARY")
    print("="*80)
    print(f"\nTopic: {topic}")
    print(f"Viral Score: {result['viral_score']['overall_viral_score']}/10")
    print(f"Rating: {result['viral_score']['rating']}")
    print(f"Quality Gate: {result['quality_gate']['status']}")
    print(f"\nTop Hook:")
    print(f'   "{result["hooks"]["top_hooks"][0]["hook_text"]}"')
    print(f"\nProcessing Time: {result['metadata']['processing_time_seconds']}s")
    print("="*80 + "\n")


def show_system_info():
    """Show system information"""
    gatekeeper = ViralAnalyserGatekeeper()
    subagents = gatekeeper.get_available_subagents()

    print("\n" + "="*80)
    print("🎯 VIRAL ANALYSIS SYSTEM")
    print("="*80)
    print("\nWorld-class viral content analysis using:")
    print("  • Anthropic Claude AI")
    print("  • Brendan Kane Methodology")
    print("  • 16 Psychology Triggers")
    print("  • 8 Specialized Subagents")
    print("\n" + "-"*80)
    print("SPECIALIZED SUBAGENTS:")
    print("-"*80)

    for i, agent in enumerate(subagents, 1):
        print(f"\n{i}. {agent['name']}")
        print(f"   {agent['capability']}")
        print(f"   Output: {agent['output']}")

    print("\n" + "="*80)
    print("\nCapabilities:")
    print("  ✓ Viral analysis of any topic")
    print("  ✓ YouTube video analysis")
    print("  ✓ Hook generation (10+ variations)")
    print("  ✓ Psychology trigger implementation")
    print("  ✓ Retention optimization")
    print("  ✓ Engagement strategy design")
    print("  ✓ Viral score prediction (0-10)")
    print("  ✓ Strategy library management")
    print("\n" + "="*80 + "\n")


def validate_config():
    """Validate configuration"""
    config = get_config_manager()
    is_valid, errors = config.validate_config()

    print("\n" + "="*80)
    print("⚙️  CONFIGURATION VALIDATION")
    print("="*80)

    if is_valid:
        print("\n✅ Configuration is valid!")
        print(f"\nAPI Keys configured:")
        print(f"  • Anthropic: {'✓' if config.get_api_key('anthropic') else '✗'}")
        print(f"  • YouTube: {'✓' if config.get_api_key('youtube') else '✗'}")
        print(f"  • OpenAI: {'✓' if config.get_api_key('openai') else '✗'}")
    else:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"  • {error}")

    print("\n" + "="*80 + "\n")

    return is_valid


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Viral Analysis System - World-class viral content analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chat mode
  python main.py

  # Analyze a topic
  python main.py --analyze "The Future of AI" --duration 15 --audience "tech enthusiasts"

  # Show system info
  python main.py --info

  # Validate configuration
  python main.py --validate
        """
    )

    parser.add_argument(
        '--analyze',
        type=str,
        help='Analyze a topic for viral potential'
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=15,
        help='Video duration in minutes (default: 15)'
    )

    parser.add_argument(
        '--audience',
        type=str,
        default='general',
        help='Target audience (default: general)'
    )

    parser.add_argument(
        '--info',
        action='store_true',
        help='Show system information'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration'
    )

    args = parser.parse_args()

    # Handle commands
    if args.info:
        show_system_info()
        return

    if args.validate:
        validate_config()
        return

    if args.analyze:
        run_analysis(args.analyze, args.duration, args.audience)
        return

    # Default: run interactive mode
    run_interactive_mode()


if __name__ == "__main__":
    main()
