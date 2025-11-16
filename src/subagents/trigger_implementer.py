"""
Trigger Implementer Subagent
Applies psychology triggers throughout script at optimal moments
"""

from typing import Dict, List, Any, Optional
import sys
sys.path.append('/home/user/fullagentyoutubedriffther/src')

from viral_analysis.psychology_trigger_detector import PsychologyTriggerDetector, PsychologyTrigger


class TriggerImplementer:
    """
    Implements psychological triggers strategically throughout content
    """

    def __init__(self):
        self.detector = PsychologyTriggerDetector()

    def create_trigger_timeline(
        self,
        video_duration_minutes: int,
        content_type: str = "documentary",
        target_audience: str = "general"
    ) -> Dict[str, Any]:
        """
        Create timeline showing when to apply each trigger

        Args:
            video_duration_minutes: Video duration
            content_type: Type of content
            target_audience: Target audience

        Returns:
            Timeline with trigger placements
        """
        plan = self.detector.generate_trigger_plan(
            video_duration_minutes,
            content_type,
            target_audience
        )

        # Create detailed timeline
        timeline = []
        for segment_name, segment_data in plan['segments'].items():
            for trigger in segment_data['recommended_triggers'][:2]:  # Top 2 per segment
                timeline.append({
                    'time_range': f"{segment_data['start_time']:.1f} - {segment_data['end_time']:.1f} min",
                    'segment': segment_name,
                    'trigger': trigger['trigger'],
                    'trigger_name': trigger['name'],
                    'implementation': trigger['implementation_guide'],
                    'examples': trigger['examples'][:2]
                })

        return {
            'video_duration': video_duration_minutes,
            'total_triggers': len(timeline),
            'timeline': timeline,
            'coverage': self._calculate_coverage(timeline, video_duration_minutes)
        }

    def implement_triggers_in_script(
        self,
        script: str,
        triggers_to_apply: List[str],
        implementation_style: str = "subtle"
    ) -> Dict[str, Any]:
        """
        Suggest specific trigger implementations in existing script

        Args:
            script: Existing script
            triggers_to_apply: List of trigger keys to apply
            implementation_style: 'subtle' or 'overt'

        Returns:
            Script with trigger suggestions
        """
        suggestions = []
        script_parts = script.split('\n\n')  # Split into paragraphs

        for i, part in enumerate(script_parts):
            if i < len(triggers_to_apply):
                trigger_key = triggers_to_apply[i]
                trigger_def = self.detector.get_trigger_definition(trigger_key)

                if trigger_def:
                    suggestions.append({
                        'paragraph_index': i,
                        'original_text': part[:100] + '...' if len(part) > 100 else part,
                        'trigger_to_add': trigger_key,
                        'trigger_name': trigger_def.name,
                        'implementation_examples': trigger_def.examples[:2],
                        'placement_guide': trigger_def.implementation_guide
                    })

        return {
            'script_length': len(script),
            'paragraphs_analyzed': len(script_parts),
            'trigger_suggestions': suggestions,
            'implementation_style': implementation_style
        }

    def optimize_trigger_distribution(
        self,
        detected_triggers: List[Dict[str, Any]],
        video_duration: int
    ) -> Dict[str, Any]:
        """
        Analyze and optimize trigger distribution

        Args:
            detected_triggers: Currently detected triggers
            video_duration: Video duration in minutes

        Returns:
            Optimization suggestions
        """
        # Calculate diversity
        diversity_score = self.detector.calculate_trigger_diversity(detected_triggers)

        # Identify gaps
        all_triggers = set(self.detector.triggers.keys())
        used_triggers = set(t['trigger'] for t in detected_triggers)
        missing_triggers = all_triggers - used_triggers

        # Calculate optimal density (triggers per minute)
        current_density = len(detected_triggers) / video_duration if video_duration > 0 else 0
        optimal_density = 2.5  # 2-3 triggers per minute for engagement

        recommendations = []

        if diversity_score < 5.0:
            recommendations.append({
                'type': 'diversity',
                'priority': 'HIGH',
                'message': f'Low trigger diversity ({diversity_score}/10). Add more variety.',
                'suggested_triggers': list(missing_triggers)[:5]
            })

        if current_density < 2.0:
            recommendations.append({
                'type': 'density',
                'priority': 'MEDIUM',
                'message': f'Low trigger density ({current_density:.1f} per min). Add more triggers.',
                'target_density': optimal_density
            })

        if current_density > 4.0:
            recommendations.append({
                'type': 'density',
                'priority': 'LOW',
                'message': f'High trigger density ({current_density:.1f} per min). May feel overwhelming.',
                'target_density': optimal_density
            })

        return {
            'diversity_score': diversity_score,
            'trigger_density': round(current_density, 2),
            'optimal_density': optimal_density,
            'missing_triggers': list(missing_triggers),
            'recommendations': recommendations
        }

    def _calculate_coverage(self, timeline: List[Dict[str, Any]], duration: int) -> Dict[str, Any]:
        """Calculate trigger coverage across video"""
        if not timeline:
            return {'percentage': 0, 'gaps': []}

        covered_minutes = set()
        for item in timeline:
            time_str = item['time_range']
            start = float(time_str.split('-')[0].strip().replace('min', ''))
            end = float(time_str.split('-')[1].strip().replace('min', ''))
            for minute in range(int(start), int(end) + 1):
                covered_minutes.add(minute)

        coverage_pct = len(covered_minutes) / duration * 100 if duration > 0 else 0

        return {
            'percentage': round(coverage_pct, 1),
            'covered_minutes': len(covered_minutes),
            'total_minutes': duration
        }

    def get_trigger_combinations(self) -> Dict[str, List[str]]:
        """Get effective trigger combinations"""
        return {
            'opening_power_combo': [
                PsychologyTrigger.CURIOSITY_GAP.value,
                PsychologyTrigger.NOVELTY.value,
                PsychologyTrigger.SOCIAL_PROOF.value
            ],
            'retention_combo': [
                PsychologyTrigger.PATTERN_INTERRUPTION.value,
                PsychologyTrigger.MYSTERY.value,
                PsychologyTrigger.STORYTELLING.value
            ],
            'engagement_combo': [
                PsychologyTrigger.CONTROVERSY.value,
                PsychologyTrigger.IDENTITY.value,
                PsychologyTrigger.TRIBAL_BELONGING.value
            ],
            'conversion_combo': [
                PsychologyTrigger.SCARCITY.value,
                PsychologyTrigger.URGENCY.value,
                PsychologyTrigger.RECIPROCITY.value
            ]
        }
