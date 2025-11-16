"""
Configuration Manager for Viral Analysis System
Handles API keys, system settings, and dynamic configuration
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class APIConfig:
    """API Configuration"""
    anthropic_api_key: Optional[str] = None
    youtube_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None


@dataclass
class ViralAnalysisConfig:
    """Viral Analysis System Configuration"""
    # Quality thresholds
    min_viral_score: float = 9.0
    min_engagement_rate: float = 5.0
    min_retention_rate: float = 40.0

    # Tier thresholds
    gold_tier_views: int = 1_000_000
    gold_tier_engagement: float = 10.0
    gold_tier_retention: float = 60.0

    silver_tier_views: int = 500_000
    silver_tier_engagement: float = 7.0
    silver_tier_retention: float = 50.0

    bronze_tier_views: int = 100_000
    bronze_tier_engagement: float = 5.0
    bronze_tier_retention: float = 40.0

    # Hook settings
    hook_variations_count: int = 10
    hook_duration_seconds: int = 15

    # Psychology triggers
    psychology_triggers_enabled: bool = True
    triggers_count: int = 16

    # Learning settings
    continuous_learning_enabled: bool = True
    max_iterations: int = 5

    # Performance settings
    max_concurrent_subagents: int = 8
    enable_caching: bool = True
    cache_ttl_hours: int = 24

    # Model settings
    primary_model: str = "claude-sonnet-4"
    fallback_model: str = "claude-haiku"
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class SystemConfig:
    """Complete System Configuration"""
    api: APIConfig
    viral_analysis: ViralAnalysisConfig
    debug: bool = False
    log_level: str = "INFO"


class ConfigManager:
    """
    Manages all configuration for the viral analysis system.
    Supports environment variables, config files, and dynamic updates.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        return str(Path(__file__).parent.parent.parent / "config" / "system_config.yaml")

    def _load_config(self) -> SystemConfig:
        """Load configuration from file and environment variables"""
        # Load from file if exists
        config_dict = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config_dict = yaml.safe_load(f) or {}
                else:
                    config_dict = json.load(f)

        # Override with environment variables
        api_config = APIConfig(
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY', config_dict.get('api', {}).get('anthropic_api_key')),
            youtube_api_key=os.getenv('YOUTUBE_API_KEY', config_dict.get('api', {}).get('youtube_api_key')),
            openai_api_key=os.getenv('OPENAI_API_KEY', config_dict.get('api', {}).get('openai_api_key'))
        )

        # Load viral analysis config
        viral_config_dict = config_dict.get('viral_analysis', {})
        viral_config = ViralAnalysisConfig(**viral_config_dict) if viral_config_dict else ViralAnalysisConfig()

        # Create system config
        system_config = SystemConfig(
            api=api_config,
            viral_analysis=viral_config,
            debug=config_dict.get('debug', False),
            log_level=config_dict.get('log_level', 'INFO')
        )

        return system_config

    def save_config(self, path: Optional[str] = None):
        """Save current configuration to file"""
        save_path = path or self.config_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        config_dict = {
            'api': asdict(self.config.api),
            'viral_analysis': asdict(self.config.viral_analysis),
            'debug': self.config.debug,
            'log_level': self.config.log_level
        }

        with open(save_path, 'w') as f:
            if save_path.endswith('.yaml') or save_path.endswith('.yml'):
                yaml.dump(config_dict, f, default_flow_style=False)
            else:
                json.dump(config_dict, f, indent=2)

    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service"""
        return getattr(self.config.api, f"{service}_api_key", None)

    def update_config(self, updates: Dict[str, Any]):
        """Dynamically update configuration"""
        for key, value in updates.items():
            if hasattr(self.config.viral_analysis, key):
                setattr(self.config.viral_analysis, key, value)
            elif hasattr(self.config, key):
                setattr(self.config, key, value)

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration and return status and errors"""
        errors = []

        # Check required API keys
        if not self.config.api.anthropic_api_key:
            errors.append("Anthropic API key is required")

        # Validate thresholds
        if self.config.viral_analysis.min_viral_score < 0 or self.config.viral_analysis.min_viral_score > 10:
            errors.append("min_viral_score must be between 0 and 10")

        if self.config.viral_analysis.max_concurrent_subagents < 1:
            errors.append("max_concurrent_subagents must be at least 1")

        return len(errors) == 0, errors

    def get_tier_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get tier classification thresholds"""
        return {
            'gold': {
                'views': self.config.viral_analysis.gold_tier_views,
                'engagement': self.config.viral_analysis.gold_tier_engagement,
                'retention': self.config.viral_analysis.gold_tier_retention
            },
            'silver': {
                'views': self.config.viral_analysis.silver_tier_views,
                'engagement': self.config.viral_analysis.silver_tier_engagement,
                'retention': self.config.viral_analysis.silver_tier_retention
            },
            'bronze': {
                'views': self.config.viral_analysis.bronze_tier_views,
                'engagement': self.config.viral_analysis.bronze_tier_engagement,
                'retention': self.config.viral_analysis.bronze_tier_retention
            }
        }

    def __repr__(self) -> str:
        return f"ConfigManager(config_path='{self.config_path}')"


# Global config instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reset_config_manager():
    """Reset global configuration manager (useful for testing)"""
    global _config_manager
    _config_manager = None
