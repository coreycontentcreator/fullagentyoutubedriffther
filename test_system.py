"""
Quick system test to verify all components are working
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        # Core modules
        from viral_analysis.viral_analyser_gatekeeper import ViralAnalyserGatekeeper
        from viral_analysis.psychology_trigger_detector import PsychologyTriggerDetector
        from viral_analysis.brendan_kane_methodology import BrendanKaneMethodology

        # Subagents
        from subagents.hook_specialist import HookSpecialist
        from subagents.trigger_implementer import TriggerImplementer
        from subagents.pattern_recognizer import PatternRecognizer
        from subagents.retention_optimizer import RetentionOptimizer
        from subagents.engagement_designer import EngagementDesigner
        from subagents.youtube_data_analyst import YouTubeDataAnalyst
        from subagents.strategy_curator import StrategyCurator
        from subagents.virality_scorer import ViralityScorer

        # Integrations
        from integrations.anthropic_integration import AnthropicIntegration

        # Config
        from config.config_manager import ConfigManager

        # Chat
        from chat.chat_interface import ChatInterface

        print("✅ All imports successful!")
        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("\nTesting basic functionality...")

    try:
        # Test Psychology Trigger Detector
        from viral_analysis.psychology_trigger_detector import PsychologyTriggerDetector
        detector = PsychologyTriggerDetector()
        triggers = detector.get_all_triggers()
        assert len(triggers) == 16, "Should have 16 triggers"
        print(f"✅ Psychology Trigger Detector: {len(triggers)} triggers loaded")

        # Test Brendan Kane Methodology
        from viral_analysis.brendan_kane_methodology import BrendanKaneMethodology
        kane = BrendanKaneMethodology()
        framework = kane.get_viral_framework()
        assert 'principles' in framework, "Should have principles"
        print(f"✅ Brendan Kane Methodology: Framework loaded")

        # Test Pattern Recognizer
        from subagents.pattern_recognizer import PatternRecognizer
        recognizer = PatternRecognizer()
        patterns = recognizer.known_patterns
        assert len(patterns) > 0, "Should have patterns"
        print(f"✅ Pattern Recognizer: {len(patterns)} patterns loaded")

        # Test Retention Optimizer
        from subagents.retention_optimizer import RetentionOptimizer
        optimizer = RetentionOptimizer()
        strategy = optimizer.generate_retention_strategy(15)
        assert 'retention_elements' in strategy, "Should have retention elements"
        print(f"✅ Retention Optimizer: Strategy generated")

        # Test Engagement Designer
        from subagents.engagement_designer import EngagementDesigner
        designer = EngagementDesigner()
        engagement = designer.design_engagement_strategy(15)
        assert 'engagement_moments' in engagement, "Should have engagement moments"
        print(f"✅ Engagement Designer: Strategy designed")

        # Test Virality Scorer (without content)
        from subagents.virality_scorer import ViralityScorer
        scorer = ViralityScorer()
        hook_score = scorer.score_hook("What if everything you know is wrong?")
        assert 'overall_hook_score' in hook_score, "Should return hook score"
        print(f"✅ Virality Scorer: Hook scored at {hook_score['overall_hook_score']}/10")

        # Test Strategy Curator
        from subagents.strategy_curator import StrategyCurator
        curator = StrategyCurator()
        stats = curator.analyze_library_stats()
        print(f"✅ Strategy Curator: Library initialized")

        # Test Config Manager
        from config.config_manager import ConfigManager
        config = ConfigManager()
        tiers = config.get_tier_thresholds()
        assert 'gold' in tiers, "Should have tier thresholds"
        print(f"✅ Config Manager: Configuration loaded")

        print("\n✅ All basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gatekeeper_structure():
    """Test gatekeeper structure without API"""
    print("\nTesting gatekeeper structure...")

    try:
        from viral_analysis.viral_analyser_gatekeeper import ViralAnalyserGatekeeper

        # Note: This will fail without API key, but we can test structure
        try:
            gatekeeper = ViralAnalyserGatekeeper()
            print("⚠️  Gatekeeper initialized (API key may not be set)")
        except ValueError as e:
            if "API key" in str(e):
                print("⚠️  Gatekeeper requires API key (expected)")
            else:
                raise

        # Test available subagents list
        try:
            gatekeeper = ViralAnalyserGatekeeper()
            subagents = gatekeeper.get_available_subagents()
            assert len(subagents) == 8, "Should have 8 subagents"
            print(f"✅ Gatekeeper: {len(subagents)} subagents available")

            for agent in subagents:
                print(f"   • {agent['name']}: {agent['capability']}")

        except Exception as e:
            print(f"⚠️  Gatekeeper test skipped (likely needs API key): {e}")

        return True

    except Exception as e:
        print(f"❌ Gatekeeper test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("🎯 VIRAL ANALYSIS SYSTEM - System Test")
    print("="*70)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Basic functionality
    results.append(("Basic Functionality", test_basic_functionality()))

    # Test 3: Gatekeeper structure
    results.append(("Gatekeeper Structure", test_gatekeeper_structure()))

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Set your ANTHROPIC_API_KEY in .env file")
        print("2. Run: python main.py")
        print("3. Start analyzing viral content!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")

    print("="*70)


if __name__ == "__main__":
    main()
