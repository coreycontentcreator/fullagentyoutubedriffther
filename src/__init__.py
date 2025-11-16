"""
Content Synthesis System
World-class YouTube documentary content generation with AI
"""
__version__ = "1.0.0"
__author__ = "Content Synthesis Team"

from src.content_synthesis import (
    ContentSynthesisGatekeeper,
    ContentPackage
)
from src.core import (
    ConfigManager,
    get_config_manager,
    AnthropicClient
)

__all__ = [
    'ContentSynthesisGatekeeper',
    'ContentPackage',
    'ConfigManager',
    'get_config_manager',
    'AnthropicClient'
]
