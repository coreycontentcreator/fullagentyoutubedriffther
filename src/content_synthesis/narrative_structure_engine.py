"""
Narrative Structure Engine
Ensures compelling story flow and optimal narrative progression
"""
import time
from typing import Dict, Any, List, Tuple
from .base_subagent import SynchronousSubagent, SubagentResult
import logging

logger = logging.getLogger(__name__)


class NarrativeStructureEngine(SynchronousSubagent):
    """
    Narrative Structure Engine Subagent
    Analyzes and optimizes narrative flow, pacing, and story structure
    """

    def __init__(self, anthropic_client, config):
        super().__init__("NarrativeStructureEngine", anthropic_client, config)

        self.system_prompt = """You are an expert storytelling consultant specializing in:
- Narrative structure and story arcs
- Pacing and tension management
- Character and theme development
- Documentary storytelling techniques
- Audience engagement through narrative

You ensure every story has a clear beginning, middle, and end with proper emotional progression."""

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        required_fields = ['script']

        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")

        return True

    def validate_output(self, output_data: Dict[str, Any]) -> float:
        """
        Validate narrative structure quality

        Criteria:
        - Has clear three-act structure
        - Proper pacing curve
        - Effective hooks and transitions
        - Emotional arc present
        - Tension management
        """
        score = 0.0
        max_score = 10.0

        # Check structure analysis (3 points)
        structure = output_data.get('structure_analysis', {})
        if structure:
            has_acts = 'acts' in structure
            has_arc = 'narrative_arc' in structure

            if has_acts and has_arc:
                score += 3.0
            elif has_acts or has_arc:
                score += 1.5

        # Check pacing analysis (2 points)
        pacing = output_data.get('pacing_analysis', {})
        if pacing and len(pacing) > 0:
            score += 2.0

        # Check hooks and transitions (2 points)
        hooks = output_data.get('hooks', [])
        transitions = output_data.get('transitions', [])

        if len(hooks) >= 3:
            score += 1.0
        if len(transitions) >= 5:
            score += 1.0

        # Check recommendations (2 points)
        recommendations = output_data.get('recommendations', [])
        if len(recommendations) >= 3:
            score += 2.0
        elif len(recommendations) >= 1:
            score += 1.0

        # Check overall quality score (1 point)
        if output_data.get('narrative_quality_score', 0) >= 7.0:
            score += 1.0

        return min(score, max_score)

    def process_sync(self, input_data: Dict[str, Any]) -> SubagentResult:
        """
        Analyze and optimize narrative structure

        Input data:
            - script: Complete script to analyze
            - target_audience: Target audience
            - video_duration: Target duration

        Returns:
            SubagentResult with narrative analysis and recommendations
        """
        start_time = time.time()

        try:
            # Validate input
            self.validate_input(input_data)

            self.log_processing("INPUT_VALIDATION", "Input data validated")

            # Extract parameters
            script = input_data['script']
            target_audience = input_data.get('target_audience', 'general')
            video_duration = input_data.get('video_duration', 15)

            # Analyze script structure
            structure_analysis = self._analyze_story_structure(script)

            self.log_processing("STRUCTURE", "Story structure analyzed")

            # Analyze pacing
            pacing_analysis = self._analyze_pacing(script, video_duration)

            self.log_processing("PACING", "Pacing analyzed")

            # Identify hooks and tension points
            hooks = self._identify_hooks(script)

            self.log_processing("HOOKS", f"Identified {len(hooks)} hooks")

            # Analyze transitions
            transitions = self._analyze_transitions(script)

            # Analyze emotional arc
            emotional_arc = self._analyze_emotional_arc(script)

            # Generate recommendations
            recommendations = self._generate_narrative_recommendations(
                structure_analysis,
                pacing_analysis,
                hooks,
                transitions,
                emotional_arc
            )

            self.log_processing("RECOMMENDATIONS", f"Generated {len(recommendations)} recommendations")

            # Calculate overall narrative quality score
            narrative_score = self._calculate_narrative_score(
                structure_analysis,
                pacing_analysis,
                hooks,
                transitions
            )

            # Prepare output
            output_data = {
                'structure_analysis': structure_analysis,
                'pacing_analysis': pacing_analysis,
                'hooks': hooks,
                'transitions': transitions,
                'emotional_arc': emotional_arc,
                'recommendations': recommendations,
                'narrative_quality_score': narrative_score,
                'strengths': self._identify_strengths(structure_analysis, pacing_analysis, hooks),
                'weaknesses': self._identify_weaknesses(structure_analysis, pacing_analysis, hooks)
            }

            # Validate output
            quality_score = self.validate_output(output_data)

            processing_time = time.time() - start_time

            self.log_processing("COMPLETION", f"Narrative analysis complete with quality score: {quality_score:.2f}")

            return self.create_result(
                success=True,
                data=output_data,
                quality_score=quality_score,
                processing_time=processing_time,
                metadata={
                    'narrative_score': narrative_score,
                    'hook_count': len(hooks)
                }
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.log_error(f"Narrative analysis failed: {str(e)}")

            return self.create_result(
                success=False,
                data={},
                quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)]
            )

    def _analyze_story_structure(self, script: str) -> Dict[str, Any]:
        """Analyze three-act structure and narrative arc"""

        word_count = len(script.split())

        # Identify acts based on content markers and position
        acts = {
            'act1': {
                'name': 'Setup',
                'start_position': 0,
                'end_position': int(word_count * 0.25),
                'purpose': 'Hook audience, establish topic, create questions'
            },
            'act2': {
                'name': 'Confrontation/Development',
                'start_position': int(word_count * 0.25),
                'end_position': int(word_count * 0.75),
                'purpose': 'Deep dive, present evidence, build tension'
            },
            'act3': {
                'name': 'Resolution',
                'start_position': int(word_count * 0.75),
                'end_position': word_count,
                'purpose': 'Climax, revelation, conclusion, CTA'
            }
        }

        # Identify narrative arc components
        has_hook = any(keyword in script[:500].lower() for keyword in ['imagine', 'what if', 'discover', 'shocking'])
        has_climax = any(keyword in script[-1000:].lower() for keyword in ['reveal', 'finally', 'conclusion', 'answer'])
        has_resolution = any(keyword in script[-500:].lower() for keyword in ['subscribe', 'next', 'summary'])

        narrative_arc = {
            'exposition': has_hook,
            'rising_action': len(script.split('\n\n')) > 10,  # Multiple sections
            'climax': has_climax,
            'falling_action': has_resolution,
            'resolution': has_resolution
        }

        completeness = sum(1 for v in narrative_arc.values() if v) / len(narrative_arc) * 100

        return {
            'acts': acts,
            'narrative_arc': narrative_arc,
            'completeness': round(completeness, 1),
            'structure_type': 'Three-Act Documentary Structure'
        }

    def _analyze_pacing(self, script: str, target_duration: int) -> Dict[str, Any]:
        """Analyze pacing and rhythm"""

        paragraphs = [p.strip() for p in script.split('\n\n') if p.strip()]

        # Calculate pacing metrics
        avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        para_length_variance = self._calculate_variance([len(p.split()) for p in paragraphs])

        # Ideal pacing: varied paragraph lengths, not too uniform
        pacing_variety_score = min(10, para_length_variance / 100)

        # Check for rhythm (short-long-short pattern)
        rhythm_score = self._analyze_rhythm([len(p.split()) for p in paragraphs])

        # Estimate speaking duration per section
        words_per_minute = 150
        section_durations = []

        words_per_section = len(script.split()) / len(paragraphs) if paragraphs else 0

        for i, para in enumerate(paragraphs):
            duration = len(para.split()) / words_per_minute
            section_durations.append({
                'section': i + 1,
                'duration_minutes': round(duration, 2),
                'word_count': len(para.split()),
                'pace': 'fast' if duration < 0.5 else 'moderate' if duration < 1.5 else 'slow'
            })

        return {
            'average_paragraph_length': round(avg_para_length, 1),
            'paragraph_count': len(paragraphs),
            'pacing_variety_score': round(pacing_variety_score, 1),
            'rhythm_score': round(rhythm_score, 1),
            'section_durations': section_durations,
            'overall_pace': 'balanced' if 3 <= pacing_variety_score <= 7 else 'needs_adjustment'
        }

    def _identify_hooks(self, script: str) -> List[Dict[str, Any]]:
        """Identify hooks and attention-grabbing moments"""

        hooks = []

        # Hook patterns
        hook_patterns = [
            ('question', ['?'], 'Rhetorical question'),
            ('curiosity', ['imagine', 'what if', 'discover', 'secret'], 'Curiosity trigger'),
            ('shock', ['shocking', 'unbelievable', 'never', 'always'], 'Shock value'),
            ('promise', ['learn', 'find out', 'reveal', 'show you'], 'Promise/benefit'),
            ('stats', ['%', 'million', 'billion', 'times'], 'Compelling statistics'),
        ]

        paragraphs = script.split('\n\n')

        for i, para in enumerate(paragraphs):
            para_lower = para.lower()

            for pattern_type, keywords, description in hook_patterns:
                if any(keyword in para_lower for keyword in keywords):
                    hooks.append({
                        'type': pattern_type,
                        'description': description,
                        'position': i,
                        'content_preview': para[:100] + '...' if len(para) > 100 else para,
                        'strength': self._estimate_hook_strength(para, pattern_type)
                    })
                    break  # Only categorize once per paragraph

        return hooks

    def _analyze_transitions(self, script: str) -> List[Dict[str, str]]:
        """Analyze transitions between sections"""

        transition_words = [
            'however', 'but', 'meanwhile', 'next', 'then', 'after',
            'before', 'now', 'finally', 'additionally', 'moreover',
            'therefore', 'thus', 'consequently'
        ]

        paragraphs = script.split('\n\n')
        transitions = []

        for i in range(len(paragraphs) - 1):
            current_para = paragraphs[i].lower()
            next_para = paragraphs[i + 1].lower()

            # Check for transition words
            transition_found = None
            for word in transition_words:
                if word in next_para[:100]:  # Check start of next paragraph
                    transition_found = word
                    break

            transitions.append({
                'from_section': i + 1,
                'to_section': i + 2,
                'transition_word': transition_found if transition_found else 'implicit',
                'quality': 'explicit' if transition_found else 'needs_improvement'
            })

        return transitions

    def _analyze_emotional_arc(self, script: str) -> Dict[str, Any]:
        """Analyze emotional progression throughout script"""

        # Simplified emotional analysis based on word choice
        sections = script.split('\n\n')

        emotional_progression = []

        for i, section in enumerate(sections):
            section_lower = section.lower()

            # Count positive/negative/neutral indicators
            positive_words = sum(section_lower.count(word) for word in ['amazing', 'incredible', 'breakthrough', 'success', 'solved'])
            negative_words = sum(section_lower.count(word) for word in ['problem', 'crisis', 'challenge', 'difficult', 'struggle'])
            tension_words = sum(section_lower.count(word) for word in ['but', 'however', 'yet', 'although', 'despite'])

            # Calculate emotional valence (-1 to 1)
            total_emotional = positive_words + negative_words + tension_words
            if total_emotional > 0:
                valence = (positive_words - negative_words) / total_emotional
            else:
                valence = 0

            emotional_progression.append({
                'section': i + 1,
                'valence': round(valence, 2),
                'tension': tension_words,
                'tone': 'positive' if valence > 0.3 else 'negative' if valence < -0.3 else 'neutral'
            })

        return {
            'progression': emotional_progression,
            'arc_type': self._classify_emotional_arc(emotional_progression),
            'peak_tension_section': max(emotional_progression, key=lambda x: x['tension'])['section']
        }

    def _classify_emotional_arc(self, progression: List[Dict[str, Any]]) -> str:
        """Classify the type of emotional arc"""

        if len(progression) < 3:
            return 'insufficient_data'

        start_valence = progression[0]['valence']
        mid_valence = progression[len(progression) // 2]['valence']
        end_valence = progression[-1]['valence']

        if start_valence < 0 and end_valence > 0:
            return 'redemption_arc'
        elif start_valence > 0 and end_valence < 0:
            return 'tragedy_arc'
        elif mid_valence < start_valence and mid_valence < end_valence:
            return 'u_shaped_arc'
        else:
            return 'progressive_arc'

    def _generate_narrative_recommendations(
            self,
            structure: Dict[str, Any],
            pacing: Dict[str, Any],
            hooks: List[Dict[str, Any]],
            transitions: List[Dict[str, str]],
            emotional_arc: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate recommendations for improving narrative"""

        recommendations = []

        # Structure recommendations
        if structure['completeness'] < 80:
            recommendations.append({
                'category': 'Structure',
                'priority': 'High',
                'issue': 'Incomplete narrative arc',
                'recommendation': 'Ensure all elements of story structure are present: exposition, rising action, climax, falling action, resolution'
            })

        # Hook recommendations
        hook_count = len(hooks)
        if hook_count < 3:
            recommendations.append({
                'category': 'Engagement',
                'priority': 'High',
                'issue': f'Only {hook_count} hooks identified',
                'recommendation': 'Add more hooks throughout the script (aim for one every 2 minutes)'
            })

        # Pacing recommendations
        if pacing['overall_pace'] == 'needs_adjustment':
            recommendations.append({
                'category': 'Pacing',
                'priority': 'Medium',
                'issue': 'Pacing lacks variety',
                'recommendation': 'Vary paragraph lengths - mix short punchy paragraphs with longer explanatory ones'
            })

        # Transition recommendations
        poor_transitions = sum(1 for t in transitions if t['quality'] == 'needs_improvement')
        if poor_transitions > len(transitions) * 0.5:
            recommendations.append({
                'category': 'Flow',
                'priority': 'Medium',
                'issue': 'Many transitions are implicit',
                'recommendation': 'Add explicit transition words/phrases to improve flow between sections'
            })

        # Emotional arc recommendations
        if emotional_arc['arc_type'] == 'insufficient_data':
            recommendations.append({
                'category': 'Emotional Impact',
                'priority': 'Low',
                'issue': 'Emotional progression unclear',
                'recommendation': 'Develop clearer emotional journey for the audience'
            })

        return recommendations

    def _calculate_narrative_score(
            self,
            structure: Dict[str, Any],
            pacing: Dict[str, Any],
            hooks: List[Dict[str, Any]],
            transitions: List[Dict[str, str]]
    ) -> float:
        """Calculate overall narrative quality score"""

        score = 0.0

        # Structure score (30%)
        score += (structure['completeness'] / 100) * 3.0

        # Pacing score (25%)
        pacing_score = min(10, pacing['pacing_variety_score'])
        score += (pacing_score / 10) * 2.5

        # Hooks score (25%)
        hook_score = min(10, len(hooks))
        score += (hook_score / 10) * 2.5

        # Transitions score (20%)
        good_transitions = sum(1 for t in transitions if t['quality'] == 'explicit')
        if transitions:
            transition_score = (good_transitions / len(transitions)) * 10
            score += (transition_score / 10) * 2.0

        return round(score, 1)

    def _estimate_hook_strength(self, content: str, hook_type: str) -> str:
        """Estimate the strength of a hook"""

        word_count = len(content.split())

        # Strong hooks are concise and at the beginning
        if hook_type == 'question' and word_count < 20:
            return 'strong'
        elif hook_type in ['curiosity', 'shock'] and word_count < 30:
            return 'strong'
        elif word_count < 50:
            return 'moderate'
        else:
            return 'weak'

    def _calculate_variance(self, values: List[int]) -> float:
        """Calculate variance of a list of values"""
        if not values:
            return 0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)

        return variance ** 0.5  # Return standard deviation

    def _analyze_rhythm(self, lengths: List[int]) -> float:
        """Analyze rhythmic pattern in paragraph lengths"""
        if len(lengths) < 3:
            return 5.0

        # Check for variation (good rhythm has ups and downs)
        changes = sum(1 for i in range(len(lengths) - 1) if (lengths[i+1] - lengths[i]) != 0)

        rhythm_score = (changes / (len(lengths) - 1)) * 10 if len(lengths) > 1 else 5.0

        return min(10, rhythm_score)

    def _identify_strengths(
            self,
            structure: Dict[str, Any],
            pacing: Dict[str, Any],
            hooks: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify narrative strengths"""

        strengths = []

        if structure['completeness'] >= 80:
            strengths.append("Strong narrative structure with all key elements present")

        if pacing['pacing_variety_score'] >= 5:
            strengths.append("Good pacing variety keeps audience engaged")

        if len(hooks) >= 5:
            strengths.append(f"Excellent hook placement with {len(hooks)} engagement points")

        if not strengths:
            strengths.append("Functional narrative foundation")

        return strengths

    def _identify_weaknesses(
            self,
            structure: Dict[str, Any],
            pacing: Dict[str, Any],
            hooks: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify narrative weaknesses"""

        weaknesses = []

        if structure['completeness'] < 70:
            weaknesses.append("Incomplete narrative arc - missing key story elements")

        if pacing['pacing_variety_score'] < 3:
            weaknesses.append("Monotonous pacing - needs more variety")

        if len(hooks) < 3:
            weaknesses.append("Insufficient hooks - audience may lose interest")

        return weaknesses
