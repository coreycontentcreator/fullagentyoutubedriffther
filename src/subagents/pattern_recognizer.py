"""
Pattern Recognizer Subagent
Identifies successful video structures and patterns
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import Counter


@dataclass
class VideoPattern:
    """Represents a successful video pattern"""
    pattern_type: str
    structure: List[str]
    avg_performance: Dict[str, float]
    usage_count: int
    success_rate: float


class PatternRecognizer:
    """
    Recognizes and catalogs successful video patterns
    """

    def __init__(self):
        self.known_patterns = self._initialize_known_patterns()

    def _initialize_known_patterns(self) -> Dict[str, VideoPattern]:
        """Initialize database of known successful patterns"""
        return {
            'hook_body_callback': VideoPattern(
                pattern_type='Hook-Body-Callback',
                structure=[
                    '1. Opening hook (0-15s)',
                    '2. Value promise (15-45s)',
                    '3. Main content with callbacks to hook',
                    '4. Callback to hook with answer',
                    '5. CTA and conclusion'
                ],
                avg_performance={'retention': 65.0, 'engagement': 8.5, 'viral_score': 8.0},
                usage_count=1000,
                success_rate=85.0
            ),
            'mystery_reveal': VideoPattern(
                pattern_type='Mystery-Reveal',
                structure=[
                    '1. Present mystery/question (0-30s)',
                    '2. Build context and suspense',
                    '3. Multiple mini-reveals',
                    '4. Big reveal at climax',
                    '5. Implications and conclusion'
                ],
                avg_performance={'retention': 70.0, 'engagement': 9.0, 'viral_score': 8.5},
                usage_count=800,
                success_rate=88.0
            ),
            'transformation_journey': VideoPattern(
                pattern_type='Transformation-Journey',
                structure=[
                    '1. Show end result (0-15s)',
                    '2. Flashback to beginning',
                    '3. Journey with obstacles',
                    '4. Breakthrough moment',
                    '5. Final transformation and takeaway'
                ],
                avg_performance={'retention': 68.0, 'engagement': 8.8, 'viral_score': 8.3},
                usage_count=600,
                success_rate=82.0
            ),
            'myth_busting': VideoPattern(
                pattern_type='Myth-Busting',
                structure=[
                    '1. State common belief (0-20s)',
                    '2. "But is it true?" moment',
                    '3. Present evidence against',
                    '4. Reveal the truth',
                    '5. Implications of new understanding'
                ],
                avg_performance={'retention': 66.0, 'engagement': 8.7, 'viral_score': 8.2},
                usage_count=750,
                success_rate=84.0
            ),
            'comparison_analysis': VideoPattern(
                pattern_type='Comparison-Analysis',
                structure=[
                    '1. Introduce two sides (0-30s)',
                    '2. Deep dive side A',
                    '3. Deep dive side B',
                    '4. Surprising comparison insights',
                    '5. Winner/conclusion with reasoning'
                ],
                avg_performance={'retention': 64.0, 'engagement': 8.3, 'viral_score': 7.8},
                usage_count=900,
                success_rate=80.0
            ),
            'story_insight': VideoPattern(
                pattern_type='Story-Insight',
                structure=[
                    '1. Start with compelling story (0-45s)',
                    '2. Continue story with tension',
                    '3. Pause for insight/analysis',
                    '4. Resume with new understanding',
                    '5. Conclude with universal takeaway'
                ],
                avg_performance={'retention': 69.0, 'engagement': 9.2, 'viral_score': 8.7},
                usage_count=500,
                success_rate=90.0
            )
        }

    def identify_pattern(self, video_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify which pattern a video structure matches

        Args:
            video_structure: Structure of the video

        Returns:
            Pattern match with confidence
        """
        segments = video_structure.get('segments', [])
        if not segments:
            return {'pattern': 'unknown', 'confidence': 0.0}

        # Analyze structure
        has_hook = any('hook' in str(s).lower() for s in segments)
        has_mystery = any('mystery' in str(s).lower() or 'question' in str(s).lower() for s in segments)
        has_transformation = any('transformation' in str(s).lower() or 'before' in str(s).lower() for s in segments)
        has_myth = any('myth' in str(s).lower() or 'wrong' in str(s).lower() or 'truth' in str(s).lower() for s in segments)
        has_comparison = any('vs' in str(s).lower() or 'versus' in str(s).lower() or 'compare' in str(s).lower() for s in segments)
        has_story = any('story' in str(s).lower() or 'narrative' in str(s).lower() for s in segments)

        # Match to pattern
        scores = {}

        if has_mystery:
            scores['mystery_reveal'] = 0.8
        if has_transformation:
            scores['transformation_journey'] = 0.85
        if has_myth:
            scores['myth_busting'] = 0.9
        if has_comparison:
            scores['comparison_analysis'] = 0.85
        if has_story:
            scores['story_insight'] = 0.8
        if has_hook and not scores:
            scores['hook_body_callback'] = 0.7

        if not scores:
            return {'pattern': 'custom', 'confidence': 0.5, 'message': 'Custom pattern detected'}

        best_pattern = max(scores.items(), key=lambda x: x[1])
        pattern_info = self.known_patterns.get(best_pattern[0])

        return {
            'pattern': best_pattern[0],
            'confidence': best_pattern[1],
            'pattern_info': pattern_info.__dict__ if pattern_info else None,
            'alternative_patterns': [{'pattern': k, 'confidence': v} for k, v in scores.items() if k != best_pattern[0]]
        }

    def suggest_optimal_pattern(
        self,
        content_summary: str,
        target_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Suggest best pattern based on content and goals

        Args:
            content_summary: Summary of content
            target_metrics: Target retention, engagement, etc.

        Returns:
            Recommended pattern
        """
        content_lower = content_summary.lower()

        # Analyze content characteristics
        is_educational = any(word in content_lower for word in ['learn', 'understand', 'explain', 'science'])
        is_controversial = any(word in content_lower for word in ['wrong', 'myth', 'truth', 'exposed'])
        is_narrative = any(word in content_lower for word in ['story', 'journey', 'experience'])
        needs_high_retention = target_metrics.get('retention', 0) > 65

        recommendations = []

        for pattern_key, pattern in self.known_patterns.items():
            score = 50.0  # Base score

            # Match pattern to content type
            if is_controversial and pattern_key == 'myth_busting':
                score += 30
            if is_narrative and pattern_key == 'story_insight':
                score += 25
            if is_educational and pattern_key in ['mystery_reveal', 'hook_body_callback']:
                score += 20

            # Match pattern to target metrics
            if needs_high_retention and pattern.avg_performance['retention'] > 65:
                score += 15

            # Factor in success rate
            score += pattern.success_rate * 0.3

            recommendations.append({
                'pattern': pattern_key,
                'pattern_info': pattern,
                'recommendation_score': min(score, 100),
                'reasoning': self._explain_recommendation(pattern_key, content_lower, target_metrics)
            })

        # Sort by score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)

        return {
            'top_recommendation': recommendations[0],
            'alternatives': recommendations[1:3],
            'all_patterns': self.known_patterns
        }

    def _explain_recommendation(
        self,
        pattern_key: str,
        content_lower: str,
        target_metrics: Dict[str, float]
    ) -> str:
        """Generate explanation for pattern recommendation"""
        reasons = []

        if pattern_key == 'mystery_reveal' and 'question' in content_lower:
            reasons.append("Content involves questions/mysteries")
        if pattern_key == 'myth_busting' and ('wrong' in content_lower or 'myth' in content_lower):
            reasons.append("Content challenges common beliefs")
        if pattern_key == 'story_insight' and 'story' in content_lower:
            reasons.append("Narrative content benefits from story structure")

        pattern = self.known_patterns.get(pattern_key)
        if pattern and pattern.avg_performance['retention'] >= target_metrics.get('retention', 60):
            reasons.append(f"Achieves target retention ({pattern.avg_performance['retention']}%)")

        return '; '.join(reasons) if reasons else "Good general fit"

    def analyze_successful_patterns(
        self,
        videos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze multiple videos to identify successful patterns

        Args:
            videos: List of video data

        Returns:
            Pattern analysis
        """
        if not videos:
            return {'error': 'No videos provided'}

        pattern_performance = {}

        for video in videos:
            pattern = self.identify_pattern(video.get('structure', {}))
            pattern_key = pattern['pattern']

            if pattern_key not in pattern_performance:
                pattern_performance[pattern_key] = {
                    'count': 0,
                    'total_views': 0,
                    'total_engagement': 0.0,
                    'total_retention': 0.0
                }

            pattern_performance[pattern_key]['count'] += 1
            pattern_performance[pattern_key]['total_views'] += video.get('views', 0)
            pattern_performance[pattern_key]['total_engagement'] += video.get('engagement_rate', 0)
            pattern_performance[pattern_key]['total_retention'] += video.get('retention_rate', 0)

        # Calculate averages
        for pattern_key, data in pattern_performance.items():
            count = data['count']
            data['avg_views'] = data['total_views'] / count if count > 0 else 0
            data['avg_engagement'] = data['total_engagement'] / count if count > 0 else 0
            data['avg_retention'] = data['total_retention'] / count if count > 0 else 0

        return {
            'videos_analyzed': len(videos),
            'patterns_found': len(pattern_performance),
            'pattern_performance': pattern_performance,
            'top_pattern': max(pattern_performance.items(), key=lambda x: x[1]['avg_views'])[0] if pattern_performance else None
        }

    def get_pattern_template(self, pattern_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed template for a specific pattern"""
        pattern = self.known_patterns.get(pattern_key)
        if not pattern:
            return None

        return {
            'pattern_type': pattern.pattern_type,
            'structure': pattern.structure,
            'expected_performance': pattern.avg_performance,
            'implementation_guide': self._get_implementation_guide(pattern_key),
            'examples': self._get_pattern_examples(pattern_key)
        }

    def _get_implementation_guide(self, pattern_key: str) -> List[str]:
        """Get implementation guide for pattern"""
        guides = {
            'mystery_reveal': [
                'Open with intriguing question',
                'Build tension throughout',
                'Use multiple small reveals',
                'Save biggest reveal for 70-80% mark',
                'Explain implications at end'
            ],
            'myth_busting': [
                'State myth clearly',
                'Show why people believe it',
                'Present counter-evidence',
                'Reveal truth dramatically',
                'Explain why myth persists'
            ]
        }
        return guides.get(pattern_key, ['Follow pattern structure'])

    def _get_pattern_examples(self, pattern_key: str) -> List[str]:
        """Get examples of pattern usage"""
        examples = {
            'mystery_reveal': [
                'Veritasium: "The Most Radioactive Places on Earth"',
                'Vsauce: "What is the Resolution of the Eye?"'
            ],
            'myth_busting': [
                'Mark Rober: "Debunking Viral TikTok Hacks"'
            ]
        }
        return examples.get(pattern_key, ['Pattern used in many top videos'])
