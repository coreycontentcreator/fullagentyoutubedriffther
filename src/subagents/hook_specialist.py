"""
Hook Specialist Subagent
Creates compelling opening hooks (first 15 seconds)
Specializes in stopping scrolling and capturing attention
"""

from typing import Dict, List, Any, Optional
import sys
sys.path.append('/home/user/fullagentyoutubedriffther/src')

from integrations.anthropic_integration import AnthropicIntegration


class HookSpecialist:
    """
    Specialized subagent for creating viral hooks
    Focuses on the critical first 0-15 seconds
    """

    def __init__(self, ai_integration: Optional[AnthropicIntegration] = None):
        self.ai = ai_integration or AnthropicIntegration()
        self.hook_templates = self._initialize_hook_templates()

    def _initialize_hook_templates(self) -> Dict[str, List[str]]:
        """Initialize proven hook templates"""
        return {
            'curiosity_gap': [
                "What if everything you know about {topic} is wrong?",
                "The secret about {topic} that {authority} don't want you to know...",
                "Here's what happens when you {action}... (but nobody talks about it)",
                "You won't believe what scientists just discovered about {topic}...",
                "The truth about {topic} that will change everything..."
            ],
            'shocking_statistic': [
                "{number}% of people don't know this about {topic}...",
                "This one fact about {topic} will blow your mind: {statistic}",
                "{number} million people are doing this wrong...",
                "The {topic} industry doesn't want you to know: {statistic}"
            ],
            'controversial_question': [
                "Is {topic} actually {negative_descriptor}?",
                "Why does everyone get {topic} wrong?",
                "Should we stop {common_practice}?",
                "What if {controversial_statement}?"
            ],
            'transformation_promise': [
                "From {before_state} to {after_state} in {timeframe}...",
                "How I {achievement} using {method}...",
                "This {simple_thing} changed everything about {topic}...",
                "The moment I realized {insight} about {topic}..."
            ],
            'mystery_hook': [
                "Nobody can explain {phenomenon}... until now",
                "The mystery behind {topic} finally revealed",
                "What's really happening with {topic}?",
                "The question nobody can answer about {topic}..."
            ],
            'urgency_hook': [
                "This is happening right now and you need to know...",
                "Why you need to understand {topic} TODAY",
                "The urgent truth about {topic} in {current_year}",
                "This changes everything we thought about {topic}..."
            ]
        }

    def generate_hooks(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None,
        count: int = 10,
        target_audience: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple hook variations

        Args:
            topic: Main topic
            context: Additional context (research, target metrics, etc.)
            count: Number of hooks to generate
            target_audience: Target audience description

        Returns:
            List of hook objects with metadata
        """
        context_str = self._build_context_string(context) if context else ""

        system_prompt = """You are a viral video hook specialist. You create hooks that:
        1. Stop scrolling in the first 3 seconds
        2. Create a curiosity gap
        3. Promise clear value
        4. Use psychological triggers
        5. Are concise (15 seconds or less when spoken)
        6. Compel viewers to keep watching

        Generate hooks that would work for top YouTubers like Veritasium, Vsauce, or MrBeast."""

        prompt = f"""Create {count} viral video hooks for this topic: {topic}

Target audience: {target_audience}
{context_str}

Requirements:
- Each hook should be 15 seconds or less when spoken
- Create strong curiosity gap
- Use psychological triggers
- Be immediately compelling
- Promise clear value

Return as JSON array:
[
  {{
    "hook_text": "The actual hook (spoken word-for-word)",
    "visual_suggestion": "What viewer sees during hook",
    "duration_estimate_seconds": 12,
    "psychology_triggers": ["curiosity", "novelty"],
    "virality_score": 8.5,
    "target_emotion": "curiosity",
    "hook_type": "curiosity_gap",
    "reasoning": "Why this hook works"
  }}
]"""

        result = self.ai.generate_text(prompt, system_prompt=system_prompt, temperature=0.8)

        try:
            import json
            text = result['text']
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            hooks = json.loads(text.strip())
            return hooks if isinstance(hooks, list) else [hooks]
        except:
            # Fallback: use templates
            return self._generate_template_hooks(topic, count)

    def _build_context_string(self, context: Dict[str, Any]) -> str:
        """Build context string from context dict"""
        parts = []
        if 'research_insights' in context:
            parts.append(f"Key insights: {context['research_insights']}")
        if 'target_metrics' in context:
            parts.append(f"Target metrics: {context['target_metrics']}")
        if 'competitor_hooks' in context:
            parts.append(f"Successful competitor hooks: {context['competitor_hooks']}")
        return "\n".join(parts)

    def _generate_template_hooks(self, topic: str, count: int) -> List[Dict[str, Any]]:
        """Generate hooks using templates (fallback)"""
        hooks = []
        template_types = list(self.hook_templates.keys())

        for i in range(min(count, len(template_types) * 2)):
            template_type = template_types[i % len(template_types)]
            templates = self.hook_templates[template_type]
            template = templates[i % len(templates)]

            # Simple substitution
            hook_text = template.replace('{topic}', topic)
            hook_text = hook_text.replace('{authority}', 'experts')
            hook_text = hook_text.replace('{action}', f'learn about {topic}')

            hooks.append({
                'hook_text': hook_text,
                'visual_suggestion': f'Attention-grabbing visual related to {topic}',
                'duration_estimate_seconds': 12,
                'psychology_triggers': ['curiosity'],
                'virality_score': 7.0,
                'target_emotion': 'curiosity',
                'hook_type': template_type,
                'reasoning': f'Uses {template_type} template'
            })

        return hooks[:count]

    def optimize_hook(self, hook: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Optimize an existing hook based on feedback

        Args:
            hook: Hook to optimize
            feedback: Feedback on what to improve

        Returns:
            Optimized hook
        """
        system_prompt = "You are a viral hook optimization expert. Improve hooks based on feedback."

        prompt = f"""Optimize this video hook:

Current hook: {hook['hook_text']}
Current virality score: {hook.get('virality_score', 'N/A')}

Feedback: {feedback}

Create an improved version that addresses the feedback while maintaining:
- Strong curiosity gap
- Clear value proposition
- Under 15 seconds
- Psychological triggers

Return as JSON:
{{
  "hook_text": "Optimized hook text",
  "visual_suggestion": "Visual description",
  "duration_estimate_seconds": 12,
  "psychology_triggers": ["list"],
  "virality_score": 9.0,
  "target_emotion": "emotion",
  "hook_type": "type",
  "reasoning": "What was improved",
  "changes_made": ["list of changes"]
}}"""

        result = self.ai.generate_text(prompt, system_prompt=system_prompt, temperature=0.7)

        try:
            import json
            text = result['text']
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]

            return json.loads(text.strip())
        except:
            return hook  # Return original if optimization fails

    def score_hook(self, hook_text: str) -> Dict[str, Any]:
        """
        Score a hook for viral potential

        Args:
            hook_text: Hook to score

        Returns:
            Scoring breakdown
        """
        criteria = {
            'curiosity_gap': 'Creates strong desire to know more',
            'clarity': 'Clear and easy to understand',
            'value_promise': 'Promises clear benefit',
            'emotional_trigger': 'Triggers emotional response',
            'brevity': 'Concise and punchy',
            'uniqueness': 'Novel or unexpected approach'
        }

        scores = {}
        hook_lower = hook_text.lower()

        # Curiosity gap
        curiosity_words = ['what if', 'secret', 'truth', 'revealed', 'nobody', 'hidden']
        scores['curiosity_gap'] = min(sum(2 for w in curiosity_words if w in hook_lower), 10)

        # Clarity (inverse of complexity)
        word_count = len(hook_text.split())
        scores['clarity'] = 10 if word_count <= 20 else max(10 - (word_count - 20) * 0.5, 3)

        # Value promise
        value_words = ['learn', 'discover', 'understand', 'know', 'see', 'find out']
        scores['value_promise'] = min(sum(2 for w in value_words if w in hook_lower), 10)

        # Emotional trigger
        emotion_words = ['shocking', 'amazing', 'incredible', 'surprising', 'revolutionary']
        scores['emotional_trigger'] = min(sum(2 for w in emotion_words if w in hook_lower), 10)

        # Brevity
        scores['brevity'] = 10 if word_count <= 15 else max(10 - (word_count - 15) * 0.3, 5)

        # Uniqueness (has question or unexpected element)
        scores['uniqueness'] = 8 if '?' in hook_text or 'what if' in hook_lower else 6

        overall = sum(scores.values()) / len(scores)

        return {
            'overall_score': round(overall, 2),
            'scores': {k: round(v, 2) for k, v in scores.items()},
            'criteria': criteria,
            'recommendation': 'Strong hook' if overall >= 8 else 'Needs improvement' if overall >= 6 else 'Weak hook'
        }

    def get_hook_templates(self) -> Dict[str, List[str]]:
        """Get all hook templates"""
        return self.hook_templates

    def analyze_competitor_hooks(self, hooks: List[str]) -> Dict[str, Any]:
        """
        Analyze successful competitor hooks to identify patterns

        Args:
            hooks: List of successful hooks from competitors

        Returns:
            Pattern analysis
        """
        if not hooks:
            return {'error': 'No hooks provided'}

        # Analyze patterns
        patterns = {
            'avg_length': sum(len(h.split()) for h in hooks) / len(hooks),
            'question_usage': sum(1 for h in hooks if '?' in h) / len(hooks) * 100,
            'common_words': self._extract_common_words(hooks),
            'common_structures': self._identify_structures(hooks)
        }

        return {
            'hook_count': len(hooks),
            'patterns': patterns,
            'recommendations': self._generate_recommendations_from_patterns(patterns)
        }

    def _extract_common_words(self, hooks: List[str]) -> List[tuple]:
        """Extract common words from hooks"""
        from collections import Counter
        import re

        all_words = []
        for hook in hooks:
            words = re.findall(r'\b\w+\b', hook.lower())
            all_words.extend([w for w in words if len(w) > 3])

        common = Counter(all_words).most_common(10)
        return common

    def _identify_structures(self, hooks: List[str]) -> List[str]:
        """Identify common hook structures"""
        structures = []
        for hook in hooks:
            if hook.startswith('What if'):
                structures.append('what_if_question')
            elif hook.startswith('How'):
                structures.append('how_to')
            elif 'secret' in hook.lower():
                structures.append('secret_reveal')
            elif '?' in hook:
                structures.append('question')
            else:
                structures.append('statement')

        from collections import Counter
        return [f"{struct}: {count}" for struct, count in Counter(structures).most_common()]

    def _generate_recommendations_from_patterns(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on pattern analysis"""
        recs = []

        avg_length = patterns['avg_length']
        if avg_length > 20:
            recs.append(f"Consider shorter hooks (current average: {avg_length:.1f} words)")

        question_pct = patterns['question_usage']
        if question_pct > 50:
            recs.append(f"Questions are effective ({question_pct:.0f}% usage)")

        return recs
