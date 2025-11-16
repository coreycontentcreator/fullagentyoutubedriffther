"""
Fact Checker Subagent
Validates claims against multiple sources
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from ..sources.base_source import ResearchPaper
from ..core.anthropic_integration import AnthropicIntegration

logger = logging.getLogger(__name__)


@dataclass
class FactCheckResult:
    """Result of fact-checking a claim"""
    claim: str
    verdict: str  # SUPPORTED, PARTIALLY_SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE
    confidence: float  # 0-10
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    reasoning: str
    sources_checked: int
    caveats: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'claim': self.claim,
            'verdict': self.verdict,
            'confidence': self.confidence,
            'supporting_evidence': self.supporting_evidence,
            'contradicting_evidence': self.contradicting_evidence,
            'reasoning': self.reasoning,
            'sources_checked': self.sources_checked,
            'caveats': self.caveats
        }


class FactChecker:
    """
    Fact Checker Subagent
    Validates claims against multiple research sources
    """

    def __init__(self, anthropic_api: Optional[AnthropicIntegration] = None):
        """
        Initialize fact checker

        Args:
            anthropic_api: Anthropic API integration for AI-powered fact-checking
        """
        self.anthropic_api = anthropic_api
        logger.info("Fact Checker initialized")

    def check_claim(
        self,
        claim: str,
        evidence_papers: List[ResearchPaper],
        context: Optional[str] = None
    ) -> FactCheckResult:
        """
        Check a claim against evidence

        Args:
            claim: Claim to fact-check
            evidence_papers: Papers to check against
            context: Additional context

        Returns:
            FactCheckResult
        """
        logger.info(f"Fact-checking claim: {claim[:100]}...")

        # Prepare evidence
        evidence = [
            {
                'source': p.source,
                'title': p.title,
                'content': p.abstract,
                'year': p.year,
                'citations': p.citation_count
            }
            for p in evidence_papers
        ]

        # Use AI if available
        if self.anthropic_api:
            result = self.anthropic_api.fact_check_claim(
                claim=claim,
                evidence=evidence,
                context=context
            )

            return FactCheckResult(
                claim=claim,
                verdict=result.get('verdict', 'INSUFFICIENT_EVIDENCE'),
                confidence=result.get('confidence', 5.0),
                supporting_evidence=result.get('supporting_evidence', []),
                contradicting_evidence=result.get('contradicting_evidence', []),
                reasoning=result.get('reasoning', ''),
                sources_checked=len(evidence_papers),
                caveats=result.get('caveats', [])
            )
        else:
            # Heuristic fact-checking
            return self._heuristic_check(claim, evidence_papers)

    def check_multiple_claims(
        self,
        claims: List[str],
        evidence_papers: List[ResearchPaper]
    ) -> List[FactCheckResult]:
        """
        Check multiple claims

        Args:
            claims: List of claims
            evidence_papers: Papers to check against

        Returns:
            List of FactCheckResults
        """
        results = []
        for claim in claims:
            result = self.check_claim(claim, evidence_papers)
            results.append(result)

        logger.info(f"Fact-checked {len(claims)} claims")
        return results

    def _heuristic_check(
        self,
        claim: str,
        papers: List[ResearchPaper]
    ) -> FactCheckResult:
        """
        Heuristic-based fact checking without AI

        Args:
            claim: Claim to check
            papers: Evidence papers

        Returns:
            FactCheckResult
        """
        # Simple keyword matching
        claim_lower = claim.lower()
        supporting = []
        contradicting = []

        for paper in papers:
            abstract_lower = paper.abstract.lower()

            # Very basic matching (in production, use better NLP)
            if any(word in abstract_lower for word in claim_lower.split()):
                supporting.append(f"{paper.title} ({paper.year})")

        if len(supporting) >= 3:
            verdict = "SUPPORTED"
            confidence = 7.0
        elif len(supporting) >= 1:
            verdict = "PARTIALLY_SUPPORTED"
            confidence = 5.0
        else:
            verdict = "INSUFFICIENT_EVIDENCE"
            confidence = 3.0

        return FactCheckResult(
            claim=claim,
            verdict=verdict,
            confidence=confidence,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            reasoning="Heuristic analysis based on keyword matching",
            sources_checked=len(papers),
            caveats=["Limited to keyword matching without AI"]
        )

    def identify_contradictions(
        self,
        papers: List[ResearchPaper]
    ) -> List[Dict[str, Any]]:
        """
        Identify contradictions between papers

        Args:
            papers: Papers to analyze

        Returns:
            List of identified contradictions
        """
        contradictions = []

        if self.anthropic_api and len(papers) >= 2:
            # Use AI to identify contradictions
            papers_summary = "\n\n".join([
                f"Paper {i+1}: {p.title}\nFindings: {p.abstract[:300]}"
                for i, p in enumerate(papers[:10])
            ])

            prompt = f"""Analyze these research papers and identify any contradictions or conflicting findings:

{papers_summary}

Return a JSON array of contradictions with format:
[
  {{
    "papers_involved": ["paper 1", "paper 2"],
    "contradiction": "description of contradiction",
    "severity": "major|minor"
  }}
]

Return ONLY valid JSON array."""

            try:
                response = self.anthropic_api.generate_completion(
                    prompt=prompt,
                    max_tokens=2048,
                    temperature=0.3
                )

                import json
                contradictions = json.loads(response.content)
            except:
                logger.warning("Failed to parse contradictions from AI response")

        return contradictions

    def __repr__(self) -> str:
        """String representation"""
        mode = "AI-powered" if self.anthropic_api else "Heuristic"
        return f"FactChecker({mode})"
