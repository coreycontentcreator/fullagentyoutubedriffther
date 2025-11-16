"""
Learning System - Continuous learning from successful patterns
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class SuccessPattern:
    """Successful pattern to learn from"""
    id: str
    type: str  # hook, trigger, structure, etc.
    content: str
    metrics: Dict[str, float]  # views, engagement, retention, etc.
    context: Dict[str, Any]
    learned_at: str
    effectiveness_score: float


class LearningSystem:
    """
    Continuous learning system that improves from successful outputs
    """

    def __init__(self, storage_path: str = "data/learning"):
        """
        Initialize learning system

        Args:
            storage_path: Path to store learning data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.patterns: List[SuccessPattern] = []
        self.pattern_weights: Dict[str, float] = defaultdict(float)
        self.learning_history: List[Dict[str, Any]] = []

        self._load_from_disk()

        logger.info(f"Learning System initialized with {len(self.patterns)} patterns")

    def learn_from_success(
        self,
        pattern_type: str,
        content: str,
        metrics: Dict[str, float],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Learn from a successful pattern

        Args:
            pattern_type: Type of pattern (hook, trigger, etc.)
            content: Pattern content
            metrics: Success metrics
            context: Additional context

        Returns:
            Pattern ID
        """
        try:
            # Calculate effectiveness score
            effectiveness = self._calculate_effectiveness(metrics)

            pattern_id = f"{pattern_type}_{datetime.now().timestamp()}"

            pattern = SuccessPattern(
                id=pattern_id,
                type=pattern_type,
                content=content,
                metrics=metrics,
                context=context or {},
                learned_at=datetime.now().isoformat(),
                effectiveness_score=effectiveness
            )

            self.patterns.append(pattern)

            # Update weights
            self.pattern_weights[pattern_type] += effectiveness

            # Record learning event
            self.learning_history.append({
                'pattern_id': pattern_id,
                'type': pattern_type,
                'effectiveness': effectiveness,
                'timestamp': pattern.learned_at
            })

            logger.info(f"Learned pattern {pattern_id} (effectiveness: {effectiveness:.2f})")

            return pattern_id

        except Exception as e:
            logger.error(f"Failed to learn pattern: {e}")
            return ""

    def get_best_patterns(
        self,
        pattern_type: str,
        top_k: int = 10,
        min_effectiveness: float = 0.7
    ) -> List[SuccessPattern]:
        """
        Get best patterns of a type

        Args:
            pattern_type: Pattern type to retrieve
            top_k: Number of patterns to return
            min_effectiveness: Minimum effectiveness threshold

        Returns:
            List of best patterns
        """
        matching = [
            p for p in self.patterns
            if p.type == pattern_type and p.effectiveness_score >= min_effectiveness
        ]

        matching.sort(key=lambda x: x.effectiveness_score, reverse=True)
        return matching[:top_k]

    def get_pattern_recommendations(
        self,
        context: Dict[str, Any],
        pattern_type: Optional[str] = None
    ) -> List[SuccessPattern]:
        """
        Get pattern recommendations based on context

        Args:
            context: Current context
            pattern_type: Optional type filter

        Returns:
            Recommended patterns
        """
        candidates = self.patterns

        if pattern_type:
            candidates = [p for p in candidates if p.type == pattern_type]

        # Score by relevance to context
        scored = []
        for pattern in candidates:
            relevance = self._calculate_relevance(pattern, context)
            scored.append((pattern, pattern.effectiveness_score * relevance))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored[:10]]

    def _calculate_effectiveness(self, metrics: Dict[str, float]) -> float:
        """Calculate effectiveness score from metrics"""
        # Weighted scoring
        weights = {
            'views': 0.2,
            'engagement_rate': 0.3,
            'retention_rate': 0.3,
            'conversion_rate': 0.2
        }

        score = 0.0
        total_weight = 0.0

        for key, weight in weights.items():
            if key in metrics:
                # Normalize to 0-1 scale
                normalized = min(metrics[key] / 100.0 if metrics[key] > 1 else metrics[key], 1.0)
                score += normalized * weight
                total_weight += weight

        if total_weight > 0:
            return score / total_weight
        return 0.5

    def _calculate_relevance(
        self,
        pattern: SuccessPattern,
        context: Dict[str, Any]
    ) -> float:
        """Calculate how relevant a pattern is to current context"""
        relevance = 0.5  # Base relevance

        # Check for matching context elements
        pattern_context = pattern.context

        matches = 0
        total = 0

        for key in ['topic', 'audience', 'style', 'duration']:
            total += 1
            if (key in context and key in pattern_context and
                context[key] == pattern_context[key]):
                matches += 1

        if total > 0:
            relevance += 0.5 * (matches / total)

        return min(relevance, 1.0)

    def get_stats(self) -> Dict[str, Any]:
        """Get learning system statistics"""
        type_distribution = defaultdict(int)
        avg_effectiveness = defaultdict(list)

        for pattern in self.patterns:
            type_distribution[pattern.type] += 1
            avg_effectiveness[pattern.type].append(pattern.effectiveness_score)

        return {
            'total_patterns': len(self.patterns),
            'pattern_types': dict(type_distribution),
            'average_effectiveness': {
                ptype: sum(scores) / len(scores)
                for ptype, scores in avg_effectiveness.items()
            },
            'pattern_weights': dict(self.pattern_weights),
            'learning_events': len(self.learning_history)
        }

    def save_to_disk(self) -> bool:
        """Save learning data to disk"""
        try:
            data_file = self.storage_path / "learning_data.json"

            data = {
                'patterns': [asdict(p) for p in self.patterns],
                'weights': dict(self.pattern_weights),
                'history': self.learning_history
            }

            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved learning data: {len(self.patterns)} patterns")
            return True

        except Exception as e:
            logger.error(f"Failed to save learning data: {e}")
            return False

    def _load_from_disk(self) -> bool:
        """Load learning data from disk"""
        try:
            data_file = self.storage_path / "learning_data.json"
            if not data_file.exists():
                logger.info("No existing learning data found")
                return False

            with open(data_file, 'r') as f:
                data = json.load(f)

            # Reconstruct patterns
            self.patterns = [
                SuccessPattern(**p) for p in data.get('patterns', [])
            ]
            self.pattern_weights = defaultdict(float, data.get('weights', {}))
            self.learning_history = data.get('history', [])

            logger.info(f"Loaded learning data from disk")
            return True

        except Exception as e:
            logger.error(f"Failed to load learning data: {e}")
            return False
