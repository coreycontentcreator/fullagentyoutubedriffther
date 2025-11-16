"""
JSTOR API Integration
Primary source for unique academic insights and scholarly articles
"""

import requests
import time
from typing import List, Dict, Any, Optional
import logging
from .base_source import BaseResearchSource, ResearchPaper, SearchResult

logger = logging.getLogger(__name__)


class JSTORSource(BaseResearchSource):
    """
    JSTOR research source - PRIMARY SOURCE for unique insights
    Requires API key from JSTOR
    """

    BASE_URL = "https://api.jstor.org/v1"

    def __init__(self, api_key: str, timeout: int = 30, max_results: int = 50):
        """
        Initialize JSTOR source

        Args:
            api_key: JSTOR API key (REQUIRED)
            timeout: Request timeout
            max_results: Maximum results per query
        """
        super().__init__(
            name="JSTOR",
            api_key=api_key,
            timeout=timeout,
            max_results=max_results
        )
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            })

    def search(self, query: str, max_results: Optional[int] = None,
               year_from: Optional[int] = None, year_to: Optional[int] = None,
               **kwargs) -> SearchResult:
        """
        Search JSTOR for papers

        Args:
            query: Search query
            max_results: Maximum results
            year_from: Start year filter
            year_to: End year filter
            **kwargs: Additional JSTOR-specific parameters

        Returns:
            SearchResult with papers
        """
        start_time = time.time()
        max_results = max_results or self.max_results

        if not self.api_key:
            logger.warning("JSTOR API key not configured, skipping search")
            return SearchResult(
                papers=[],
                total_results=0,
                query=query,
                source=self.name,
                search_time=0,
                metadata={"error": "API key not configured"}
            )

        try:
            self._increment_request_count()

            # Build query parameters
            params = {
                "q": query,
                "limit": min(max_results, 100),
                "format": "json"
            }

            # Add filters
            filters = []
            if year_from and year_to:
                filters.append(f"pub_year:[{year_from} TO {year_to}]")
            elif year_from:
                filters.append(f"pub_year:[{year_from} TO *]")
            elif year_to:
                filters.append(f"pub_year:[* TO {year_to}]")

            if filters:
                params["fq"] = " AND ".join(filters)

            # Make request
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get("docs", []):
                try:
                    paper = self._parse_paper(item)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing JSTOR paper: {e}")
                    continue

            search_time = time.time() - start_time
            total_results = data.get("numFound", len(papers))

            logger.info(f"JSTOR: Found {len(papers)} papers in {search_time:.2f}s")

            return SearchResult(
                papers=papers,
                total_results=total_results,
                query=query,
                source=self.name,
                search_time=search_time,
                metadata={
                    "start": data.get("start", 0),
                    "facets": data.get("facets", {})
                }
            )

        except Exception as e:
            self._increment_error_count()
            logger.error(f"JSTOR search error: {e}")
            return SearchResult(
                papers=[],
                total_results=0,
                query=query,
                source=self.name,
                search_time=time.time() - start_time,
                metadata={"error": str(e)}
            )

    def get_paper_details(self, paper_id: str) -> Optional[ResearchPaper]:
        """
        Get detailed information about a specific paper

        Args:
            paper_id: JSTOR item ID or stable URL

        Returns:
            ResearchPaper object or None
        """
        if not self.api_key:
            logger.warning("JSTOR API key not configured")
            return None

        try:
            self._increment_request_count()

            response = self.session.get(
                f"{self.BASE_URL}/item/{paper_id}",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return self._parse_paper(data)

        except Exception as e:
            self._increment_error_count()
            logger.error(f"Error getting JSTOR paper details: {e}")
            return None

    def _parse_paper(self, data: Dict[str, Any]) -> ResearchPaper:
        """
        Parse JSTOR paper data into ResearchPaper object

        Args:
            data: Raw paper data from API

        Returns:
            ResearchPaper object
        """
        # Extract title
        title = data.get("title", ["Untitled"])
        if isinstance(title, list):
            title = title[0] if title else "Untitled"

        # Extract authors
        authors = []
        for author in data.get("author", []):
            if isinstance(author, str):
                authors.append(author)
            elif isinstance(author, dict):
                name = author.get("name", "")
                if name:
                    authors.append(name)

        # Extract year
        year = None
        pub_date = data.get("pub_date") or data.get("publication_date")
        if pub_date:
            if isinstance(pub_date, str):
                year = self._extract_year(pub_date)
            elif isinstance(pub_date, list) and pub_date:
                year = self._extract_year(pub_date[0])

        # Abstract
        abstract = data.get("abstract", "No abstract available")
        if isinstance(abstract, list):
            abstract = abstract[0] if abstract else "No abstract available"

        # DOI and URL
        doi = data.get("doi")
        stable_url = data.get("stable_url") or data.get("url")
        item_id = data.get("id") or data.get("item_id")
        url = stable_url or (f"https://www.jstor.org/stable/{item_id}" if item_id else None)

        # Publication
        publication = data.get("container_title") or data.get("journal_title", "Unknown")
        if isinstance(publication, list):
            publication = publication[0] if publication else "Unknown"

        # Keywords/subjects
        keywords = data.get("subject", [])
        if not isinstance(keywords, list):
            keywords = [keywords] if keywords else []

        # JSTOR articles are generally peer-reviewed
        peer_reviewed = True

        return ResearchPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            year=year,
            source=self.name,
            url=url,
            doi=doi,
            citation_count=0,  # JSTOR doesn't provide citation counts in API
            publication=publication,
            keywords=keywords,
            references=[],
            pdf_url=None,  # JSTOR PDFs require authentication
            peer_reviewed=peer_reviewed,
            open_access=False,  # JSTOR is subscription-based
            metadata={
                "item_id": item_id,
                "stable_url": stable_url,
                "publisher": data.get("publisher"),
                "language": data.get("language"),
                "page_range": data.get("page_range")
            }
        )

    def requires_api_key(self) -> bool:
        """JSTOR requires API key"""
        return True

    def get_priority(self) -> int:
        """HIGHEST priority - primary source for unique insights"""
        return 10

    def supports_advanced_search(self) -> bool:
        """Supports advanced search and filtering"""
        return True

    def get_rate_limit(self) -> Optional[int]:
        """JSTOR rate limits vary by agreement"""
        return 60  # Conservative estimate (requests per minute)
