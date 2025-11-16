#!/usr/bin/env python3
"""
Advanced Usage Example
Demonstrates advanced features and customization
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config_manager import get_config_manager
from src.core.anthropic_client import AnthropicClient
from src.content_synthesis import ContentSynthesisGatekeeper


def example_1_custom_configuration():
    """Example 1: Custom configuration and scaling"""

    print("\n" + "="*70)
    print("  EXAMPLE 1: Custom Configuration & Dynamic Scaling")
    print("="*70 + "\n")

    # Load and customize configuration
    config_manager = get_config_manager()

    # Scale configuration based on requirements
    config_manager.scale_for_request({
        'video_duration': 30,  # 30-minute video
        'quality_level': 'world-class',  # Highest quality
        'complexity': 'complex'  # Complex topic
    })

    print("✅ Configuration scaled for world-class 30-minute documentary")
    print(f"   Quality threshold: {config_manager.get_content_synthesis_config().quality_threshold}")
    print(f"   Max iterations: {config_manager.get_system_config().max_iterations}")

    return config_manager


def example_2_with_research_data():
    """Example 2: Generation with research data"""

    print("\n" + "="*70)
    print("  EXAMPLE 2: Generation with Research Data")
    print("="*70 + "\n")

    config_manager = get_config_manager()
    anthropic_config = config_manager.get_anthropic_config()
    anthropic_client = AnthropicClient(
        api_key=anthropic_config.api_key,
        model=anthropic_config.model
    )

    content_config = config_manager.get_content_synthesis_config()
    gatekeeper = ContentSynthesisGatekeeper(anthropic_client, content_config)

    # Simulated research data
    research_data = {
        'key_findings': [
            'Quantum computers use quantum bits (qubits) that can exist in superposition',
            'Google achieved quantum supremacy in 2019 with Sycamore processor',
            'IBM and other companies are developing cloud-accessible quantum computers',
            'Quantum computing could revolutionize cryptography, drug discovery, and optimization'
        ],
        'citations': [
            'Nature 574, 505–510 (2019)',
            'Science 365, 1163–1165 (2019)'
        ],
        'unique_insights': [
            'Quantum computers excel at simulating quantum systems',
            'Error correction remains a major challenge'
        ]
    }

    print("📚 Using research data with key findings:")
    for finding in research_data['key_findings'][:2]:
        print(f"   - {finding}")

    print("\n🚀 Generating content...")

    package = gatekeeper.generate_content_sync(
        topic="Quantum Computing: The Next Computing Revolution",
        research_data=research_data,
        video_duration=15,
        target_audience="tech enthusiasts",
        tone="engaging but authoritative",
        style="documentary"
    )

    print(f"\n✅ Generated with quality score: {package.quality_score}/10")

    return package


def example_3_viral_optimization():
    """Example 3: Viral optimization with strategy"""

    print("\n" + "="*70)
    print("  EXAMPLE 3: Viral Optimization")
    print("="*70 + "\n")

    config_manager = get_config_manager()
    anthropic_config = config_manager.get_anthropic_config()
    anthropic_client = AnthropicClient(
        api_key=anthropic_config.api_key,
        model=anthropic_config.model
    )

    content_config = config_manager.get_content_synthesis_config()
    gatekeeper = ContentSynthesisGatekeeper(anthropic_client, content_config)

    # Viral strategy
    viral_strategy = {
        'hooks': [
            "What if I told you the next pandemic is already here?",
            "Scientists just discovered something that changes everything we know...",
            "This technology could save millions of lives, but nobody's talking about it"
        ],
        'psychology_triggers': [
            'curiosity_gap',
            'social_proof',
            'authority',
            'urgency'
        ],
        'engagement_moments': [
            {'timestamp': '0:15', 'type': 'question', 'content': 'But first, have you ever wondered...'},
            {'timestamp': '5:00', 'type': 'reveal', 'content': 'Here's what the research actually shows...'},
            {'timestamp': '10:00', 'type': 'cta', 'content': 'If you're finding this fascinating, hit subscribe...'}
        ]
    }

    print("🎯 Using viral optimization strategy:")
    print(f"   - {len(viral_strategy['hooks'])} hook variations")
    print(f"   - {len(viral_strategy['psychology_triggers'])} psychology triggers")
    print(f"   - {len(viral_strategy['engagement_moments'])} engagement moments")

    print("\n🚀 Generating viral-optimized content...")

    package = gatekeeper.generate_content_sync(
        topic="The Hidden Pandemic: Mental Health in the Digital Age",
        viral_strategy=viral_strategy,
        video_duration=12,
        target_audience="millennials and gen-z",
        tone="engaging",
        style="documentary"
    )

    print(f"\n✅ Generated with quality score: {package.quality_score}/10")
    print(f"   Engagement score: {package.validation_report['validation_passes']['engagement']['score']}/10")

    return package


def example_4_iterative_refinement():
    """Example 4: Manual iterative refinement"""

    print("\n" + "="*70)
    print("  EXAMPLE 4: Manual Iterative Refinement")
    print("="*70 + "\n")

    config_manager = get_config_manager()
    anthropic_config = config_manager.get_anthropic_config()
    anthropic_client = AnthropicClient(
        api_key=anthropic_config.api_key,
        model=anthropic_config.model
    )

    content_config = config_manager.get_content_synthesis_config()
    gatekeeper = ContentSynthesisGatekeeper(anthropic_client, content_config)

    print("🔄 Generating with manual iteration control...")

    # First pass - quick generation
    print("\n   Pass 1: Quick generation (no iteration)...")
    package_v1 = gatekeeper.generate_content_sync(
        topic="The Science of Sleep",
        video_duration=10,
        enable_iteration=False
    )

    print(f"   ✅ V1 Quality: {package_v1.quality_score}/10")

    # Second pass - with refinement
    print("\n   Pass 2: Refined version (max 3 iterations)...")
    package_v2 = gatekeeper.generate_content_sync(
        topic="The Science of Sleep",
        video_duration=10,
        enable_iteration=True,
        max_iterations=3
    )

    print(f"   ✅ V2 Quality: {package_v2.quality_score}/10")

    print(f"\n📊 Improvement: {package_v2.quality_score - package_v1.quality_score:+.1f} points")

    return package_v2


def example_5_subagent_access():
    """Example 5: Direct subagent access"""

    print("\n" + "="*70)
    print("  EXAMPLE 5: Direct Subagent Access")
    print("="*70 + "\n")

    config_manager = get_config_manager()
    anthropic_config = config_manager.get_anthropic_config()
    anthropic_client = AnthropicClient(
        api_key=anthropic_config.api_key,
        model=anthropic_config.model
    )

    content_config = config_manager.get_content_synthesis_config()

    # Access individual subagents
    from src.content_synthesis import ScriptArchitect, ContentValidator

    print("🎯 Using individual subagents directly...")

    # 1. Generate script only
    print("\n   1. Script generation only...")
    script_architect = ScriptArchitect(anthropic_client, content_config)

    script_result = script_architect.process_sync({
        'topic': 'The Future of Space Tourism',
        'research_data': {},
        'video_duration': 10,
        'tone': 'exciting and inspirational',
        'style': 'documentary'
    })

    print(f"   ✅ Script: {script_result.data['word_count']} words")

    # 2. Validate script
    print("\n   2. Script validation only...")
    validator = ContentValidator(anthropic_client, content_config)

    validation_result = validator.process_sync({
        'script': script_result.data['script']
    })

    print(f"   ✅ Validation score: {validation_result.quality_score}/10")

    # 3. Display validation details
    print("\n   📋 Validation breakdown:")
    for category, result in validation_result.data['validation_passes'].items():
        print(f"      {category.replace('_', ' ').title()}: {result['score']}/10")

    return validation_result


def main():
    """Run all advanced examples"""

    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Error: Please set ANTHROPIC_API_KEY environment variable")
        return 1

    print("\n" + "="*70)
    print("  CONTENT SYNTHESIS SYSTEM - Advanced Examples")
    print("="*70)

    try:
        # Example 1: Custom configuration
        example_1_custom_configuration()

        # Example 2: With research data
        package2 = example_2_with_research_data()

        # Example 3: Viral optimization
        package3 = example_3_viral_optimization()

        # Example 4: Iterative refinement
        package4 = example_4_iterative_refinement()

        # Example 5: Direct subagent access
        example_5_subagent_access()

        print("\n" + "="*70)
        print("  ✅ All advanced examples completed successfully!")
        print("="*70 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
