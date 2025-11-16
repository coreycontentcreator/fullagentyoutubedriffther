"""
Content Retriever Agent - Specialized gatekeeper for vector database operations
Handles all indexing and retrieval for other gatekeeper agents in the system
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from vector_database import VectorDatabase, ContentType, ViralTier, VectorEntry


class ContentRetrieverAgent:
    """
    Content Retriever Agent - Gatekeeps access to the vector database.

    Responsibilities:
    1. Index new content from all gatekeepers (Research, Viral, Content Synthesis)
    2. Retrieve relevant content for gatekeeper agents
    3. Manage database quality and curation
    4. Provide intelligent recommendations based on patterns
    5. Learn from successful content and update strategies

    Acts as the single point of access to the vector database, ensuring
    consistency and quality control for all stored and retrieved information.
    """

    def __init__(self,
                 vector_db: Optional[VectorDatabase] = None,
                 storage_path: str = "./data/vector_db",
                 openai_api_key: Optional[str] = None):
        """
        Initialize the Content Retriever Agent.

        Args:
            vector_db: Existing VectorDatabase instance (or creates new one)
            storage_path: Path for database storage
            openai_api_key: OpenAI API key for embeddings
        """
        self.vector_db = vector_db or VectorDatabase(
            storage_path=storage_path,
            openai_api_key=openai_api_key
        )

        self.retrieval_history: List[Dict[str, Any]] = []

        print("✅ Content Retriever Agent initialized")

    # ==================== INDEXING OPERATIONS ====================

    def index_research(self,
                      research_content: str,
                      topic: str,
                      sources: List[str],
                      key_insights: List[str],
                      citations: List[Dict[str, str]],
                      quality_score: float) -> str:
        """
        Index research data from Research Gatekeeper.

        Args:
            research_content: Complete research text
            topic: Research topic
            sources: Data sources used (JSTOR, Semantic Scholar, etc.)
            key_insights: Key findings
            citations: Citation information
            quality_score: Research quality score (0-10)

        Returns:
            Entry ID in database
        """
        print(f"📥 Indexing research on topic: {topic}")

        # Validate quality (Research Gatekeeper requires ≥8.0)
        if quality_score < 8.0:
            print(f"⚠️  Warning: Research quality score {quality_score} is below standard (8.0)")

        entry_id = self.vector_db.add_research_data(
            research_content=research_content,
            topic=topic,
            sources=sources,
            key_insights=key_insights,
            citations=citations
        )

        # Update metadata with quality score
        self.vector_db.update_entry_metadata(entry_id, {'quality_score': quality_score})

        print(f"✅ Research indexed: {entry_id}")
        return entry_id

    def index_viral_strategy(self,
                            strategy_content: str,
                            topic: str,
                            hooks: List[str],
                            psychology_triggers: List[str],
                            retention_strategy: str,
                            engagement_strategy: str,
                            viral_score: float,
                            video_duration: Optional[int] = None,
                            target_audience: Optional[str] = None,
                            viral_tier: Optional[ViralTier] = None) -> str:
        """
        Index viral strategy from Viral Analyser Gatekeeper.

        Args:
            strategy_content: Strategy description
            topic: Content topic
            hooks: List of hook variations
            psychology_triggers: Psychology triggers used
            retention_strategy: Retention optimization approach
            engagement_strategy: Engagement optimization approach
            viral_score: Predicted viral score (0-10)
            video_duration: Target video length in minutes
            target_audience: Target audience description
            viral_tier: Performance tier (if from analyzed video)

        Returns:
            Entry ID in database
        """
        print(f"📥 Indexing viral strategy for: {topic}")

        # Validate viral score (Viral Gatekeeper requires ≥9.0)
        if viral_score < 9.0:
            print(f"⚠️  Warning: Viral score {viral_score} is below standard (9.0)")

        entry_id = self.vector_db.add_viral_strategy(
            strategy_content=strategy_content,
            topic=topic,
            hooks=hooks,
            psychology_triggers=psychology_triggers,
            retention_strategy=retention_strategy,
            viral_score=viral_score,
            viral_tier=viral_tier
        )

        # Add additional metadata
        additional_metadata = {
            'engagement_strategy': engagement_strategy,
            'video_duration': video_duration,
            'target_audience': target_audience
        }
        self.vector_db.update_entry_metadata(entry_id, additional_metadata)

        print(f"✅ Viral strategy indexed: {entry_id}")
        return entry_id

    def index_video_analysis(self,
                            analysis_content: str,
                            video_id: str,
                            video_url: str,
                            title: str,
                            channel: str,
                            views: int,
                            likes: int,
                            comments: int,
                            engagement_rate: float,
                            retention_rate: float,
                            identified_triggers: List[str],
                            hook_analysis: Dict[str, Any],
                            structure: Dict[str, Any]) -> str:
        """
        Index YouTube video analysis from Viral Analyser Gatekeeper.

        Automatically classifies video into viral tier based on metrics:
        - Gold: 1M+ views, 10%+ engagement, 60%+ retention
        - Silver: 500K+ views, 7%+ engagement, 50%+ retention
        - Bronze: 100K+ views, 5%+ engagement, 40%+ retention

        Args:
            analysis_content: Complete analysis text
            video_id: YouTube video ID
            video_url: Full video URL
            title: Video title
            channel: Channel name
            views: View count
            likes: Like count
            comments: Comment count
            engagement_rate: Engagement rate (%)
            retention_rate: Estimated retention rate (%)
            identified_triggers: Psychology triggers found
            hook_analysis: Hook effectiveness analysis
            structure: Video structure breakdown

        Returns:
            Entry ID in database
        """
        print(f"📥 Indexing video analysis: {title}")

        # Classify into viral tier
        viral_tier = self._classify_viral_tier(views, engagement_rate, retention_rate)

        metrics = {
            'title': title,
            'channel': channel,
            'views': views,
            'likes': likes,
            'comments': comments,
            'engagement_rate': engagement_rate,
            'retention_rate': retention_rate,
            'hook_analysis': hook_analysis
        }

        entry_id = self.vector_db.add_video_analysis(
            analysis_content=analysis_content,
            video_id=video_id,
            video_url=video_url,
            metrics=metrics,
            identified_triggers=identified_triggers,
            structure=structure,
            viral_tier=viral_tier
        )

        print(f"✅ Video analysis indexed: {entry_id} (Tier: {viral_tier.value})")
        return entry_id

    def index_output(self,
                    output_content: str,
                    output_type: str,
                    topic: str,
                    quality_score: float,
                    viral_score: float,
                    production_ready: bool = True,
                    related_research_id: Optional[str] = None,
                    related_strategy_id: Optional[str] = None) -> str:
        """
        Index final output from Content Synthesis Gatekeeper.

        Args:
            output_content: Final output (script, scenes, etc.)
            output_type: Type of output (script, visual_scenes, production_notes)
            topic: Content topic
            quality_score: Quality score (0-10)
            viral_score: Predicted viral score (0-10)
            production_ready: Whether content is production ready
            related_research_id: ID of related research entry
            related_strategy_id: ID of related viral strategy entry

        Returns:
            Entry ID in database
        """
        print(f"📥 Indexing output: {output_type} for {topic}")

        # Validate quality (Content Synthesis requires ≥9.0)
        if quality_score < 9.0:
            print(f"⚠️  Warning: Output quality score {quality_score} is below standard (9.0)")

        entry_id = self.vector_db.add_output_data(
            output_content=output_content,
            output_type=output_type,
            topic=topic,
            quality_score=quality_score,
            production_ready=production_ready
        )

        # Add relationships and viral score
        additional_metadata = {
            'viral_score': viral_score,
            'related_research_id': related_research_id,
            'related_strategy_id': related_strategy_id
        }
        self.vector_db.update_entry_metadata(entry_id, additional_metadata)

        print(f"✅ Output indexed: {entry_id}")
        return entry_id

    # ==================== RETRIEVAL OPERATIONS ====================

    def retrieve_research(self,
                         query: str,
                         top_k: int = 5,
                         min_quality: float = 8.0) -> List[Tuple[VectorEntry, float]]:
        """
        Retrieve relevant research for a query.

        Args:
            query: Search query
            top_k: Number of results to return
            min_quality: Minimum quality score filter

        Returns:
            List of (entry, similarity_score) tuples
        """
        print(f"🔍 Retrieving research for: {query}")

        results = self.vector_db.search(
            query=query,
            content_type=ContentType.RESEARCH,
            top_k=top_k
        )

        # Filter by quality
        filtered_results = [
            (entry, score) for entry, score in results
            if entry.metadata.get('quality_score', 0) >= min_quality
        ]

        self._log_retrieval('research', query, len(filtered_results))
        return filtered_results

    def retrieve_viral_strategies(self,
                                 topic: str,
                                 viral_tier: Optional[ViralTier] = None,
                                 top_k: int = 5) -> List[Tuple[VectorEntry, float]]:
        """
        Retrieve viral strategies for a topic.

        Args:
            topic: Content topic
            viral_tier: Filter by specific tier (Gold/Silver/Bronze)
            top_k: Number of results

        Returns:
            List of (entry, similarity_score) tuples, sorted by viral score
        """
        print(f"🔍 Retrieving viral strategies for: {topic}")

        results = self.vector_db.search(
            query=topic,
            content_type=ContentType.VIRAL_STRATEGY,
            viral_tier=viral_tier,
            top_k=top_k * 2  # Get more, then sort by viral score
        )

        # Sort by viral score (secondary sort after similarity)
        results.sort(key=lambda x: (x[1], x[0].metadata.get('viral_score', 0)), reverse=True)
        results = results[:top_k]

        self._log_retrieval('viral_strategy', topic, len(results))
        return results

    def retrieve_successful_patterns(self,
                                    topic: str,
                                    min_tier: ViralTier = ViralTier.BRONZE,
                                    top_k: int = 10) -> List[VectorEntry]:
        """
        Retrieve successful video patterns for a topic.

        Args:
            topic: Content topic
            min_tier: Minimum viral tier to include
            top_k: Number of patterns to return

        Returns:
            List of video analysis entries
        """
        print(f"🔍 Retrieving successful patterns for: {topic}")

        # Get video analyses
        results = self.vector_db.search(
            query=topic,
            content_type=ContentType.VIDEO_ANALYSIS,
            top_k=top_k * 2
        )

        # Filter by tier and sort by views
        tier_order = {ViralTier.GOLD: 3, ViralTier.SILVER: 2, ViralTier.BRONZE: 1}
        min_tier_value = tier_order.get(min_tier, 0)

        filtered = [
            entry for entry, _ in results
            if tier_order.get(entry.viral_tier, 0) >= min_tier_value
        ]

        # Sort by views (descending)
        filtered.sort(key=lambda x: x.metadata.get('views', 0), reverse=True)

        self._log_retrieval('patterns', topic, len(filtered[:top_k]))
        return filtered[:top_k]

    def retrieve_best_hooks(self,
                           topic: str,
                           viral_tier: ViralTier = ViralTier.GOLD,
                           limit: int = 10) -> List[str]:
        """
        Retrieve best performing hooks for a topic.

        Args:
            topic: Content topic
            viral_tier: Tier to retrieve from
            limit: Maximum number of hooks

        Returns:
            List of hook texts
        """
        print(f"🔍 Retrieving best hooks for: {topic}")

        # Get viral strategies from specified tier
        strategies = self.vector_db.search(
            query=topic,
            content_type=ContentType.VIRAL_STRATEGY,
            viral_tier=viral_tier,
            top_k=20
        )

        # Extract hooks
        all_hooks = []
        for entry, similarity in strategies:
            hooks = entry.metadata.get('hooks', [])
            # Tag each hook with its viral score and similarity
            for hook in hooks:
                all_hooks.append({
                    'hook': hook,
                    'viral_score': entry.metadata.get('viral_score', 0),
                    'similarity': similarity
                })

        # Sort by viral score and similarity
        all_hooks.sort(key=lambda x: (x['viral_score'], x['similarity']), reverse=True)

        # Return just the hook texts
        result_hooks = [h['hook'] for h in all_hooks[:limit]]

        print(f"✅ Retrieved {len(result_hooks)} hooks")
        return result_hooks

    def retrieve_psychology_triggers(self,
                                    topic: str,
                                    viral_tier: ViralTier = ViralTier.GOLD) -> Dict[str, int]:
        """
        Retrieve most effective psychology triggers for a topic based on successful videos.

        Args:
            topic: Content topic
            viral_tier: Minimum tier to analyze

        Returns:
            Dictionary of trigger: frequency
        """
        print(f"🔍 Analyzing psychology triggers for: {topic}")

        # Get successful video analyses
        analyses = self.retrieve_successful_patterns(topic, min_tier=viral_tier, top_k=50)

        # Count trigger usage
        trigger_counts = {}
        for entry in analyses:
            triggers = entry.metadata.get('identified_triggers', [])
            for trigger in triggers:
                trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

        # Sort by frequency
        sorted_triggers = dict(sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True))

        print(f"✅ Found {len(sorted_triggers)} unique triggers")
        return sorted_triggers

    def get_recommendations(self,
                           topic: str,
                           content_type: str = "viral_strategy") -> Dict[str, Any]:
        """
        Get intelligent recommendations for creating content on a topic.

        Args:
            topic: Content topic
            content_type: Type of recommendations (viral_strategy, research, etc.)

        Returns:
            Dictionary with recommendations
        """
        print(f"💡 Generating recommendations for: {topic}")

        recommendations = {
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        }

        if content_type == "viral_strategy":
            # Get best patterns
            gold_patterns = self.retrieve_successful_patterns(topic, min_tier=ViralTier.GOLD, top_k=5)

            # Get best hooks
            hooks = self.retrieve_best_hooks(topic, viral_tier=ViralTier.GOLD, limit=10)

            # Get effective triggers
            triggers = self.retrieve_psychology_triggers(topic, viral_tier=ViralTier.GOLD)

            recommendations.update({
                'top_patterns': [
                    {
                        'video_id': p.metadata.get('video_id'),
                        'title': p.metadata.get('metrics', {}).get('title'),
                        'views': p.metadata.get('views'),
                        'engagement_rate': p.metadata.get('engagement_rate'),
                        'structure': p.metadata.get('structure')
                    }
                    for p in gold_patterns[:3]
                ],
                'recommended_hooks': hooks[:5],
                'recommended_triggers': list(triggers.keys())[:10],
                'trigger_effectiveness': triggers
            })

        elif content_type == "research":
            # Get related research
            research = self.retrieve_research(topic, top_k=5, min_quality=8.0)

            recommendations.update({
                'related_research': [
                    {
                        'topic': r.metadata.get('topic'),
                        'sources': r.metadata.get('sources'),
                        'key_insights': r.metadata.get('key_insights'),
                        'quality_score': r.metadata.get('quality_score')
                    }
                    for r, _ in research
                ]
            })

        print(f"✅ Generated recommendations")
        return recommendations

    # ==================== UTILITY OPERATIONS ====================

    def _classify_viral_tier(self,
                            views: int,
                            engagement_rate: float,
                            retention_rate: float) -> ViralTier:
        """
        Classify video into viral tier based on metrics.

        Gold: 1M+ views, 10%+ engagement, 60%+ retention
        Silver: 500K+ views, 7%+ engagement, 50%+ retention
        Bronze: 100K+ views, 5%+ engagement, 40%+ retention
        """
        if views >= 1_000_000 and engagement_rate >= 10.0 and retention_rate >= 60.0:
            return ViralTier.GOLD
        elif views >= 500_000 and engagement_rate >= 7.0 and retention_rate >= 50.0:
            return ViralTier.SILVER
        elif views >= 100_000 and engagement_rate >= 5.0 and retention_rate >= 40.0:
            return ViralTier.BRONZE
        else:
            return ViralTier.PENDING

    def _log_retrieval(self, operation: str, query: str, result_count: int):
        """Log retrieval operation for analytics"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'query': query,
            'result_count': result_count
        }
        self.retrieval_history.append(log_entry)

    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = self.vector_db.get_statistics()

        # Add retrieval stats
        stats['retrieval_history_count'] = len(self.retrieval_history)

        # Recent retrievals
        if self.retrieval_history:
            stats['recent_retrievals'] = self.retrieval_history[-10:]

        return stats

    def validate_database_quality(self) -> Dict[str, Any]:
        """
        Validate overall database quality.

        Returns:
            Quality report
        """
        print("🔍 Validating database quality...")

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_entries': len(self.vector_db.entries),
            'quality_issues': []
        }

        # Check research quality
        research_entries = self.vector_db.get_by_content_type(ContentType.RESEARCH)
        low_quality_research = [
            e for e in research_entries
            if e.metadata.get('quality_score', 10) < 8.0
        ]
        if low_quality_research:
            report['quality_issues'].append(
                f"{len(low_quality_research)} research entries below quality threshold (8.0)"
            )

        # Check viral strategies
        viral_entries = self.vector_db.get_by_content_type(ContentType.VIRAL_STRATEGY)
        low_viral_score = [
            e for e in viral_entries
            if e.metadata.get('viral_score', 10) < 9.0
        ]
        if low_viral_score:
            report['quality_issues'].append(
                f"{len(low_viral_score)} viral strategies below score threshold (9.0)"
            )

        # Check for tier distribution
        tier_counts = {
            'gold': len(self.vector_db.get_by_tier(ViralTier.GOLD)),
            'silver': len(self.vector_db.get_by_tier(ViralTier.SILVER)),
            'bronze': len(self.vector_db.get_by_tier(ViralTier.BRONZE))
        }
        report['tier_distribution'] = tier_counts

        # Overall health
        report['health_status'] = 'GOOD' if len(report['quality_issues']) == 0 else 'NEEDS_ATTENTION'

        print(f"✅ Validation complete: {report['health_status']}")
        return report


