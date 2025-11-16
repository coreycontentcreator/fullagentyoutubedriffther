#!/usr/bin/env python3
"""
Test script to validate all imports work correctly
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all critical imports"""

    print("Testing imports...")

    try:
        # Core imports
        print("  ✓ Testing core imports...")
        from src.core.config_manager import ConfigManager, get_config_manager
        from src.core.anthropic_client import AnthropicClient

        # Content synthesis imports
        print("  ✓ Testing content synthesis imports...")
        from src.content_synthesis import (
            ContentSynthesisGatekeeper,
            ContentPackage,
            ScriptArchitect,
            VisualSceneArchitect,
            ProductionNotesGenerator,
            NarrativeStructureEngine,
            ContentValidator
        )

        # Chat interface
        print("  ✓ Testing chat interface...")
        from src.chat_interface import ChatInterface

        print("\n✅ All imports successful!")
        print("\nSystem is ready to use!")

        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
