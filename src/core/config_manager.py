"""
Configuration Manager for Content Synthesis System
Handles API keys, system settings, and dynamic configuration
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnthropicConfig:
    """Anthropic API Configuration"""
    api_key: str
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 8000
    temperature: float = 0.7
    timeout: int = 300


@dataclass
class SystemConfig:
    """System-wide Configuration"""
    log_level: str = "INFO"
    output_dir: str = "outputs"
    max_iterations: int = 5
    quality_threshold: float = 9.0
    enable_caching: bool = True
    cache_ttl: int = 3600


@dataclass
class ContentSynthesisConfig:
    """Content Synthesis Gatekeeper Configuration"""
    min_script_length: int = 5000
    max_script_length: int = 15000
    target_video_duration: int = 15  # minutes
    min_scene_count: int = 50
    max_scene_count: int = 200
    quality_threshold: float = 9.0
    enable_multi_pass_validation: bool = True
    hook_interval: int = 120  # seconds (2 minutes)


class ConfigManager:
    """
    Central configuration manager for the Content Synthesis system
    Supports dynamic scaling and runtime configuration updates
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.anthropic_config: Optional[AnthropicConfig] = None
        self.system_config: SystemConfig = SystemConfig()
        self.content_synthesis_config: ContentSynthesisConfig = ContentSynthesisConfig()

        self._load_config()
        self._setup_logging()

    def _get_default_config_path(self) -> str:
        """Get default configuration path"""
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / "config" / "config.yaml"

        if not config_file.exists():
            # Create default config if it doesn't exist
            self._create_default_config(config_file)

        return str(config_file)

    def _create_default_config(self, config_path: Path):
        """Create default configuration file"""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        default_config = {
            "anthropic": {
                "api_key": "${ANTHROPIC_API_KEY}",
                "model": "claude-sonnet-4-5-20250929",
                "max_tokens": 8000,
                "temperature": 0.7,
                "timeout": 300
            },
            "system": {
                "log_level": "INFO",
                "output_dir": "outputs",
                "max_iterations": 5,
                "quality_threshold": 9.0,
                "enable_caching": True,
                "cache_ttl": 3600
            },
            "content_synthesis": {
                "min_script_length": 5000,
                "max_script_length": 15000,
                "target_video_duration": 15,
                "min_scene_count": 50,
                "max_scene_count": 200,
                "quality_threshold": 9.0,
                "enable_multi_pass_validation": True,
                "hook_interval": 120
            }
        }

        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)

        logger.info(f"Created default configuration at {config_path}")

    def _load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)

            # Load Anthropic config
            if 'anthropic' in config:
                anthropic_data = config['anthropic'].copy()
                # Resolve environment variables
                api_key = anthropic_data.get('api_key', '')
                if api_key.startswith('${') and api_key.endswith('}'):
                    env_var = api_key[2:-1]
                    anthropic_data['api_key'] = os.getenv(env_var, '')

                self.anthropic_config = AnthropicConfig(**anthropic_data)

            # Load system config
            if 'system' in config:
                self.system_config = SystemConfig(**config['system'])

            # Load content synthesis config
            if 'content_synthesis' in config:
                self.content_synthesis_config = ContentSynthesisConfig(**config['content_synthesis'])

            logger.info(f"Configuration loaded from {self.config_path}")

        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}")
            self._create_default_config(Path(self.config_path))
            self._load_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def _setup_logging(self):
        """Setup logging based on configuration"""
        logging.basicConfig(
            level=getattr(logging, self.system_config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('content_synthesis.log')
            ]
        )

    def get_anthropic_config(self) -> AnthropicConfig:
        """Get Anthropic API configuration"""
        if not self.anthropic_config:
            raise ValueError("Anthropic configuration not loaded")

        if not self.anthropic_config.api_key:
            raise ValueError("Anthropic API key not set. Please set ANTHROPIC_API_KEY environment variable")

        return self.anthropic_config

    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return self.system_config

    def get_content_synthesis_config(self) -> ContentSynthesisConfig:
        """Get content synthesis configuration"""
        return self.content_synthesis_config

    def update_config(self, section: str, updates: Dict[str, Any]):
        """
        Dynamically update configuration at runtime
        Enables scaling based on user requests

        Args:
            section: Configuration section ('anthropic', 'system', 'content_synthesis')
            updates: Dictionary of configuration updates
        """
        if section == 'anthropic' and self.anthropic_config:
            for key, value in updates.items():
                if hasattr(self.anthropic_config, key):
                    setattr(self.anthropic_config, key, value)

        elif section == 'system':
            for key, value in updates.items():
                if hasattr(self.system_config, key):
                    setattr(self.system_config, key, value)

        elif section == 'content_synthesis':
            for key, value in updates.items():
                if hasattr(self.content_synthesis_config, key):
                    setattr(self.content_synthesis_config, key, value)

        logger.info(f"Configuration updated: {section} - {updates}")

    def scale_for_request(self, request_params: Dict[str, Any]):
        """
        Dynamically scale configuration based on user request

        Args:
            request_params: User request parameters
                - video_duration: Target video duration in minutes
                - quality_level: 'standard', 'high', 'world-class'
                - complexity: 'simple', 'moderate', 'complex'
        """
        # Scale based on video duration
        if 'video_duration' in request_params:
            duration = request_params['video_duration']
            words_per_minute = 150

            updates = {
                'target_video_duration': duration,
                'min_script_length': int(duration * words_per_minute * 0.8),
                'max_script_length': int(duration * words_per_minute * 1.2),
                'min_scene_count': int(duration * 3),
                'max_scene_count': int(duration * 10),
                'hook_interval': 120 if duration > 10 else 90
            }

            self.update_config('content_synthesis', updates)

        # Scale based on quality level
        if 'quality_level' in request_params:
            quality_map = {
                'standard': {'quality_threshold': 7.0, 'max_iterations': 3},
                'high': {'quality_threshold': 8.5, 'max_iterations': 5},
                'world-class': {'quality_threshold': 9.5, 'max_iterations': 7}
            }

            quality_settings = quality_map.get(request_params['quality_level'], quality_map['high'])
            self.update_config('content_synthesis', {'quality_threshold': quality_settings['quality_threshold']})
            self.update_config('system', {'max_iterations': quality_settings['max_iterations']})

        # Scale based on complexity
        if 'complexity' in request_params:
            complexity = request_params['complexity']

            if complexity == 'complex':
                self.update_config('anthropic', {'max_tokens': 12000, 'temperature': 0.8})
            elif complexity == 'simple':
                self.update_config('anthropic', {'max_tokens': 4000, 'temperature': 0.6})

        logger.info(f"Configuration scaled for request: {request_params}")

    def save_config(self, output_path: Optional[str] = None):
        """Save current configuration to file"""
        output_path = output_path or self.config_path

        config_data = {
            "anthropic": asdict(self.anthropic_config) if self.anthropic_config else {},
            "system": asdict(self.system_config),
            "content_synthesis": asdict(self.content_synthesis_config)
        }

        with open(output_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)

        logger.info(f"Configuration saved to {output_path}")

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            "anthropic": asdict(self.anthropic_config) if self.anthropic_config else {},
            "system": asdict(self.system_config),
            "content_synthesis": asdict(self.content_synthesis_config)
        }


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager(config_path)

    return _config_manager


def reset_config_manager():
    """Reset global configuration manager (useful for testing)"""
    global _config_manager
    _config_manager = None
