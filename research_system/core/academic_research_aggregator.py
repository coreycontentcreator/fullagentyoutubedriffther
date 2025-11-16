"""
Academic Research Aggregator
Coordinates multi-database research queries and combines results
"""

import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import logging
from collections import defaultdict

from ..sources.base_source import BaseResearchSource, ResearchPaper, SearchResult, get_source_registry
from ..sources.semantic_scholar import SemanticScholarSource
from ..sources.crossref_source import CrossRefSource
from ..sources.jstor_source import JSTORSource
from ..sources.arxiv_pubmed import ArXivSource, PubMedSource
from ..sources.openalex_source import OpenAlexSource
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class AggregatedResearch:
    """Container for aggregated research results from multiple sources"""
    papers: List[ResearchPaper]
    total_papers: int
    sources_queried: List[str]
    sources_succeeded: List[str]
    sources_failed: List[str]
    query: str
    search_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.papers)

    def get_papers_by_source(self, source_name: str) -> List[ResearchPaper]:
        """Get papers from a specific source"""
        return [p for p in self.papers if p.source.lower() == source_name.lower()]

    def get_top_papers(self, n: int = 10, by: str = "citations") -> List[ResearchPaper]:
        """
        Get top N papers by specified criterion

        Args:
            n: Number of papers to return
            by: Criterion ("citations", "year", "relevance")

        Returns:
            List of top papers
        """
        if by == "citations":
            return sorted(self.papers, key=lambda p: p.citation_count, reverse=True)[:n]
        elif by == "year":
            return sorted(self.papers, key=lambda p: p.year or 0, reverse=True)[:n]
        else:
            return self.papers[:n]


