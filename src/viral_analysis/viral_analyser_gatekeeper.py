"""
Viral Analyser Gatekeeper - Main viral analysis coordinator
Coordinates psychology triggers, hooks, and pattern analysis
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .psychology_triggers import PsychologyTriggers, TriggerApplication
from .hook_generator import HookGenerator, Hook
from .pattern_analyzer import PatternAnalyzer, ViralPattern

logger = logging.getLogger(__name__)


@dataclass
class ViralStrategy:
    """Complete viral strategy document"""
    topic: str
    hooks: List[Hook]
    triggers: List[TriggerApplication]
    patterns: List[ViralPattern]
    retention_strategy: Dict[str, Any]
    engagement_moments: List[Dict[str, str]]
    cta_placements: List[Dict[str, str]]
    virality_score: float
    generated_at: str
    processing_time: float


class ViralAnalyserGatekeeper:
    """
    Viral Analyser Gatekeeper - Coordinates all viral optimization
    Ensures content has maximum viral potential
    """

    def __init__(
        self,
        intelligence_layer,
        vector_database=None,
        quality_threshold: float = 9.0
    ):
        """
        Initialize Viral Analyser Gatekeeper

        Args:
            intelligence_layer: AI intelligence layer
            vector_database: Vector database for pattern storage
            quality_threshold: Minimum virality score
        """
        self.intelligence = intelligence_layer
        self.vector_db = vector_database
        self.quality_threshold = quality_threshold

        # Initialize subsystems
        self.psychology = PsychologyTriggers()
        self.hook_generator = HookGenerator(intelligence_layer, self.psychology)
        self.pattern_analyzer = PatternAnalyzer(vector_database)

        logger.info(f"Viral Analyser Gatekeeper initialized (threshold: {quality_threshold})")

    async def analyze_and_optimize(
        self,
        topic: str,
        research_report: Any,
        target_audience: str,
        video_duration: int,
        style: str = "documentary"
    ) -> ViralStrategy:
        """
        Analyze and create complete viral strategy

        Args:
            topic: Video topic
            research_report: Research findings
            target_audience: Target audience
            video_duration: Video duration in minutes
            style: Video style

        Returns:
            Complete viral strategy
        """
        start_time = datetime.now()
        logger.info(f"Analyzing viral strategy for: {topic}")

        # Step 1: Generate hooks
        key_insight = self._extract_key_insight(research_report)
        hooks = await self.hook_generator.generate_hooks(
            topic=topic,
            key_insight=key_insight,
            target_audience=target_audience,
            count=10
        )
        logger.info(f"Generated {len(hooks)} hooks")

        # Step 2: Get trigger recommendations
        triggers = self.psychology.get_trigger_recommendations(
            topic=topic,
            audience=target_audience,
            video_duration=video_duration
        )
        logger.info(f"Recommended {len(triggers)} psychology triggers")

        # Step 3: Analyze patterns
        patterns = await self.pattern_analyzer.analyze_patterns(
            topic=topic,
            research_data=research_report.__dict__ if hasattr(research_report, '__dict__') else {}
        )
        logger.info(f"Identified {len(patterns)} viral patterns")

        # Step 4: Create retention strategy
        retention_strategy = await self._create_retention_strategy(
            video_duration=video_duration,
            triggers=triggers,
            hooks=hooks
        )

        # Step 5: Plan engagement moments
        engagement_moments = self._plan_engagement_moments(video_duration, triggers)

        # Step 6: Determine CTA placements
        cta_placements = self._plan_cta_placements(video_duration)

        # Step 7: Calculate virality score
        virality_score = self._calculate_virality_score(
            hooks=hooks,
            triggers=triggers,
            patterns=patterns
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        strategy = ViralStrategy(
            topic=topic,
            hooks=hooks,
            triggers=triggers,
            patterns=patterns,
            retention_strategy=retention_strategy,
            engagement_moments=engagement_moments,
            cta_placements=cta_placements,
            virality_score=virality_score,
            generated_at=datetime.now().isoformat(),
            processing_time=processing_time
        )

        logger.info(f"Viral strategy complete: Score {virality_score:.1f}/10")

        return strategy

    def _extract_key_insight(self, research_report: Any) -> str:
        """Extract key insight from research"""
        if hasattr(research_report, 'key_insights') and research_report.key_insights:
            return research_report.key_insights[0]
        return "groundbreaking discovery"

    async def _create_retention_strategy(
        self,
        video_duration: int,
        triggers: List[TriggerApplication],
        hooks: List[Hook]
    ) -> Dict[str, Any]:
        """Create retention optimization strategy"""
        # Place hooks every 2-3 minutes
        hook_intervals = []
        interval = 2.5  # minutes

        current_time = 0
        while current_time < video_duration:
            hook_intervals.append({
                "time": f"{int(current_time)}:{int((current_time % 1) * 60):02d}",
                "type": "pattern_interruption",
                "purpose": "Regain attention"
            })
            current_time += interval

        return {
            "hook_intervals": hook_intervals,
            "opening_hook": hooks[0].text if hooks else "Strong opening required",
            "mid_roll_hooks": len(hook_intervals),
            "retention_target": "60%+",
            "strategy": "Progressive revelation with regular pattern interruptions"
        }

    def _plan_engagement_moments(
        self,
        video_duration: int,
        triggers: List[TriggerApplication]
    ) -> List[Dict[str, str]]:
        """Plan moments designed for engagement"""
        moments = []

        # Opening engagement
        moments.append({
            "time": "0:15",
            "type": "question",
            "action": "Pose engaging question to encourage comments"
        })

        # Middle engagement
        if video_duration > 8:
            moments.append({
                "time": f"{video_duration // 2}:00",
                "type": "poll",
                "action": "Ask viewers to comment their opinion"
            })

        # End engagement
        moments.append({
            "time": f"{video_duration - 1}:00",
            "type": "cta",
            "action": "Encourage likes, comments, and shares"
        })

        return moments

    def _plan_cta_placements(self, video_duration: int) -> List[Dict[str, str]]:
        """Plan call-to-action placements"""
        placements = []

        # Soft CTA early
        placements.append({
            "time": "1:30",
            "type": "soft_cta",
            "message": "If you're enjoying this, hit that like button"
        })

        # Main CTA at end
        placements.append({
            "time": f"{video_duration - 0.5}:00",
            "type": "main_cta",
            "message": "Subscribe for more content like this"
        })

        return placements

    def _calculate_virality_score(
        self,
        hooks: List[Hook],
        triggers: List[TriggerApplication],
        patterns: List[ViralPattern]
    ) -> float:
        """Calculate overall virality potential score"""
        scores = []

        # Hook quality
        if hooks:
            avg_hook_score = sum(h.virality_score for h in hooks) / len(hooks)
            scores.append(avg_hook_score)
        else:
            scores.append(5.0)

        # Trigger effectiveness
        if triggers:
            avg_trigger_effectiveness = sum(t.effectiveness_score for t in triggers) / len(triggers)
            scores.append(avg_trigger_effectiveness * 10)
        else:
            scores.append(7.0)

        # Pattern success rate
        if patterns:
            avg_pattern_success = sum(p.success_rate for p in patterns) / len(patterns)
            scores.append(avg_pattern_success * 10)
        else:
            scores.append(7.0)

        return round(sum(scores) / len(scores), 1)

    def generate_summary(self, strategy: ViralStrategy) -> str:
        """Generate human-readable viral strategy summary"""
        best_hook = max(strategy.hooks, key=lambda h: h.virality_score) if strategy.hooks else None

        summary = f"""