if __name__ == "__main__":
    # Example usage
    print("Content Retriever Agent - Example Usage")
    print("=" * 50)

    # Initialize agent
    agent = ContentRetrieverAgent()

    # Example: Index research from Research Gatekeeper
    research_id = agent.index_research(
        research_content="Quantum computing breakthrough research findings...",
        topic="Quantum Computing",
        sources=["JSTOR", "Semantic Scholar", "arXiv"],
        key_insights=["Quantum supremacy achieved", "Error correction improved"],
        citations=[{"title": "Quantum Advances 2025", "author": "Smith et al."}],
        quality_score=9.5
    )

    # Example: Index viral strategy from Viral Analyser Gatekeeper
    strategy_id = agent.index_viral_strategy(
        strategy_content="Complete viral strategy for quantum computing video...",
        topic="Quantum Computing",
        hooks=["What if computers could break all encryption?", "The quantum revolution is here"],
        psychology_triggers=["Curiosity Gap", "Fear", "Authority", "Novelty"],
        retention_strategy="Pattern interruption every 90 seconds",
        engagement_strategy="Questions in comments, controversial statements",
        viral_score=9.7,
        video_duration=15,
        target_audience="Tech enthusiasts 25-40",
        viral_tier=ViralTier.GOLD
    )

    # Example: Index video analysis
    video_id = agent.index_video_analysis(
        analysis_content="Analysis of viral quantum computing video...",
        video_id="abc123xyz",
        video_url="https://youtube.com/watch?v=abc123xyz",
        title="Quantum Computers Will Change Everything",
        channel="Tech Explained",
        views=2_500_000,
        likes=150_000,
        comments=8_500,
        engagement_rate=12.5,
        retention_rate=65.0,
        identified_triggers=["Curiosity Gap", "Authority", "Transformation"],
        hook_analysis={"effectiveness": "high", "retention_at_15s": 92.0},
        structure={"intro": "0-15s", "main": "15s-12m", "conclusion": "12m-15m"}
    )

    # Example: Retrieve recommendations
    recommendations = agent.get_recommendations(
        topic="Quantum Computing",
        content_type="viral_strategy"
    )

    print("\n📊 Recommendations:")
    print(f"  - Best hooks: {len(recommendations.get('recommended_hooks', []))}")
    print(f"  - Top patterns: {len(recommendations.get('top_patterns', []))}")
    print(f"  - Recommended triggers: {recommendations.get('recommended_triggers', [])[:5]}")

    # Show database stats
    stats = agent.get_database_stats()
    print(f"\n📈 Database Statistics:")
    print(f"  - Total entries: {stats['total_entries']}")
    print(f"  - By tier: {stats['by_viral_tier']}")

    # Validate quality
    quality_report = agent.validate_database_quality()
    print(f"\n✅ Database Health: {quality_report['health_status']}")
