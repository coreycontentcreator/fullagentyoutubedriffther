"""
Virality Scorer Subagent
Predicts viral potential on 1-10 scale
"""

from typing import Dict, List, Any, Optional
import sys
sys.path.append('/home/user/fullagentyoutubedriffther/src')

from viral_analysis.brendan_kane_methodology import BrendanKaneMethodology, ViralMetrics


class ViralityScorer:
    """
    Scores content for viral potential using multiple methodologies
    """

    def __init__(self):
        self.brendan_kane = BrendanKaneMethodology()
        self.scoring_weights = self._initialize_scoring_weights()

    def _initialize_scoring_weights(self) -> Dict[str, float]:
        """Initialize scoring criteria weights"""
        return {
            'hook_strength': 0.25,
            'value_delivery': 0.15,
            'emotional_impact': 0.20,
            'psychology_triggers': 0.15,
            'shareability': 0.10,
            'retention_potential': 0.10,
            'production_quality': 0.05
        }

    def score_content(
        self,
        content: Dict[str, Any],
        detailed: bool = True
    ) -> Dict[str, Any]:
        """
        Score content for viral potential

        Args:
            content: Content to score (script, hooks, structure, etc.)
            detailed: Include detailed breakdown

        Returns:
            Viral score with breakdown
        """
        # Use Brendan Kane methodology as base
        kane_metrics = self.brendan_kane.analyze_viral_potential(content)

        # Calculate component scores
        scores = {
            'hook_strength': kane_metrics.hook_strength,
            'value_delivery': kane_metrics.value_delivery,
            'emotional_impact': kane_metrics.emotional_impact,
            'psychology_triggers': self._score_psychology_triggers(content),
            'shareability': kane_metrics.shareability,
            'retention_potential': kane_metrics.retention_potential,
            'production_quality': self._score_production_quality(content)
        }

        # Calculate weighted overall score
        overall_score = sum(
            scores[criterion] * weight
            for criterion, weight in self.scoring_weights.items()
        )

        result = {
            'overall_viral_score': round(overall_score, 2),
            'confidence': self._calculate_confidence(content),
            'rating': self._get_rating(overall_score),
            'scores': {k: round(v, 2) for k, v in scores.items()}
        }

        if detailed:
            result['detailed_analysis'] = {
                'strengths': self._identify_strengths(scores),
                'weaknesses': self._identify_weaknesses(scores),
                'recommendations': self.brendan_kane.generate_optimization_recommendations(
                    kane_metrics,
                    content
                ),
                'viral_potential_tier': self._predict_tier(overall_score),
                'expected_performance': self._estimate_performance(overall_score)
            }

        return result

    def score_hook(self, hook: str) -> Dict[str, Any]:
        """
        Score a hook for viral potential

        Args:
            hook: Hook text to score

        Returns:
            Hook score with breakdown
        """
        scores = {}

        hook_lower = hook.lower()

        # Curiosity gap (0-10)
        curiosity_words = ['what', 'why', 'how', 'secret', 'truth', 'nobody', 'hidden']
        scores['curiosity_gap'] = min(sum(2 for w in curiosity_words if w in hook_lower), 10)

        # Emotional trigger (0-10)
        emotion_words = ['shocking', 'amazing', 'incredible', 'surprising', 'revolutionary', 'changed']
        scores['emotional_trigger'] = min(sum(2 for w in emotion_words if w in hook_lower), 10)

        # Clarity (0-10)
        word_count = len(hook.split())
        scores['clarity'] = 10 if word_count <= 15 else max(10 - (word_count - 15) * 0.3, 5)

        # Specificity (0-10)
        numbers = sum(1 for char in hook if char.isdigit())
        scores['specificity'] = min(6 + numbers, 10)

        # Pattern interrupt (0-10)
        interrupt_elements = ['?', '!', 'but', 'however', 'what if']
        scores['pattern_interrupt'] = min(sum(2 for e in interrupt_elements if e in hook_lower), 10)

        overall = sum(scores.values()) / len(scores)

        return {
            'overall_hook_score': round(overall, 2),
            'scores': {k: round(v, 2) for k, v in scores.items()},
            'rating': self._get_rating(overall),
            'recommendations': self._generate_hook_recommendations(scores, overall)
        }

    def predict_performance(
        self,
        viral_score: float,
        channel_size: Optional[int] = None,
        niche: str = "general"
    ) -> Dict[str, Any]:
        """
        Predict video performance based on viral score

        Args:
            viral_score: Viral score (0-10)
            channel_size: Current subscriber count
            niche: Content niche

        Returns:
            Performance predictions
        """
        # Base multipliers by score
        score_multipliers = {
            (9.5, 10.0): {'views': 10.0, 'engagement': 12.0, 'growth': 15.0},
            (9.0, 9.5): {'views': 7.0, 'engagement': 9.0, 'growth': 10.0},
            (8.5, 9.0): {'views': 5.0, 'engagement': 7.0, 'growth': 7.0},
            (8.0, 8.5): {'views': 3.5, 'engagement': 5.0, 'growth': 5.0},
            (7.0, 8.0): {'views': 2.0, 'engagement': 3.0, 'growth': 3.0},
            (6.0, 7.0): {'views': 1.5, 'engagement': 2.0, 'growth': 2.0},
            (0.0, 6.0): {'views': 1.0, 'engagement': 1.0, 'growth': 1.0}
        }

        # Find multiplier
        multiplier = {'views': 1.0, 'engagement': 1.0, 'growth': 1.0}
        for (low, high), mult in score_multipliers.items():
            if low <= viral_score < high:
                multiplier = mult
                break

        # Calculate predictions
        base_views = channel_size or 10000  # Default baseline
        predicted_views = int(base_views * multiplier['views'])

        return {
            'viral_score': viral_score,
            'predictions': {
                'expected_views': {
                    'low': int(predicted_views * 0.7),
                    'mid': predicted_views,
                    'high': int(predicted_views * 1.5)
                },
                'expected_engagement_rate': {
                    'low': round(3.0 * multiplier['engagement'] * 0.8, 2),
                    'mid': round(3.0 * multiplier['engagement'], 2),
                    'high': round(3.0 * multiplier['engagement'] * 1.3, 2)
                },
                'subscriber_growth': {
                    'low': int(base_views * 0.01 * multiplier['growth'] * 0.7),
                    'mid': int(base_views * 0.01 * multiplier['growth']),
                    'high': int(base_views * 0.01 * multiplier['growth'] * 1.5)
                }
            },
            'confidence_level': 'high' if viral_score >= 8.5 else 'medium' if viral_score >= 7.0 else 'low',
            'notes': f'Predictions based on {niche} niche and viral score of {viral_score}/10'
        }

    def compare_scores(
        self,
        content_versions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare viral scores of multiple content versions

        Args:
            content_versions: List of content variants to compare

        Returns:
            Comparison analysis
        """
        scores = []

        for i, content in enumerate(content_versions):
            score_result = self.score_content(content, detailed=False)
            scores.append({
                'version': i + 1,
                'overall_score': score_result['overall_viral_score'],
                'rating': score_result['rating'],
                'component_scores': score_result['scores']
            })

        # Sort by score
        scores.sort(key=lambda x: x['overall_score'], reverse=True)

        return {
            'versions_compared': len(content_versions),
            'ranked_scores': scores,
            'best_version': scores[0]['version'],
            'score_range': {
                'highest': scores[0]['overall_score'],
                'lowest': scores[-1]['overall_score'],
                'difference': round(scores[0]['overall_score'] - scores[-1]['overall_score'], 2)
            },
            'recommendation': f"Version {scores[0]['version']} has highest viral potential"
        }

    def _score_psychology_triggers(self, content: Dict[str, Any]) -> float:
        """Score psychology trigger usage"""
        triggers = content.get('psychology_triggers', [])
        if not triggers:
            return 5.0

        # Score based on quantity and diversity
        trigger_count = len(triggers)
        unique_triggers = len(set(t.get('trigger', '') for t in triggers))

        # Optimal: 8-12 triggers with good diversity
        quantity_score = min(trigger_count / 10 * 10, 10)
        diversity_score = min(unique_triggers / 8 * 10, 10)

        return (quantity_score * 0.6 + diversity_score * 0.4)

    def _score_production_quality(self, content: Dict[str, Any]) -> float:
        """Score production quality indicators"""
        # This would analyze visual descriptions, audio notes, etc.
        # For now, return baseline
        production_notes = content.get('production_notes', {})
        if production_notes:
            return 8.0
        return 6.0

    def _calculate_confidence(self, content: Dict[str, Any]) -> str:
        """Calculate confidence in score"""
        has_script = bool(content.get('script'))
        has_hooks = bool(content.get('hooks'))
        has_structure = bool(content.get('structure'))

        confidence_score = sum([has_script, has_hooks, has_structure])

        if confidence_score >= 3:
            return 'high'
        elif confidence_score >= 2:
            return 'medium'
        else:
            return 'low'

    def _get_rating(self, score: float) -> str:
        """Get rating from score"""
        if score >= 9.5:
            return 'Exceptional - Viral potential'
        elif score >= 9.0:
            return 'Excellent - High viral potential'
        elif score >= 8.0:
            return 'Very Good - Good viral potential'
        elif score >= 7.0:
            return 'Good - Moderate viral potential'
        elif score >= 6.0:
            return 'Average - Some viral elements'
        else:
            return 'Needs Improvement'

    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify strengths from scores"""
        strengths = []
        for criterion, score in scores.items():
            if score >= 8.0:
                strengths.append(f"Strong {criterion.replace('_', ' ')} ({score:.1f}/10)")
        return strengths or ['No major strengths identified']

    def _identify_weaknesses(self, scores: Dict[str, float]) -> List[str]:
        """Identify weaknesses from scores"""
        weaknesses = []
        for criterion, score in scores.items():
            if score < 7.0:
                weaknesses.append(f"Weak {criterion.replace('_', ' ')} ({score:.1f}/10)")
        return weaknesses or ['No major weaknesses']

    def _predict_tier(self, viral_score: float) -> str:
        """Predict viral tier from score"""
        if viral_score >= 9.5:
            return 'Likely Gold Tier'
        elif viral_score >= 8.5:
            return 'Likely Silver Tier'
        elif viral_score >= 7.5:
            return 'Likely Bronze Tier'
        else:
            return 'Below Bronze Tier'

    def _estimate_performance(self, viral_score: float) -> Dict[str, str]:
        """Estimate performance ranges"""
        if viral_score >= 9.0:
            return {
                'views': '500K - 5M+',
                'engagement': '8-12%',
                'retention': '60-75%'
            }
        elif viral_score >= 8.0:
            return {
                'views': '100K - 1M',
                'engagement': '6-9%',
                'retention': '50-65%'
            }
        elif viral_score >= 7.0:
            return {
                'views': '50K - 500K',
                'engagement': '4-7%',
                'retention': '40-55%'
            }
        else:
            return {
                'views': '10K - 100K',
                'engagement': '2-5%',
                'retention': '30-45%'
            }

    def _generate_hook_recommendations(self, scores: Dict[str, float], overall: float) -> List[str]:
        """Generate hook improvement recommendations"""
        recs = []

        if scores.get('curiosity_gap', 0) < 7:
            recs.append('Add stronger curiosity gap (use "what", "why", "secret")')

        if scores.get('emotional_trigger', 0) < 7:
            recs.append('Increase emotional impact with power words')

        if scores.get('clarity', 0) < 8:
            recs.append('Simplify hook - aim for under 15 words')

        if scores.get('pattern_interrupt', 0) < 7:
            recs.append('Add pattern interrupt (question mark, "but", unexpected element)')

        if not recs and overall < 9:
            recs.append('Good hook! Consider A/B testing variations')

        return recs
