"""
Strategy Curator Subagent
Manages viral strategy library with tiered storage
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from pathlib import Path


class StrategyCurator:
    """
    Curates and manages viral strategy library
    Organizes strategies by tier (Gold/Silver/Bronze)
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or '/home/user/fullagentyoutubedriffther/data/strategies'
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        self.strategies = self._load_strategies()

    def _load_strategies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load strategies from storage"""
        strategies = {'gold': [], 'silver': [], 'bronze': []}

        for tier in ['gold', 'silver', 'bronze']:
            file_path = Path(self.storage_path) / f'{tier}_strategies.json'
            if file_path.exists():
                with open(file_path, 'r') as f:
                    strategies[tier] = json.load(f)

        return strategies

    def _save_strategies(self):
        """Save strategies to storage"""
        for tier, tier_strategies in self.strategies.items():
            file_path = Path(self.storage_path) / f'{tier}_strategies.json'
            with open(file_path, 'w') as f:
                json.dump(tier_strategies, f, indent=2)

    def add_strategy(
        self,
        strategy: Dict[str, Any],
        tier: str,
        auto_save: bool = True
    ) -> Dict[str, Any]:
        """
        Add new strategy to library

        Args:
            strategy: Strategy data
            tier: Tier classification (gold/silver/bronze)
            auto_save: Auto-save to disk

        Returns:
            Added strategy with metadata
        """
        if tier not in ['gold', 'silver', 'bronze']:
            return {'error': f'Invalid tier: {tier}'}

        # Add metadata
        strategy['added_date'] = datetime.now().isoformat()
        strategy['tier'] = tier
        strategy['id'] = f"{tier}_{len(self.strategies[tier]) + 1}_{int(datetime.now().timestamp())}"

        # Add to library
        self.strategies[tier].append(strategy)

        if auto_save:
            self._save_strategies()

        return {
            'status': 'added',
            'tier': tier,
            'strategy_id': strategy['id'],
            'total_in_tier': len(self.strategies[tier])
        }

    def get_strategies_by_tier(self, tier: str) -> List[Dict[str, Any]]:
        """Get all strategies for a tier"""
        return self.strategies.get(tier, [])

    def search_strategies(
        self,
        topic: Optional[str] = None,
        min_views: Optional[int] = None,
        pattern_type: Optional[str] = None,
        tier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search strategies by criteria

        Args:
            topic: Filter by topic
            min_views: Minimum view count
            pattern_type: Filter by pattern type
            tier: Filter by tier

        Returns:
            Matching strategies
        """
        results = []

        # Determine which tiers to search
        tiers_to_search = [tier] if tier else ['gold', 'silver', 'bronze']

        for search_tier in tiers_to_search:
            for strategy in self.strategies.get(search_tier, []):
                # Apply filters
                if topic and topic.lower() not in strategy.get('topic', '').lower():
                    continue

                if min_views and strategy.get('views', 0) < min_views:
                    continue

                if pattern_type and strategy.get('pattern_type') != pattern_type:
                    continue

                results.append(strategy)

        return results

    def get_top_strategies(
        self,
        count: int = 10,
        sort_by: str = 'views'
    ) -> List[Dict[str, Any]]:
        """
        Get top performing strategies

        Args:
            count: Number of strategies to return
            sort_by: Sort criteria (views, engagement_rate, viral_score)

        Returns:
            Top strategies
        """
        all_strategies = []
        for tier in ['gold', 'silver', 'bronze']:
            all_strategies.extend(self.strategies[tier])

        # Sort by criteria
        all_strategies.sort(
            key=lambda x: x.get(sort_by, 0),
            reverse=True
        )

        return all_strategies[:count]

    def get_strategy_recommendations(
        self,
        content_type: str,
        target_audience: str,
        video_duration: int
    ) -> List[Dict[str, Any]]:
        """
        Get recommended strategies based on content parameters

        Args:
            content_type: Type of content
            target_audience: Target audience
            video_duration: Video duration in minutes

        Returns:
            Recommended strategies
        """
        recommendations = []

        # Search for similar content
        for tier in ['gold', 'silver', 'bronze']:
            for strategy in self.strategies[tier]:
                score = 0

                # Match content type
                if strategy.get('content_type', '').lower() == content_type.lower():
                    score += 3

                # Match similar duration (within 30%)
                strategy_duration = strategy.get('duration_minutes', 0)
                if strategy_duration > 0:
                    duration_diff = abs(strategy_duration - video_duration) / video_duration
                    if duration_diff < 0.3:
                        score += 2

                # Match audience
                if target_audience.lower() in strategy.get('target_audience', '').lower():
                    score += 2

                # Higher tier = higher score
                tier_bonus = {'gold': 3, 'silver': 2, 'bronze': 1}
                score += tier_bonus.get(tier, 0)

                if score >= 3:  # Minimum relevance threshold
                    recommendations.append({
                        'strategy': strategy,
                        'relevance_score': score,
                        'tier': tier
                    })

        # Sort by relevance
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)

        return recommendations[:5]  # Top 5

    def analyze_library_stats(self) -> Dict[str, Any]:
        """Get statistics about strategy library"""
        stats = {
            'total_strategies': sum(len(strategies) for strategies in self.strategies.values()),
            'by_tier': {
                tier: len(strategies)
                for tier, strategies in self.strategies.items()
            },
            'avg_performance': {},
            'common_patterns': self._identify_common_patterns()
        }

        # Calculate average performance by tier
        for tier, strategies in self.strategies.items():
            if strategies:
                stats['avg_performance'][tier] = {
                    'avg_views': sum(s.get('views', 0) for s in strategies) / len(strategies),
                    'avg_engagement': sum(s.get('engagement_rate', 0) for s in strategies) / len(strategies),
                    'avg_viral_score': sum(s.get('viral_score', 0) for s in strategies) / len(strategies)
                }

        return stats

    def export_strategy(self, strategy_id: str, format: str = 'json') -> Dict[str, Any]:
        """
        Export a specific strategy

        Args:
            strategy_id: Strategy ID
            format: Export format (json, markdown)

        Returns:
            Exported strategy
        """
        # Find strategy
        strategy = None
        for tier in ['gold', 'silver', 'bronze']:
            for s in self.strategies[tier]:
                if s.get('id') == strategy_id:
                    strategy = s
                    break

        if not strategy:
            return {'error': 'Strategy not found'}

        if format == 'markdown':
            return self._export_as_markdown(strategy)
        else:
            return strategy

    def create_strategy_from_video(
        self,
        video_analysis: Dict[str, Any],
        tier: str
    ) -> Dict[str, Any]:
        """
        Create strategy entry from video analysis

        Args:
            video_analysis: Analyzed video data
            tier: Tier classification

        Returns:
            Created strategy
        """
        strategy = {
            'video_id': video_analysis.get('video_id'),
            'video_url': video_analysis.get('video_url'),
            'topic': video_analysis.get('metadata', {}).get('title', 'Unknown'),
            'views': video_analysis.get('performance_metrics', {}).get('views', 0),
            'engagement_rate': video_analysis.get('performance_metrics', {}).get('engagement_rate', 0),
            'viral_score': video_analysis.get('viral_score', 0),
            'duration_minutes': video_analysis.get('metadata', {}).get('duration', 0) // 60,
            'successful_elements': {
                'hooks': video_analysis.get('detailed_analysis', {}).get('hook_analysis', {}),
                'psychology_triggers': video_analysis.get('detailed_analysis', {}).get('viral_elements', {}).get('psychology_triggers_detected', []),
                'pattern_type': 'unknown'
            },
            'replication_guide': {
                'hook_style': 'Analyze actual hook from video',
                'structure': 'Extract from video structure',
                'key_moments': 'Identify peak engagement moments'
            }
        }

        return self.add_strategy(strategy, tier)

    def _identify_common_patterns(self) -> Dict[str, Any]:
        """Identify common patterns across all strategies"""
        all_strategies = []
        for tier in ['gold', 'silver', 'bronze']:
            all_strategies.extend(self.strategies[tier])

        if not all_strategies:
            return {}

        # Count pattern types
        from collections import Counter
        pattern_types = Counter(s.get('pattern_type', 'unknown') for s in all_strategies)

        return {
            'most_common_patterns': pattern_types.most_common(5),
            'total_analyzed': len(all_strategies)
        }

    def _export_as_markdown(self, strategy: Dict[str, Any]) -> str:
        """Export strategy as markdown"""
        md = f"""# Viral Strategy: {strategy.get('topic', 'Unknown')}

## Performance Metrics
- **Views**: {strategy.get('views', 0):,}
- **Engagement Rate**: {strategy.get('engagement_rate', 0):.2f}%
- **Viral Score**: {strategy.get('viral_score', 0):.1f}/10
- **Tier**: {strategy.get('tier', 'unknown').upper()}

## Successful Elements
{json.dumps(strategy.get('successful_elements', {}), indent=2)}

## Replication Guide
{json.dumps(strategy.get('replication_guide', {}), indent=2)}

---
*Strategy ID: {strategy.get('id', 'unknown')}*
*Added: {strategy.get('added_date', 'unknown')}*
"""
        return md