class AcademicResearchAggregator:
    """
    Coordinates research queries across multiple databases
    Implements the Database Coordinator subagent functionality
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize research aggregator

        Args:
            config: Configuration manager
        """
        self.config = config
        self.registry = get_source_registry()
        self._initialize_sources()

        logger.info(f"Research Aggregator initialized with {len(self.registry)} sources")

    def _initialize_sources(self) -> None:
        """Initialize all available research sources"""
        # Semantic Scholar
        if self.config.is_source_enabled('semantic_scholar'):
            source = SemanticScholarSource(
                api_key=self.config.api_config.semantic_scholar_api_key,
                timeout=self.config.research_config.timeout_seconds,
                max_results=self.config.research_config.max_papers_per_source
            )
            self.registry.register(source, self.config.get_source_priority('semantic_scholar'))

        # CrossRef
        if self.config.is_source_enabled('crossref'):
            source = CrossRefSource(
                email=self.config.api_config.openalex_email,  # Use same email
                timeout=self.config.research_config.timeout_seconds,
                max_results=self.config.research_config.max_papers_per_source
            )
            self.registry.register(source, self.config.get_source_priority('crossref'))

        # JSTOR (Primary source)
        if self.config.is_source_enabled('jstor'):
            source = JSTORSource(
                api_key=self.config.api_config.jstor_api_key,
                timeout=self.config.research_config.timeout_seconds,
                max_results=self.config.research_config.max_papers_per_source
            )
            self.registry.register(source, self.config.get_source_priority('jstor'))

        # arXiv
        if self.config.is_source_enabled('arxiv'):
            source = ArXivSource(
                timeout=self.config.research_config.timeout_seconds,
                max_results=self.config.research_config.max_papers_per_source
            )
            self.registry.register(source, self.config.get_source_priority('arxiv'))

        # PubMed
        if self.config.is_source_enabled('pubmed'):
            source = PubMedSource(
                api_key=self.config.api_config.pubmed_api_key,
                email=self.config.api_config.openalex_email,
                timeout=self.config.research_config.timeout_seconds,
                max_results=self.config.research_config.max_papers_per_source
            )
            self.registry.register(source, self.config.get_source_priority('pubmed'))

        # OpenAlex
        if self.config.is_source_enabled('openalex'):
            source = OpenAlexSource(
                email=self.config.api_config.openalex_email,
                timeout=self.config.research_config.timeout_seconds,
                max_results=self.config.research_config.max_papers_per_source
            )
            self.registry.register(source, self.config.get_source_priority('openalex'))

    def add_custom_source(self, source: BaseResearchSource, priority: Optional[int] = None) -> None:
        """
        Add a custom research source dynamically

        Args:
            source: Research source to add
            priority: Priority level (1-10)
        """
        self.registry.register(source, priority)
        logger.info(f"Added custom research source: {source.name}")

    def search_all_sources(
        self,
        query: str,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        max_papers_per_source: Optional[int] = None,
        sources_to_use: Optional[List[str]] = None
    ) -> AggregatedResearch:
        """
        Search across all enabled sources in parallel

        Args:
            query: Search query
            year_from: Start year filter
            year_to: End year filter
            max_papers_per_source: Maximum papers per source
            sources_to_use: Specific sources to query (None = all enabled)

        Returns:
            AggregatedResearch with combined results
        """
        import time
        start_time = time.time()

        # Get sources to query
        if sources_to_use:
            sources = [self.registry.get_source(name) for name in sources_to_use]
            sources = [s for s in sources if s is not None]
        else:
            sources = self.registry.get_enabled_sources()

        if not sources:
            logger.warning("No enabled sources available for research")
            return AggregatedResearch(
                papers=[],
                total_papers=0,
                sources_queried=[],
                sources_succeeded=[],
                sources_failed=[],
                query=query,
                search_time=0,
                metadata={"error": "No sources available"}
            )

        logger.info(f"Querying {len(sources)} sources: {[s.name for s in sources]}")

        # Execute searches
        if self.config.research_config.parallel_requests:
            results = self._search_parallel(
                sources, query, year_from, year_to, max_papers_per_source
            )
        else:
            results = self._search_sequential(
                sources, query, year_from, year_to, max_papers_per_source
            )

        # Combine and deduplicate results
        all_papers = []
        sources_queried = []
        sources_succeeded = []
        sources_failed = []

        for source, result in results.items():
            sources_queried.append(source)
            if result.papers:
                all_papers.extend(result.papers)
                sources_succeeded.append(source)
            else:
                sources_failed.append(source)

        # Deduplicate papers
        deduplicated_papers = self._deduplicate_papers(all_papers)

        # Sort by priority source first, then by citations
        sorted_papers = self._prioritize_papers(deduplicated_papers)

        # Limit total papers
        max_total = self.config.research_config.total_max_papers
        sorted_papers = sorted_papers[:max_total]

        search_time = time.time() - start_time

        logger.info(
            f"Research complete: {len(sorted_papers)} unique papers from "
            f"{len(sources_succeeded)}/{len(sources_queried)} sources in {search_time:.2f}s"
        )

        return AggregatedResearch(
            papers=sorted_papers,
            total_papers=len(sorted_papers),
            sources_queried=sources_queried,
            sources_succeeded=sources_succeeded,
            sources_failed=sources_failed,
            query=query,
            search_time=search_time,
            metadata={
                "total_found_before_dedup": len(all_papers),
                "deduplication_removed": len(all_papers) - len(deduplicated_papers)
            }
        )

    def _search_parallel(
        self,
        sources: List[BaseResearchSource],
        query: str,
        year_from: Optional[int],
        year_to: Optional[int],
        max_papers_per_source: Optional[int]
    ) -> Dict[str, SearchResult]:
        """Execute searches in parallel using thread pool"""
        results = {}
        max_workers = min(len(sources), self.config.research_config.max_concurrent_requests)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(
                    source.search,
                    query,
                    max_papers_per_source or source.max_results,
                    year_from,
                    year_to
                ): source.name
                for source in sources
            }

            for future in concurrent.futures.as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    result = future.result(timeout=self.config.research_config.timeout_seconds)
                    results[source_name] = result
                except Exception as e:
                    logger.error(f"Error querying {source_name}: {e}")
                    results[source_name] = SearchResult(
                        papers=[],
                        total_results=0,
                        query=query,
                        source=source_name,
                        search_time=0,
                        metadata={"error": str(e)}
                    )

        return results

    def _search_sequential(
        self,
        sources: List[BaseResearchSource],
        query: str,
        year_from: Optional[int],
        year_to: Optional[int],
        max_papers_per_source: Optional[int]
    ) -> Dict[str, SearchResult]:
        """Execute searches sequentially"""
        results = {}

        for source in sources:
            try:
                result = source.search(
                    query,
                    max_papers_per_source or source.max_results,
                    year_from,
                    year_to
                )
                results[source.name] = result
            except Exception as e:
                logger.error(f"Error querying {source.name}: {e}")
                results[source.name] = SearchResult(
                    papers=[],
                    total_results=0,
                    query=query,
                    source=source.name,
                    search_time=0,
                    metadata={"error": str(e)}
                )

        return results

    def _deduplicate_papers(self, papers: List[ResearchPaper]) -> List[ResearchPaper]:
        """
        Deduplicate papers based on DOI, title similarity, or arXiv ID

        Args:
            papers: List of potentially duplicate papers

        Returns:
            Deduplicated list of papers
        """
        seen_dois: Set[str] = set()
        seen_titles: Set[str] = set()
        seen_arxiv: Set[str] = set()
        unique_papers = []

        for paper in papers:
            # Check DOI
            if paper.doi:
                doi_normalized = paper.doi.lower().strip()
                if doi_normalized in seen_dois:
                    continue
                seen_dois.add(doi_normalized)

            # Check arXiv ID
            arxiv_id = paper.metadata.get('arxiv_id')
            if arxiv_id:
                if arxiv_id in seen_arxiv:
                    continue
                seen_arxiv.add(arxiv_id)

            # Check title similarity (normalized)
            title_normalized = self._normalize_title(paper.title)
            if title_normalized in seen_titles:
                continue
            seen_titles.add(title_normalized)

            unique_papers.append(paper)

        logger.info(f"Deduplicated {len(papers)} papers to {len(unique_papers)} unique papers")
        return unique_papers

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        import re
        # Remove special characters, extra spaces, and convert to lowercase
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        normalized = ' '.join(normalized.split())
        return normalized

    def _prioritize_papers(self, papers: List[ResearchPaper]) -> List[ResearchPaper]:
        """
        Sort papers by source priority and citation count

        Args:
            papers: List of papers

        Returns:
            Sorted list of papers
        """
        # Create priority score for each paper
        def paper_score(paper: ResearchPaper) -> tuple:
            source_priority = self.config.get_source_priority(paper.source)
            citation_count = paper.citation_count
            year = paper.year or 0
            return (source_priority, citation_count, year)

        return sorted(papers, key=paper_score, reverse=True)

    def search_by_topic_areas(
        self,
        topic: str,
        focus_areas: List[str],
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ) -> Dict[str, AggregatedResearch]:
        """
        Search multiple focus areas within a topic

        Args:
            topic: Main research topic
            focus_areas: Specific areas to focus on
            year_from: Start year
            year_to: End year

        Returns:
            Dictionary mapping focus areas to research results
        """
        results = {}

        for area in focus_areas:
            query = f"{topic} {area}"
            logger.info(f"Searching focus area: {area}")
            results[area] = self.search_all_sources(
                query=query,
                year_from=year_from,
                year_to=year_to
            )

        return results

    def get_source_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all sources

        Returns:
            Dictionary of source statistics
        """
        stats = {}
        for source in self.registry.get_all_sources():
            stats[source.name] = source.get_stats()
        return stats

    def reset_statistics(self) -> None:
        """Reset statistics for all sources"""
        for source in self.registry.get_all_sources():
            source.reset_stats()
        logger.info("Reset statistics for all sources")
