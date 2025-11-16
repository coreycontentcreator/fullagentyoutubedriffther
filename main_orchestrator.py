#!/usr/bin/env python3
"""
Modular Agentic System - Main Application with Master Orchestrator
World-class AI content generation system for macOS
"""

import os
import sys
import argparse
import logging
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.anthropic_client import AnthropicClient
from src.intelligence import IntelligenceLayer
from src.orchestrator import MasterOrchestrator, OrchestratorConfig


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / 'system.log')
        ]
    )


def check_api_key():
    """Check if API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key or api_key == 'your-anthropic-api-key-here':
        print("\n" + "="*70)
        print("  ❌ ANTHROPIC API KEY NOT CONFIGURED")
        print("="*70)
        print("\nThe Modular Agentic System requires an Anthropic API key.")
        print("\nTo configure:")
        print("\n1. Get your API key from: https://console.anthropic.com/")
        print("\n2. Edit .env file and set:")
        print("   ANTHROPIC_API_KEY=your-actual-api-key")
        print("\n" + "="*70 + "\n")
        return False

    return True


async def run_interactive_mode():
    """Run in interactive mode"""
    print("\n" + "="*70)
    print("  🚀 MODULAR AGENTIC SYSTEM - Interactive Mode")
    print("="*70)
    print("\nWorld-class AI content generation with 5 integrated modules:")
    print("  1. Research Gatekeeper - Multi-database research")
    print("  2. Viral Analyser - Psychology triggers & patterns")
    print("  3. Content Synthesis - Production-ready scripts")
    print("  4. Intelligence Layer - Advanced AI reasoning")
    print("  5. Database & Storage - Learning & optimization")
    print("\n" + "="*70 + "\n")

    # Get user input
    topic = input("Enter your topic: ").strip()
    if not topic:
        print("❌ Topic is required")
        return 1

    duration = input("Video duration in minutes (default: 15): ").strip()
    duration = int(duration) if duration.isdigit() else 15

    audience = input("Target audience (default: general audience): ").strip()
    audience = audience if audience else "general audience"

    print("\n" + "="*70)
    print("  📝 Generating Content...")
    print("="*70)
    print(f"\nTopic: {topic}")
    print(f"Duration: {duration} minutes")
    print(f"Audience: {audience}")
    print("\nThis will take 10-20 minutes. Please wait...\n")

    # Initialize system
    api_key = os.getenv('ANTHROPIC_API_KEY')
    anthropic_client = AnthropicClient(api_key=api_key)
    intelligence_layer = IntelligenceLayer(anthropic_client)

    config = OrchestratorConfig(
        enable_research=True,
        enable_viral_analysis=True,
        enable_content_synthesis=True,
        enable_learning=True,
        quality_threshold=9.0,
        max_iterations=3
    )

    orchestrator = MasterOrchestrator(intelligence_layer, config)

    try:
        # Generate content
        package = await orchestrator.generate_complete_content(
            topic=topic,
            target_audience=audience,
            video_duration=duration,
            style="documentary",
            tone="engaging"
        )

        # Display results
        print("\n" + "="*70)
        print("  ✅ CONTENT GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Overall Quality Score: {package.overall_score:.1f}/10")
        print(f"🔄 Iterations: {package.iteration_count}")
        print(f"⏱️  Total Time: {package.total_time:.1f}s")
        print(f"\n📝 Research Sources: {package.research_report.sources_count if hasattr(package.research_report, 'sources_count') else 'N/A'}")
        print(f"🎯 Viral Hooks Generated: {len(package.viral_strategy.hooks) if hasattr(package.viral_strategy, 'hooks') else 'N/A'}")
        print(f"📄 Script Length: {package.content_output.get('word_count', 'N/A')} words")

        # Save
        output_path = await orchestrator.save_package(package)
        print(f"\n💾 Saved to: {output_path}")

        print("\n" + "="*70 + "\n")

        # Ask if user wants to see details
        show_details = input("Show detailed results? (y/n): ").strip().lower()
        if show_details == 'y':
            print("\n" + "="*70)
            print("  DETAILED RESULTS")
            print("="*70)

            print("\n## Research Summary")
            print(orchestrator.research_gatekeeper.generate_summary(package.research_report))

            print("\n## Viral Strategy")
            print(orchestrator.viral_gatekeeper.generate_summary(package.viral_strategy))

            print("\n## Content Script")
            print(package.content_output.get('script', 'N/A')[:1000] + "...")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        logging.error(f"Generation failed: {e}", exc_info=True)
        return 1


async def run_cli_mode(args):
    """Run in CLI mode"""
    print("\n🚀 Starting content generation...\n")

    # Initialize system
    api_key = os.getenv('ANTHROPIC_API_KEY')
    anthropic_client = AnthropicClient(api_key=api_key)
    intelligence_layer = IntelligenceLayer(anthropic_client)

    config = OrchestratorConfig(
        enable_research=not args.skip_research,
        enable_viral_analysis=not args.skip_viral,
        enable_content_synthesis=True,
        enable_learning=not args.no_learning,
        quality_threshold=args.quality_threshold,
        max_iterations=args.max_iterations
    )

    orchestrator = MasterOrchestrator(intelligence_layer, config)

    try:
        package = await orchestrator.generate_complete_content(
            topic=args.topic,
            target_audience=args.audience,
            video_duration=args.duration,
            style=args.style,
            tone=args.tone
        )

        print("\n" + "="*70)
        print("  ✅ GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Quality Score: {package.overall_score:.1f}/10")
        print(f"⏱️  Time: {package.total_time:.1f}s")

        if args.output:
            output_path = await orchestrator.save_package(package, args.output)
            print(f"💾 Saved to: {output_path}")

        print("\n" + "="*70 + "\n")
        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        logging.error(f"Generation failed: {e}", exc_info=True)
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Modular Agentic System - World-class AI content generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  python main_orchestrator.py

  # CLI mode
  python main_orchestrator.py --topic "The Future of AI" --duration 15

  # Skip research phase (faster, lower quality)
  python main_orchestrator.py --topic "Climate Change" --skip-research

  # Custom quality threshold
  python main_orchestrator.py --topic "Space" --quality-threshold 8.5

For more information, visit ARCHITECTURE.md
        """
    )

    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--topic', type=str,
                       help='Content topic')
    parser.add_argument('--duration', type=int, default=15,
                       help='Video duration in minutes (default: 15)')
    parser.add_argument('--audience', type=str, default='general audience',
                       help='Target audience')
    parser.add_argument('--style', type=str, default='documentary',
                       choices=['documentary', 'educational', 'cinematic', 'casual'],
                       help='Visual style')
    parser.add_argument('--tone', type=str, default='engaging',
                       choices=['engaging', 'authoritative', 'casual', 'professional'],
                       help='Content tone')
    parser.add_argument('--quality-threshold', type=float, default=9.0,
                       help='Minimum quality score (default: 9.0)')
    parser.add_argument('--max-iterations', type=int, default=3,
                       help='Maximum refinement iterations (default: 3)')
    parser.add_argument('--skip-research', action='store_true',
                       help='Skip research phase (faster)')
    parser.add_argument('--skip-viral', action='store_true',
                       help='Skip viral analysis phase')
    parser.add_argument('--no-learning', action='store_true',
                       help='Disable learning system')
    parser.add_argument('--output', type=str, default='outputs',
                       help='Output directory (default: outputs)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    # Check API key
    if not check_api_key():
        return 1

    try:
        # Determine mode
        if args.interactive or not args.topic:
            return asyncio.run(run_interactive_mode())
        else:
            return asyncio.run(run_cli_mode(args))

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        return 0
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}\n")
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
