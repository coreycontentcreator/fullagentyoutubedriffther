#!/usr/bin/env python3
"""
Quick Start Example
Demonstrates basic usage of the Content Synthesis System
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config_manager import get_config_manager
from src.core.anthropic_client import AnthropicClient
from src.content_synthesis import ContentSynthesisGatekeeper


def main():
    """Quick start example"""

    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Error: Please set ANTHROPIC_API_KEY environment variable")
        return 1

    print("\n" + "="*70)
    print("  CONTENT SYNTHESIS SYSTEM - Quick Start Example")
    print("="*70 + "\n")

    # 1. Load configuration
    print("📋 Loading configuration...")
    config_manager = get_config_manager()

    # 2. Initialize Anthropic client
    print("🤖 Initializing AI client...")
    anthropic_config = config_manager.get_anthropic_config()
    anthropic_client = AnthropicClient(
        api_key=anthropic_config.api_key,
        model=anthropic_config.model,
        max_tokens=anthropic_config.max_tokens,
        temperature=anthropic_config.temperature
    )

    # 3. Initialize Content Synthesis Gatekeeper
    print("🎬 Initializing Content Synthesis Gatekeeper...")
    content_config = config_manager.get_content_synthesis_config()
    gatekeeper = ContentSynthesisGatekeeper(
        anthropic_client=anthropic_client,
        config=content_config
    )

    # 4. Generate content
    print("\n🚀 Generating content for 'The Future of Artificial Intelligence'...")
    print("   This will take a few minutes...\n")

    package = gatekeeper.quick_generate(
        topic="The Future of Artificial Intelligence",
        video_duration=10,
        style="documentary"
    )

    # 5. Display results
    print("\n" + "="*70)
    print("  ✅ GENERATION COMPLETE!")
    print("="*70)
    print(f"\n📊 Quality Score: {package.quality_score}/10")
    print(f"📝 Script: {package.word_count} words")
    print(f"🎬 Scenes: {package.scene_count}")
    print(f"⏱️  Time: {package.total_processing_time:.1f}s")
    print(f"🔄 Iterations: {package.iteration_count}")

    # 6. Display validation results
    print("\n📋 Validation Results:")
    for category, result in package.validation_report['validation_passes'].items():
        status = "✅" if result['score'] >= 7 else "⚠️"
        print(f"   {status} {category.replace('_', ' ').title()}: {result['score']}/10")

    # 7. Display script preview
    print("\n📄 Script Preview (first 500 characters):")
    print("-" * 70)
    print(package.script[:500] + "...")
    print("-" * 70)

    # 8. Save output
    print("\n💾 Saving content package...")
    output_path = gatekeeper.save_content_package(package, "outputs")
    print(f"   Saved to: {output_path}")

    print("\n" + "="*70)
    print("  🎉 Quick start example completed successfully!")
    print("="*70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
