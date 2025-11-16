"""
Gatekeeper Interface Definitions

Defines abstract interfaces for all gatekeepers in the system:
- Research Gatekeeper
- Viral Analyser Gatekeeper
- Content Synthesis Gatekeeper

These interfaces ensure consistent interaction patterns and enable
modular integration.

Author: AI Research Team
Date: November 2025
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GatekeeperStatus(Enum):
    """Status of gatekeeper processing."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ITERATING = "iterating"


class QualityDecision(Enum):
    """Quality validation decisions."""
    PASS = "pass"
    FAIL = "fail"
    ITERATE = "iterate"


@dataclass
class QualityMetrics:
    """Quality metrics for validation."""
    overall_score: float
    criterion_scores: Dict[str, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    passes_threshold: bool = False
    threshold_value: float = 0.0


@dataclass
class GatekeeperResult:
    """Standard result structure from gatekeepers."""
    status: GatekeeperStatus
    output: Dict[str, Any]
    quality_metrics: Optional[QualityMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    iteration_count: int = 0
    error: Optional[str] = None


class BaseGatekeeper(ABC):
    """
    Abstract base class for all gatekeepers.

    All gatekeepers must implement:
    - process(): Main processing logic
    - validate_quality(): Quality validation
    - iterate(): Improvement iteration
    """

    def __init__(self, config: Dict[str, Any], logger: Any):
        """
        Initialize gatekeeper.

        Args:
            config: Gatekeeper configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.status = GatekeeperStatus.PENDING
        self.iteration_count = 0
        self.max_iterations = config.get('max_iterations', 5)

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> GatekeeperResult:
        """
        Process input data through the gatekeeper.

        Args:
            input_data: Input data for processing

        Returns:
            GatekeeperResult with output and quality metrics
        """
        pass

    @abstractmethod
    def validate_quality(self, output: Dict[str, Any]) -> QualityMetrics:
        """
        Validate output quality against thresholds.

        Args:
            output: Output to validate

        Returns:
            QualityMetrics with scores and pass/fail decision
        """
        pass

    @abstractmethod
    def iterate(
        self,
        previous_output: Dict[str, Any],
        quality_metrics: QualityMetrics
    ) -> GatekeeperResult:
        """
        Improve output based on quality feedback.

        Args:
            previous_output: Previous output that didn't pass validation
            quality_metrics: Quality metrics indicating issues

        Returns:
            GatekeeperResult with improved output
        """
        pass

    def get_status(self) -> GatekeeperStatus:
        """Get current gatekeeper status."""
        return self.status

    def reset(self):
        """Reset gatekeeper state."""
        self.status = GatekeeperStatus.PENDING
        self.iteration_count = 0


class ResearchGatekeeperInterface(BaseGatekeeper):
    """
    Interface for Research Gatekeeper.

    Responsibilities:
    - Multi-database academic research
    - Source validation and credibility checking
    - Citation tracking
    - Insight synthesis
    - Fact verification
    """

    @abstractmethod
    def conduct_research(
        self,
        topic: str,
        focus_areas: Optional[List[str]] = None,
        min_papers: int = 50,
        databases: Optional[List[str]] = None
    ) -> GatekeeperResult:
        """
        Conduct comprehensive research on a topic.

        Args:
            topic: Research topic
            focus_areas: Specific areas to focus on
            min_papers: Minimum number of papers to analyze
            databases: Specific databases to search

        Returns:
            GatekeeperResult with research findings
        """
        pass

    @abstractmethod
    def validate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate source credibility and quality.

        Args:
            sources: List of research sources

        Returns:
            Validated and scored sources
        """
        pass

    @abstractmethod
    def synthesize_insights(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize insights from research data.

        Args:
            research_data: Raw research data

        Returns:
            Synthesized insights and key findings
        """
        pass


class ViralAnalyserGatekeeperInterface(BaseGatekeeper):
    """
    Interface for Viral Analyser Gatekeeper.

    Responsibilities:
    - YouTube video analysis
    - Hook generation
    - Psychology trigger identification
    - Pattern recognition
    - Viral strategy creation
    """

    @abstractmethod
    def analyze_viral_patterns(
        self,
        topic: str,
        research_context: Dict[str, Any],
        target_audience: Optional[str] = None
    ) -> GatekeeperResult:
        """
        Analyze viral patterns for the topic.

        Args:
            topic: Content topic
            research_context: Research findings for context
            target_audience: Target audience description

        Returns:
            GatekeeperResult with viral strategy
        """
        pass

    @abstractmethod
    def generate_hooks(
        self,
        topic: str,
        context: Dict[str, Any],
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate compelling opening hooks.

        Args:
            topic: Content topic
            context: Context for hook generation
            count: Number of hooks to generate

        Returns:
            List of hooks with virality scores
        """
        pass

    @abstractmethod
    def identify_psychology_triggers(
        self,
        content: str,
        existing_triggers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Identify applicable psychology triggers.

        Args:
            content: Content to analyze
            existing_triggers: Already identified triggers

        Returns:
            Mapping of triggers to application points
        """
        pass

    @abstractmethod
    def analyze_youtube_video(
        self,
        video_url: str,
        store_in_library: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a YouTube video for viral patterns.

        Args:
            video_url: YouTube video URL
            store_in_library: Whether to store in viral strategy library

        Returns:
            Video analysis with metrics and patterns
        """
        pass


class ContentSynthesisGatekeeperInterface(BaseGatekeeper):
    """
    Interface for Content Synthesis Gatekeeper.

    Responsibilities:
    - Script generation
    - Visual scene creation
    - Production notes
    - Narrative structure
    - Quality validation
    """

    @abstractmethod
    def generate_script(
        self,
        research: Dict[str, Any],
        viral_strategy: Dict[str, Any],
        style: str = "documentary",
        duration_minutes: int = 15
    ) -> GatekeeperResult:
        """
        Generate complete video script.

        Args:
            research: Research findings
            viral_strategy: Viral strategy and hooks
            style: Video style
            duration_minutes: Target duration

        Returns:
            GatekeeperResult with complete script package
        """
        pass

    @abstractmethod
    def create_visual_scenes(
        self,
        script: str,
        style: str
    ) -> List[Dict[str, Any]]:
        """
        Create visual scene descriptions.

        Args:
            script: Video script
            style: Visual style

        Returns:
            List of scene descriptions
        """
        pass

    @abstractmethod
    def generate_production_notes(
        self,
        script: str,
        scenes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate production notes and guidance.

        Args:
            script: Video script
            scenes: Visual scenes

        Returns:
            Production notes with timing and requirements
        """
        pass

    @abstractmethod
    def validate_narrative_flow(
        self,
        script: str,
        viral_strategy: Dict[str, Any]
    ) -> QualityMetrics:
        """
        Validate narrative structure and flow.

        Args:
            script: Script to validate
            viral_strategy: Viral strategy to check against

        Returns:
            Quality metrics for narrative flow
        """
        pass


# Factory for creating gatekeeper instances
class GatekeeperFactory:
    """Factory for creating and managing gatekeeper instances."""

    _gatekeepers: Dict[str, BaseGatekeeper] = {}

    @classmethod
    def register_gatekeeper(cls, name: str, gatekeeper: BaseGatekeeper):
        """Register a gatekeeper instance."""
        cls._gatekeepers[name] = gatekeeper

    @classmethod
    def get_gatekeeper(cls, name: str) -> Optional[BaseGatekeeper]:
        """Get a gatekeeper instance by name."""
        return cls._gatekeepers.get(name)

    @classmethod
    def get_all_gatekeepers(cls) -> Dict[str, BaseGatekeeper]:
        """Get all registered gatekeepers."""
        return cls._gatekeepers.copy()

    @classmethod
    def reset(cls):
        """Reset all gatekeepers (mainly for testing)."""
        for gatekeeper in cls._gatekeepers.values():
            gatekeeper.reset()

    @classmethod
    def clear(cls):
        """Clear all registered gatekeepers."""
        cls._gatekeepers.clear()
