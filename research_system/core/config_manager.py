"""
Configuration Manager for Research System
Handles API keys, system settings, and environment configuration
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """API Configuration for external services"""
    anthropic_api_key: Optional[str] = None
    semantic_scholar_api_key: Optional[str] = None
    jstor_api_key: Optional[str] = None
    crossref_api_key: Optional[str] = None
    pubmed_api_key: Optional[str] = None
    arxiv_api_key: Optional[str] = None
    openalex_email: Optional[str] = None

    def __post_init__(self):
        """Load API keys from environment variables if not provided"""
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.semantic_scholar_api_key:
            self.semantic_scholar_api_key = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        if not self.jstor_api_key:
            self.jstor_api_key = os.getenv('JSTOR_API_KEY')
        if not self.crossref_api_key:
            self.crossref_api_key = os.getenv('CROSSREF_API_KEY')
        if not self.pubmed_api_key:
            self.pubmed_api_key = os.getenv('PUBMED_API_KEY')
        if not self.arxiv_api_key:
            self.arxiv_api_key = os.getenv('ARXIV_API_KEY')
        if not self.openalex_email:
            self.openalex_email = os.getenv('OPENALEX_EMAIL')


@dataclass
class ResearchConfig:
    """Research system configuration"""
    min_quality_threshold: float = 8.0
    max_papers_per_source: int = 20
    total_max_papers: int = 100
    timeout_seconds: int = 30
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    parallel_requests: bool = True
    max_concurrent_requests: int = 5

    # Source priorities (1-10, higher = more important)
    source_priorities: Dict[str, int] = field(default_factory=lambda: {
        'jstor': 10,  # Primary source for unique insights
        'semantic_scholar': 9,
        'crossref': 8,
        'arxiv': 7,
        'pubmed': 7,
        'openalex': 6
    })

    # Quality thresholds for each validation criterion
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'academic_rigor': 8.0,
        'source_diversity': 7.0,
        'citation_quality': 8.0,
        'novelty': 7.5,
        'credibility': 9.0
    })


@dataclass
class SubagentConfig:
    """Subagent configuration"""
    citation_tracker_enabled: bool = True
    credibility_analyzer_enabled: bool = True
    insight_synthesizer_enabled: bool = True
    fact_checker_enabled: bool = True
    database_coordinator_enabled: bool = True

    # Anthropic model settings for subagents
    insight_synthesis_model: str = "claude-sonnet-4-5-20250929"
    fact_checking_model: str = "claude-sonnet-4-5-20250929"
    credibility_analysis_model: str = "claude-3-5-haiku-20241022"


@dataclass
class SystemConfig:
    """Overall system configuration"""
    max_iterations: int = 5
    enable_learning: bool = True
    output_directory: str = "research_system/outputs"
    cache_directory: str = "research_system/cache"
    log_level: str = "INFO"
    verbose: bool = True


class ConfigManager:
    """
    Manages all configuration for the Research System
    Provides centralized access to settings and API keys
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_file: Path to YAML configuration file (optional)
        """
        self.config_file = config_file
        self.api_config = APIConfig()
        self.research_config = ResearchConfig()
        self.subagent_config = SubagentConfig()
        self.system_config = SystemConfig()

        # Load from file if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)

        # Validate configuration
        self.validate()

        # Setup logging
        self._setup_logging()

        logger.info("Configuration Manager initialized successfully")

    def load_from_file(self, config_file: str) -> None:
        """
        Load configuration from YAML file

        Args:
            config_file: Path to YAML configuration file
        """
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)

            # Update configurations
            if 'api' in config_data:
                for key, value in config_data['api'].items():
                    if hasattr(self.api_config, key):
                        setattr(self.api_config, key, value)

            if 'research' in config_data:
                for key, value in config_data['research'].items():
                    if hasattr(self.research_config, key):
                        setattr(self.research_config, key, value)

            if 'subagents' in config_data:
                for key, value in config_data['subagents'].items():
                    if hasattr(self.subagent_config, key):
                        setattr(self.subagent_config, key, value)

            if 'system' in config_data:
                for key, value in config_data['system'].items():
                    if hasattr(self.system_config, key):
                        setattr(self.system_config, key, value)

            logger.info(f"Configuration loaded from {config_file}")

        except Exception as e:
            logger.error(f"Error loading configuration from {config_file}: {e}")
            raise

    def save_to_file(self, config_file: str) -> None:
        """
        Save current configuration to YAML file

        Args:
            config_file: Path to save configuration
        """
        config_data = {
            'api': {
                'anthropic_api_key': '${ANTHROPIC_API_KEY}',
                'semantic_scholar_api_key': '${SEMANTIC_SCHOLAR_API_KEY}',
                'jstor_api_key': '${JSTOR_API_KEY}',
                'crossref_api_key': '${CROSSREF_API_KEY}',
                'pubmed_api_key': '${PUBMED_API_KEY}',
                'arxiv_api_key': '${ARXIV_API_KEY}',
                'openalex_email': '${OPENALEX_EMAIL}'
            },
            'research': {
                'min_quality_threshold': self.research_config.min_quality_threshold,
                'max_papers_per_source': self.research_config.max_papers_per_source,
                'total_max_papers': self.research_config.total_max_papers,
                'timeout_seconds': self.research_config.timeout_seconds,
                'enable_caching': self.research_config.enable_caching,
                'cache_ttl_hours': self.research_config.cache_ttl_hours,
                'parallel_requests': self.research_config.parallel_requests,
                'max_concurrent_requests': self.research_config.max_concurrent_requests,
                'source_priorities': self.research_config.source_priorities,
                'quality_thresholds': self.research_config.quality_thresholds
            },
            'subagents': {
                'citation_tracker_enabled': self.subagent_config.citation_tracker_enabled,
                'credibility_analyzer_enabled': self.subagent_config.credibility_analyzer_enabled,
                'insight_synthesizer_enabled': self.subagent_config.insight_synthesizer_enabled,
                'fact_checker_enabled': self.subagent_config.fact_checker_enabled,
                'database_coordinator_enabled': self.subagent_config.database_coordinator_enabled,
                'insight_synthesis_model': self.subagent_config.insight_synthesis_model,
                'fact_checking_model': self.subagent_config.fact_checking_model,
                'credibility_analysis_model': self.subagent_config.credibility_analysis_model
            },
            'system': {
                'max_iterations': self.system_config.max_iterations,
                'enable_learning': self.system_config.enable_learning,
                'output_directory': self.system_config.output_directory,
                'cache_directory': self.system_config.cache_directory,
                'log_level': self.system_config.log_level,
                'verbose': self.system_config.verbose
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Configuration saved to {config_file}")

    def validate(self) -> bool:
        """
        Validate configuration settings

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Check critical API keys
        if not self.api_config.anthropic_api_key:
            logger.warning("Anthropic API key not set. AI features will not work.")

        # Validate thresholds
        if not 0 <= self.research_config.min_quality_threshold <= 10:
            raise ValueError("min_quality_threshold must be between 0 and 10")

        # Validate directories
        Path(self.system_config.output_directory).mkdir(parents=True, exist_ok=True)
        Path(self.system_config.cache_directory).mkdir(parents=True, exist_ok=True)

        return True

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        log_level = getattr(logging, self.system_config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def get_source_priority(self, source_name: str) -> int:
        """
        Get priority for a research source

        Args:
            source_name: Name of the research source

        Returns:
            Priority value (1-10)
        """
        return self.research_config.source_priorities.get(source_name.lower(), 5)

    def is_source_enabled(self, source_name: str) -> bool:
        """
        Check if a research source should be used

        Args:
            source_name: Name of the research source

        Returns:
            True if source is enabled
        """
        # All sources with API keys are enabled
        source_key_map = {
            'jstor': self.api_config.jstor_api_key,
            'semantic_scholar': True,  # Free API
            'crossref': True,  # Free API (optional key for higher rate limits)
            'arxiv': True,  # Free API
            'pubmed': True,  # Free API
            'openalex': self.api_config.openalex_email  # Requires email
        }

        return bool(source_key_map.get(source_name.lower(), False))

    def add_custom_source(self, source_name: str, priority: int = 5,
                         api_key: Optional[str] = None) -> None:
        """
        Add a custom research source dynamically

        Args:
            source_name: Name of the new source
            priority: Priority level (1-10)
            api_key: Optional API key for the source
        """
        self.research_config.source_priorities[source_name.lower()] = priority
        logger.info(f"Added custom research source: {source_name} (priority: {priority})")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary

        Returns:
            Dictionary representation of configuration
        """
        return {
            'api': self.api_config.__dict__,
            'research': {
                **self.research_config.__dict__
            },
            'subagents': self.subagent_config.__dict__,
            'system': self.system_config.__dict__
        }

    def __repr__(self) -> str:
        """String representation of configuration"""
        return f"ConfigManager(sources={len(self.research_config.source_priorities)})"


# Singleton instance
_config_manager_instance = None


def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """
    Get or create ConfigManager singleton instance

    Args:
        config_file: Optional path to configuration file

    Returns:
        ConfigManager instance
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager(config_file)
    return _config_manager_instance
