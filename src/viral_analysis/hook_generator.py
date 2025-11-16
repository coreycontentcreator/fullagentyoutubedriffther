"""
Hook Generator - Creates compelling opening hooks
Generates multiple hook variations for maximum engagement
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Hook:
    """Generated hook"""
    text: str
    trigger_types: List[str]
    virality_score: float
    reasoning: str
    variation_type: str


class HookGenerator:
    """
    Generates viral opening hooks using psychology triggers
    """

    def __init__(self, intelligence_layer, psychology_triggers):
        """
        Initialize hook generator

        Args:
            intelligence_layer: AI intelligence layer
            psychology_triggers: Psychology triggers system
        """
        self.intelligence = intelligence_layer
        self.psychology = psychology_triggers

        logger.info("Hook Generator initialized")

    async def generate_hooks(
        self,
        topic: str,
        key_insight: str,
        target_audience: str,
        count: int = 10
    ) -> List[Hook]:
        """
        Generate multiple hook variations

        Args:
            topic: Video topic
            key_insight: Main insight/revelation
            target_audience: Target audience
            count: Number of hooks to generate

        Returns:
            List of generated hooks
        """
        from ..intelligence.intelligence_layer import AIRequest, TaskComplexity

        prompt = f"""Generate {count} compelling video hooks for this topic.

        Topic: {topic}
        Key Insight: {key_insight}
        Target Audience: {target_audience}

        Each hook should:
        1. Be 15-30 seconds of script
        2. Use psychological triggers (curiosity, storytelling, etc.)
        3. Be highly engaging
        4. Create desire to watch more

        Provide hooks as JSON array with:
        - text: Hook script
        - triggers: Psychology triggers used
        - score: Virality score (0-10)
        - reasoning: Why it works
        - type: Variation type (question, statement, story, mystery, etc.)"""

        request = AIRequest(
            prompt=prompt,
            task_type="hook_generation",
            complexity=TaskComplexity.COMPLEX,
            temperature=0.8
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            hooks_data = json.loads(response.content)

            hooks = []
            for hook_data in hooks_data[:count]:
                hook = Hook(
                    text=hook_data.get('text', ''),
                    trigger_types=hook_data.get('triggers', []),
                    virality_score=hook_data.get('score', 7.0),
                    reasoning=hook_data.get('reasoning', ''),
                    variation_type=hook_data.get('type', 'general')
                )
                hooks.append(hook)

            logger.info(f"Generated {len(hooks)} hooks")
            return hooks

        except Exception as e:
            logger.error(f"Failed to parse hooks: {e}")

            # Fallback: Generate basic hooks
            return [
                Hook(
                    text=f"What if everything you knew about {topic} was wrong?",
                    trigger_types=["curiosity_gap", "controversy"],
                    virality_score=8.0,
                    reasoning="Uses curiosity gap and challenges assumptions",
                    variation_type="question"
                ),
                Hook(
                    text=f"Scientists just discovered something shocking about {topic}...",
                    trigger_types=["authority", "curiosity_gap"],
                    virality_score=8.5,
                    reasoning="Combines authority with curiosity",
                    variation_type="revelation"
                )
            ]

    async def optimize_hook(self, hook: Hook) -> Hook:
        """
        Optimize a hook for higher virality

        Args:
            hook: Hook to optimize

        Returns:
            Optimized hook
        """
        from ..intelligence.intelligence_layer import AIRequest, TaskComplexity

        prompt = f"""Optimize this video hook for maximum virality:

        Current Hook: {hook.text}
        Current Score: {hook.virality_score}
        Triggers Used: {', '.join(hook.trigger_types)}

        Improve by:
        1. Making it more compelling
        2. Adding stronger triggers
        3. Creating more curiosity
        4. Being more specific

        Return optimized hook as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="hook_optimization",
            complexity=TaskComplexity.MODERATE,
            temperature=0.7
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            optimized_data = json.loads(response.content)

            return Hook(
                text=optimized_data.get('text', hook.text),
                trigger_types=optimized_data.get('triggers', hook.trigger_types),
                virality_score=min(optimized_data.get('score', hook.virality_score), 10.0),
                reasoning=optimized_data.get('reasoning', hook.reasoning),
                variation_type=hook.variation_type
            )

        except:
            return hook
