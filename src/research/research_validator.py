"""
Research Validator - Source credibility and fact verification
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ResearchValidator:
    """
    Validates research quality and source credibility
    """

    def __init__(self, intelligence_layer):
        """
        Initialize research validator

        Args:
            intelligence_layer: AI intelligence layer
        """
        self.intelligence = intelligence_layer
        logger.info("Research Validator initialized")

    async def validate_research(
        self,
        papers: List[Dict[str, Any]],
        insights: List[str]
    ) -> float:
        """
        Validate research quality

        Args:
            papers: List of research papers
            insights: Extracted insights

        Returns:
            Quality score (0-10)
        """
        from ..intelligence.intelligence_layer import AIRequest, TaskComplexity

        papers_info = "\n".join([
            f"- {p.get('title', 'Unknown')} ({p.get('year', 'n.d.')})"
            for p in papers[:10]
        ])

        prompt = f"""Evaluate the quality of this research:

        Papers ({len(papers)} total):
        {papers_info}

        Insights extracted: {len(insights)}

        Assess:
        1. Source credibility
        2. Research diversity
        3. Insight quality
        4. Academic rigor

        Return quality score (0-10) as JSON: {{"score": X.X, "reasoning": "..."}}"""

        request = AIRequest(
            prompt=prompt,
            task_type="research_validation",
            complexity=TaskComplexity.MODERATE,
            temperature=0.2
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            result = json.loads(response.content)
            return float(result.get('score', 8.0))
        except:
            # Heuristic scoring
            diversity_score = min(len(set(p.get('database', 'unknown') for p in papers)) / 3.0, 1.0)
            volume_score = min(len(papers) / 50.0, 1.0)
            insight_score = min(len(insights) / 10.0, 1.0)

            return round((diversity_score + volume_score + insight_score) / 3.0 * 10, 1)