# Viral Strategy: {strategy.topic}

**Generated**: {strategy.generated_at}
**Virality Score**: {strategy.virality_score}/10
**Processing Time**: {strategy.processing_time:.1f}s

## Best Opening Hook ({best_hook.virality_score}/10 if best_hook else 'N/A')

{best_hook.text if best_hook else 'No hooks generated'}

*Triggers*: {', '.join(best_hook.trigger_types) if best_hook else 'None'}

## Psychology Triggers ({len(strategy.triggers)})

{chr(10).join(f'{i+1}. **{t.trigger_type.value}** ({t.effectiveness_score:.0%} effective) - {t.description}' for i, t in enumerate(strategy.triggers[:8]))}

## Retention Strategy

- **Hook Intervals**: {len(strategy.retention_strategy.get('hook_intervals', []))}
- **Target Retention**: {strategy.retention_strategy.get('retention_target', 'N/A')}
- **Strategy**: {strategy.retention_strategy.get('strategy', 'N/A')}

## Engagement Moments

{chr(10).join(f"- **{m['time']}**: {m['action']}" for m in strategy.engagement_moments)}

## Call-to-Action Placements

{chr(10).join(f"- **{cta['time']}** ({cta['type']}): {cta['message']}" for cta in strategy.cta_placements)}

## Viral Patterns

{chr(10).join(f"- **{p.pattern_type}** ({p.success_rate:.0%} success): {p.description}" for p in strategy.patterns)}
"""
        return summary.strip()
