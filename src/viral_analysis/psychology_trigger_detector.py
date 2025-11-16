"""
Psychology Trigger Detector
Identifies and implements 16 psychological triggers for virality
Based on proven psychological principles and Brendan Kane methodology
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class PsychologyTrigger(Enum):
    """16 Psychological Triggers for Viral Content"""
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
class TriggerDefinition:
    """Definition of a psychology trigger"""
    name: str
    description: str
    implementation_guide: str
    examples: List[str]
    effectiveness_score: float
    best_placement: List[str]  # opening, middle, climax, conclusion


class PsychologyTriggerDetector:
    """
    Detects and implements psychological triggers in content.
    Uses AI and pattern matching to identify trigger usage.
    """

    def __init__(self):
        self.triggers = self._initialize_triggers()

    def _initialize_triggers(self) -> Dict[str, TriggerDefinition]:
        """Initialize all 16 psychology triggers with definitions"""
        return {
            PsychologyTrigger.CURIOSITY_GAP.value: TriggerDefinition(
                name="Curiosity Gap",
                description="Create a gap between what viewers know and want to know",
                implementation_guide="Tease information without revealing the answer immediately. Use 'what if', 'the secret', 'what nobody tells you'",
                examples=[
                    "What if everything you know about X is wrong?",
                    "The secret that experts don't want you to know...",
                    "Here's what happens when... (but we'll show you later)"
                ],
                effectiveness_score=9.5,
                best_placement=["opening", "middle"]
            ),
            PsychologyTrigger.SOCIAL_PROOF.value: TriggerDefinition(
                name="Social Proof",
                description="Show that others are doing/believing something",
                implementation_guide="Reference millions of people, experts, studies, popular opinion",
                examples=[
                    "Over 10 million people are doing this...",
                    "Scientists discovered...",
                    "The method used by Fortune 500 companies..."
                ],
                effectiveness_score=8.5,
                best_placement=["opening", "middle"]
            ),
            PsychologyTrigger.AUTHORITY.value: TriggerDefinition(
                name="Authority",
                description="Establish credibility and expertise",
                implementation_guide="Cite experts, research, credentials, data",
                examples=[
                    "According to Harvard research...",
                    "Top experts agree...",
                    "The data shows conclusively..."
                ],
                effectiveness_score=8.0,
                best_placement=["opening", "middle"]
            ),
            PsychologyTrigger.SCARCITY.value: TriggerDefinition(
                name="Scarcity",
                description="Suggest limited availability or rare information",
                implementation_guide="Emphasize rarity, exclusivity, time-sensitivity",
                examples=[
                    "This rarely happens...",
                    "Few people know about...",
                    "This window is closing..."
                ],
                effectiveness_score=7.5,
                best_placement=["opening", "conclusion"]
            ),
            PsychologyTrigger.RECIPROCITY.value: TriggerDefinition(
                name="Reciprocity",
                description="Give value first to encourage engagement",
                implementation_guide="Provide immediate value, free insights, actionable tips",
                examples=[
                    "I'm going to show you exactly how...",
                    "Here's a free framework you can use...",
                    "Let me give you the complete breakdown..."
                ],
                effectiveness_score=8.0,
                best_placement=["opening", "middle", "conclusion"]
            ),
            PsychologyTrigger.STORYTELLING.value: TriggerDefinition(
                name="Storytelling",
                description="Use narrative structure to engage emotionally",
                implementation_guide="Personal stories, case studies, hero's journey",
                examples=[
                    "Let me tell you about someone who...",
                    "This is the story of how...",
                    "It started when..."
                ],
                effectiveness_score=9.0,
                best_placement=["opening", "middle"]
            ),
            PsychologyTrigger.PATTERN_INTERRUPTION.value: TriggerDefinition(
                name="Pattern Interruption",
                description="Break expected patterns to regain attention",
                implementation_guide="Unexpected statements, format changes, surprising facts",
                examples=[
                    "Wait... that's not what happened",
                    "But here's where it gets weird...",
                    "You won't believe what happened next..."
                ],
                effectiveness_score=8.5,
                best_placement=["middle", "climax"]
            ),
            PsychologyTrigger.LOSS_AVERSION.value: TriggerDefinition(
                name="Loss Aversion",
                description="Highlight what viewers might lose by not watching",
                implementation_guide="Emphasize missed opportunities, mistakes to avoid, costs of ignorance",
                examples=[
                    "Don't make this costly mistake...",
                    "What you're losing by not knowing...",
                    "The price of ignoring this..."
                ],
                effectiveness_score=8.0,
                best_placement=["opening", "middle"]
            ),
            PsychologyTrigger.NOVELTY.value: TriggerDefinition(
                name="Novelty",
                description="Present new, unusual, or surprising information",
                implementation_guide="Emphasize 'new', 'never before', 'just discovered'",
                examples=[
                    "Scientists just discovered...",
                    "A brand new approach to...",
                    "This changes everything we thought about..."
                ],
                effectiveness_score=9.0,
                best_placement=["opening", "climax"]
            ),
            PsychologyTrigger.CONTROVERSY.value: TriggerDefinition(
                name="Controversy",
                description="Present opposing views or challenge conventional wisdom",
                implementation_guide="Challenge beliefs, present alternative views, debate",
                examples=[
                    "Why everyone is wrong about...",
                    "The truth they don't want you to know...",
                    "This contradicts everything you've heard..."
                ],
                effectiveness_score=8.0,
                best_placement=["opening", "middle"]
            ),
            PsychologyTrigger.IDENTITY.value: TriggerDefinition(
                name="Identity",
                description="Connect to viewer's self-image and aspirations",
                implementation_guide="Target specific groups, lifestyles, values",
                examples=[
                    "If you're someone who values...",
                    "For people who want to be...",
                    "This is for ambitious people who..."
                ],
                effectiveness_score=8.5,
                best_placement=["opening", "conclusion"]
            ),
            PsychologyTrigger.PROGRESS.value: TriggerDefinition(
                name="Progress",
                description="Show advancement, improvement, or evolution",
                implementation_guide="Before/after, transformation journey, milestones",
                examples=[
                    "From zero to...",
                    "How I went from X to Y...",
                    "The evolution of..."
                ],
                effectiveness_score=8.0,
                best_placement=["middle", "climax"]
            ),
            PsychologyTrigger.TRANSFORMATION.value: TriggerDefinition(
                name="Transformation",
                description="Promise or demonstrate significant change",
                implementation_guide="Show dramatic change, life-changing impact, breakthrough",
                examples=[
                    "This completely transformed...",
                    "Life before and after...",
                    "The moment everything changed..."
                ],
                effectiveness_score=9.0,
                best_placement=["opening", "climax", "conclusion"]
            ),
            PsychologyTrigger.MYSTERY.value: TriggerDefinition(
                name="Mystery",
                description="Create intrigue through unanswered questions",
                implementation_guide="Pose questions, create suspense, delay revelation",
                examples=[
                    "The question that nobody can answer...",
                    "What's really going on with...",
                    "The mystery behind..."
                ],
                effectiveness_score=9.0,
                best_placement=["opening", "middle"]
            ),
            PsychologyTrigger.URGENCY.value: TriggerDefinition(
                name="Urgency",
                description="Create time pressure or immediate relevance",
                implementation_guide="Emphasize 'now', 'today', 'right now', current events",
                examples=[
                    "This is happening right now...",
                    "Why you need to know this today...",
                    "The urgent truth about..."
                ],
                effectiveness_score=7.5,
                best_placement=["opening", "conclusion"]
            ),
            PsychologyTrigger.TRIBAL_BELONGING.value: TriggerDefinition(
                name="Tribal Belonging",
                description="Create in-group connection and community",
                implementation_guide="Use 'we', 'us', shared values, common enemies",
                examples=[
                    "We all know the feeling when...",
                    "If you're like me and...",
                    "For those of us who understand..."
                ],
                effectiveness_score=8.5,
                best_placement=["opening", "conclusion"]
            )
        }

    def detect_triggers(self, content: str) -> List[Dict[str, Any]]:
        """
        Detect psychology triggers present in content

        Args:
            content: Content to analyze

        Returns:
            List of detected triggers with confidence scores
        """
        detected = []
        content_lower = content.lower()

        # Define detection patterns for each trigger
        patterns = {
            PsychologyTrigger.CURIOSITY_GAP.value: [
                'what if', 'the secret', 'what nobody', 'what they don\'t', 'you won\'t believe',
                'wait until you', 'but here\'s', 'the truth about', 'what really'
            ],
            PsychologyTrigger.SOCIAL_PROOF.value: [
                'million', 'thousands', 'everyone', 'people are', 'experts', 'studies show',
                'research shows', 'proven', 'scientists'
            ],
            PsychologyTrigger.AUTHORITY.value: [
                'research', 'study', 'expert', 'scientist', 'professor', 'harvard', 'stanford',
                'data shows', 'according to'
            ],
            PsychologyTrigger.SCARCITY.value: [
                'rare', 'limited', 'exclusive', 'few people', 'only', 'secret', 'hidden'
            ],
            PsychologyTrigger.RECIPROCITY.value: [
                'i\'ll show you', 'let me give', 'here\'s how', 'free', 'you can use',
                'i\'m going to share'
            ],
            PsychologyTrigger.STORYTELLING.value: [
                'story', 'once', 'when i', 'there was', 'imagine', 'picture this',
                'let me tell you'
            ],
            PsychologyTrigger.PATTERN_INTERRUPTION.value: [
                'but wait', 'however', 'surprisingly', 'unexpectedly', 'plot twist',
                'here\'s where it gets', 'you won\'t believe'
            ],
            PsychologyTrigger.LOSS_AVERSION.value: [
                'don\'t make', 'avoid', 'mistake', 'losing', 'miss out', 'without knowing',
                'cost of'
            ],
            PsychologyTrigger.NOVELTY.value: [
                'new', 'just discovered', 'breakthrough', 'never before', 'first time',
                'revolutionary', 'innovative'
            ],
            PsychologyTrigger.CONTROVERSY.value: [
                'wrong about', 'myth', 'lie', 'truth', 'exposed', 'challenge', 'debate',
                'controversial'
            ],
            PsychologyTrigger.IDENTITY.value: [
                'if you\'re', 'for people who', 'ambitious', 'smart people', 'successful',
                'like you'
            ],
            PsychologyTrigger.PROGRESS.value: [
                'from', 'to', 'journey', 'evolution', 'growth', 'improvement', 'before and after'
            ],
            PsychologyTrigger.TRANSFORMATION.value: [
                'transformed', 'changed', 'breakthrough', 'revolutionized', 'game-changer',
                'life-changing'
            ],
            PsychologyTrigger.MYSTERY.value: [
                'mystery', 'unknown', 'unexplained', 'question', 'puzzle', 'enigma',
                'nobody knows'
            ],
            PsychologyTrigger.URGENCY.value: [
                'now', 'today', 'urgent', 'immediately', 'right now', 'happening now',
                'breaking'
            ],
            PsychologyTrigger.TRIBAL_BELONGING.value: [
                'we', 'us', 'our', 'together', 'community', 'if you\'re like me',
                'people like us'
            ]
        }

        # Detect each trigger
        for trigger_key, keywords in patterns.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > 0:
                trigger = self.triggers[trigger_key]
                confidence = min(matches / len(keywords) * 10, 10.0)

                detected.append({
                    'trigger': trigger_key,
                    'name': trigger.name,
                    'confidence': round(confidence, 2),
                    'match_count': matches,
                    'effectiveness_score': trigger.effectiveness_score
                })

        # Sort by confidence
        detected.sort(key=lambda x: x['confidence'], reverse=True)
        return detected

    def suggest_triggers(
        self,
        content_type: str,
        target_audience: str,
        placement: str = "opening"
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal triggers for content

        Args:
            content_type: Type of content (documentary, educational, entertainment)
            target_audience: Target audience description
            placement: Where in video (opening, middle, climax, conclusion)

        Returns:
            List of recommended triggers
        """
        recommendations = []

        for trigger_key, trigger in self.triggers.items():
            if placement in trigger.best_placement:
                score = trigger.effectiveness_score

                # Adjust score based on content type
                if content_type.lower() in ['documentary', 'educational']:
                    if trigger_key in [
                        PsychologyTrigger.AUTHORITY.value,
                        PsychologyTrigger.SOCIAL_PROOF.value,
                        PsychologyTrigger.NOVELTY.value
                    ]:
                        score += 1.0
                elif content_type.lower() == 'entertainment':
                    if trigger_key in [
                        PsychologyTrigger.STORYTELLING.value,
                        PsychologyTrigger.PATTERN_INTERRUPTION.value,
                        PsychologyTrigger.MYSTERY.value
                    ]:
                        score += 1.0

                recommendations.append({
                    'trigger': trigger_key,
                    'name': trigger.name,
                    'score': min(score, 10.0),
                    'implementation_guide': trigger.implementation_guide,
                    'examples': trigger.examples
                })

        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:10]  # Top 10

    def generate_trigger_plan(
        self,
        video_duration: int,
        content_type: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """
        Generate complete trigger implementation plan for video

        Args:
            video_duration: Video duration in minutes
            content_type: Type of content
            target_audience: Target audience

        Returns:
            Complete trigger plan with timing
        """
        segments = {
            'opening': (0, 0.25),  # First 0-15 seconds
            'hook_extension': (0.25, 2),  # 15 sec - 2 min
            'middle': (2, video_duration * 0.7),
            'climax': (video_duration * 0.7, video_duration * 0.9),
            'conclusion': (video_duration * 0.9, video_duration)
        }

        plan = {
            'video_duration': video_duration,
            'content_type': content_type,
            'target_audience': target_audience,
            'segments': {}
        }

        for segment_name, (start, end) in segments.items():
            placement = 'opening' if 'opening' in segment_name or 'hook' in segment_name else \
                       'climax' if 'climax' in segment_name else \
                       'conclusion' if 'conclusion' in segment_name else 'middle'

            triggers = self.suggest_triggers(content_type, target_audience, placement)[:3]

            plan['segments'][segment_name] = {
                'start_time': start,
                'end_time': end,
                'recommended_triggers': triggers,
                'trigger_count': len(triggers)
            }

        return plan

    def get_trigger_definition(self, trigger_key: str) -> Optional[TriggerDefinition]:
        """Get definition for a specific trigger"""
        return self.triggers.get(trigger_key)

    def get_all_triggers(self) -> Dict[str, TriggerDefinition]:
        """Get all trigger definitions"""
        return self.triggers

    def calculate_trigger_diversity(self, detected_triggers: List[Dict[str, Any]]) -> float:
        """
        Calculate diversity score (higher is better)

        Args:
            detected_triggers: List of detected triggers

        Returns:
            Diversity score 0-10
        """
        if not detected_triggers:
            return 0.0

        unique_triggers = len(detected_triggers)
        total_possible = len(self.triggers)

        diversity = (unique_triggers / total_possible) * 10
        return round(diversity, 2)
