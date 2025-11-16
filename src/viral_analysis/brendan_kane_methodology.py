"""
Brendan Kane Viral Methodology Implementation
Based on "One Million Followers" and viral content principles
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ViralPrinciple(Enum):
    """Core viral principles from Brendan Kane"""
    HOOK_FIRST_3_SECONDS = "hook_first_3_seconds"
    VALUE_IN_FIRST_15_SECONDS = "value_in_first_15_seconds"
    PATTERN_INTERRUPTION = "pattern_interruption"
    EMOTIONAL_RESONANCE = "emotional_resonance"
    SOCIAL_CURRENCY = "social_currency"
    SHAREABILITY = "shareability"
    RETENTION_LOOPS = "retention_loops"
    CALL_TO_ACTION = "call_to_action"


@dataclass
class ViralMetrics:
    """Viral performance metrics"""
    hook_strength: float  # 0-10
    value_delivery: float  # 0-10
    emotional_impact: float  # 0-10
    shareability: float  # 0-10
    retention_potential: float  # 0-10
    overall_viral_score: float  # 0-10


class BrendanKaneMethodology:
    """
    Implementation of Brendan Kane's viral content methodology
    Focuses on rapid growth, engagement, and viral mechanics
    """

    def __init__(self):
        self.principles = self._initialize_principles()

    def _initialize_principles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize viral principles with guidelines"""
        return {
            ViralPrinciple.HOOK_FIRST_3_SECONDS.value: {
                'name': 'Hook in First 3 Seconds',
                'description': 'Capture attention immediately to stop scrolling',
                'guidelines': [
                    'Start with visual/verbal pattern interrupt',
                    'Use unexpected statement or question',
                    'Show most compelling visual immediately',
                    'Create immediate curiosity gap'
                ],
                'examples': [
                    'Open with shocking statistic',
                    'Start with controversial statement',
                    'Show unexpected visual',
                    'Ask provocative question'
                ],
                'weight': 10.0
            },
            ViralPrinciple.VALUE_IN_FIRST_15_SECONDS.value: {
                'name': 'Value in First 15 Seconds',
                'description': 'Clearly communicate what viewer will gain',
                'guidelines': [
                    'State clear benefit/learning outcome',
                    'Promise transformation or insight',
                    'Show preview of conclusion',
                    'Establish credibility quickly'
                ],
                'examples': [
                    '"In the next 10 minutes, you\'ll learn..."',
                    '"I\'m going to show you exactly how..."',
                    '"Here\'s what most people get wrong..."'
                ],
                'weight': 9.5
            },
            ViralPrinciple.PATTERN_INTERRUPTION.value: {
                'name': 'Pattern Interruption',
                'description': 'Break expected patterns every 2-3 minutes',
                'guidelines': [
                    'Change visual format',
                    'Insert unexpected element',
                    'Shift tone or pace',
                    'Reveal surprising information'
                ],
                'examples': [
                    'Sudden format change',
                    'Unexpected sound effect',
                    'Visual surprise',
                    'Tone shift'
                ],
                'weight': 8.5
            },
            ViralPrinciple.EMOTIONAL_RESONANCE.value: {
                'name': 'Emotional Resonance',
                'description': 'Create strong emotional connection',
                'guidelines': [
                    'Target specific emotions (awe, curiosity, surprise)',
                    'Use relatable scenarios',
                    'Create empathy through storytelling',
                    'Build emotional arc'
                ],
                'examples': [
                    'Personal transformation story',
                    'Relatable struggle',
                    'Moment of revelation',
                    'Inspiring outcome'
                ],
                'weight': 9.0
            },
            ViralPrinciple.SOCIAL_CURRENCY.value: {
                'name': 'Social Currency',
                'description': 'Make viewers look good for sharing',
                'guidelines': [
                    'Provide insider knowledge',
                    'Share counter-intuitive insights',
                    'Give "smart" talking points',
                    'Create identity association'
                ],
                'examples': [
                    'Non-obvious insights',
                    'Expert-level knowledge',
                    'Trend forecasting',
                    'Exclusive information'
                ],
                'weight': 8.0
            },
            ViralPrinciple.SHAREABILITY.value: {
                'name': 'Shareability',
                'description': 'Design content to be easily shared',
                'guidelines': [
                    'Create shareable moments',
                    'Include quotable statements',
                    'Design for screenshot/clip',
                    'Make message clear and concise'
                ],
                'examples': [
                    'Quotable one-liners',
                    'Visual infographic moments',
                    'Surprising statistics',
                    'Controversial but defensible claims'
                ],
                'weight': 8.5
            },
            ViralPrinciple.RETENTION_LOOPS.value: {
                'name': 'Retention Loops',
                'description': 'Keep viewers watching throughout',
                'guidelines': [
                    'Tease upcoming content',
                    'Create open loops',
                    'Use callbacks to earlier points',
                    'Build to climax'
                ],
                'examples': [
                    '"Wait until you see what happens next..."',
                    '"Remember what I said earlier? Here\'s why..."',
                    '"The best part is coming..."',
                    'Progressive revelation'
                ],
                'weight': 9.0
            },
            ViralPrinciple.CALL_TO_ACTION.value: {
                'name': 'Call to Action',
                'description': 'Guide viewer to next action',
                'guidelines': [
                    'Clear, specific CTA',
                    'Explain benefit of action',
                    'Make action easy',
                    'Create urgency'
                ],
                'examples': [
                    '"Comment below if you..."',
                    '"Share this with someone who..."',
                    '"Subscribe for..."',
                    '"Watch this next video to..."'
                ],
                'weight': 7.5
            }
        }

    def analyze_viral_potential(self, content: Dict[str, Any]) -> ViralMetrics:
        """
        Analyze content for viral potential using Brendan Kane methodology

        Args:
            content: Dictionary with content details (script, hooks, structure)

        Returns:
            ViralMetrics with detailed scoring
        """
        script = content.get('script', '')
        hooks = content.get('hooks', [])
        structure = content.get('structure', {})

        # Analyze hook strength (first 3-15 seconds)
        hook_strength = self._analyze_hook_strength(hooks, script)

        # Analyze value delivery
        value_delivery = self._analyze_value_delivery(script)

        # Analyze emotional impact
        emotional_impact = self._analyze_emotional_impact(script, structure)

        # Analyze shareability
        shareability = self._analyze_shareability(content)

        # Analyze retention potential
        retention_potential = self._analyze_retention(structure, script)

        # Calculate overall score (weighted average)
        overall_score = (
            hook_strength * 0.25 +
            value_delivery * 0.20 +
            emotional_impact * 0.20 +
            shareability * 0.15 +
            retention_potential * 0.20
        )

        return ViralMetrics(
            hook_strength=round(hook_strength, 2),
            value_delivery=round(value_delivery, 2),
            emotional_impact=round(emotional_impact, 2),
            shareability=round(shareability, 2),
            retention_potential=round(retention_potential, 2),
            overall_viral_score=round(overall_score, 2)
        )

    def _analyze_hook_strength(self, hooks: List[Dict[str, Any]], script: str) -> float:
        """Analyze hook quality (0-10)"""
        if not hooks:
            return 5.0

        # Check for strong hook elements
        score = 5.0

        hook_text = hooks[0].get('hook_text', '') if hooks else ''
        combined = (hook_text + ' ' + script[:500]).lower()

        # Positive indicators
        if any(word in combined for word in ['what if', 'imagine', 'secret', 'nobody tells']):
            score += 1.0
        if any(word in combined for word in ['discover', 'revealed', 'truth', 'exposed']):
            score += 0.5
        if len(hook_text) < 100:  # Concise hook
            score += 0.5
        if 'psychology_triggers' in hooks[0] and len(hooks[0]['psychology_triggers']) >= 2:
            score += 1.0

        # Check for question in hook
        if '?' in hook_text:
            score += 0.5

        return min(score, 10.0)

    def _analyze_value_delivery(self, script: str) -> float:
        """Analyze value delivery in first 15 seconds (0-10)"""
        opening = script[:500].lower()
        score = 5.0

        # Look for value propositions
        value_phrases = [
            'you will learn', 'i\'ll show you', 'you\'ll discover',
            'here\'s how', 'this is how', 'the way to',
            'you\'ll understand', 'you can', 'you\'ll be able'
        ]

        if any(phrase in opening for phrase in value_phrases):
            score += 2.0

        # Look for specificity
        if any(word in opening for word in ['exactly', 'specifically', 'precisely']):
            score += 1.0

        # Look for timeframe
        if any(word in opening for word in ['minutes', 'today', 'now', 'immediately']):
            score += 1.0

        # Check for credibility markers
        if any(word in opening for word in ['research', 'study', 'expert', 'proven']):
            score += 1.0

        return min(score, 10.0)

    def _analyze_emotional_impact(self, script: str, structure: Dict[str, Any]) -> float:
        """Analyze emotional resonance (0-10)"""
        score = 5.0
        script_lower = script.lower()

        # Emotional words
        emotion_words = [
            'amazing', 'shocking', 'incredible', 'stunning', 'revolutionary',
            'breakthrough', 'transformed', 'powerful', 'fascinating', 'remarkable',
            'surprising', 'extraordinary', 'unbelievable'
        ]

        emotion_count = sum(1 for word in emotion_words if word in script_lower)
        score += min(emotion_count * 0.3, 2.0)

        # Story elements
        if any(word in script_lower for word in ['story', 'when i', 'imagine', 'picture this']):
            score += 1.5

        # Personal connection
        if any(word in script_lower for word in ['you', 'your', 'yourself']):
            score += 1.0

        # Transformation arc
        if 'transformation' in structure or any(word in script_lower for word in ['before', 'after', 'changed']):
            score += 1.5

        return min(score, 10.0)

    def _analyze_shareability(self, content: Dict[str, Any]) -> float:
        """Analyze shareability (0-10)"""
        score = 5.0
        script = content.get('script', '').lower()

        # Quotable elements
        if '"' in script or '\'' in script:
            score += 1.0

        # Statistics/numbers (shareable facts)
        import re
        numbers = re.findall(r'\d+%|\d+x|\d+ million|\d+ billion', script)
        score += min(len(numbers) * 0.5, 2.0)

        # Controversial/surprising elements
        if any(word in script for word in ['wrong about', 'myth', 'actually', 'truth']):
            score += 1.5

        # Social currency
        if any(word in script for word in ['secret', 'insider', 'expert', 'exclusive']):
            score += 1.0

        # Clear message
        if len(script) > 500:  # Substantial content
            score += 0.5

        return min(score, 10.0)

    def _analyze_retention(self, structure: Dict[str, Any], script: str) -> float:
        """Analyze retention potential (0-10)"""
        score = 5.0

        # Check for retention loops
        script_lower = script.lower()
        loop_phrases = [
            'wait until', 'coming up', 'in a moment', 'you\'ll see',
            'later', 'but first', 'remember when', 'as i mentioned'
        ]

        loop_count = sum(1 for phrase in loop_phrases if phrase in script_lower)
        score += min(loop_count * 0.5, 2.0)

        # Check for pattern interruptions
        if 'pattern_interruptions' in structure:
            score += min(len(structure['pattern_interruptions']) * 0.5, 2.0)

        # Check for pacing (sections/segments)
        if 'segments' in structure:
            segment_count = len(structure['segments'])
            if 3 <= segment_count <= 7:  # Good pacing
                score += 1.5

        # Mystery/questions
        question_count = script.count('?')
        score += min(question_count * 0.2, 1.0)

        return min(score, 10.0)

    def generate_optimization_recommendations(
        self,
        metrics: ViralMetrics,
        content: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate specific recommendations to improve viral potential

        Args:
            metrics: Current viral metrics
            content: Content to optimize

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        # Hook recommendations
        if metrics.hook_strength < 8.0:
            recommendations.append({
                'category': 'Hook',
                'priority': 'HIGH',
                'issue': f'Hook strength is {metrics.hook_strength}/10',
                'recommendation': 'Strengthen opening hook with pattern interrupt and curiosity gap',
                'examples': [
                    'Start with shocking statistic',
                    'Open with controversial question',
                    'Use unexpected visual or sound'
                ]
            })

        # Value delivery recommendations
        if metrics.value_delivery < 8.0:
            recommendations.append({
                'category': 'Value Delivery',
                'priority': 'HIGH',
                'issue': f'Value delivery is {metrics.value_delivery}/10',
                'recommendation': 'Clarify value proposition in first 15 seconds',
                'examples': [
                    'State exactly what viewers will learn',
                    'Promise specific transformation',
                    'Show credibility markers early'
                ]
            })

        # Emotional impact recommendations
        if metrics.emotional_impact < 7.5:
            recommendations.append({
                'category': 'Emotional Impact',
                'priority': 'MEDIUM',
                'issue': f'Emotional impact is {metrics.emotional_impact}/10',
                'recommendation': 'Increase emotional resonance through storytelling',
                'examples': [
                    'Add personal story or case study',
                    'Use more emotional language',
                    'Create relatable scenarios'
                ]
            })

        # Shareability recommendations
        if metrics.shareability < 7.5:
            recommendations.append({
                'category': 'Shareability',
                'priority': 'MEDIUM',
                'issue': f'Shareability is {metrics.shareability}/10',
                'recommendation': 'Add shareable moments and social currency',
                'examples': [
                    'Include quotable one-liners',
                    'Add surprising statistics',
                    'Create screenshot-worthy visuals'
                ]
            })

        # Retention recommendations
        if metrics.retention_potential < 8.0:
            recommendations.append({
                'category': 'Retention',
                'priority': 'HIGH',
                'issue': f'Retention potential is {metrics.retention_potential}/10',
                'recommendation': 'Add retention loops and pattern interruptions',
                'examples': [
                    'Tease upcoming content',
                    'Create open loops',
                    'Add surprise elements every 2-3 minutes'
                ]
            })

        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: priority_order[x['priority']])

        return recommendations

    def get_viral_framework(self) -> Dict[str, Any]:
        """Get complete viral framework structure"""
        return {
            'principles': self.principles,
            'methodology': 'Brendan Kane One Million Followers',
            'key_metrics': [
                'Hook strength (0-3 seconds)',
                'Value delivery (0-15 seconds)',
                'Emotional resonance',
                'Shareability',
                'Retention loops'
            ],
            'success_criteria': {
                'hook_strength': 8.0,
                'value_delivery': 8.0,
                'emotional_impact': 7.5,
                'shareability': 7.5,
                'retention_potential': 8.0,
                'overall_viral_score': 8.5
            }
        }
