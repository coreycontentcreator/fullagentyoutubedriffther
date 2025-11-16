"""
Quality Validator - Cross-module quality validation
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class QualityValidator:
    """
    Validates quality across all modules
    """

    def __init__(self, threshold: float = 9.0):
        """Initialize quality validator"""
        self.threshold = threshold
        logger.info(f"Quality Validator initialized (threshold: {threshold})")

    async def validate_package(
        self,
        research: Any,
        viral: Any,
        content: Any
    ) -> Dict[str, float]:
        """Validate complete package"""
        scores = {
            "research": getattr(research, 'quality_score', 8.0),
            "viral": getattr(viral, 'virality_score', 8.0),
            "content": content.get('quality_score', 8.0) if isinstance(content, dict) else 8.0
        }

        overall = sum(scores.values()) / len(scores)
        scores['overall'] = overall

        passes = overall >= self.threshold
        logger.info(f"Validation: {overall:.1f}/10 - {'PASS' if passes else 'NEEDS IMPROVEMENT'}")

        return scores
