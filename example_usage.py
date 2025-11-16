"""
Example Usage of Vector Database and Content Retriever Agent
Demonstrates the complete workflow for the Viral YouTube Synthesis System
"""

import os
from content_retriever_agent import ContentRetrieverAgent
from vector_database import ViralTier


def main():
    """Main example workflow"""

    print("=" * 70)
    print("VECTOR DATABASE & CONTENT RETRIEVER AGENT - EXAMPLE USAGE")
    print("=" * 70)
    print()

    # ========== INITIALIZATION ==========
    print("📌 STEP 1: Initialize Content Retriever Agent")
    print("-" * 70)

    # Initialize the agent (will create database if it doesn't exist)
    # Make sure OPENAI_API_KEY is set in environment or .env file
    agent = ContentRetrieverAgent(
        storage_path="./data/vector_db"
    )

    print("✅ Content Retriever Agent initialized")
    print()

    # ========== INDEXING: RESEARCH GATEKEEPER ==========
    print("📌 STEP 2: Index Research Data (from Research Gatekeeper)")
    print("-" * 70)

    research_id = agent.index_research(
        research_content="""
        Quantum computing represents a fundamental paradigm shift in computational
        capabilities, leveraging quantum mechanical phenomena such as superposition
        and entanglement to perform calculations exponentially faster than classical
        computers for certain problem classes.

        Recent breakthroughs in 2024-2025 have demonstrated quantum supremacy in
        practical applications, including cryptography, drug discovery, and
        optimization problems. Error correction methods have improved by an order
        of magnitude, making quantum computers more reliable and commercially viable.

        Key findings from multi-database research (JSTOR, Semantic Scholar, arXiv):
        1. Quantum supremacy achieved in multiple domains beyond theoretical proofs
        2. Error correction breakthrough reduces decoherence by 90%
        3. Commercial quantum computing services now available from major tech companies
        4. National security implications driving government investment
        5. Potential to break current encryption standards within 5-10 years
        """,
        topic="Quantum Computing Revolution",
        sources=["JSTOR", "Semantic Scholar", "arXiv", "PubMed", "CrossRef"],
        key_insights=[
            "Quantum supremacy achieved in practical applications",
            "90% improvement in error correction methods",
            "Commercial services now available",
            "Encryption security implications imminent"
        ],
        citations=[
            {
                "title": "Practical Quantum Supremacy in Cryptographic Applications",
                "author": "Zhang et al.",
                "journal": "Nature",
                "year": "2024"
            },
            {
                "title": "Error Correction Breakthroughs in Quantum Computing",
                "author": "Smith & Johnson",
                "journal": "Science",
                "year": "2025"
            }
        ],
        quality_score=9.5
    )

    print(f"✅ Research indexed with ID: {research_id}")
    print()

    # ========== INDEXING: VIRAL ANALYSER GATEKEEPER ==========
    print("📌 STEP 3: Index Viral Strategy (from Viral Analyser Gatekeeper)")
    print("-" * 70)

    strategy_id = agent.index_viral_strategy(
        strategy_content="""
        VIRAL STRATEGY FOR QUANTUM COMPUTING VIDEO

        Opening Hook (0-15s):
        "What if I told you that every password, every bank account, every secret
        message on the internet could be cracked in 60 seconds?"

        Hook Type: Curiosity Gap + Fear/Urgency
        Retention at 15s: Predicted 90%+

        Psychology Trigger Placement:
        1. Curiosity Gap (0-15s): Set up encryption threat
        2. Authority (45s-2m): Expert interviews, credentials
        3. Novelty (2m-4m): Show quantum computer visuals
        4. Fear/Urgency (4m-6m): Timeline for encryption breaking
        5. Transformation (6m-8m): How quantum will change everything
        6. Pattern Interruption (8m-10m): Visual shift to solutions
        7. Social Proof (10m-12m): Major companies investing
        8. Mystery (12m-14m): What's being kept secret
        9. Tribal Belonging (14m-15m): Be ahead of the curve

        Retention Strategy:
        - Visual changes every 90 seconds
        - B-roll integration at 2-minute intervals
        - Question posed to audience every 3 minutes
        - Music shifts at key moments

        Engagement Strategy:
        - "Comment below: Are you worried about quantum hacking?"
        - Controversial statement: "Your privacy is already gone"
        - Call to action: "Share this with someone who needs to know"
        """,
        topic="Quantum Computing Revolution",
        hooks=[
            "What if every password could be cracked in 60 seconds?",
            "The quantum revolution that terrifies governments",
            "Why tech giants are racing to build quantum computers",
            "The technology that will end online privacy forever",
            "Quantum computers: Humanity's greatest achievement or biggest threat?"
        ],
        psychology_triggers=[
            "Curiosity Gap",
            "Fear/Urgency",
            "Authority",
            "Novelty",
            "Transformation",
            "Pattern Interruption",
            "Social Proof",
            "Mystery",
            "Tribal Belonging"
        ],
        retention_strategy="Pattern interruption every 90 seconds with visual changes and B-roll",
        engagement_strategy="Questions, controversial statements, strong CTAs",
        viral_score=9.7,
        video_duration=15,
        target_audience="Tech enthusiasts, privacy advocates, 25-45, 65% male",
        viral_tier=ViralTier.GOLD
    )

    print(f"✅ Viral strategy indexed with ID: {strategy_id}")
    print()

    # ========== INDEXING: VIDEO ANALYSIS ==========
    print("📌 STEP 4: Index YouTube Video Analysis (from Viral Analyser)")
    print("-" * 70)

    video_id = agent.index_video_analysis(
        analysis_content="""
        ANALYSIS: "Quantum Computers Explained" by Tech Vision

        This video achieves exceptional performance through:

        1. Hook Effectiveness (92% retention at 15s):
           - Opens with dramatic statement about encryption
           - Visual of "hacking" animation immediately grabs attention
           - Question posed directly to viewer

        2. Structure Analysis:
           - Perfect pacing with visual changes every 60-90 seconds
           - Authority established through expert interviews at 2-minute mark
           - Pattern interruptions prevent drop-off

        3. Psychology Triggers Identified:
           - Primary: Curiosity Gap (maintained throughout)
           - Secondary: Fear/Urgency (encryption threat)
           - Tertiary: Authority (expert credentials shown)
           - Additional: Novelty, Transformation, Mystery

        4. Engagement Drivers:
           - Question at 3-minute mark drives comments
           - Controversial statement at 7 minutes sparks debate
           - Strong CTA at end increases shares

        5. Retention Analysis:
           - 15s: 92% (excellent hook)
           - 2min: 78% (above average)
           - 5min: 68% (strong mid-roll)
           - 10min: 58% (good for length)
           - Complete: 45% (excellent for 15min video)

        Overall: Gold tier performance with replicable patterns
        """,
        video_id="dQw4w9WgXcQ",
        video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        title="Quantum Computers Explained - The End of Encryption?",
        channel="Tech Vision",
        views=2_800_000,
        likes=185_000,
        comments=12_400,
        engagement_rate=14.2,  # (185k + 12.4k) / 2.8M * 100
        retention_rate=68.0,
        identified_triggers=[
            "Curiosity Gap",
            "Fear/Urgency",
            "Authority",
            "Novelty",
            "Transformation",
            "Mystery"
        ],
        hook_analysis={
            "type": "curiosity_gap",
            "effectiveness": "excellent",
            "retention_at_15s": 92.0,
            "hook_text": "What if I told you everything you know about computer security is about to change?"
        },
        structure={
            "hook": "0-15s",
            "intro": "15s-45s",
            "authority_building": "45s-2m",
            "main_explanation": "2m-8m",
            "implications": "8m-12m",
            "solutions": "12m-14m",
            "conclusion_cta": "14m-15m"
        }
    )

    print(f"✅ Video analysis indexed with ID: {video_id}")
    print()

    # ========== INDEXING: OUTPUT DATA ==========
    print("📌 STEP 5: Index Final Output (from Content Synthesis Gatekeeper)")
    print("-" * 70)

    output_id = agent.index_output(
        output_content="""
        QUANTUM COMPUTING DOCUMENTARY - FINAL SCRIPT

        [OPENING HOOK - 0:00-0:15]

        VISUAL: Black screen, sound of keyboard typing rapidly
        VISUAL: Suddenly, red "ACCESS DENIED" flashing on screen
        VISUAL: Cut to dramatic quantum computer imagery

        NARRATOR (urgent tone):
        "What if I told you that every password, every bank account,
        every secret message on the internet... could be cracked in
        just 60 seconds?"

        VISUAL: Timer counting down from 60
        VISUAL: Various security symbols breaking apart

        [INTRODUCTION - 0:15-0:45]

        VISUAL: Host on camera in modern tech studio

        HOST:
        "You're not prepared for what's coming. And neither is anyone
        else. I'm [Name], and today we're diving into the quantum
        revolution that's about to change everything about technology,
        security, and the future of humanity itself."

        VISUAL: B-roll of quantum computers, scientists working

        [... FULL SCRIPT CONTINUES ...]
        """,
        output_type="script",
        topic="Quantum Computing Revolution",
        quality_score=9.8,
        viral_score=9.5,
        production_ready=True,
        related_research_id=research_id,
        related_strategy_id=strategy_id
    )

    print(f"✅ Output indexed with ID: {output_id}")
    print()

    # ========== RETRIEVAL: RESEARCH ==========
    print("📌 STEP 6: Retrieve Relevant Research")
    print("-" * 70)

    research_results = agent.retrieve_research(
        query="quantum computing security encryption",
        top_k=3,
        min_quality=8.0
    )

    print(f"Found {len(research_results)} research entries:")
    for i, (entry, similarity) in enumerate(research_results, 1):
        print(f"\n  {i}. Similarity: {similarity:.3f}")
        print(f"     Topic: {entry.metadata['topic']}")
        print(f"     Quality: {entry.metadata.get('quality_score', 'N/A')}")
        print(f"     Sources: {', '.join(entry.metadata['sources'][:3])}")

    print()

    # ========== RETRIEVAL: VIRAL STRATEGIES ==========
    print("📌 STEP 7: Retrieve Viral Strategies")
    print("-" * 70)

    viral_results = agent.retrieve_viral_strategies(
        topic="Quantum Computing",
        viral_tier=ViralTier.GOLD,
        top_k=3
    )

    print(f"Found {len(viral_results)} viral strategies:")
    for i, (entry, similarity) in enumerate(viral_results, 1):
        print(f"\n  {i}. Viral Score: {entry.metadata['viral_score']}")
        print(f"     Similarity: {similarity:.3f}")
        print(f"     Hooks: {len(entry.metadata['hooks'])}")
        print(f"     Top Hook: {entry.metadata['hooks'][0][:60]}...")
        print(f"     Triggers: {', '.join(entry.metadata['psychology_triggers'][:4])}")

    print()

    # ========== RETRIEVAL: BEST HOOKS ==========
    print("📌 STEP 8: Retrieve Best Hooks")
    print("-" * 70)

    hooks = agent.retrieve_best_hooks(
        topic="Quantum Computing",
        viral_tier=ViralTier.GOLD,
        limit=5
    )

    print(f"Top {len(hooks)} Hooks:")
    for i, hook in enumerate(hooks, 1):
        print(f"  {i}. {hook}")

    print()

    # ========== RETRIEVAL: PSYCHOLOGY TRIGGERS ==========
    print("📌 STEP 9: Analyze Most Effective Psychology Triggers")
    print("-" * 70)

    triggers = agent.retrieve_psychology_triggers(
        topic="Quantum Computing",
        viral_tier=ViralTier.GOLD
    )

    print("Most Effective Triggers:")
    for trigger, count in list(triggers.items())[:10]:
        print(f"  • {trigger}: used in {count} successful video(s)")

    print()

    # ========== RECOMMENDATIONS ==========
    print("📌 STEP 10: Get Intelligent Recommendations")
    print("-" * 70)

    recommendations = agent.get_recommendations(
        topic="Quantum Computing",
        content_type="viral_strategy"
    )

    print("📊 RECOMMENDATIONS FOR QUANTUM COMPUTING")
    print()

    if recommendations.get('top_patterns'):
        print("🎯 Top Patterns:")
        for i, pattern in enumerate(recommendations['top_patterns'], 1):
            print(f"  {i}. {pattern.get('title', 'N/A')}")
            print(f"     Views: {pattern.get('views', 0):,}")
            print(f"     Engagement: {pattern.get('engagement_rate', 0):.1f}%")
        print()

    if recommendations.get('recommended_hooks'):
        print("💡 Recommended Hooks:")
        for i, hook in enumerate(recommendations['recommended_hooks'][:3], 1):
            print(f"  {i}. {hook}")
        print()

    if recommendations.get('recommended_triggers'):
        print("🧠 Recommended Psychology Triggers:")
        for i, trigger in enumerate(recommendations['recommended_triggers'][:5], 1):
            print(f"  {i}. {trigger}")
        print()

    # ========== DATABASE STATISTICS ==========
    print("📌 STEP 11: Database Statistics")
    print("-" * 70)

    stats = agent.get_database_stats()

    print(f"Total Entries: {stats['total_entries']}")
    print()
    print("By Content Type:")
    for content_type, count in stats['by_content_type'].items():
        print(f"  • {content_type}: {count}")
    print()
    print("By Viral Tier:")
    for tier, count in stats['by_viral_tier'].items():
        print(f"  • {tier}: {count}")
    print()
    if 'avg_viral_score' in stats:
        print(f"Average Viral Score: {stats['avg_viral_score']:.2f}")
    print()

    # ========== QUALITY VALIDATION ==========
    print("📌 STEP 12: Validate Database Quality")
    print("-" * 70)

    quality_report = agent.validate_database_quality()

    print(f"Health Status: {quality_report['health_status']}")
    print(f"Total Entries: {quality_report['total_entries']}")
    print()
    print("Tier Distribution:")
    for tier, count in quality_report['tier_distribution'].items():
        print(f"  • {tier.capitalize()}: {count}")
    print()

    if quality_report['quality_issues']:
        print("⚠️  Quality Issues:")
        for issue in quality_report['quality_issues']:
            print(f"  • {issue}")
    else:
        print("✅ No quality issues detected!")

    print()
    print("=" * 70)
    print("✅ EXAMPLE WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("=" * 70)
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment")
        print("=" * 70)
        print()
        print("To run this example, you need to set your OpenAI API key:")
        print()
        print("Option 1: Set environment variable")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print()
        print("Option 2: Create .env file")
        print("  cp .env.example .env")
        print("  # Edit .env and add your API key")
        print()
        print("Get your API key at: https://platform.openai.com/api-keys")
        print()
        print("=" * 70)
        exit(1)

    # Run the example
    main()
