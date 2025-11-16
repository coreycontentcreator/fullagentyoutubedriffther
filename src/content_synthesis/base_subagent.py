"""
Base Subagent Class
Foundation for all Content Synthesis subagents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SubagentResult:
    """Standard result format for all subagents"""
    success: bool
    data: Dict[str, Any]
    quality_score: float
    processing_time: float
    errors: list
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'data': self.data,
            'quality_score': self.quality_score,
            'processing_time': self.processing_time,
            'errors': self.errors,
            'metadata': self.metadata
        }


class BaseSubagent(ABC):
    """
    Base class for all subagents in the Content Synthesis system
    Provides common functionality and enforces standard interface
    """

    def __init__(self, name: str, anthropic_client, config):
        """
        Initialize subagent

        Args:
            name: Subagent name
            anthropic_client: AnthropicClient instance
            config: Configuration object
        """
        self.name = name
        self.anthropic_client = anthropic_client
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{name}")

        self.logger.info(f"{name} subagent initialized")

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> SubagentResult:
        """
        Process input and generate output
        Must be implemented by each subagent

        Args:
            input_data: Input data for processing

        Returns:
            SubagentResult with processed data
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data
        Must be implemented by each subagent

        Args:
            input_data: Input to validate

        Returns:
            True if valid, raises ValueError if not
        """
        pass

    @abstractmethod
    def validate_output(self, output_data: Dict[str, Any]) -> float:
        """
        Validate and score output quality
        Must be implemented by each subagent

        Args:
            output_data: Output to validate

        Returns:
            Quality score (0.0-10.0)
        """
        pass

    def create_result(
            self,
            success: bool,
            data: Dict[str, Any],
            quality_score: float,
            processing_time: float,
            errors: Optional[list] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> SubagentResult:
        """
        Create standardized result

        Args:
            success: Whether processing succeeded
            data: Processed data
            quality_score: Quality score (0.0-10.0)
            processing_time: Processing time in seconds
            errors: List of errors
            metadata: Additional metadata

        Returns:
            SubagentResult
        """
        return SubagentResult(
            success=success,
            data=data,
            quality_score=quality_score,
            processing_time=processing_time,
            errors=errors or [],
            metadata=metadata or {}
        )

    def log_processing(self, stage: str, details: str):
        """Log processing stage"""
        self.logger.info(f"[{self.name}] {stage}: {details}")

    def log_error(self, error: str):
        """Log error"""
        self.logger.error(f"[{self.name}] ERROR: {error}")

    def log_warning(self, warning: str):
        """Log warning"""
        self.logger.warning(f"[{self.name}] WARNING: {warning}")


class SynchronousSubagent(BaseSubagent):
    """
    Synchronous version of BaseSubagent for simpler implementations
    """

    @abstractmethod
    def process_sync(self, input_data: Dict[str, Any]) -> SubagentResult:
        """
        Synchronous processing method
        Must be implemented by each subagent

        Args:
            input_data: Input data for processing

        Returns:
            SubagentResult
        """
        pass

    async def process(self, input_data: Dict[str, Any]) -> SubagentResult:
        """
        Async wrapper for synchronous processing
        Calls process_sync internally

        Args:
            input_data: Input data

        Returns:
            SubagentResult
        """
        return self.process_sync(input_data)
