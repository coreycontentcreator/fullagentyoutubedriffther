#!/usr/bin/env python3
"""
Modular Agentic System - Quick Demo
Demonstrates the full system capabilities
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


async def run_demo():
    """Run a quick demonstration of the system"""
    print("\n" + "="*70)
    print("  🎬 MODULAR AGENTIC SYSTEM - DEMO")
    print("="*70)
    print("\nThis demo showcases all 5 integrated modules:\n")

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == 'your-anthropic-api-key-here':
        print("❌ Please configure ANTHROPIC_API_KEY in .env file first!\n")
        return

    # Initialize system
    print("📦 Initializing system modules...")
    from src.core.anthropic_client import AnthropicClient
    from src.intelligence import IntelligenceLayer
    from src.orchestrator import MasterOrchestrator, OrchestratorConfig

    anthropic_client = AnthropicClient(api_key=api_key)
    intelligence_layer = IntelligenceLayer(anthropic_client)

    config = OrchestratorConfig(
        enable_research=True,
        enable_viral_analysis=True,
        enable_content_synthesis=True,
        enable_learning=True,
        quality_threshold=8.5,  # Lower for demo
        max_iterations=2  # Faster for demo
    )

    orchestrator = MasterOrchestrator(intelligence_layer, config)

    print("✅ System initialized!\n")

    # Demo topic
    demo_topic = "The Future of Artificial Intelligence"
    print(f"📝 Demo Topic: {demo_topic}")
    print(f"⏱️  Duration: 10 minutes")
    print(f"👥 Audience: Tech enthusiasts\n")

    print("="*70)
    print("  🚀 GENERATING CONTENT...")
    print("="*70)
    print("\nThis will take 5-10 minutes. Progress will be shown...\n")

    try:
        # Generate content
        package = await orchestrator.generate_complete_content(
            topic=demo_topic,
            target_audience="tech enthusiasts",
            video_duration=10,
            style="documentary",
            tone="engaging"
        )

        # Display results
        print("\n" + "="*70)
        print("  ✅ DEMO COMPLETE!")
        print("="*70)

        print(f"\n📊 RESULTS:\n")
        print(f"  Overall Score: {package.overall_score:.1f}/10")
        print(f"  Iterations: {package.iteration_count}")
        print(f"  Total Time: {package.total_time:.1f}s")
        print(f"  ")
        print(f"  Research:")
        print(f"    - Sources: {package.research_report.sources_count if hasattr(package.research_report, 'sources_count') else 'N/A'}")
        print(f"    - Quality: {package.research_report.quality_score if hasattr(package.research_report, 'quality_score') else 'N/A'}/10")
        print(f"  ")
        print(f"  Viral Strategy:")
        print(f"    - Hooks: {len(package.viral_strategy.hooks) if hasattr(package.viral_strategy, 'hooks') else 'N/A'} variations")
        print(f"    - Score: {package.viral_strategy.virality_score if hasattr(package.viral_strategy, 'virality_score') else 'N/A'}/10")
        print(f"  ")
        print(f"  Content:")
        print(f"    - Words: {package.content_output.get('word_count', 'N/A')}")
        print(f"    - Duration: ~{package.content_output.get('estimated_duration', 'N/A'):.1f} minutes")

        # Show best hook
        if hasattr(package.viral_strategy, 'hooks') and package.viral_strategy.hooks:
            best_hook = max(package.viral_strategy.hooks, key=lambda h: h.virality_score)
            print(f"\n🎯 BEST HOOK ({best_hook.virality_score}/10):")
            print(f"\n{best_hook.text}\n")

        # Show key insights
        if hasattr(package.research_report, 'key_insights') and package.research_report.key_insights:
            print(f"💡 KEY INSIGHTS:")
            for i, insight in enumerate(package.research_report.key_insights[:3], 1):
                print(f"  {i}. {insight}")

        # Save
        print(f"\n💾 Saving results...")
        output_path = await orchestrator.save_package(package)
        print(f"✅ Saved to: {output_path}")

        print("\n" + "="*70)
        print("  🎉 DEMO SUCCESSFUL!")
        print("="*70)
        print("\nThe system is ready for production use!")
        print("\nNext steps:")
        print("  1. Review the generated content in outputs/")
        print("  2. Run with your own topics: python3 main_orchestrator.py")
        print("  3. Read USER_GUIDE.md for advanced usage")
        print("\n" + "="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_demo())
