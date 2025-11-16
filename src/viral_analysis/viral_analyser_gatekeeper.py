"""
Viral Analyser Gatekeeper
Main coordinator for viral analysis system with 8 specialized subagents
Implements quality gates and orchestrates the complete viral analysis pipeline
"""

from typing import Dict, List, Any, Optional
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

sys.path.append('/home/user/fullagentyoutubedriffther/src')

from subagents.hook_specialist import HookSpecialist
from subagents.trigger_implementer import TriggerImplementer
from subagents.pattern_recognizer import PatternRecognizer
from subagents.retention_optimizer import RetentionOptimizer
from subagents.engagement_designer import EngagementDesigner
from subagents.youtube_data_analyst import YouTubeDataAnalyst
from subagents.strategy_curator import StrategyCurator
from subagents.virality_scorer import ViralityScorer

from integrations.anthropic_integration import AnthropicIntegration
from viral_analysis.psychology_trigger_detector import PsychologyTriggerDetector
from viral_analysis.brendan_kane_methodology import BrendanKaneMethodology
from config.config_manager import get_config_manager


class ViralAnalyserGatekeeper:
    """
    Main gatekeeper for viral analysis system.
    Coordinates 8 specialized subagents to analyze and optimize content for virality.

    Subagents:
    1. Hook Specialist - Creates compelling opening hooks
    2. Trigger Implementer - Applies psychology triggers
    3. Pattern Recognizer - Identifies successful patterns
    4. Retention Optimizer - Maximizes viewer retention
    5. Engagement Designer - Designs engagement moments
    6. YouTube Data Analyst - Analyzes competitor videos
    7. Strategy Curator - Manages viral strategy library
    8. Virality Scorer - Predicts viral potential
    """

    def __init__(self, config_manager=None):
        """Initialize gatekeeper with all subagents"""
        self.config = config_manager or get_config_manager()

        # Initialize AI integration
        api_key = self.config.get_api_key('anthropic')
        self.ai = AnthropicIntegration(api_key) if api_key else None

        # Initialize core frameworks
        self.trigger_detector = PsychologyTriggerDetector()
        self.brendan_kane = BrendanKaneMethodology()

        # Initialize 8 specialized subagents
        self.hook_specialist = HookSpecialist(self.ai)
        self.trigger_implementer = TriggerImplementer()
        self.pattern_recognizer = PatternRecognizer()
        self.retention_optimizer = RetentionOptimizer()
        self.engagement_designer = EngagementDesigner()
        self.youtube_analyst = YouTubeDataAnalyst(self.config.get_api_key('youtube'))
        self.strategy_curator = StrategyCurator()
        self.virality_scorer = ViralityScorer()

        # Quality thresholds
        self.min_viral_score = self.config.config.viral_analysis.min_viral_score
        self.max_iterations = self.config.config.viral_analysis.max_iterations

        # Metrics tracking
        self.analysis_count = 0
        self.total_processing_time = 0

    def analyze_content(
        self,
        topic: str,
        research_context: Optional[Dict[str, Any]] = None,
        target_audience: str = "general",
        video_duration_minutes: int = 15,
        content_type: str = "documentary"
    ) -> Dict[str, Any]:
        """
        Complete viral analysis of content

        Args:
            topic: Main topic
            research_context: Research findings (optional)
            target_audience: Target audience description
            video_duration_minutes: Planned video duration
            content_type: Type of content

        Returns:
            Complete viral analysis with all subagent outputs
        """
        start_time = datetime.now()

        print(f"\n🎯 Viral Analysis Gatekeeper: Starting analysis for '{topic}'")
        print(f"   Target: {target_audience} | Duration: {video_duration_minutes}min | Type: {content_type}\n")

        # Step 1: Generate hooks (Hook Specialist)
        print("1️⃣  Hook Specialist: Generating viral hooks...")
        hooks = self.hook_specialist.generate_hooks(
            topic=topic,
            context=research_context,
            count=self.config.config.viral_analysis.hook_variations_count,
            target_audience=target_audience
        )
        print(f"   ✓ Generated {len(hooks)} hook variations\n")

        # Step 2: Create psychology trigger plan (Trigger Implementer)
        print("2️⃣  Trigger Implementer: Creating psychology trigger timeline...")
        trigger_timeline = self.trigger_implementer.create_trigger_timeline(
            video_duration_minutes=video_duration_minutes,
            content_type=content_type,
            target_audience=target_audience
        )
        print(f"   ✓ Created timeline with {trigger_timeline['total_triggers']} trigger placements\n")

        # Step 3: Identify optimal pattern (Pattern Recognizer)
        print("3️⃣  Pattern Recognizer: Identifying optimal content pattern...")
        content_summary = f"{topic} - {content_type} for {target_audience}"
        target_metrics = {
            'retention': 65.0,
            'engagement': 8.0
        }
        pattern_recommendation = self.pattern_recognizer.suggest_optimal_pattern(
            content_summary,
            target_metrics
        )
        print(f"   ✓ Recommended pattern: {pattern_recommendation['top_recommendation']['pattern']}\n")

        # Step 4: Generate retention strategy (Retention Optimizer)
        print("4️⃣  Retention Optimizer: Designing retention strategy...")
        retention_strategy = self.retention_optimizer.generate_retention_strategy(
            video_duration_minutes=video_duration_minutes,
            content_type=content_type
        )
        print(f"   ✓ Created retention strategy with {len(retention_strategy['retention_elements'])} key elements\n")

        # Step 5: Design engagement strategy (Engagement Designer)
        print("5️⃣  Engagement Designer: Planning engagement moments...")
        engagement_strategy = self.engagement_designer.design_engagement_strategy(
            video_duration_minutes=video_duration_minutes,
            content_type=content_type,
            target_audience=target_audience
        )
        print(f"   ✓ Designed {len(engagement_strategy['engagement_moments'])} strategic engagement moments\n")

        # Step 6: Get strategy recommendations (Strategy Curator)
        print("6️⃣  Strategy Curator: Retrieving similar successful strategies...")
        similar_strategies = self.strategy_curator.get_strategy_recommendations(
            content_type=content_type,
            target_audience=target_audience,
            video_duration=video_duration_minutes
        )
        print(f"   ✓ Found {len(similar_strategies)} relevant strategies from library\n")

        # Step 7: Assemble content package for scoring
        content_package = {
            'topic': topic,
            'hooks': hooks,
            'script': self._generate_sample_script(topic, hooks[0] if hooks else None),
            'structure': {
                'pattern': pattern_recommendation['top_recommendation']['pattern'],
                'segments': retention_strategy['retention_elements']
            },
            'psychology_triggers': trigger_timeline['timeline'],
            'engagement_moments': engagement_strategy['engagement_moments'],
            'duration_minutes': video_duration_minutes
        }

        # Step 8: Score viral potential (Virality Scorer)
        print("7️⃣  Virality Scorer: Calculating viral potential...")
        viral_score_result = self.virality_scorer.score_content(
            content_package,
            detailed=True
        )
        print(f"   ✓ Viral Score: {viral_score_result['overall_viral_score']}/10 - {viral_score_result['rating']}\n")

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        self.analysis_count += 1
        self.total_processing_time += processing_time

        # Validate quality gate
        passed_quality_gate = viral_score_result['overall_viral_score'] >= self.min_viral_score

        # Compile complete analysis
        analysis_result = {
            'metadata': {
                'topic': topic,
                'target_audience': target_audience,
                'video_duration_minutes': video_duration_minutes,
                'content_type': content_type,
                'analysis_timestamp': datetime.now().isoformat(),
                'processing_time_seconds': round(processing_time, 2)
            },
            'quality_gate': {
                'passed': passed_quality_gate,
                'viral_score': viral_score_result['overall_viral_score'],
                'threshold': self.min_viral_score,
                'status': 'APPROVED ✅' if passed_quality_gate else 'NEEDS IMPROVEMENT ⚠️'
            },
            'hooks': {
                'generated_count': len(hooks),
                'top_hooks': hooks[:3],  # Top 3
                'all_hooks': hooks
            },
            'psychology_triggers': {
                'timeline': trigger_timeline,
                'total_triggers': trigger_timeline['total_triggers']
            },
            'content_pattern': {
                'recommended_pattern': pattern_recommendation['top_recommendation'],
                'alternatives': pattern_recommendation['alternatives']
            },
            'retention_strategy': retention_strategy,
            'engagement_strategy': engagement_strategy,
            'viral_score': viral_score_result,
            'similar_strategies': similar_strategies,
            'recommendations': self._generate_comprehensive_recommendations(
                viral_score_result,
                passed_quality_gate
            )
        }

        print(f"\n{'='*70}")
        print(f"🎯 ANALYSIS COMPLETE - {analysis_result['quality_gate']['status']}")
        print(f"   Viral Score: {viral_score_result['overall_viral_score']}/10")
        print(f"   Processing Time: {processing_time:.2f}s")
        print(f"{'='*70}\n")

        return analysis_result

    def analyze_youtube_video(
        self,
        video_url: str,
        store_in_library: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze existing YouTube video for viral elements

        Args:
            video_url: YouTube video URL
            store_in_library: Whether to store in strategy library

        Returns:
            Video analysis
        """
        print(f"\n📹 Analyzing YouTube video: {video_url}\n")

        # Step 1: Analyze video data (YouTube Data Analyst)
        print("1️⃣  YouTube Data Analyst: Fetching video data...")
        video_analysis = self.youtube_analyst.analyze_video(video_url, detailed=True)
        print(f"   ✓ Analysis complete\n")

        # Step 2: Calculate tier
        metrics = video_analysis['performance_metrics']
        tier = self.youtube_analyst.calculate_viral_tier(
            views=metrics['views'],
            engagement_rate=metrics['engagement_rate'],
            retention_rate=video_analysis.get('detailed_analysis', {}).get('retention_analysis', {}).get('estimated_retention', 50.0)
        )

        video_analysis['tier'] = tier

        # Step 3: Store in library if requested and meets threshold
        if store_in_library and tier in ['gold', 'silver', 'bronze']:
            print(f"2️⃣  Strategy Curator: Storing {tier.upper()} tier strategy...")
            storage_result = self.strategy_curator.create_strategy_from_video(
                video_analysis,
                tier
            )
            print(f"   ✓ Stored as strategy ID: {storage_result.get('strategy_id')}\n")
            video_analysis['stored_in_library'] = storage_result

        return video_analysis

    def optimize_content(
        self,
        current_content: Dict[str, Any],
        optimization_focus: str = "overall"
    ) -> Dict[str, Any]:
        """
        Optimize existing content for better viral performance

        Args:
            current_content: Current content package
            optimization_focus: What to optimize (hooks, retention, engagement, overall)

        Returns:
            Optimized content with improvements
        """
        print(f"\n🔧 Optimizing content - Focus: {optimization_focus}\n")

        optimizations = {
            'focus': optimization_focus,
            'improvements': []
        }

        # Score current state
        current_score = self.virality_scorer.score_content(current_content, detailed=True)

        if optimization_focus in ['hooks', 'overall']:
            # Optimize hooks
            current_hooks = current_content.get('hooks', [])
            if current_hooks:
                feedback = "Strengthen curiosity gap and emotional impact"
                optimized_hook = self.hook_specialist.optimize_hook(current_hooks[0], feedback)
                optimizations['improvements'].append({
                    'area': 'hooks',
                    'change': 'Optimized primary hook',
                    'before': current_hooks[0],
                    'after': optimized_hook
                })

        if optimization_focus in ['retention', 'overall']:
            # Optimize retention
            video_duration = current_content.get('duration_minutes', 15)
            retention_analysis = self.retention_optimizer.analyze_retention_risk(
                video_duration * 60,
                current_content.get('structure', {})
            )
            optimizations['improvements'].append({
                'area': 'retention',
                'risks_identified': len(retention_analysis['retention_risks']),
                'recommendations': retention_analysis['retention_risks'][:3]
            })

        if optimization_focus in ['engagement', 'overall']:
            # Optimize engagement
            topic = current_content.get('topic', 'the topic')
            comment_prompts = self.engagement_designer.create_comment_prompts(
                topic,
                ['insight1', 'insight2']
            )
            optimizations['improvements'].append({
                'area': 'engagement',
                'change': 'Added strategic comment prompts',
                'prompts': comment_prompts[:2]
            })

        # Re-score after optimizations
        # In production, would apply all optimizations and re-score
        optimizations['current_score'] = current_score['overall_viral_score']
        optimizations['estimated_improvement'] = '+0.5 to +1.5 points'

        print(f"✓ Optimization complete: {len(optimizations['improvements'])} improvements identified\n")

        return optimizations

    def _generate_sample_script(self, topic: str, hook: Optional[Dict[str, Any]]) -> str:
        """Generate a sample script for scoring purposes"""
        hook_text = hook['hook_text'] if hook else f"Discover the truth about {topic}"

        script = f"""{hook_text}

Today, we're diving deep into {topic}, and what you're about to learn will change how you think about this forever.

You'll discover the secrets that experts have known for years, the science behind why this matters, and exactly how you can apply this knowledge in your own life.

By the end of this video, you'll understand {topic} better than 95% of people. Let's get started.

[Main content would continue here with research-backed insights, storytelling, and psychology triggers strategically placed throughout]
"""
        return script

    def _generate_comprehensive_recommendations(
        self,
        viral_score_result: Dict[str, Any],
        passed_quality_gate: bool
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations"""
        recommendations = []

        if not passed_quality_gate:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Quality Gate',
                'recommendation': 'Viral score below threshold. Focus on implementing recommendations from detailed analysis.',
                'action_items': viral_score_result.get('detailed_analysis', {}).get('recommendations', [])[:3]
            })

        # Get weaknesses from detailed analysis
        weaknesses = viral_score_result.get('detailed_analysis', {}).get('weaknesses', [])
        for weakness in weaknesses[:2]:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Improvement Area',
                'recommendation': f"Address identified weakness: {weakness}",
                'action_items': ['Review subagent recommendations', 'Implement optimizations', 'Re-test']
            })

        # Add best practice recommendations
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Best Practices',
            'recommendation': 'Follow Brendan Kane viral methodology',
            'action_items': [
                'Optimize first 3 seconds for maximum impact',
                'Deliver value promise within 15 seconds',
                'Add pattern interruptions every 2-3 minutes'
            ]
        })

        return recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """Get gatekeeper statistics"""
        return {
            'total_analyses': self.analysis_count,
            'total_processing_time': round(self.total_processing_time, 2),
            'avg_processing_time': round(self.total_processing_time / self.analysis_count, 2) if self.analysis_count > 0 else 0,
            'strategy_library_size': self.strategy_curator.analyze_library_stats()['total_strategies'],
            'quality_threshold': self.min_viral_score
        }

    def get_available_subagents(self) -> List[Dict[str, str]]:
        """Get list of available subagents and their capabilities"""
        return [
            {
                'name': 'Hook Specialist',
                'capability': 'Creates compelling opening hooks (0-15 seconds)',
                'output': 'Multiple hook variations with virality scores'
            },
            {
                'name': 'Trigger Implementer',
                'capability': 'Applies 16 psychology triggers strategically',
                'output': 'Trigger timeline with placement recommendations'
            },
            {
                'name': 'Pattern Recognizer',
                'capability': 'Identifies successful video structures',
                'output': 'Optimal pattern recommendation with implementation guide'
            },
            {
                'name': 'Retention Optimizer',
                'capability': 'Maximizes viewer retention',
                'output': 'Retention strategy with timed elements'
            },
            {
                'name': 'Engagement Designer',
                'capability': 'Designs moments for comments/shares',
                'output': 'Engagement strategy with CTA placements'
            },
            {
                'name': 'YouTube Data Analyst',
                'capability': 'Analyzes competitor videos',
                'output': 'Video performance analysis and tier classification'
            },
            {
                'name': 'Strategy Curator',
                'capability': 'Manages viral strategy library',
                'output': 'Similar successful strategies and recommendations'
            },
            {
                'name': 'Virality Scorer',
                'capability': 'Predicts viral potential (0-10 scale)',
                'output': 'Detailed score breakdown with recommendations'
            }
        ]
