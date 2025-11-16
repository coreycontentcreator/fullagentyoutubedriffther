"""
Base Research Source Abstract Class
Provides interface for all research sources to ensure modularity and extensibility
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResearchPaper:
    """Standardized research paper data structure"""
    title: str
    authors: List[str]
    abstract: str
    year: Optional[int] = None
    source: str = "Unknown"
    url: Optional[str] = None
    doi: Optional[str] = None
    citation_count: int = 0
    publication: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    pdf_url: Optional[str] = None

    # Quality indicators
    peer_reviewed: bool = False
    open_access: bool = False

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    fetched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'year': self.year,
            'source': self.source,
            'url': self.url,
            'doi': self.doi,
            'citation_count': self.citation_count,
            'publication': self.publication,
            'keywords': self.keywords,
            'references': self.references,
            'pdf_url': self.pdf_url,
            'peer_reviewed': self.peer_reviewed,
            'open_access': self.open_access,
            'metadata': self.metadata,
            'fetched_at': self.fetched_at.isoformat()
        }

    def __repr__(self) -> str:
        """String representation"""
        authors_str = ', '.join(self.authors[:2])
        if len(self.authors) > 2:
            authors_str += f" et al."
        return f"ResearchPaper('{self.title[:50]}...', {authors_str}, {self.year})"


@dataclass
class SearchResult:
    """Search result container"""
    papers: List[ResearchPaper]
    total_results: int
    query: str
    source: str
    search_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.papers)

    def __iter__(self):
        return iter(self.papers)


class BaseResearchSource(ABC):
    """
    Abstract base class for all research sources
    Ensures consistent interface and enables easy addition of new sources
    """

    def __init__(self, name: str, api_key: Optional[str] = None,
                 timeout: int = 30, max_results: int = 50):
        """
        Initialize research source

        Args:
            name: Name of the research source
            api_key: API key if required
            timeout: Request timeout in seconds
            max_results: Maximum results to return
        """
        self.name = name
        self.api_key = api_key
        self.timeout = timeout
        self.max_results = max_results
        self.request_count = 0
        self.error_count = 0

        logger.info(f"Initialized research source: {name}")

    @abstractmethod
    def search(self, query: str, max_results: Optional[int] = None,
               year_from: Optional[int] = None, year_to: Optional[int] = None,
               **kwargs) -> SearchResult:
        """
        Search for research papers

        Args:
            query: Search query
            max_results: Maximum number of results
            year_from: Start year filter
            year_to: End year filter
            **kwargs: Source-specific parameters

        Returns:
            SearchResult object with papers

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        pass

    @abstractmethod
    def get_paper_details(self, paper_id: str) -> Optional[ResearchPaper]:
        """
        Get detailed information about a specific paper

        Args:
            paper_id: Unique identifier for the paper (DOI, arXiv ID, etc.)

        Returns:
            ResearchPaper object or None if not found

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        pass

    def validate_configuration(self) -> bool:
        """
        Validate source configuration

        Returns:
            True if configuration is valid
        """
        if self.requires_api_key() and not self.api_key:
            logger.warning(f"{self.name} requires an API key but none provided")
            return False
        return True

    @abstractmethod
    def requires_api_key(self) -> bool:
        """
        Check if this source requires an API key

        Returns:
            True if API key is required
        """
        pass

    def get_priority(self) -> int:
        """
        Get priority of this source (1-10, higher = more important)
        Override in subclass to set custom priority

        Returns:
            Priority value
        """
        return 5

    def supports_advanced_search(self) -> bool:
        """
        Check if this source supports advanced search features

        Returns:
            True if advanced search is supported
        """
        return False

    def get_rate_limit(self) -> Optional[int]:
        """
        Get rate limit for this source (requests per minute)

        Returns:
            Rate limit or None if no limit
        """
        return None

    def get_citation_network(self, paper_id: str, depth: int = 1) -> List[ResearchPaper]:
        """
        Get citation network for a paper (papers citing this + papers cited by this)

        Args:
            paper_id: Paper identifier
            depth: Depth of citation network to retrieve

        Returns:
            List of related papers
        """
        logger.warning(f"{self.name} does not support citation network retrieval")
        return []

    def get_related_papers(self, paper_id: str, max_results: int = 10) -> List[ResearchPaper]:
        """
        Get papers related to a given paper

        Args:
            paper_id: Paper identifier
            max_results: Maximum number of related papers

        Returns:
            List of related papers
        """
        logger.warning(f"{self.name} does not support related paper retrieval")
        return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for this source

        Returns:
            Dictionary with statistics
        """
        return {
            'name': self.name,
            'requests_made': self.request_count,
            'errors_encountered': self.error_count,
            'success_rate': (self.request_count - self.error_count) / max(self.request_count, 1)
        }

    def reset_stats(self) -> None:
        """Reset statistics"""
        self.request_count = 0
        self.error_count = 0

    def _increment_request_count(self) -> None:
        """Increment request counter"""
        self.request_count += 1

    def _increment_error_count(self) -> None:
        """Increment error counter"""
        self.error_count += 1

    def _standardize_authors(self, authors: Any) -> List[str]:
        """
        Standardize author format from various source formats

        Args:
            authors: Authors in any format

        Returns:
            List of author names as strings
        """
        if isinstance(authors, str):
            return [authors]
        elif isinstance(authors, list):
            result = []
            for author in authors:
                if isinstance(author, str):
                    result.append(author)
                elif isinstance(author, dict):
                    # Handle various author dict formats
                    name = author.get('name') or author.get('full_name') or \
                           f"{author.get('first_name', '')} {author.get('last_name', '')}".strip()
                    if name:
                        result.append(name)
            return result
        return []

    def _extract_year(self, date_str: Any) -> Optional[int]:
        """
        Extract year from various date formats

        Args:
            date_str: Date in any format

        Returns:
            Year as integer or None
        """
        if isinstance(date_str, int):
            return date_str
        elif isinstance(date_str, str):
            try:
                # Try to extract year from string
                import re
                year_match = re.search(r'(\d{4})', date_str)
                if year_match:
                    return int(year_match.group(1))
            except:
                pass
        return None

    def __repr__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(name='{self.name}', requests={self.request_count})"


