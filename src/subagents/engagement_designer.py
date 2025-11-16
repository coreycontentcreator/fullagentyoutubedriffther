"""
Engagement Designer Subagent
Designs moments for comments, shares, and interactions
"""

from typing import Dict, List, Any, Optional


class EngagementDesigner:
    """
    Designs strategic engagement moments throughout video
    """

    def __init__(self):
        self.engagement_types = self._initialize_engagement_types()

    def _initialize_engagement_types(self) -> Dict[str, Dict[str, Any]]:
        """Initialize engagement mechanisms"""
        return {
            'comment_prompt': {
                'description': 'Encourage viewers to comment',
                'techniques': [
                    'Ask controversial question',
                    'Request personal experience',
                    'Pose debate topic',
                    'Ask for opinion'
                ],
                'effectiveness': 8.5
            },
            'share_trigger': {
                'description': 'Motivate sharing',
                'techniques': [
                    'Create "mind-blown" moment',
                    'Share counter-intuitive insight',
                    'Provide social currency',
                    'Make viewer look smart for sharing'
                ],
                'effectiveness': 7.5
            },
            'like_cue': {
                'description': 'Prompt likes naturally',
                'techniques': [
                    'Deliver exceptional value',
                    'Create emotional peak',
                    'Surprise with quality',
                    'Remind subtly if enjoyed'
                ],
                'effectiveness': 7.0
            },
            'subscribe_conversion': {
                'description': 'Convert to subscriber',
                'techniques': [
                    'Promise similar content',
                    'Tease next video',
                    'Show value of subscribing',
                    'Make specific promise'
                ],
                'effectiveness': 8.0
            },
            'community_building': {
                'description': 'Build community feeling',
                'techniques': [
                    'Use "we/us" language',
                    'Reference shared values',
                    'Create in-group identity',
                    'Acknowledge loyal viewers'
                ],
                'effectiveness': 8.5
            }
        }

    def design_engagement_strategy(
        self,
        video_duration_minutes: int,
        content_type: str = "documentary",
        target_audience: str = "general"
    ) -> Dict[str, Any]:
        """
        Design complete engagement strategy

        Args:
            video_duration_minutes: Video duration
            content_type: Type of content
            target_audience: Target audience

        Returns:
            Engagement strategy with timed prompts
        """
        duration_seconds = video_duration_minutes * 60

        strategy = {
            'video_duration': video_duration_minutes,
            'engagement_moments': []
        }

        # Early engagement (first minute) - build connection
        strategy['engagement_moments'].append({
            'timestamp': '0:30-0:45',
            'engagement_type': 'community_building',
            'action': 'Establish connection with audience',
            'example_phrases': [
                "If you've ever wondered about...",
                "We're going to explore...",
                "For those of you who love..."
            ],
            'purpose': 'Create immediate connection',
            'priority': 'HIGH'
        })

        # Mid-video (around 30-40% mark) - first comment prompt
        mid_point = int(duration_seconds * 0.35)
        strategy['engagement_moments'].append({
            'timestamp': self._format_timestamp(mid_point),
            'engagement_type': 'comment_prompt',
            'action': 'Ask for viewer input or opinion',
            'example_phrases': [
                "What do you think about this? Let me know in the comments",
                "Have you experienced this? Comment below",
                "I'm curious - comment if you..."
            ],
            'purpose': 'Early engagement to boost algorithm',
            'priority': 'HIGH'
        })

        # Peak moment (70-75% mark) - share trigger
        peak = int(duration_seconds * 0.72)
        strategy['engagement_moments'].append({
            'timestamp': self._format_timestamp(peak),
            'engagement_type': 'share_trigger',
            'action': 'Create shareable moment',
            'techniques': [
                'Deliver biggest insight/revelation',
                'Create quotable moment',
                'Provide social currency',
                'Make viewer look smart for sharing'
            ],
            'purpose': 'Maximize shareability at emotional peak',
            'priority': 'CRITICAL'
        })

        # Late engagement (85-90% mark) - subscribe CTA
        late = int(duration_seconds * 0.87)
        strategy['engagement_moments'].append({
            'timestamp': self._format_timestamp(late),
            'engagement_type': 'subscribe_conversion',
            'action': 'Natural subscribe prompt',
            'example_phrases': [
                "If you enjoyed this, we have more coming...",
                "Subscribe for the next video on...",
                "Join our community of X people who..."
            ],
            'purpose': 'Convert satisfied viewers',
            'priority': 'HIGH'
        })

        # End (95%+) - final engagement
        end = int(duration_seconds * 0.95)
        strategy['engagement_moments'].append({
            'timestamp': self._format_timestamp(end),
            'engagement_type': 'like_cue',
            'action': 'Soft like reminder',
            'example_phrases': [
                "If this was valuable, let me know by...",
                "Your support helps us create more of this"
            ],
            'purpose': 'Final engagement push',
            'priority': 'MEDIUM'
        })

        return strategy

    def create_comment_prompts(
        self,
        topic: str,
        content_insights: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Create effective comment prompts

        Args:
            topic: Video topic
            content_insights: Key insights from video

        Returns:
            List of comment prompt options
        """
        prompts = []

        # Opinion-based prompts
        prompts.append({
            'type': 'opinion',
            'prompt': f"What's your take on {topic}? Drop your thoughts below!",
            'effectiveness': 8.0,
            'expected_response_rate': 'medium-high'
        })

        # Experience-based prompts
        prompts.append({
            'type': 'experience',
            'prompt': f"Have you ever experienced this with {topic}? Share your story!",
            'effectiveness': 9.0,
            'expected_response_rate': 'high'
        })

        # Debate prompts
        if len(content_insights) >= 2:
            prompts.append({
                'type': 'debate',
                'prompt': f"Team {content_insights[0]} or Team {content_insights[1]}? Comment below!",
                'effectiveness': 9.5,
                'expected_response_rate': 'very high'
            })

        # Prediction prompts
        prompts.append({
            'type': 'prediction',
            'prompt': f"Where do you think {topic} is headed? Comment your prediction!",
            'effectiveness': 7.5,
            'expected_response_rate': 'medium'
        })

        # Question prompts
        prompts.append({
            'type': 'question',
            'prompt': f"What else do you want to know about {topic}? Ask in comments!",
            'effectiveness': 8.0,
            'expected_response_rate': 'medium-high'
        })

        return prompts

    def design_shareable_moments(
        self,
        key_insights: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Design moments optimized for sharing

        Args:
            key_insights: Key insights from content

        Returns:
            List of shareable moment designs
        """
        moments = []

        for i, insight in enumerate(key_insights[:5]):  # Top 5 insights
            moments.append({
                'insight': insight,
                'presentation': {
                    'visual': 'Clean, quotable text overlay on compelling visual',
                    'audio': 'Emphatic delivery with slight pause after',
                    'pacing': 'Give viewers 2-3 seconds to absorb'
                },
                'shareability_score': 8.0 + (i * 0.2),  # Diminishing importance
                'share_triggers': [
                    'Counter-intuitive insight',
                    'Makes viewer look smart',
                    'Challenges common belief'
                ],
                'implementation': f'Present at key moment, make visually striking, pause for impact'
            })

        return moments

    def optimize_cta_placement(
        self,
        video_duration_minutes: int,
        cta_type: str = "subscribe"
    ) -> Dict[str, Any]:
        """
        Optimize call-to-action placement

        Args:
            video_duration_minutes: Video duration
            cta_type: Type of CTA (subscribe, like, comment, external)

        Returns:
            CTA placement strategy
        """
        duration_seconds = video_duration_minutes * 60

        # Optimal CTA timings based on type
        cta_strategies = {
            'subscribe': {
                'primary_time': int(duration_seconds * 0.87),  # Near end after value delivery
                'secondary_time': int(duration_seconds * 0.30),  # Early for engaged viewers
                'approach': 'Value-based - show what subscribers get'
            },
            'like': {
                'primary_time': int(duration_seconds * 0.92),  # Very end
                'secondary_time': None,
                'approach': 'Soft reminder - "if you enjoyed this..."'
            },
            'comment': {
                'primary_time': int(duration_seconds * 0.35),  # Early-mid for engagement
                'secondary_time': int(duration_seconds * 0.85),  # End for final thoughts
                'approach': 'Question-based - ask specific question'
            },
            'external': {
                'primary_time': int(duration_seconds * 0.95),  # Very end
                'secondary_time': None,
                'approach': 'Natural transition to related content'
            }
        }

        strategy = cta_strategies.get(cta_type, cta_strategies['subscribe'])

        return {
            'cta_type': cta_type,
            'primary_placement': self._format_timestamp(strategy['primary_time']),
            'secondary_placement': self._format_timestamp(strategy['secondary_time']) if strategy['secondary_time'] else None,
            'approach': strategy['approach'],
            'best_practices': self._get_cta_best_practices(cta_type)
        }

    def calculate_engagement_score(
        self,
        video_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate engagement score based on metrics

        Args:
            video_data: Video metrics

        Returns:
            Engagement score breakdown
        """
        views = video_data.get('views', 0)
        likes = video_data.get('likes', 0)
        comments = video_data.get('comments', 0)
        shares = video_data.get('shares', 0)

        # Calculate rates
        like_rate = (likes / views * 100) if views > 0 else 0
        comment_rate = (comments / views * 100) if views > 0 else 0
        share_rate = (shares / views * 100) if views > 0 else 0

        # Calculate weighted engagement score
        engagement_score = (
            like_rate * 0.4 +
            comment_rate * 0.35 +
            share_rate * 0.25
        )

        # Normalize to 0-10 scale
        normalized_score = min(engagement_score * 2, 10.0)

        return {
            'overall_engagement_score': round(normalized_score, 2),
            'like_rate': round(like_rate, 3),
            'comment_rate': round(comment_rate, 3),
            'share_rate': round(share_rate, 3),
            'metrics': {
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': shares
            },
            'rating': self._rate_engagement(normalized_score)
        }

    def _get_cta_best_practices(self, cta_type: str) -> List[str]:
        """Get best practices for CTA type"""
        practices = {
            'subscribe': [
                'Show value of subscribing (what they get)',
                'Make it specific - "subscribe for more videos on X"',
                'Time it after delivering value',
                'Be authentic, not pushy'
            ],
            'like': [
                'Frame as support/feedback, not demand',
                'Tie to value received',
                'Keep it brief and natural',
                'Only ask if video delivered value'
            ],
            'comment': [
                'Ask specific, engaging question',
                'Make it easy to answer',
                'Show you read comments',
                'Prompt debate or discussion'
            ]
        }
        return practices.get(cta_type, ['Be natural and value-focused'])

    def _rate_engagement(self, score: float) -> str:
        """Rate engagement level"""
        if score >= 9.0:
            return 'Exceptional'
        elif score >= 7.5:
            return 'Excellent'
        elif score >= 6.0:
            return 'Good'
        elif score >= 4.0:
            return 'Average'
        else:
            return 'Needs Improvement'

    def _format_timestamp(self, seconds: int) -> str:
        """Format seconds to MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
