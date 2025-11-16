"""
Retention Optimizer Subagent
Maximizes viewer retention through strategic content placement
"""

from typing import Dict, List, Any, Optional


class RetentionOptimizer:
    """
    Optimizes content for maximum viewer retention
    """

    def __init__(self):
        self.critical_moments = self._initialize_critical_moments()

    def _initialize_critical_moments(self) -> Dict[int, str]:
        """Initialize critical retention moments (seconds from start)"""
        return {
            3: "Initial hook - stop scrolling",
            15: "Value promise - why stay",
            30: "First retention loop",
            60: "One minute mark - critical drop point",
            120: "Two minute mark - pattern interrupt needed",
            180: "Three minute mark - mid-roll hook",
            300: "Five minute mark - re-engagement",
            420: "Seven minute mark - build to climax",
            600: "Ten minute mark - maintain momentum"
        }

    def analyze_retention_risk(
        self,
        video_duration_seconds: int,
        content_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze retention risks in video structure

        Args:
            video_duration_seconds: Video duration
            content_structure: Video structure

        Returns:
            Risk analysis with recommendations
        """
        risks = []

        # Check critical moments
        for timestamp, requirement in self.critical_moments.items():
            if timestamp < video_duration_seconds:
                # Check if there's content addressing this moment
                has_element = self._check_moment_coverage(timestamp, content_structure)
                if not has_element:
                    risks.append({
                        'timestamp': timestamp,
                        'timestamp_formatted': self._format_timestamp(timestamp),
                        'risk_level': 'HIGH' if timestamp <= 60 else 'MEDIUM',
                        'missing_element': requirement,
                        'recommendation': f"Add {requirement} at {self._format_timestamp(timestamp)}"
                    })

        # Analyze pacing
        pacing_analysis = self._analyze_pacing(video_duration_seconds, content_structure)

        # Check for dead zones (segments without engagement elements)
        dead_zones = self._identify_dead_zones(content_structure)

        return {
            'video_duration': video_duration_seconds,
            'retention_risks': risks,
            'pacing_analysis': pacing_analysis,
            'dead_zones': dead_zones,
            'overall_risk_level': self._calculate_overall_risk(risks, dead_zones)
        }

    def generate_retention_strategy(
        self,
        video_duration_minutes: int,
        content_type: str = "documentary"
    ) -> Dict[str, Any]:
        """
        Generate complete retention strategy for video

        Args:
            video_duration_minutes: Video duration
            content_type: Type of content

        Returns:
            Retention strategy with timed elements
        """
        duration_seconds = video_duration_minutes * 60

        # Calculate optimal hook intervals (every 2-3 minutes)
        hook_interval = 150 if content_type == "educational" else 120  # seconds
        hook_placements = list(range(0, duration_seconds, hook_interval))

        # Generate strategy
        strategy = {
            'video_duration_minutes': video_duration_minutes,
            'content_type': content_type,
            'retention_elements': []
        }

        # Opening (0-15s)
        strategy['retention_elements'].append({
            'time': '0:00-0:15',
            'element_type': 'opening_hook',
            'purpose': 'Stop scrolling and capture attention',
            'techniques': [
                'Pattern interrupt (visual/audio)',
                'Provocative question or statement',
                'Show most compelling visual',
                'Create immediate curiosity gap'
            ],
            'priority': 'CRITICAL'
        })

        # Value promise (15-45s)
        strategy['retention_elements'].append({
            'time': '0:15-0:45',
            'element_type': 'value_promise',
            'purpose': 'Clarify what viewer will gain',
            'techniques': [
                'State clear benefit',
                'Preview conclusion/revelation',
                'Establish credibility',
                'Set expectations'
            ],
            'priority': 'CRITICAL'
        })

        # Mid-roll hooks
        for i, timestamp in enumerate(hook_placements[1:], 1):
            if timestamp < duration_seconds:
                strategy['retention_elements'].append({
                    'time': self._format_timestamp(timestamp),
                    'element_type': 'mid_roll_hook',
                    'purpose': 'Re-engage viewers and prevent drop-off',
                    'techniques': [
                        'Pattern interruption',
                        'Tease upcoming content',
                        'Surprising fact or reveal',
                        'Format change'
                    ],
                    'priority': 'HIGH'
                })

        # Climax (70-80% mark)
        climax_time = int(duration_seconds * 0.75)
        strategy['retention_elements'].append({
            'time': self._format_timestamp(climax_time),
            'element_type': 'climax',
            'purpose': 'Deliver on promise and peak engagement',
            'techniques': [
                'Main revelation/answer',
                'Emotional peak',
                'Visual spectacle',
                'Satisfying conclusion to setup'
            ],
            'priority': 'HIGH'
        })

        # CTA (90-100% mark)
        cta_time = int(duration_seconds * 0.92)
        strategy['retention_elements'].append({
            'time': self._format_timestamp(cta_time),
            'element_type': 'call_to_action',
            'purpose': 'Convert viewers to subscribers/engagement',
            'techniques': [
                'Natural CTA tied to value',
                'Suggest next video',
                'Prompt for comments',
                'Thank and reward viewer'
            ],
            'priority': 'MEDIUM'
        })

        return strategy

    def optimize_content_pacing(
        self,
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimize pacing of content segments

        Args:
            segments: List of content segments

        Returns:
            Pacing optimization recommendations
        """
        if not segments:
            return {'error': 'No segments provided'}

        recommendations = []

        for i, segment in enumerate(segments):
            duration = segment.get('duration', 0)
            segment_type = segment.get('type', 'unknown')

            # Check segment duration
            if duration > 180:  # Over 3 minutes
                recommendations.append({
                    'segment': i,
                    'issue': f'Segment too long ({duration}s)',
                    'recommendation': 'Split segment or add pattern interrupt',
                    'priority': 'HIGH'
                })

            # Check for variety
            if i > 0:
                prev_type = segments[i-1].get('type', 'unknown')
                if prev_type == segment_type:
                    recommendations.append({
                        'segment': i,
                        'issue': f'Repetitive segment type ({segment_type})',
                        'recommendation': 'Vary content type for engagement',
                        'priority': 'MEDIUM'
                    })

        return {
            'segments_analyzed': len(segments),
            'recommendations': recommendations,
            'pacing_score': self._calculate_pacing_score(segments, recommendations)
        }

    def suggest_pattern_interruptions(
        self,
        video_duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """
        Suggest where to place pattern interruptions

        Args:
            video_duration_minutes: Video duration

        Returns:
            List of suggested interruption points
        """
        duration_seconds = video_duration_minutes * 60
        interrupt_interval = 120  # Every 2 minutes

        interruptions = []

        for timestamp in range(interrupt_interval, duration_seconds, interrupt_interval):
            interruptions.append({
                'timestamp': self._format_timestamp(timestamp),
                'timestamp_seconds': timestamp,
                'interruption_types': [
                    'Visual format change (e.g., animation, chart, B-roll)',
                    'Tone shift (serious to humorous or vice versa)',
                    'Unexpected sound effect or music change',
                    'Direct address to camera',
                    'Surprising fact or statistic',
                    'Quick demonstration or example'
                ],
                'purpose': 'Reset attention and maintain engagement',
                'implementation': 'Choose 1-2 techniques that fit content naturally'
            })

        return interruptions

    def _check_moment_coverage(self, timestamp: int, structure: Dict[str, Any]) -> bool:
        """Check if a critical moment is covered in structure"""
        # Simplified check - in production, would analyze actual structure
        segments = structure.get('segments', [])
        return len(segments) > 0  # Placeholder

    def _analyze_pacing(self, duration: int, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content pacing"""
        segments = structure.get('segments', [])

        if not segments:
            return {'score': 5.0, 'message': 'No segments to analyze'}

        # Calculate average segment length
        avg_length = duration / len(segments) if len(segments) > 0 else duration

        # Ideal segment length: 60-180 seconds
        if 60 <= avg_length <= 180:
            score = 9.0
            message = 'Excellent pacing'
        elif 30 <= avg_length <= 240:
            score = 7.0
            message = 'Good pacing'
        else:
            score = 5.0
            message = 'Pacing needs optimization'

        return {
            'score': score,
            'message': message,
            'avg_segment_length': round(avg_length, 1),
            'segment_count': len(segments),
            'ideal_range': '60-180 seconds per segment'
        }

    def _identify_dead_zones(self, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify segments with low engagement potential"""
        segments = structure.get('segments', [])
        dead_zones = []

        for i, segment in enumerate(segments):
            engagement_score = segment.get('engagement_score', 5.0)
            if engagement_score < 6.0:
                dead_zones.append({
                    'segment': i,
                    'segment_name': segment.get('name', f'Segment {i}'),
                    'engagement_score': engagement_score,
                    'issue': 'Low engagement potential',
                    'fix': 'Add hook, story element, or surprising fact'
                })

        return dead_zones

    def _calculate_overall_risk(
        self,
        risks: List[Dict[str, Any]],
        dead_zones: List[Dict[str, Any]]
    ) -> str:
        """Calculate overall retention risk level"""
        high_risks = sum(1 for r in risks if r['risk_level'] == 'HIGH')

        if high_risks >= 3 or len(dead_zones) >= 3:
            return 'HIGH'
        elif high_risks >= 1 or len(dead_zones) >= 1:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _calculate_pacing_score(
        self,
        segments: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]]
    ) -> float:
        """Calculate pacing score 0-10"""
        if not segments:
            return 5.0

        base_score = 8.0
        high_priority_issues = sum(1 for r in recommendations if r['priority'] == 'HIGH')
        medium_priority_issues = sum(1 for r in recommendations if r['priority'] == 'MEDIUM')

        score = base_score - (high_priority_issues * 1.5) - (medium_priority_issues * 0.5)
        return max(0.0, min(10.0, score))

    def _format_timestamp(self, seconds: int) -> str:
        """Format seconds to MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
