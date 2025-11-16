"""
CrossRef API Integration
Comprehensive metadata for scholarly publications with DOI
"""

import requests
import time
from typing import List, Dict, Any, Optional
import logging
from .base_source import BaseResearchSource, ResearchPaper, SearchResult

logger = logging.getLogger(__name__)


class CrossRefSource(BaseResearchSource):
    """
    CrossRef research source
    Free API for DOI-based scholarly publication metadata
    """

    BASE_URL = "https://api.crossref.org"

    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None,
                 timeout: int = 30, max_results: int = 50):
        """
        Initialize CrossRef source

        Args:
            api_key: Optional API key (not required)
            email: Email for polite pool (faster rate limits)
            timeout: Request timeout
            max_results: Maximum results per query
        """
        super().__init__(
            name="CrossRef",
            api_key=api_key,
            timeout=timeout,
            max_results=max_results
        )
        self.email = email
        self.session = requests.Session()

        # Set user agent for polite pool
        if email:
            self.session.headers.update({
                "User-Agent": f"ResearchSystem/1.0 (mailto:{email})"
            })

    def search(self, query: str, max_results: Optional[int] = None,
               year_from: Optional[int] = None, year_to: Optional[int] = None,
               **kwargs) -> SearchResult:
        """
        Search CrossRef for papers

        Args:
            query: Search query
            max_results: Maximum results
            year_from: Start year filter
            year_to: End year filter
            **kwargs: Additional parameters

        Returns:
            SearchResult with papers
        """
        start_time = time.time()
        max_results = max_results or self.max_results

        try:
            self._increment_request_count()

            # Build query parameters
            params = {
                "query": query,
                "rows": min(max_results, 100),
                "select": "DOI,title,author,abstract,published,publisher,type,link,"
                         "is-referenced-by-count,subject,ISSN,container-title"
            }

            # Add filters
            filters = []
            if year_from:
                filters.append(f"from-pub-date:{year_from}")
            if year_to:
                filters.append(f"until-pub-date:{year_to}")

            if filters:
                params["filter"] = ",".join(filters)

            # Make request
            response = self.session.get(
                f"{self.BASE_URL}/works",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get("message", {}).get("items", []):
                try:
                    paper = self._parse_paper(item)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing paper: {e}")
                    continue

            search_time = time.time() - start_time
            total_results = data.get("message", {}).get("total-results", len(papers))

            logger.info(f"CrossRef: Found {len(papers)} papers in {search_time:.2f}s")

            return SearchResult(
                papers=papers,
                total_results=total_results,
                query=query,
                source=self.name,
                search_time=search_time
            )

        except Exception as e:
            self._increment_error_count()
            logger.error(f"CrossRef search error: {e}")
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
        Get detailed information about a specific paper via DOI

        Args:
            paper_id: DOI of the paper

        Returns:
            ResearchPaper object or None
        """
        try:
            self._increment_request_count()

            # Clean DOI
            doi = paper_id.replace("https://doi.org/", "").replace("doi:", "")

            response = self.session.get(
                f"{self.BASE_URL}/works/{doi}",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return self._parse_paper(data.get("message", {}))

        except Exception as e:
            self._increment_error_count()
            logger.error(f"Error getting paper details: {e}")
            return None

    def _parse_paper(self, data: Dict[str, Any]) -> ResearchPaper:
        """
        Parse CrossRef paper data into ResearchPaper object

        Args:
            data: Raw paper data from API

        Returns:
            ResearchPaper object
        """
        # Extract title
        title_list = data.get("title", [])
        title = title_list[0] if title_list else "Untitled"

        # Extract authors
        authors = []
        for author in data.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)

        # Extract year
        published = data.get("published") or data.get("published-print") or data.get("published-online")
        year = None
        if published and "date-parts" in published:
            date_parts = published["date-parts"][0]
            if date_parts:
                year = date_parts[0]

        # Extract abstract
        abstract = data.get("abstract", "No abstract available")

        # DOI
        doi = data.get("DOI")
        url = f"https://doi.org/{doi}" if doi else None

        # Publication venue
        container_title = data.get("container-title", [])
        publication = container_title[0] if container_title else "Unknown"

        # Citation count
        citation_count = data.get("is-referenced-by-count", 0)

        # Type
        paper_type = data.get("type", "")
        peer_reviewed = paper_type in ["journal-article", "proceedings-article"]

        # PDF link
        pdf_url = None
        for link in data.get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL")
                break

        # Keywords/subjects
        keywords = data.get("subject", [])

        return ResearchPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            year=year,
            source=self.name,
            url=url,
            doi=doi,
            citation_count=citation_count,
            publication=publication,
            keywords=keywords,
            references=[],
            pdf_url=pdf_url,
            peer_reviewed=peer_reviewed,
            open_access="license" in data,
            metadata={
                "publisher": data.get("publisher"),
                "type": paper_type,
                "issn": data.get("ISSN", [])
            }
        )

    def requires_api_key(self) -> bool:
        """CrossRef doesn't require API key"""
        return False

    def get_priority(self) -> int:
        """Medium-high priority"""
        return 8

    def supports_advanced_search(self) -> bool:
        """Supports advanced filtering"""
        return True

    def get_rate_limit(self) -> Optional[int]:
        """
        50 requests/second in polite pool (with email)
        Otherwise throttled
        """
        return 1000 if self.email else 50  # requests per minute
