"""
Research Validator
Validates research quality and enforces quality gates
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from ..sources.base_source import ResearchPaper
from ..subagents.credibility_analyzer import CredibilityAnalyzer, CredibilityScore
from ..subagents.citation_tracker import CitationTracker
from ..core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of research validation"""
    passed: bool
    overall_score: float
    academic_rigor_score: float
    source_diversity_score: float
    citation_quality_score: float
    novelty_score: float
    credibility_score: float
    issues: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'passed': self.passed,
            'overall_score': self.overall_score,
            'academic_rigor_score': self.academic_rigor_score,
            'source_diversity_score': self.source_diversity_score,
            'citation_quality_score': self.citation_quality_score,
            'novelty_score': self.novelty_score,
            'credibility_score': self.credibility_score,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'metadata': self.metadata
        }


class ResearchValidator:
    """
    Research Validator
    Validates research quality according to academic standards
    """

    def __init__(
        self,
        config: ConfigManager,
        credibility_analyzer: CredibilityAnalyzer,
        citation_tracker: CitationTracker
    ):
        """
        Initialize research validator

        Args:
            config: Configuration manager
            credibility_analyzer: Credibility analyzer subagent
            citation_tracker: Citation tracker subagent
        """
        self.config = config
        self.credibility_analyzer = credibility_analyzer
        self.citation_tracker = citation_tracker
        self.thresholds = config.research_config.quality_thresholds

        logger.info("Research Validator initialized with quality thresholds")

    def validate_research(
        self,
        papers: List[ResearchPaper],
        topic: str
    ) -> ValidationResult:
        """
        Validate research quality

        Args:
            papers: Research papers to validate
            topic: Research topic

        Returns:
            ValidationResult with detailed scores and recommendations
        """
        logger.info(f"Validating research on topic: {topic}")
        logger.info(f"Number of papers: {len(papers)}")

        issues = []
        recommendations = []
        metadata = {}

        # 1. Academic Rigor Score
        academic_rigor = self._assess_academic_rigor(papers)
        if academic_rigor < self.thresholds['academic_rigor']:
            issues.append(f"Academic rigor score ({academic_rigor:.1f}) below threshold ({self.thresholds['academic_rigor']})")
            recommendations.append("Include more peer-reviewed journal articles and reduce reliance on preprints")

        # 2. Source Diversity Score
        source_diversity = self._assess_source_diversity(papers)
        if source_diversity < self.thresholds['source_diversity']:
            issues.append(f"Source diversity score ({source_diversity:.1f}) below threshold ({self.thresholds['source_diversity']})")
            recommendations.append("Expand search to include more diverse academic sources")

        # 3. Citation Quality Score
        citation_quality = self._assess_citation_quality(papers)
        if citation_quality < self.thresholds['citation_quality']:
            issues.append(f"Citation quality score ({citation_quality:.1f}) below threshold ({self.thresholds['citation_quality']})")
            recommendations.append("Include more highly-cited seminal works in the field")

        # 4. Novelty Score
        novelty = self._assess_novelty(papers)
        if novelty < self.thresholds['novelty']:
            issues.append(f"Novelty score ({novelty:.1f}) below threshold ({self.thresholds['novelty']})")
            recommendations.append("Include more recent publications to capture latest developments")

        # 5. Credibility Score
        credibility = self._assess_overall_credibility(papers)
        if credibility < self.thresholds['credibility']:
            issues.append(f"Credibility score ({credibility:.1f}) below threshold ({self.thresholds['credibility']})")
            recommendations.append("Review and filter sources with low credibility scores")

        # Calculate overall score (weighted average)
        overall_score = (
            academic_rigor * 0.25 +
            source_diversity * 0.15 +
            citation_quality * 0.20 +
            novelty * 0.15 +
            credibility * 0.25
        )

        # Determine if validation passed
        min_threshold = self.config.research_config.min_quality_threshold
        passed = overall_score >= min_threshold and len(issues) == 0

        logger.info(f"Validation {'PASSED' if passed else 'FAILED'}: Overall score {overall_score:.1f}/10")

        return ValidationResult(
            passed=passed,
            overall_score=overall_score,
            academic_rigor_score=academic_rigor,
            source_diversity_score=source_diversity,
            citation_quality_score=citation_quality,
            novelty_score=novelty,
            credibility_score=credibility,
            issues=issues,
            recommendations=recommendations,
            metadata={
                'total_papers': len(papers),
                'peer_reviewed_count': sum(1 for p in papers if p.peer_reviewed),
                'open_access_count': sum(1 for p in papers if p.open_access),
                'sources_used': list(set(p.source for p in papers))
            }
        )

    def _assess_academic_rigor(self, papers: List[ResearchPaper]) -> float:
        """
        Assess academic rigor based on peer review status and publication quality

        Args:
            papers: List of papers

        Returns:
            Score 0-10
        """
        if not papers:
            return 0.0

        # Percentage of peer-reviewed papers
        peer_reviewed_count = sum(1 for p in papers if p.peer_reviewed)
        peer_reviewed_ratio = peer_reviewed_count / len(papers)

        # Average publication quality (based on source)
        quality_scores = {
            'JSTOR': 10.0,
            'PubMed': 9.5,
            'Semantic Scholar': 8.5,
            'CrossRef': 8.0,
            'OpenAlex': 7.5,
            'arXiv': 6.0
        }

        avg_quality = sum(quality_scores.get(p.source, 7.0) for p in papers) / len(papers)

        # Combined score
        score = (peer_reviewed_ratio * 10 * 0.6) + (avg_quality * 0.4)

        logger.debug(f"Academic rigor: {score:.1f} (peer-reviewed: {peer_reviewed_ratio*100:.0f}%)")
        return min(10.0, score)

    def _assess_source_diversity(self, papers: List[ResearchPaper]) -> float:
        """
        Assess diversity of sources used

        Args:
            papers: List of papers

        Returns:
            Score 0-10
        """
        if not papers:
            return 0.0

        unique_sources = len(set(p.source for p in papers))
        unique_publications = len(set(p.publication for p in papers))

        # More sources and publications = better diversity
        source_score = min(10.0, unique_sources * 1.5)
        publication_score = min(10.0, unique_publications * 0.5)

        score = (source_score * 0.6 + publication_score * 0.4)

        logger.debug(f"Source diversity: {score:.1f} ({unique_sources} sources, {unique_publications} publications)")
        return score

    def _assess_citation_quality(self, papers: List[ResearchPaper]) -> float:
        """
        Assess quality based on citation counts

        Args:
            papers: List of papers

        Returns:
            Score 0-10
        """
        if not papers:
            return 0.0

        # Calculate percentiles for citation counts
        citation_counts = [p.citation_count for p in papers]
        avg_citations = sum(citation_counts) / len(citation_counts)

        # Count highly cited papers (>50 citations)
        highly_cited = sum(1 for c in citation_counts if c > 50)
        highly_cited_ratio = highly_cited / len(papers)

        # Score based on average citations and ratio of highly cited
        avg_score = min(10.0, (avg_citations / 50) * 5)  # 50 citations = 5 points
        ratio_score = highly_cited_ratio * 5  # Up to 5 points

        score = avg_score + ratio_score

        logger.debug(f"Citation quality: {score:.1f} (avg citations: {avg_citations:.0f})")
        return min(10.0, score)

    def _assess_novelty(self, papers: List[ResearchPaper]) -> float:
        """
        Assess novelty based on publication recency

        Args:
            papers: List of papers

        Returns:
            Score 0-10
        """
        if not papers:
            return 0.0

        from datetime import datetime
        current_year = datetime.now().year

        # Count papers by recency
        recent_papers = sum(1 for p in papers if p.year and p.year >= current_year - 3)
        moderately_recent = sum(1 for p in papers if p.year and current_year - 6 <= p.year < current_year - 3)

        recent_ratio = recent_papers / len(papers)
        moderate_ratio = moderately_recent / len(papers)

        # Score: heavily weight recent papers
        score = (recent_ratio * 10 * 0.7) + (moderate_ratio * 10 * 0.3)

        logger.debug(f"Novelty: {score:.1f} ({recent_ratio*100:.0f}% from last 3 years)")
        return score

    def _assess_overall_credibility(self, papers: List[ResearchPaper]) -> float:
        """
        Assess overall credibility using CredibilityAnalyzer

        Args:
            papers: List of papers

        Returns:
            Score 0-10
        """
        if not papers:
            return 0.0

        total_score = 0.0
        for paper in papers:
            cred_score = self.credibility_analyzer.analyze_paper(paper, use_ai=False)
            total_score += cred_score.overall_score

        avg_credibility = total_score / len(papers)

        logger.debug(f"Overall credibility: {avg_credibility:.1f}")
        return avg_credibility

    def suggest_improvements(self, papers: List[ResearchPaper]) -> List[str]:
        """
        Suggest specific improvements to research quality

        Args:
            papers: List of papers

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Check peer review ratio
        peer_reviewed_count = sum(1 for p in papers if p.peer_reviewed)
        if peer_reviewed_count / len(papers) < 0.7:
            suggestions.append("Increase proportion of peer-reviewed papers to at least 70%")

        # Check source diversity
        unique_sources = len(set(p.source for p in papers))
        if unique_sources < 3:
            suggestions.append("Include papers from at least 3 different academic databases")

        # Check for JSTOR papers (primary source)
        jstor_count = sum(1 for p in papers if p.source == "JSTOR")
        if jstor_count == 0:
            suggestions.append("Add JSTOR papers for unique academic insights")

        # Check recency
        from datetime import datetime
        current_year = datetime.now().year
        recent_count = sum(1 for p in papers if p.year and p.year >= current_year - 5)
        if recent_count / len(papers) < 0.4:
            suggestions.append("Include more recent papers (last 5 years) to capture latest research")

        # Check citation impact
        avg_citations = sum(p.citation_count for p in papers) / len(papers)
        if avg_citations < 20:
            suggestions.append("Include more highly-cited influential papers in the field")

        return suggestions

    def __repr__(self) -> str:
        """String representation"""
        return f"ResearchValidator(threshold={self.config.research_config.min_quality_threshold})"
