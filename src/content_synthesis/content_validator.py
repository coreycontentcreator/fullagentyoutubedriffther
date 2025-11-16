"""
Content Validator Subagent
Multi-pass validation for quality, accuracy, and engagement
"""
import time
import re
from typing import Dict, Any, List, Tuple
from .base_subagent import SynchronousSubagent, SubagentResult
import logging

logger = logging.getLogger(__name__)


class ContentValidator(SynchronousSubagent):
    """
    Content Validator Subagent
    Performs multi-pass validation on generated content for quality assurance
    """

    def __init__(self, anthropic_client, config):
        super().__init__("ContentValidator", anthropic_client, config)

        self.system_prompt = """You are an expert content quality assurance specialist with expertise in:
- Quality assessment and validation
- Readability and engagement analysis
- Fact-checking and accuracy verification
- Production feasibility assessment
- YouTube content optimization

You provide detailed, actionable feedback to improve content quality."""

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        if 'script' not in input_data:
            raise ValueError("Missing required field: script")

        return True

    def validate_output(self, output_data: Dict[str, Any]) -> float:
        """Calculate overall validation score"""
        # The output is the validation itself, so we return the overall score
        return output_data.get('overall_quality_score', 0.0)

    def process_sync(self, input_data: Dict[str, Any]) -> SubagentResult:
        """
        Perform multi-pass content validation

        Input data:
            - script: Script to validate
            - visual_scenes: Visual scenes (optional)
            - production_notes: Production notes (optional)
            - narrative_analysis: Narrative analysis (optional)
            - research_data: Original research data (optional)

        Returns:
            SubagentResult with comprehensive validation report
        """
        start_time = time.time()

        try:
            # Validate input
            self.validate_input(input_data)

            self.log_processing("INPUT_VALIDATION", "Input data validated")

            script = input_data['script']
            visual_scenes = input_data.get('visual_scenes', [])
            production_notes = input_data.get('production_notes', {})
            narrative_analysis = input_data.get('narrative_analysis', {})
            research_data = input_data.get('research_data', {})

            # Pass 1: Readability validation
            self.log_processing("PASS_1", "Validating readability")
            readability_result = self._validate_readability(script)

            # Pass 2: Engagement validation
            self.log_processing("PASS_2", "Validating engagement")
            engagement_result = self._validate_engagement(script, visual_scenes)

            # Pass 3: Accuracy validation
            self.log_processing("PASS_3", "Validating accuracy")
            accuracy_result = self._validate_accuracy(script, research_data)

            # Pass 4: Production feasibility
            self.log_processing("PASS_4", "Validating production feasibility")
            feasibility_result = self._validate_production_feasibility(
                script, visual_scenes, production_notes
            )

            # Pass 5: YouTube optimization
            self.log_processing("PASS_5", "Validating YouTube optimization")
            youtube_result = self._validate_youtube_optimization(script)

            # Calculate overall quality score
            overall_score = self._calculate_overall_score(
                readability_result,
                engagement_result,
                accuracy_result,
                feasibility_result,
                youtube_result
            )

            # Generate improvement recommendations
            recommendations = self._generate_recommendations(
                readability_result,
                engagement_result,
                accuracy_result,
                feasibility_result,
                youtube_result,
                overall_score
            )

            # Determine if content passes quality threshold
            threshold = self.config.quality_threshold
            passes_validation = overall_score >= threshold

            # Prepare output
            output_data = {
                'passes_validation': passes_validation,
                'overall_quality_score': overall_score,
                'quality_threshold': threshold,
                'validation_passes': {
                    'readability': readability_result,
                    'engagement': engagement_result,
                    'accuracy': accuracy_result,
                    'production_feasibility': feasibility_result,
                    'youtube_optimization': youtube_result
                },
                'recommendations': recommendations,
                'critical_issues': self._identify_critical_issues(
                    readability_result,
                    engagement_result,
                    accuracy_result,
                    feasibility_result,
                    youtube_result
                ),
                'strengths': self._identify_strengths(
                    readability_result,
                    engagement_result,
                    accuracy_result,
                    feasibility_result,
                    youtube_result
                )
            }

            # Quality score is the validation score itself
            quality_score = overall_score

            processing_time = time.time() - start_time

            status = "PASSED" if passes_validation else "NEEDS_IMPROVEMENT"
            self.log_processing("COMPLETION", f"Validation {status} with score: {overall_score:.2f}/{threshold}")

            return self.create_result(
                success=True,
                data=output_data,
                quality_score=quality_score,
                processing_time=processing_time,
                metadata={
                    'passes_validation': passes_validation,
                    'threshold': threshold
                }
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.log_error(f"Content validation failed: {str(e)}")

            return self.create_result(
                success=False,
                data={},
                quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)]
            )

    def _validate_readability(self, script: str) -> Dict[str, Any]:
        """Validate readability and comprehension"""

        # Calculate readability metrics
        word_count = len(script.split())
        sentence_count = script.count('.') + script.count('!') + script.count('?')
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Count complex words (3+ syllables - simplified)
        complex_words = sum(1 for word in script.split() if len(word) > 10)
        complex_word_percentage = (complex_words / word_count * 100) if word_count > 0 else 0

        # Readability score (simplified Flesch-Kincaid)
        # Target: 8th-10th grade level for YouTube
        reading_level = 0.39 * avg_sentence_length + 11.8 * (complex_word_percentage / 100) - 15.59

        # Score readability (0-10)
        if 8 <= reading_level <= 12:
            readability_score = 10.0
        elif 6 <= reading_level <= 14:
            readability_score = 7.5
        elif reading_level < 6:
            readability_score = 6.0  # Too simple
        else:
            readability_score = 5.0  # Too complex

        # Check for conversational tone
        personal_pronouns = sum(script.lower().count(word) for word in [' you ', ' your ', ' we ', ' our '])
        conversational_score = min(10, (personal_pronouns / (word_count / 100)) * 2)

        # Check for active voice (simplified check)
        passive_indicators = sum(script.lower().count(phrase) for phrase in [' was ', ' were ', ' been ', ' being '])
        active_voice_percentage = max(0, 100 - (passive_indicators / (word_count / 100)) * 10)
        active_voice_score = active_voice_percentage / 10

        # Overall readability
        overall_readability = (readability_score + conversational_score + active_voice_score) / 3

        return {
            'score': round(overall_readability, 1),
            'reading_level': round(reading_level, 1),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'complex_word_percentage': round(complex_word_percentage, 1),
            'conversational_score': round(conversational_score, 1),
            'active_voice_score': round(active_voice_score, 1),
            'issues': self._identify_readability_issues(reading_level, avg_sentence_length, complex_word_percentage)
        }

    def _validate_engagement(self, script: str, visual_scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate engagement potential"""

        # Check for hooks
        hook_indicators = ['?', 'imagine', 'what if', 'discover', 'you won\'t believe']
        hook_count = sum(script.lower().count(indicator) for indicator in hook_indicators)
        hook_score = min(10, hook_count)

        # Check for pattern interruptions
        script_sections = script.split('\n\n')
        variety_score = min(10, len(set(len(s.split()) for s in script_sections)) / 2)

        # Check for emotional triggers
        emotional_words = ['amazing', 'shocking', 'incredible', 'surprising', 'devastating', 'beautiful']
        emotional_count = sum(script.lower().count(word) for word in emotional_words)
        emotional_score = min(10, emotional_count / 2)

        # Check for visual variety
        if visual_scenes:
            shot_types = set(scene.get('shot_type', '') for scene in visual_scenes)
            visual_variety_score = min(10, len(shot_types))
        else:
            visual_variety_score = 5.0  # Neutral if no visual scenes

        # Check for CTAs
        cta_phrases = ['subscribe', 'like', 'comment', 'share', 'bell']
        cta_count = sum(script.lower().count(phrase) for phrase in cta_phrases)
        cta_score = min(10, cta_count * 3)

        # Overall engagement
        overall_engagement = (hook_score + variety_score + emotional_score + visual_variety_score + cta_score) / 5

        return {
            'score': round(overall_engagement, 1),
            'hook_count': hook_count,
            'hook_score': round(hook_score, 1),
            'variety_score': round(variety_score, 1),
            'emotional_score': round(emotional_score, 1),
            'visual_variety_score': round(visual_variety_score, 1),
            'cta_score': round(cta_score, 1),
            'issues': self._identify_engagement_issues(hook_count, cta_count, emotional_count)
        }

    def _validate_accuracy(self, script: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate accuracy and factual correctness"""

        # Check for claims that need citations
        claim_indicators = ['research shows', 'studies', 'according to', 'scientists', 'experts']
        claim_count = sum(script.lower().count(indicator) for indicator in claim_indicators)

        # Check for specific numbers and statistics
        numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?%?', script)
        stat_count = len(numbers)

        # Check if research data is referenced
        if research_data:
            key_findings = research_data.get('key_findings', [])
            # Simple check: are key findings mentioned in script?
            findings_mentioned = 0
            for finding in key_findings[:5]:  # Check first 5
                # Extract key terms from finding
                finding_str = str(finding).lower()
                key_terms = [word for word in finding_str.split() if len(word) > 5][:3]
                if any(term in script.lower() for term in key_terms):
                    findings_mentioned += 1

            accuracy_score = (findings_mentioned / min(5, len(key_findings)) * 10) if key_findings else 7.0
        else:
            # No research data to validate against
            accuracy_score = 7.0

        # Check for weasel words (may indicate lack of accuracy)
        weasel_words = ['might', 'maybe', 'possibly', 'probably', 'some say']
        weasel_count = sum(script.lower().count(word) for word in weasel_words)
        weasel_penalty = min(2, weasel_count * 0.5)

        accuracy_score = max(0, accuracy_score - weasel_penalty)

        return {
            'score': round(accuracy_score, 1),
            'claim_count': claim_count,
            'statistic_count': stat_count,
            'weasel_word_count': weasel_count,
            'issues': self._identify_accuracy_issues(claim_count, stat_count, weasel_count)
        }

    def _validate_production_feasibility(
            self,
            script: str,
            visual_scenes: List[Dict[str, Any]],
            production_notes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate production feasibility"""

        feasibility_score = 10.0
        issues = []

        # Check script length vs. target
        word_count = len(script.split())
        if word_count < self.config.min_script_length:
            feasibility_score -= 2
            issues.append(f"Script too short ({word_count} words, min: {self.config.min_script_length})")
        elif word_count > self.config.max_script_length:
            feasibility_score -= 1
            issues.append(f"Script very long ({word_count} words, max: {self.config.max_script_length})")

        # Check scene count
        scene_count = len(visual_scenes)
        if scene_count < self.config.min_scene_count:
            feasibility_score -= 1
            issues.append(f"Too few scenes ({scene_count}, min: {self.config.min_scene_count})")
        elif scene_count > self.config.max_scene_count:
            feasibility_score -= 0.5
            issues.append(f"Very many scenes ({scene_count}) - may be complex to produce")

        # Check for unrealistic requirements
        if visual_scenes:
            complex_scenes = sum(1 for scene in visual_scenes
                                  if 'aerial' in scene.get('shot_type', '').lower()
                                  or 'drone' in scene.get('description', '').lower())

            if complex_scenes > 5:
                feasibility_score -= 1
                issues.append(f"Many complex shots requiring special equipment ({complex_scenes} aerial/drone shots)")

        # Check production timeline realism
        if production_notes:
            budget = production_notes.get('budget_estimate', {})
            if budget.get('total', 0) > 50000:
                feasibility_score -= 0.5
                issues.append("High budget requirement may limit feasibility")

        feasibility_score = max(0, feasibility_score)

        return {
            'score': round(feasibility_score, 1),
            'word_count': word_count,
            'scene_count': scene_count,
            'issues': issues
        }

    def _validate_youtube_optimization(self, script: str) -> Dict[str, Any]:
        """Validate YouTube-specific optimization"""

        optimization_score = 0.0

        # Check for strong opening (first 15 seconds = ~50 words)
        opening_words = script.split()[:50]
        opening_text = ' '.join(opening_words).lower()

        has_hook = any(word in opening_text for word in ['imagine', 'what if', 'discover', 'secret'])
        has_question = '?' in opening_text
        has_stats = any(char.isdigit() for char in opening_text)

        if has_hook or has_question or has_stats:
            optimization_score += 3
        else:
            optimization_score += 1

        # Check for retention hooks throughout (every ~2 minutes = ~300 words)
        word_count = len(script.split())
        sections = word_count // 300
        retention_hooks = script.count('?') + script.lower().count('but')

        if retention_hooks >= sections:
            optimization_score += 2
        else:
            optimization_score += 1

        # Check for pattern interrupts
        para_lengths = [len(p.split()) for p in script.split('\n\n')]
        if len(set(para_lengths)) > 5:  # Varied lengths
            optimization_score += 2
        else:
            optimization_score += 1

        # Check for CTA
        has_cta = any(word in script.lower() for word in ['subscribe', 'like', 'comment'])
        if has_cta:
            optimization_score += 2
        else:
            optimization_score += 0

        # Check for end screen prompt
        last_100_words = ' '.join(script.split()[-100:]).lower()
        has_end_cta = 'next' in last_100_words or 'watch' in last_100_words
        if has_end_cta:
            optimization_score += 1

        return {
            'score': round(optimization_score, 1),
            'has_strong_opening': has_hook or has_question or has_stats,
            'retention_hook_count': retention_hooks,
            'has_cta': has_cta,
            'has_end_screen': has_end_cta,
            'issues': self._identify_youtube_issues(
                has_hook or has_question or has_stats,
                retention_hooks,
                has_cta
            )
        }

    def _calculate_overall_score(
            self,
            readability: Dict[str, Any],
            engagement: Dict[str, Any],
            accuracy: Dict[str, Any],
            feasibility: Dict[str, Any],
            youtube: Dict[str, Any]
    ) -> float:
        """Calculate weighted overall quality score"""

        # Weights
        weights = {
            'readability': 0.15,
            'engagement': 0.30,
            'accuracy': 0.20,
            'feasibility': 0.15,
            'youtube': 0.20
        }

        overall = (
                readability['score'] * weights['readability'] +
                engagement['score'] * weights['engagement'] +
                accuracy['score'] * weights['accuracy'] +
                feasibility['score'] * weights['feasibility'] +
                youtube['score'] * weights['youtube']
        )

        return round(overall, 1)

    def _generate_recommendations(
            self,
            readability: Dict[str, Any],
            engagement: Dict[str, Any],
            accuracy: Dict[str, Any],
            feasibility: Dict[str, Any],
            youtube: Dict[str, Any],
            overall_score: float
    ) -> List[Dict[str, str]]:
        """Generate prioritized recommendations for improvement"""

        recommendations = []

        # Priority recommendations based on lowest scores
        scores = {
            'readability': readability['score'],
            'engagement': engagement['score'],
            'accuracy': accuracy['score'],
            'feasibility': feasibility['score'],
            'youtube': youtube['score']
        }

        # Add recommendations for areas scoring below 7.0
        for area, score in sorted(scores.items(), key=lambda x: x[1]):
            if score < 7.0:
                priority = 'High' if score < 5.0 else 'Medium'

                if area == 'readability':
                    recommendations.append({
                        'priority': priority,
                        'area': 'Readability',
                        'recommendation': 'Simplify sentence structure and use more conversational language'
                    })

                elif area == 'engagement':
                    recommendations.append({
                        'priority': priority,
                        'area': 'Engagement',
                        'recommendation': 'Add more hooks, questions, and emotional triggers throughout the script'
                    })

                elif area == 'accuracy':
                    recommendations.append({
                        'priority': priority,
                        'area': 'Accuracy',
                        'recommendation': 'Add more specific data points and reduce vague language'
                    })

                elif area == 'feasibility':
                    recommendations.append({
                        'priority': priority,
                        'area': 'Production',
                        'recommendation': 'Adjust scope to be more production-friendly'
                    })

                elif area == 'youtube':
                    recommendations.append({
                        'priority': priority,
                        'area': 'YouTube Optimization',
                        'recommendation': 'Strengthen opening hook and add retention elements'
                    })

        # If overall score is good, add optimization recommendations
        if overall_score >= 8.0 and len(recommendations) < 3:
            recommendations.append({
                'priority': 'Low',
                'area': 'Optimization',
                'recommendation': 'Content is strong - consider A/B testing different hooks'
            })

        return recommendations

    def _identify_critical_issues(self, *args) -> List[str]:
        """Identify critical issues that must be addressed"""
        critical_issues = []

        for validation_result in args:
            if validation_result['score'] < 5.0:
                for issue in validation_result.get('issues', []):
                    if issue not in critical_issues:
                        critical_issues.append(issue)

        return critical_issues

    def _identify_strengths(self, *args) -> List[str]:
        """Identify content strengths"""
        strengths = []

        for validation_result in args:
            if validation_result['score'] >= 8.0:
                area = 'Quality area'  # This would be more specific in real implementation
                strengths.append(f"Strong performance in validation")

        if not strengths:
            strengths = ["Functional content foundation"]

        return strengths[:5]  # Top 5 strengths

    def _identify_readability_issues(self, reading_level: float, avg_sentence: float, complex_pct: float) -> List[str]:
        """Identify specific readability issues"""
        issues = []

        if reading_level > 14:
            issues.append("Reading level too high - simplify language")
        elif reading_level < 6:
            issues.append("Reading level too low - may lack depth")

        if avg_sentence > 25:
            issues.append("Sentences too long - break into shorter segments")

        if complex_pct > 20:
            issues.append("Too many complex words - use simpler alternatives")

        return issues

    def _identify_engagement_issues(self, hooks: int, ctas: int, emotional: int) -> List[str]:
        """Identify engagement issues"""
        issues = []

        if hooks < 5:
            issues.append("Insufficient hooks - add more throughout script")

        if ctas < 1:
            issues.append("No call-to-action - add subscribe/like prompts")

        if emotional < 3:
            issues.append("Limited emotional triggers - add more impact")

        return issues

    def _identify_accuracy_issues(self, claims: int, stats: int, weasel: int) -> List[str]:
        """Identify accuracy issues"""
        issues = []

        if claims > 5 and stats < 3:
            issues.append("Many claims but few statistics - add data support")

        if weasel > 5:
            issues.append("Too many weasel words - be more definitive")

        return issues

    def _identify_youtube_issues(self, strong_opening: bool, hooks: int, has_cta: bool) -> List[str]:
        """Identify YouTube optimization issues"""
        issues = []

        if not strong_opening:
            issues.append("Opening hook weak - strengthen first 15 seconds")

        if hooks < 3:
            issues.append("Add retention hooks every 2 minutes")

        if not has_cta:
            issues.append("Missing call-to-action - add subscribe/like prompt")

        return issues
