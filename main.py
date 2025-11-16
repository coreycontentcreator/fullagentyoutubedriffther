#!/usr/bin/env python3
"""
Content Synthesis System - Main Application
Entry point for the content generation system
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config_manager import get_config_manager
from src.core.anthropic_client import AnthropicClient
from src.content_synthesis import ContentSynthesisGatekeeper
from src.chat_interface import ChatInterface


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('content_synthesis.log')
        ]
    )


def check_api_key():
    """Check if API key is configured"""
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("\n" + "="*70)
        print("  ❌ ANTHROPIC API KEY NOT FOUND")
        print("="*70)
        print("\nThe Content Synthesis System requires an Anthropic API key to function.")
        print("\nTo set your API key:")
        print("\n1. Get your API key from: https://console.anthropic.com/")
        print("\n2. Set the environment variable:")
        print("   export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\n   Or create a .env file with:")
        print("   ANTHROPIC_API_KEY=your-api-key-here")
        print("\n" + "="*70 + "\n")
        return False

    return True


def run_interactive_mode():
    """Run interactive chat interface"""
    print("\n🚀 Starting Content Synthesis System in Interactive Mode...\n")

    interface = ChatInterface()
    interface.start_interactive_session()


def run_cli_mode(args):
    """Run in CLI mode with arguments"""
    print("\n🚀 Starting Content Synthesis System in CLI Mode...\n")

    # Load configuration
    config_manager = get_config_manager()

    # Initialize Anthropic client
    anthropic_config = config_manager.get_anthropic_config()
    anthropic_client = AnthropicClient(
        api_key=anthropic_config.api_key,
        model=anthropic_config.model,
        max_tokens=anthropic_config.max_tokens,
        temperature=anthropic_config.temperature
    )

    # Initialize gatekeeper
    content_config = config_manager.get_content_synthesis_config()
    gatekeeper = ContentSynthesisGatekeeper(
        anthropic_client=anthropic_client,
        config=content_config
    )

    print(f"📝 Topic: {args.topic}")
    print(f"⏱️  Duration: {args.duration} minutes")
    print(f"🎨 Style: {args.style}")
    print(f"👥 Audience: {args.audience}")
    print("\nGenerating content... This may take several minutes.\n")

    try:
        # Generate content
        package = gatekeeper.generate_content_sync(
            topic=args.topic,
            video_duration=args.duration,
            style=args.style,
            target_audience=args.audience,
            tone=args.tone,
            budget_level=args.budget,
            enable_iteration=not args.no_iteration,
            max_iterations=args.max_iterations
        )

        # Display results
        print("\n" + "="*70)
        print("  ✅ CONTENT GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Quality Score: {package.quality_score}/10")
        print(f"📝 Script: {package.word_count} words (~{package.estimated_duration:.1f} minutes)")
        print(f"🎬 Visual Scenes: {package.scene_count}")
        print(f"🔄 Iterations: {package.iteration_count}")
        print(f"⏱️  Processing Time: {package.total_processing_time:.1f}s")

        # Save if requested
        if args.output:
            output_path = gatekeeper.save_content_package(package, args.output)
            print(f"\n💾 Saved to: {output_path}")

        print("\n" + "="*70 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        logging.error(f"Generation failed: {e}", exc_info=True)
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Content Synthesis System - World-class YouTube content generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  python main.py

  # CLI mode
  python main.py --topic "The Future of AI" --duration 15

  # With custom settings
  python main.py --topic "Climate Change" --duration 20 --style cinematic --audience students

  # Quick generation without iteration
  python main.py --topic "Space Exploration" --no-iteration

For more information, visit the documentation.
        """
    )

    # Mode selection
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive chat mode (default if no topic provided)'
    )

    # Content parameters
    parser.add_argument(
        '--topic',
        type=str,
        help='Video topic'
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=15,
        help='Target video duration in minutes (default: 15)'
    )

    parser.add_argument(
        '--style',
        type=str,
        default='documentary',
        choices=['documentary', 'educational', 'cinematic', 'casual'],
        help='Visual style (default: documentary)'
    )

    parser.add_argument(
        '--tone',
        type=str,
        default='engaging',
        choices=['engaging', 'authoritative', 'casual', 'professional'],
        help='Script tone (default: engaging)'
    )

    parser.add_argument(
        '--audience',
        type=str,
        default='general audience',
        help='Target audience (default: general audience)'
    )

    parser.add_argument(
        '--budget',
        type=str,
        default='medium',
        choices=['low', 'medium', 'high'],
        help='Production budget level (default: medium)'
    )

    # System parameters
    parser.add_argument(
        '--no-iteration',
        action='store_true',
        help='Disable iterative refinement'
    )

    parser.add_argument(
        '--max-iterations',
        type=int,
        default=5,
        help='Maximum refinement iterations (default: 5)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='outputs',
        help='Output directory (default: outputs)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Check API key
    if not check_api_key():
        return 1

    try:
        # Determine mode
        if args.interactive or not args.topic:
            # Interactive mode
            return run_interactive_mode()
        else:
            # CLI mode
            return run_cli_mode(args)

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        return 0
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}\n")
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
