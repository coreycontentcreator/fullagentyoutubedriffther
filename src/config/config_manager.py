"""
Configuration Manager for Master Orchestrator System

This module manages all system configuration, API keys, thresholds,
and environment settings for the viral YouTube synthesis system.

Author: AI Research Team
Date: November 2025
Version: 1.0.0
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import logging


@dataclass
class AnthropicConfig:
    """Anthropic API configuration"""
    api_key: str
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 8000
    temperature: float = 0.7
    timeout: int = 300


@dataclass
class VectorDatabaseConfig:
    """Vector database configuration"""
    provider: str = "chromadb"
    collection_name: str = "viral_strategies"
    embedding_model: str = "text-embedding-3-large"
    dimension: int = 1536
    distance_metric: str = "cosine"


@dataclass
class GatekeeperThresholds:
    """Quality thresholds for gatekeepers"""
    research_quality_min: float = 8.0
    viral_potential_min: float = 9.0
    script_quality_min: float = 9.0
    production_feasibility_min: float = 8.0
    overall_quality_min: float = 9.0
    max_iterations: int = 5


@dataclass
class YouTubeConfig:
    """YouTube API configuration"""
    api_key: str
    api_version: str = "v3"
    max_results: int = 50
    tier_thresholds: Dict[str, Dict[str, float]] = None

    def __post_init__(self):
        if self.tier_thresholds is None:
            self.tier_thresholds = {
                "gold": {"views": 1_000_000, "engagement": 0.10, "retention": 0.60},
                "silver": {"views": 500_000, "engagement": 0.07, "retention": 0.50},
                "bronze": {"views": 100_000, "engagement": 0.05, "retention": 0.40}
            }


@dataclass
class SystemConfig:
    """Main system configuration"""
    project_root: Path
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_caching: bool = True
    cache_ttl: int = 3600
    enable_learning: bool = True
    modular_mode: bool = True
    outputs_dir: Path = None
    logs_dir: Path = None

    def __post_init__(self):
        if self.outputs_dir is None:
            self.outputs_dir = self.project_root / "outputs"
        if self.logs_dir is None:
            self.logs_dir = self.project_root / "logs"

        # Create directories if they don't exist
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


class ConfigurationManager:
    """
    Centralized configuration management for the Master Orchestrator System.

    This class loads, validates, and provides access to all system configurations
    including API keys, thresholds, and environment settings.
    """

    def __init__(self, config_path: Optional[Path] = None, env_path: Optional[Path] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to YAML configuration file
            env_path: Path to .env file containing API keys
        """
        self.logger = self._setup_logger()

        # Determine project root
        self.project_root = Path(__file__).parent.parent.parent

        # Set default paths
        if config_path is None:
            config_path = self.project_root / "config.yaml"
        if env_path is None:
            env_path = self.project_root / ".env"

        self.config_path = Path(config_path)
        self.env_path = Path(env_path)

        # Load configurations
        self._load_environment()
        self._load_config_file()
        self._initialize_configs()
        self._validate_configuration()

        self.logger.info("Configuration Manager initialized successfully")

    def _setup_logger(self) -> logging.Logger:
        """Setup basic logger for configuration manager."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _load_environment(self):
        """Load environment variables from .env file."""
        if self.env_path.exists():
            load_dotenv(self.env_path)
            self.logger.info(f"Loaded environment from {self.env_path}")
        else:
            self.logger.warning(f"Environment file not found: {self.env_path}")

    def _load_config_file(self):
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
            self.logger.info(f"Loaded configuration from {self.config_path}")
        else:
            self.logger.warning(f"Config file not found: {self.config_path}. Using defaults.")
            self.config_data = {}

    def _initialize_configs(self):
        """Initialize all configuration objects."""
        # System configuration
        system_config = self.config_data.get('system', {})
        self.system = SystemConfig(
            project_root=self.project_root,
            log_level=system_config.get('log_level', 'INFO'),
            enable_caching=system_config.get('enable_caching', True),
            cache_ttl=system_config.get('cache_ttl', 3600),
            enable_learning=system_config.get('enable_learning', True),
            modular_mode=system_config.get('modular_mode', True)
        )

        # Anthropic configuration
        anthropic_config = self.config_data.get('anthropic', {})
        self.anthropic = AnthropicConfig(
            api_key=os.getenv('ANTHROPIC_API_KEY', anthropic_config.get('api_key', '')),
            model=anthropic_config.get('model', 'claude-sonnet-4-5-20250929'),
            max_tokens=anthropic_config.get('max_tokens', 8000),
            temperature=anthropic_config.get('temperature', 0.7),
            timeout=anthropic_config.get('timeout', 300)
        )

        # Vector database configuration
        vector_db_config = self.config_data.get('vector_database', {})
        self.vector_database = VectorDatabaseConfig(
            provider=vector_db_config.get('provider', 'chromadb'),
            collection_name=vector_db_config.get('collection_name', 'viral_strategies'),
            embedding_model=vector_db_config.get('embedding_model', 'text-embedding-3-large'),
            dimension=vector_db_config.get('dimension', 1536),
            distance_metric=vector_db_config.get('distance_metric', 'cosine')
        )

        # Gatekeeper thresholds
        threshold_config = self.config_data.get('gatekeeper_thresholds', {})
        self.thresholds = GatekeeperThresholds(
            research_quality_min=threshold_config.get('research_quality_min', 8.0),
            viral_potential_min=threshold_config.get('viral_potential_min', 9.0),
            script_quality_min=threshold_config.get('script_quality_min', 9.0),
            production_feasibility_min=threshold_config.get('production_feasibility_min', 8.0),
            overall_quality_min=threshold_config.get('overall_quality_min', 9.0),
            max_iterations=threshold_config.get('max_iterations', 5)
        )

        # YouTube configuration
        youtube_config = self.config_data.get('youtube', {})
        self.youtube = YouTubeConfig(
            api_key=os.getenv('YOUTUBE_API_KEY', youtube_config.get('api_key', '')),
            api_version=youtube_config.get('api_version', 'v3'),
            max_results=youtube_config.get('max_results', 50),
            tier_thresholds=youtube_config.get('tier_thresholds')
        )

    def _validate_configuration(self):
        """Validate critical configuration values."""
        errors = []

        # Validate API keys
        if not self.anthropic.api_key:
            errors.append("Anthropic API key not configured")

        if not self.youtube.api_key:
            self.logger.warning("YouTube API key not configured - YouTube features will be disabled")

        # Validate thresholds
        if not 0 <= self.thresholds.research_quality_min <= 10:
            errors.append("Research quality threshold must be between 0 and 10")

        if not 0 <= self.thresholds.viral_potential_min <= 10:
            errors.append("Viral potential threshold must be between 0 and 10")

        if self.thresholds.max_iterations < 1:
            errors.append("Max iterations must be at least 1")

        # Validate paths
        if not self.system.project_root.exists():
            errors.append(f"Project root does not exist: {self.system.project_root}")

        if errors:
            error_msg = "\n".join(errors)
            self.logger.error(f"Configuration validation failed:\n{error_msg}")
            raise ValueError(f"Invalid configuration:\n{error_msg}")

        self.logger.info("Configuration validation passed")

    def get_anthropic_config(self) -> Dict[str, Any]:
        """Get Anthropic API configuration as dictionary."""
        return asdict(self.anthropic)

    def get_vector_db_config(self) -> Dict[str, Any]:
        """Get vector database configuration as dictionary."""
        return asdict(self.vector_database)

    def get_youtube_config(self) -> Dict[str, Any]:
        """Get YouTube API configuration as dictionary."""
        config_dict = asdict(self.youtube)
        return config_dict

    def get_thresholds(self) -> Dict[str, Any]:
        """Get gatekeeper thresholds as dictionary."""
        return asdict(self.thresholds)

    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration as dictionary."""
        config = asdict(self.system)
        config['project_root'] = str(self.system.project_root)
        config['outputs_dir'] = str(self.system.outputs_dir)
        config['logs_dir'] = str(self.system.logs_dir)
        return config

    def save_config(self, output_path: Optional[Path] = None):
        """
        Save current configuration to YAML file.

        Args:
            output_path: Path to save configuration (defaults to config.yaml)
        """
        if output_path is None:
            output_path = self.config_path

        config_data = {
            'system': self.get_system_config(),
            'anthropic': {k: v for k, v in self.get_anthropic_config().items() if k != 'api_key'},
            'vector_database': self.get_vector_db_config(),
            'gatekeeper_thresholds': self.get_thresholds(),
            'youtube': {k: v for k, v in self.get_youtube_config().items() if k != 'api_key'}
        }

        with open(output_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

        self.logger.info(f"Configuration saved to {output_path}")

    def update_threshold(self, threshold_name: str, value: float):
        """
        Update a gatekeeper threshold value.

        Args:
            threshold_name: Name of the threshold to update
            value: New threshold value
        """
        if hasattr(self.thresholds, threshold_name):
            setattr(self.thresholds, threshold_name, value)
            self.logger.info(f"Updated threshold {threshold_name} to {value}")
        else:
            raise ValueError(f"Unknown threshold: {threshold_name}")

    def __repr__(self) -> str:
        """String representation of configuration manager."""
        return (
            f"ConfigurationManager(\n"
            f"  Project Root: {self.system.project_root}\n"
            f"  Log Level: {self.system.log_level}\n"
            f"  Anthropic Model: {self.anthropic.model}\n"
            f"  Vector DB: {self.vector_database.provider}\n"
            f"  Modular Mode: {self.system.modular_mode}\n"
            f"  Learning Enabled: {self.system.enable_learning}\n"
            f")"
        )


# Singleton instance for global access
_config_instance: Optional[ConfigurationManager] = None


def get_config(config_path: Optional[Path] = None, env_path: Optional[Path] = None) -> ConfigurationManager:
    """
    Get or create the global configuration manager instance.

    Args:
        config_path: Path to YAML configuration file
        env_path: Path to .env file

    Returns:
        ConfigurationManager instance
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = ConfigurationManager(config_path, env_path)

    return _config_instance


def reset_config():
    """Reset the global configuration instance (mainly for testing)."""
    global _config_instance
    _config_instance = None


if __name__ == "__main__":
    # Example usage and testing
    config = ConfigurationManager()
    print(config)
    print("\nAnthropic Config:", config.get_anthropic_config())
    print("\nThresholds:", config.get_thresholds())
