"""
Psychology Triggers - 16 proven psychological triggers for virality
Based on Brendan Kane's methodology
"""

import logging
from typing import Dict, List, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """16 psychological triggers for viral content"""
    CURIOSITY_GAP = "curiosity_gap"
    SOCIAL_PROOF = "social_proof"
    AUTHORITY = "authority"
    SCARCITY = "scarcity"
    RECIPROCITY = "reciprocity"
    STORYTELLING = "storytelling"
    PATTERN_INTERRUPTION = "pattern_interruption"
    LOSS_AVERSION = "loss_aversion"
    NOVELTY = "novelty"
    CONTROVERSY = "controversy"
    IDENTITY = "identity"
    PROGRESS = "progress"
    TRANSFORMATION = "transformation"
    MYSTERY = "mystery"
    URGENCY = "urgency"
    TRIBAL_BELONGING = "tribal_belonging"


@dataclass
class TriggerApplication:
    """Application of a psychology trigger"""
    trigger_type: TriggerType
    description: str
    implementation: str
    effectiveness_score: float
    timing: str  # when to use in video
    examples: List[str]


class PsychologyTriggers:
    """
    Manages and applies 16 psychological triggers for viral content
    """

    def __init__(self):
        """Initialize psychology triggers system"""
        self.triggers = self._initialize_triggers()
        logger.info("Psychology Triggers initialized with 16 triggers")

    def _initialize_triggers(self) -> Dict[TriggerType, Dict[str, Any]]:
        """Initialize trigger database"""
        return {
            TriggerType.CURIOSITY_GAP: {
                "name": "Curiosity Gap",
                "description": "Create information gap that viewers want filled",
                "effectiveness": 0.95,
                "examples": [
                    "What scientists discovered will shock you...",
                    "The secret that changed everything...",
                    "You won't believe what happened next..."
                ],
                "best_timing": "Opening, transitions"
            },
            TriggerType.SOCIAL_PROOF: {
                "name": "Social Proof",
                "description": "Show others doing/believing something",
                "effectiveness": 0.90,
                "examples": [
                    "Millions are already doing this...",
                    "Top experts agree...",
                    "The method everyone's talking about..."
                ],
                "best_timing": "Middle sections"
            },
            TriggerType.AUTHORITY: {
                "name": "Authority",
                "description": "Reference credible experts and sources",
                "effectiveness": 0.88,
                "examples": [
                    "According to Harvard researchers...",
                    "Nobel Prize winner explains...",
                    "Leading expert reveals..."
                ],
                "best_timing": "Throughout"
            },
            TriggerType.SCARCITY: {
                "name": "Scarcity",
                "description": "Limited availability or exclusivity",
                "effectiveness": 0.85,
                "examples": [
                    "Only a few people know this...",
                    "Rare footage shows...",
                    "This window won't last..."
                ],
                "best_timing": "CTA sections"
            },
            TriggerType.STORYTELLING: {
                "name": "Storytelling",
                "description": "Use narrative structure with emotional arc",
                "effectiveness": 0.93,
                "examples": [
                    "Once there was a scientist who...",
                    "This is the story of how...",
                    "It all started when..."
                ],
                "best_timing": "Throughout"
            },
            TriggerType.PATTERN_INTERRUPTION: {
                "name": "Pattern Interruption",
                "description": "Break expected patterns to regain attention",
                "effectiveness": 0.87,
                "examples": [
                    "But here's where it gets interesting...",
                    "Wait - there's more...",
                    "Plot twist..."
                ],
                "best_timing": "Every 2-3 minutes"
            },
            TriggerType.LOSS_AVERSION: {
                "name": "Loss Aversion",
                "description": "Highlight what viewer might miss",
                "effectiveness": 0.84,
                "examples": [
                    "Don't miss out on...",
                    "What you're losing by not knowing...",
                    "The cost of ignoring this..."
                ],
                "best_timing": "Middle and end"
            },
            TriggerType.TRANSFORMATION: {
                "name": "Transformation",
                "description": "Show before/after or change process",
                "effectiveness": 0.91,
                "examples": [
                    "How this changed everything...",
                    "From unknown to famous in...",
                    "The complete transformation..."
                ],
                "best_timing": "Main content"
            },
            TriggerType.MYSTERY: {
                "name": "Mystery",
                "description": "Pose questions and delay answers",
                "effectiveness": 0.89,
                "examples": [
                    "The question nobody can answer...",
                    "A mystery that baffled experts...",
                    "The unexplained phenomenon..."
                ],
                "best_timing": "Opening and throughout"
            },
            TriggerType.NOVELTY: {
                "name": "Novelty",
                "description": "Present new, unexpected information",
                "effectiveness": 0.86,
                "examples": [
                    "Never-before-seen...",
                    "A breakthrough discovery...",
                    "The new way to..."
                ],
                "best_timing": "Opening"
            },
            TriggerType.CONTROVERSY: {
                "name": "Controversy",
                "description": "Present contrarian or debated views",
                "effectiveness": 0.82,
                "examples": [
                    "Why experts are wrong about...",
                    "The controversial truth...",
                    "What they don't want you to know..."
                ],
                "best_timing": "Use carefully"
            },
            TriggerType.IDENTITY: {
                "name": "Identity",
                "description": "Connect to viewer's self-image",
                "effectiveness": 0.88,
                "examples": [
                    "If you're someone who...",
                    "For people who value...",
                    "True [type of person] know..."
                ],
                "best_timing": "Opening and throughout"
            },
            TriggerType.PROGRESS: {
                "name": "Progress",
                "description": "Show advancement or achievement",
                "effectiveness": 0.85,
                "examples": [
                    "The breakthrough that...",
                    "How far we've come...",
                    "The next level of..."
                ],
                "best_timing": "Main content"
            },
            TriggerType.URGENCY: {
                "name": "Urgency",
                "description": "Create time pressure",
                "effectiveness": 0.83,
                "examples": [
                    "This is happening now...",
                    "Time is running out...",
                    "Critical moment for..."
                ],
                "best_timing": "CTA sections"
            },
            TriggerType.TRIBAL_BELONGING: {
                "name": "Tribal Belonging",
                "description": "Create in-group feeling",
                "effectiveness": 0.87,
                "examples": [
                    "For those in the know...",
                    "Join the movement...",
                    "We understand..."
                ],
                "best_timing": "Throughout"
            },
            TriggerType.RECIPROCITY: {
                "name": "Reciprocity",
                "description": "Give value first",
                "effectiveness": 0.84,
                "examples": [
                    "I'm going to show you...",
                    "Here's everything you need...",
                    "Let me share with you..."
                ],
                "best_timing": "Opening"
            }
        }

    def get_trigger_recommendations(
        self,
        topic: str,
        audience: str,
        video_duration: int
    ) -> List[TriggerApplication]:
        """
        Get recommended triggers for content

        Args:
            topic: Content topic
            audience: Target audience
            video_duration: Video length in minutes

        Returns:
            List of recommended trigger applications
        """
        recommendations = []

        # Always include core triggers
        core_triggers = [
            TriggerType.CURIOSITY_GAP,
            TriggerType.STORYTELLING,
            TriggerType.TRANSFORMATION
        ]

        # Add based on duration
        if video_duration > 10:
            core_triggers.extend([
                TriggerType.PATTERN_INTERRUPTION,
                TriggerType.MYSTERY,
                TriggerType.SOCIAL_PROOF
            ])

        # Add based on topic characteristics
        # (simplified - in production would use ML/AI)
        core_triggers.extend([
            TriggerType.AUTHORITY,
            TriggerType.NOVELTY
        ])

        for trigger_type in core_triggers:
            trigger_info = self.triggers[trigger_type]
            application = TriggerApplication(
                trigger_type=trigger_type,
                description=trigger_info["description"],
                implementation=f"Apply {trigger_info['name']} by: {trigger_info['examples'][0]}",
                effectiveness_score=trigger_info["effectiveness"],
                timing=trigger_info["best_timing"],
                examples=trigger_info["examples"]
            )
            recommendations.append(application)

        # Sort by effectiveness
        recommendations.sort(key=lambda x: x.effectiveness_score, reverse=True)

        return recommendations

    def analyze_trigger_usage(self, content: str) -> Dict[TriggerType, float]:
        """
        Analyze which triggers are used in content

        Args:
            content: Content to analyze

        Returns:
            Dictionary of trigger types and usage scores
        """
        usage = {}

        # Simple keyword-based analysis
        # In production, would use NLP/AI
        content_lower = content.lower()

        for trigger_type, info in self.triggers.items():
            score = 0.0

            # Check for examples in content
            for example in info["examples"]:
                if any(word in content_lower for word in example.lower().split()):
                    score += 0.3

            usage[trigger_type] = min(score, 1.0)

        return usage

    def get_all_triggers(self) -> List[Dict[str, Any]]:
        """Get information about all triggers"""
        return [
            {
                "type": trigger_type.value,
                "name": info["name"],
                "description": info["description"],
                "effectiveness": info["effectiveness"],
                "examples": info["examples"],
                "timing": info["best_timing"]
            }
            for trigger_type, info in self.triggers.items()
        ]
