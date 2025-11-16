"""
Semantic Scholar API Integration
Free, comprehensive research database with citation analysis
"""

import requests
import time
from typing import List, Dict, Any, Optional
import logging
from .base_source import BaseResearchSource, ResearchPaper, SearchResult

logger = logging.getLogger(__name__)


class SemanticScholarSource(BaseResearchSource):
    """
    Semantic Scholar research source
    Free API with excellent citation analysis and paper recommendations
    """

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_results: int = 50):
        """
        Initialize Semantic Scholar source

        Args:
            api_key: Optional API key for higher rate limits
            timeout: Request timeout
            max_results: Maximum results per query
        """
        super().__init__(
            name="Semantic Scholar",
            api_key=api_key,
            timeout=timeout,
            max_results=max_results
        )
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"x-api-key": api_key})

    def search(self, query: str, max_results: Optional[int] = None,
               year_from: Optional[int] = None, year_to: Optional[int] = None,
               **kwargs) -> SearchResult:
        """
        Search Semantic Scholar for papers

        Args:
            query: Search query
            max_results: Maximum results (default: self.max_results)
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
                "limit": min(max_results, 100),  # API limit is 100
                "fields": "paperId,title,abstract,authors,year,citationCount,publicationDate,"
                         "venue,openAccessPdf,externalIds,publicationTypes,url,referenceCount"
            }

            # Add year filters if provided
            if year_from:
                params["year"] = f"{year_from}-"
            if year_to:
                if "year" in params:
                    params["year"] += str(year_to)
                else:
                    params["year"] = f"-{year_to}"

            # Make request
            response = self.session.get(
                f"{self.BASE_URL}/paper/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get("data", []):
                try:
                    paper = self._parse_paper(item)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing paper: {e}")
                    continue

            search_time = time.time() - start_time

            logger.info(f"Semantic Scholar: Found {len(papers)} papers in {search_time:.2f}s")

            return SearchResult(
                papers=papers,
                total_results=data.get("total", len(papers)),
                query=query,
                source=self.name,
                search_time=search_time,
                metadata={"offset": data.get("offset", 0)}
            )

        except Exception as e:
            self._increment_error_count()
            logger.error(f"Semantic Scholar search error: {e}")
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
            paper_id: Semantic Scholar paper ID or DOI

        Returns:
            ResearchPaper object or None
        """
        try:
            self._increment_request_count()

            response = self.session.get(
                f"{self.BASE_URL}/paper/{paper_id}",
                params={
                    "fields": "paperId,title,abstract,authors,year,citationCount,publicationDate,"
                             "venue,openAccessPdf,externalIds,publicationTypes,url,referenceCount,"
                             "citations,references"
                },
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return self._parse_paper(data)

        except Exception as e:
            self._increment_error_count()
            logger.error(f"Error getting paper details: {e}")
            return None

    def get_related_papers(self, paper_id: str, max_results: int = 10) -> List[ResearchPaper]:
        """
        Get papers related to a given paper

        Args:
            paper_id: Paper identifier
            max_results: Maximum number of related papers

        Returns:
            List of related papers
        """
        try:
            self._increment_request_count()

            response = self.session.get(
                f"{self.BASE_URL}/paper/{paper_id}/recommendations",
                params={"limit": max_results},
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get("recommendedPapers", []):
                try:
                    paper = self._parse_paper(item)
                    papers.append(paper)
                except:
                    continue

            return papers

        except Exception as e:
            logger.error(f"Error getting related papers: {e}")
            return []

    def get_citation_network(self, paper_id: str, depth: int = 1) -> List[ResearchPaper]:
        """
        Get citation network for a paper

        Args:
            paper_id: Paper identifier
            depth: Depth of citation network (currently only supports 1)

        Returns:
            List of citing and cited papers
        """
        papers = []

        try:
            # Get papers that cite this paper
            self._increment_request_count()
            response = self.session.get(
                f"{self.BASE_URL}/paper/{paper_id}/citations",
                params={"limit": 20},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("data", []):
                try:
                    citing_paper = item.get("citingPaper", {})
                    paper = self._parse_paper(citing_paper)
                    papers.append(paper)
                except:
                    continue

            # Get papers cited by this paper
            self._increment_request_count()
            response = self.session.get(
                f"{self.BASE_URL}/paper/{paper_id}/references",
                params={"limit": 20},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("data", []):
                try:
                    cited_paper = item.get("citedPaper", {})
                    paper = self._parse_paper(cited_paper)
                    papers.append(paper)
                except:
                    continue

        except Exception as e:
            logger.error(f"Error getting citation network: {e}")

        return papers

    def _parse_paper(self, data: Dict[str, Any]) -> ResearchPaper:
        """
        Parse Semantic Scholar paper data into ResearchPaper object

        Args:
            data: Raw paper data from API

        Returns:
            ResearchPaper object
        """
        authors = [
            author.get("name", "Unknown")
            for author in data.get("authors", [])
        ]

        external_ids = data.get("externalIds", {})
        doi = external_ids.get("DOI")
        arxiv_id = external_ids.get("ArXiv")

        # Get PDF URL
        pdf_url = None
        if data.get("openAccessPdf"):
            pdf_url = data["openAccessPdf"].get("url")

        # Check if peer-reviewed
        publication_types = data.get("publicationTypes", [])
        peer_reviewed = "JournalArticle" in publication_types or "Conference" in publication_types

        return ResearchPaper(
            title=data.get("title", "Untitled"),
            authors=authors,
            abstract=data.get("abstract", "No abstract available"),
            year=data.get("year"),
            source=self.name,
            url=data.get("url"),
            doi=doi,
            citation_count=data.get("citationCount", 0),
            publication=data.get("venue", "Unknown"),
            keywords=[],
            references=[],
            pdf_url=pdf_url,
            peer_reviewed=peer_reviewed,
            open_access=bool(pdf_url),
            metadata={
                "paper_id": data.get("paperId"),
                "arxiv_id": arxiv_id,
                "publication_date": data.get("publicationDate"),
                "reference_count": data.get("referenceCount", 0)
            }
        )

    def requires_api_key(self) -> bool:
        """Semantic Scholar doesn't require API key but benefits from one"""
        return False

    def get_priority(self) -> int:
        """High priority source"""
        return 9

    def supports_advanced_search(self) -> bool:
        """Supports advanced search features"""
        return True

    def get_rate_limit(self) -> Optional[int]:
        """
        Rate limit depends on whether API key is used
        With key: 1000/5min, Without: 100/5min
        """
        return 200 if self.api_key else 20  # requests per minute (conservative)