class ResearchSourceRegistry:
    """
    Registry for managing research sources dynamically
    Allows adding, removing, and querying available sources
    """

    def __init__(self):
        """Initialize registry"""
        self.sources: Dict[str, BaseResearchSource] = {}
        self.source_priorities: Dict[str, int] = {}

    def register(self, source: BaseResearchSource, priority: Optional[int] = None) -> None:
        """
        Register a research source

        Args:
            source: Research source to register
            priority: Priority (1-10, higher = more important)
        """
        self.sources[source.name.lower()] = source
        self.source_priorities[source.name.lower()] = priority or source.get_priority()
        logger.info(f"Registered research source: {source.name} (priority: {self.source_priorities[source.name.lower()]})")

    def unregister(self, source_name: str) -> None:
        """
        Unregister a research source

        Args:
            source_name: Name of source to unregister
        """
        source_name_lower = source_name.lower()
        if source_name_lower in self.sources:
            del self.sources[source_name_lower]
            del self.source_priorities[source_name_lower]
            logger.info(f"Unregistered research source: {source_name}")

    def get_source(self, source_name: str) -> Optional[BaseResearchSource]:
        """
        Get a research source by name

        Args:
            source_name: Name of source

        Returns:
            Research source or None if not found
        """
        return self.sources.get(source_name.lower())

    def get_all_sources(self) -> List[BaseResearchSource]:
        """
        Get all registered sources

        Returns:
            List of all sources
        """
        return list(self.sources.values())

    def get_sources_by_priority(self) -> List[BaseResearchSource]:
        """
        Get sources ordered by priority (highest first)

        Returns:
            List of sources ordered by priority
        """
        sorted_names = sorted(
            self.sources.keys(),
            key=lambda x: self.source_priorities[x],
            reverse=True
        )
        return [self.sources[name] for name in sorted_names]

    def get_enabled_sources(self) -> List[BaseResearchSource]:
        """
        Get all enabled and configured sources

        Returns:
            List of enabled sources
        """
        return [source for source in self.sources.values()
                if source.validate_configuration()]

    def __len__(self) -> int:
        """Get number of registered sources"""
        return len(self.sources)

    def __repr__(self) -> str:
        """String representation"""
        return f"ResearchSourceRegistry({len(self.sources)} sources)"


# Global registry instance
_registry = ResearchSourceRegistry()


def get_source_registry() -> ResearchSourceRegistry:
    """
    Get global source registry

    Returns:
        ResearchSourceRegistry instance
    """
    return _registry
