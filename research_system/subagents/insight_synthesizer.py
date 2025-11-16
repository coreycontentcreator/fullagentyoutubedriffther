"""
Insight Synthesizer Subagent
Combines findings from multiple sources using Claude AI
"""

from typing import List, Dict, Any, Optional
import logging

from ..sources.base_source import ResearchPaper
from ..core.anthropic_integration import AnthropicIntegration

logger = logging.getLogger(__name__)


class InsightSynthesizer:
    """
    Insight Synthesizer Subagent
    Uses Claude AI to synthesize insights from multiple research sources
    """

    def __init__(self, anthropic_api: AnthropicIntegration):
        """
        Initialize insight synthesizer

        Args:
            anthropic_api: Anthropic API integration (REQUIRED)
        """
        if not anthropic_api:
            raise ValueError("Anthropic API integration is required for InsightSynthesizer")

        self.anthropic_api = anthropic_api
        logger.info("Insight Synthesizer initialized with Claude AI")

    def synthesize_research(
        self,
        papers: List[ResearchPaper],
        topic: str,
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """
        Synthesize research findings from multiple papers

        Args:
            papers: List of research papers
            topic: Research topic
            focus_areas: Specific areas to focus on

        Returns:
            Synthesized research summary (markdown format)
        """
        logger.info(f"Synthesizing insights from {len(papers)} papers on topic: {topic}")

        synthesis = self.anthropic_api.synthesize_research(
            papers=[p.to_dict() for p in papers],
            topic=topic,
            focus_areas=focus_areas
        )

        logger.info("Research synthesis complete")
        return synthesis

    def generate_insights(
        self,
        research_data: Dict[str, Any],
        research_question: str
    ) -> List[str]:
        """
        Generate novel insights from research data

        Args:
            research_data: Structured research data
            research_question: Research question to address

        Returns:
            List of novel insights
        """
        logger.info(f"Generating insights for question: {research_question}")

        insights = self.anthropic_api.generate_insights(
            research_data=research_data,
            research_question=research_question
        )

        logger.info(f"Generated {len(insights)} insights")
        return insights

    def identify_knowledge_gaps(
        self,
        research_synthesis: str,
        topic: str
    ) -> List[str]:
        """
        Identify knowledge gaps in research

        Args:
            research_synthesis: Synthesized research
            topic: Research topic

        Returns:
            List of identified knowledge gaps
        """
        logger.info(f"Identifying knowledge gaps for topic: {topic}")

        gaps = self.anthropic_api.identify_knowledge_gaps(
            research_synthesis=research_synthesis,
            topic=topic
        )

        logger.info(f"Identified {len(gaps)} knowledge gaps")
        return gaps

    def compare_sources(
        self,
        papers: List[ResearchPaper],
        aspect: str = "methodology"
    ) -> str:
        """
        Compare multiple sources on a specific aspect

        Args:
            papers: Papers to compare
            aspect: Aspect to compare (methodology, findings, conclusions)

        Returns:
            Comparison analysis
        """
        papers_summary = "\n\n".join([
            f"Paper {i+1}: {p.title}\nAuthors: {', '.join(p.authors[:3])}\n"
            f"Abstract: {p.abstract[:300]}..."
            for i, p in enumerate(papers[:5])
        ])

        prompt = f"""Compare these research papers on their {aspect}:

{papers_summary}

Provide a detailed comparison highlighting:
1. Similarities in {aspect}
2. Key differences
3. Strengths and limitations of each approach
4. Which approach seems most robust and why

Format in clear markdown."""

        response = self.anthropic_api.generate_completion(
            prompt=prompt,
            max_tokens=2048,
            temperature=0.7
        )

        return response.content

    def __repr__(self) -> str:
        """String representation"""
        return "InsightSynthesizer(Claude AI-powered)"
