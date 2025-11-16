"""
Vector Database Interface

Provides interface for storing and retrieving viral strategies,
patterns, and learned knowledge using vector embeddings.

Author: AI Research Team
Date: November 2025
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ViralTier(Enum):
    """Tier classification for viral videos."""
    GOLD = "gold"      # 1M+ views, 10%+ engagement, 60%+ retention
    SILVER = "silver"  # 500K+ views, 7%+ engagement, 50%+ retention
    BRONZE = "bronze"  # 100K+ views, 5%+ engagement, 40%+ retention
    UNCLASSIFIED = "unclassified"


@dataclass
class ViralStrategy:
    """Viral strategy data structure."""
    id: str
    video_url: str
    title: str
    topic: str
    tier: ViralTier
    metrics: Dict[str, float]  # views, engagement, retention
    hooks: List[str]
    psychology_triggers: List[str]
    structure: Dict[str, Any]
    patterns: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Vector database search result."""
    item: Dict[str, Any]
    score: float
    distance: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class VectorDatabaseInterface(ABC):
    """
    Abstract interface for vector database operations.

    Supports storing and retrieving:
    - Viral strategies (successful video patterns)
    - Research insights
    - Content patterns
    - Learning data
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the vector database.

        Args:
            config: Database configuration

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def store_viral_strategy(
        self,
        strategy: ViralStrategy,
        embedding: Optional[List[float]] = None
    ) -> str:
        """
        Store a viral strategy in the database.

        Args:
            strategy: Viral strategy to store
            embedding: Optional pre-computed embedding

        Returns:
            Strategy ID
        """
        pass

    @abstractmethod
    def search_similar_strategies(
        self,
        query: str,
        tier: Optional[ViralTier] = None,
        topic: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search for similar viral strategies.

        Args:
            query: Search query
            tier: Filter by viral tier
            topic: Filter by topic
            limit: Maximum results to return

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    def get_strategy_by_id(self, strategy_id: str) -> Optional[ViralStrategy]:
        """
        Retrieve a specific strategy by ID.

        Args:
            strategy_id: Strategy ID

        Returns:
            ViralStrategy or None if not found
        """
        pass

    @abstractmethod
    def get_strategies_by_tier(
        self,
        tier: ViralTier,
        limit: int = 50
    ) -> List[ViralStrategy]:
        """
        Get all strategies of a specific tier.

        Args:
            tier: Viral tier to filter by
            limit: Maximum results

        Returns:
            List of strategies
        """
        pass

    @abstractmethod
    def store_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        embedding: Optional[List[float]] = None
    ) -> str:
        """
        Store a content pattern.

        Args:
            pattern_type: Type of pattern (hook, structure, trigger)
            pattern_data: Pattern data
            embedding: Optional pre-computed embedding

        Returns:
            Pattern ID
        """
        pass

    @abstractmethod
    def search_patterns(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search for similar patterns.

        Args:
            query: Search query
            pattern_type: Filter by pattern type
            limit: Maximum results

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    def update_strategy_metrics(
        self,
        strategy_id: str,
        new_metrics: Dict[str, float]
    ) -> bool:
        """
        Update metrics for an existing strategy.

        Args:
            strategy_id: Strategy ID
            new_metrics: Updated metrics

        Returns:
            True if update successful
        """
        pass

    @abstractmethod
    def delete_strategy(self, strategy_id: str) -> bool:
        """
        Delete a strategy from the database.

        Args:
            strategy_id: Strategy ID

        Returns:
            True if deletion successful
        """
        pass

    @abstractmethod
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.

        Returns:
            Statistics including count by tier, topics, etc.
        """
        pass

    @abstractmethod
    def clear_collection(self, confirm: bool = False) -> bool:
        """
        Clear all data from the collection.

        Args:
            confirm: Must be True to proceed

        Returns:
            True if cleared successfully
        """
        pass


class MockVectorDatabase(VectorDatabaseInterface):
    """
    Mock implementation of vector database for development and testing.

    Stores data in memory without actual vector operations.
    """

    def __init__(self):
        self.strategies: Dict[str, ViralStrategy] = {}
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.initialized = False

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize mock database."""
        self.initialized = True
        return True

    def store_viral_strategy(
        self,
        strategy: ViralStrategy,
        embedding: Optional[List[float]] = None
    ) -> str:
        """Store strategy in memory."""
        self.strategies[strategy.id] = strategy
        return strategy.id

    def search_similar_strategies(
        self,
        query: str,
        tier: Optional[ViralTier] = None,
        topic: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search strategies (simplified)."""
        results = []
        for strategy in self.strategies.values():
            if tier and strategy.tier != tier:
                continue
            if topic and strategy.topic != topic:
                continue

            # Simple keyword matching
            score = 0.5
            if query.lower() in strategy.title.lower():
                score += 0.3
            if query.lower() in strategy.topic.lower():
                score += 0.2

            results.append(SearchResult(
                item=strategy.__dict__,
                score=score,
                distance=1.0 - score
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def get_strategy_by_id(self, strategy_id: str) -> Optional[ViralStrategy]:
        """Get strategy by ID."""
        return self.strategies.get(strategy_id)

    def get_strategies_by_tier(
        self,
        tier: ViralTier,
        limit: int = 50
    ) -> List[ViralStrategy]:
        """Get strategies by tier."""
        strategies = [s for s in self.strategies.values() if s.tier == tier]
        return strategies[:limit]

    def store_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        embedding: Optional[List[float]] = None
    ) -> str:
        """Store pattern in memory."""
        pattern_id = f"{pattern_type}_{len(self.patterns)}"
        self.patterns[pattern_id] = {
            "type": pattern_type,
            "data": pattern_data,
            "id": pattern_id
        }
        return pattern_id

    def search_patterns(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search patterns (simplified)."""
        results = []
        for pattern in self.patterns.values():
            if pattern_type and pattern["type"] != pattern_type:
                continue

            results.append(SearchResult(
                item=pattern["data"],
                score=0.7,
                distance=0.3
            ))

        return results[:limit]

    def update_strategy_metrics(
        self,
        strategy_id: str,
        new_metrics: Dict[str, float]
    ) -> bool:
        """Update strategy metrics."""
        if strategy_id in self.strategies:
            self.strategies[strategy_id].metrics.update(new_metrics)
            return True
        return False

    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete strategy."""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            return True
        return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        tier_counts = {}
        for strategy in self.strategies.values():
            tier_counts[strategy.tier.value] = tier_counts.get(strategy.tier.value, 0) + 1

        return {
            "total_strategies": len(self.strategies),
            "total_patterns": len(self.patterns),
            "tier_distribution": tier_counts
        }

    def clear_collection(self, confirm: bool = False) -> bool:
        """Clear all data."""
        if confirm:
            self.strategies.clear()
            self.patterns.clear()
            return True
        return False
