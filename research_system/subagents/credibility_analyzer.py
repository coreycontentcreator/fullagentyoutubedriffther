"""
Credibility Analyzer Subagent
Assesses source quality, bias, and credibility of research papers
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from ..sources.base_source import ResearchPaper
from ..core.anthropic_integration import AnthropicIntegration

logger = logging.getLogger(__name__)


@dataclass
class CredibilityScore:
    """Container for credibility analysis results"""
    overall_score: float  # 0-10
    author_reputation: float
    publication_quality: float
    methodology_rigor: float
    peer_review_status: float
    citation_impact: float
    bias_indicators: List[str]
    strengths: List[str]
    weaknesses: List[str]
    assessment: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'overall_score': self.overall_score,
            'author_reputation': self.author_reputation,
            'publication_quality': self.publication_quality,
            'methodology_rigor': self.methodology_rigor,
            'peer_review_status': self.peer_review_status,
            'citation_impact': self.citation_impact,
            'bias_indicators': self.bias_indicators,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'assessment': self.assessment
        }


class CredibilityAnalyzer:
    """
    Credibility Analyzer Subagent
    Evaluates the credibility and quality of research sources
    """

    def __init__(self, anthropic_api: Optional[AnthropicIntegration] = None):
        """
        Initialize credibility analyzer

        Args:
            anthropic_api: Anthropic API integration for AI-powered analysis
        """
        self.anthropic_api = anthropic_api
        self.credibility_cache: Dict[str, CredibilityScore] = {}

        logger.info("Credibility Analyzer initialized")

    def analyze_paper(self, paper: ResearchPaper, use_ai: bool = True) -> CredibilityScore:
        """
        Analyze credibility of a research paper

        Args:
            paper: Research paper to analyze
            use_ai: Whether to use AI for analysis

        Returns:
            CredibilityScore with detailed assessment
        """
        # Check cache
        paper_id = self._get_paper_id(paper)
        if paper_id in self.credibility_cache:
            return self.credibility_cache[paper_id]

        # Perform heuristic analysis
        heuristic_score = self._heuristic_analysis(paper)

        # Enhance with AI if available and requested
        if use_ai and self.anthropic_api:
            try:
                ai_analysis = self.anthropic_api.analyze_credibility(
                    paper=paper.to_dict()
                )
                # Merge heuristic and AI analysis
                score = self._merge_analyses(heuristic_score, ai_analysis)
            except Exception as e:
                logger.warning(f"AI analysis failed, using heuristic only: {e}")
                score = heuristic_score
        else:
            score = heuristic_score

        # Cache result
        self.credibility_cache[paper_id] = score

        logger.debug(f"Analyzed credibility for: {paper.title[:50]}... (score: {score.overall_score:.1f})")

        return score

    def analyze_papers_batch(self, papers: List[ResearchPaper]) -> Dict[str, CredibilityScore]:
        """
        Analyze multiple papers

        Args:
            papers: List of papers to analyze

        Returns:
            Dictionary mapping paper IDs to credibility scores
        """
        results = {}
        for paper in papers:
            paper_id = self._get_paper_id(paper)
            results[paper_id] = self.analyze_paper(paper)

        logger.info(f"Analyzed credibility for {len(papers)} papers")
        return results

    def _heuristic_analysis(self, paper: ResearchPaper) -> CredibilityScore:
        """
        Perform heuristic-based credibility analysis

        Args:
            paper: Research paper

        Returns:
            CredibilityScore
        """
        # Citation impact score (0-10)
        citation_impact = min(10.0, (paper.citation_count / 100) * 10)

        # Peer review status (0-10)
        peer_review_status = 10.0 if paper.peer_reviewed else 5.0

        # Publication quality (based on source)
        pub_quality = self._assess_publication_quality(paper)

        # Author reputation (based on available data)
        author_reputation = 7.0  # Default neutral score

        # Methodology rigor (heuristic based on abstract length and keywords)
        methodology_rigor = self._assess_methodology(paper)

        # Identify potential bias indicators
        bias_indicators = self._detect_bias_indicators(paper)

        # Calculate overall score
        overall_score = (
            citation_impact * 0.25 +
            peer_review_status * 0.25 +
            pub_quality * 0.20 +
            author_reputation * 0.15 +
            methodology_rigor * 0.15
        )

        # Identify strengths and weaknesses
        strengths = self._identify_strengths(paper)
        weaknesses = self._identify_weaknesses(paper)

        # Generate assessment
        assessment = self._generate_assessment(overall_score, paper)

        return CredibilityScore(
            overall_score=overall_score,
            author_reputation=author_reputation,
            publication_quality=pub_quality,
            methodology_rigor=methodology_rigor,
            peer_review_status=peer_review_status,
            citation_impact=citation_impact,
            bias_indicators=bias_indicators,
            strengths=strengths,
            weaknesses=weaknesses,
            assessment=assessment
        )

    def _assess_publication_quality(self, paper: ResearchPaper) -> float:
        """Assess publication venue quality"""
        # High-quality sources
        if paper.source in ["JSTOR", "PubMed"]:
            return 9.5
        elif paper.source in ["Semantic Scholar", "CrossRef"]:
            return 8.5
        elif paper.source in ["OpenAlex"]:
            return 8.0
        elif paper.source in ["arXiv"]:
            return 7.0  # Preprints, not peer-reviewed
        else:
            return 7.0

    def _assess_methodology(self, paper: ResearchPaper) -> float:
        """Assess methodology rigor based on available information"""
        score = 7.0  # Baseline

        # Abstract length (longer often means more detailed)
        if paper.abstract:
            abstract_len = len(paper.abstract)
            if abstract_len > 1000:
                score += 1.5
            elif abstract_len > 500:
                score += 1.0
            elif abstract_len < 200:
                score -= 1.0

        # Keywords indicate methodological rigor
        rigorous_keywords = ['methodology', 'experimental', 'systematic', 'meta-analysis',
                            'randomized', 'controlled', 'empirical', 'quantitative']
        keyword_matches = sum(1 for kw in paper.keywords
                            if any(rigorous in kw.lower() for rigorous in rigorous_keywords))
        score += min(2.0, keyword_matches * 0.5)

        return min(10.0, max(0.0, score))

    def _detect_bias_indicators(self, paper: ResearchPaper) -> List[str]:
        """Detect potential bias indicators"""
        indicators = []

        # Check for potential conflicts (heuristic)
        if paper.metadata.get('funding_source'):
            indicators.append("Industry funding detected")

        # Very recent papers may not be well-validated
        if paper.year and paper.year >= 2024:
            if paper.citation_count < 5:
                indicators.append("Recent publication with limited citations")

        # Preprints
        if not paper.peer_reviewed:
            indicators.append("Not peer-reviewed")

        # Limited author information
        if not paper.authors or len(paper.authors) == 0:
            indicators.append("No author information available")

        return indicators

    def _identify_strengths(self, paper: ResearchPaper) -> List[str]:
        """Identify paper strengths"""
        strengths = []

        if paper.peer_reviewed:
            strengths.append("Peer-reviewed publication")

        if paper.citation_count > 100:
            strengths.append(f"Highly cited ({paper.citation_count} citations)")
        elif paper.citation_count > 50:
            strengths.append(f"Well-cited ({paper.citation_count} citations)")

        if paper.open_access:
            strengths.append("Open access - freely available")

        if paper.source in ["JSTOR", "PubMed"]:
            strengths.append(f"Published in reputable source ({paper.source})")

        if len(paper.authors) >= 3:
            strengths.append("Multi-author collaboration")

        return strengths

    def _identify_weaknesses(self, paper: ResearchPaper) -> List[str]:
        """Identify paper weaknesses"""
        weaknesses = []

        if not paper.peer_reviewed:
            weaknesses.append("Not peer-reviewed (preprint)")

        if paper.citation_count == 0:
            weaknesses.append("No citations yet")

        if not paper.doi:
            weaknesses.append("No DOI available")

        if paper.abstract == "No abstract available":
            weaknesses.append("Abstract not available")

        if not paper.year:
            weaknesses.append("Publication year unknown")

        return weaknesses

    def _generate_assessment(self, score: float, paper: ResearchPaper) -> str:
        """Generate textual assessment"""
        if score >= 9.0:
            quality = "Excellent"
            recommendation = "Highly reliable source"
        elif score >= 8.0:
            quality = "Very Good"
            recommendation = "Reliable source"
        elif score >= 7.0:
            quality = "Good"
            recommendation = "Generally reliable, verify key claims"
        elif score >= 6.0:
            quality = "Fair"
            recommendation = "Use with caution, cross-reference important claims"
        else:
            quality = "Limited"
            recommendation = "Verify all claims independently"

        return f"{quality} credibility. {recommendation}."

    def _merge_analyses(self, heuristic: CredibilityScore, ai_analysis: Dict[str, Any]) -> CredibilityScore:
        """Merge heuristic and AI analyses"""
        # Average scores where both available
        overall = (heuristic.overall_score + ai_analysis.get('credibility_score', heuristic.overall_score)) / 2
        author_rep = (heuristic.author_reputation + ai_analysis.get('author_reputation', heuristic.author_reputation)) / 2
        pub_qual = (heuristic.publication_quality + ai_analysis.get('publication_quality', heuristic.publication_quality)) / 2
        method_rigor = (heuristic.methodology_rigor + ai_analysis.get('methodology_rigor', heuristic.methodology_rigor)) / 2

        # Combine bias indicators and strengths/weaknesses
        bias = list(set(heuristic.bias_indicators + ai_analysis.get('bias_indicators', [])))
        strengths = list(set(heuristic.strengths + ai_analysis.get('strengths', [])))
        weaknesses = list(set(heuristic.weaknesses + ai_analysis.get('weaknesses', [])))

        # Use AI assessment if available
        assessment = ai_analysis.get('overall_assessment', heuristic.assessment)

        return CredibilityScore(
            overall_score=overall,
            author_reputation=author_rep,
            publication_quality=pub_qual,
            methodology_rigor=method_rigor,
            peer_review_status=heuristic.peer_review_status,
            citation_impact=heuristic.citation_impact,
            bias_indicators=bias,
            strengths=strengths,
            weaknesses=weaknesses,
            assessment=assessment
        )

    def filter_by_credibility(self, papers: List[ResearchPaper],
                             min_score: float = 7.0) -> List[ResearchPaper]:
        """
        Filter papers by minimum credibility score

        Args:
            papers: List of papers
            min_score: Minimum credibility score (0-10)

        Returns:
            Filtered list of papers
        """
        filtered = []
        for paper in papers:
            score = self.analyze_paper(paper)
            if score.overall_score >= min_score:
                filtered.append(paper)

        logger.info(f"Filtered {len(papers)} papers to {len(filtered)} meeting credibility threshold {min_score}")
        return filtered

    def get_average_credibility(self, papers: List[ResearchPaper]) -> float:
        """
        Calculate average credibility score for papers

        Args:
            papers: List of papers

        Returns:
            Average credibility score
        """
        if not papers:
            return 0.0

        total = sum(self.analyze_paper(p).overall_score for p in papers)
        return total / len(papers)

    def _get_paper_id(self, paper: ResearchPaper) -> str:
        """Generate unique paper ID"""
        if paper.doi:
            return f"doi:{paper.doi}"
        else:
            import hashlib
            return hashlib.md5(paper.title.encode()).hexdigest()[:12]

    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics"""
        return {
            'papers_analyzed': len(self.credibility_cache),
            'average_score': sum(s.overall_score for s in self.credibility_cache.values()) / max(len(self.credibility_cache), 1)
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"CredibilityAnalyzer({len(self.credibility_cache)} papers analyzed)"
