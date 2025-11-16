"""
OpenAlex API Integration
Comprehensive open catalog of scholarly papers, authors, institutions
"""

import requests
import time
from typing import List, Dict, Any, Optional
import logging
from .base_source import BaseResearchSource, ResearchPaper, SearchResult

logger = logging.getLogger(__name__)


class OpenAlexSource(BaseResearchSource):
    """
    OpenAlex research source
    Free, open API for comprehensive scholarly metadata
    """

    BASE_URL = "https://api.openalex.org"

    def __init__(self, email: Optional[str] = None, timeout: int = 30, max_results: int = 50):
        """
        Initialize OpenAlex source

        Args:
            email: Email for polite pool (faster, more reliable service)
            timeout: Request timeout
            max_results: Maximum results per query
        """
        super().__init__(
            name="OpenAlex",
            api_key=None,
            timeout=timeout,
            max_results=max_results
        )
        self.email = email
        self.session = requests.Session()

        # Set user agent for polite pool
        if email:
            self.session.headers.update({
                "User-Agent": f"mailto:{email}"
            })

    def search(self, query: str, max_results: Optional[int] = None,
               year_from: Optional[int] = None, year_to: Optional[int] = None,
               **kwargs) -> SearchResult:
        """
        Search OpenAlex for papers

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

            # Build filter string
            filters = [f"default.search:{query}"]

            if year_from:
                filters.append(f"from_publication_date:{year_from}-01-01")
            if year_to:
                filters.append(f"to_publication_date:{year_to}-12-31")

            # Build parameters
            params = {
                "filter": ",".join(filters),
                "per-page": min(max_results, 200),
                "select": "id,doi,title,display_name,publication_date,authorships,abstract_inverted_index,"
                         "cited_by_count,is_oa,open_access,primary_location,type,biblio"
            }

            # Make request
            response = self.session.get(
                f"{self.BASE_URL}/works",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get("results", []):
                try:
                    paper = self._parse_paper(item)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing OpenAlex paper: {e}")
                    continue

            search_time = time.time() - start_time
            total_results = data.get("meta", {}).get("count", len(papers))

            logger.info(f"OpenAlex: Found {len(papers)} papers in {search_time:.2f}s")

            return SearchResult(
                papers=papers,
                total_results=total_results,
                query=query,
                source=self.name,
                search_time=search_time,
                metadata={
                    "per_page": data.get("meta", {}).get("per_page"),
                    "page": data.get("meta", {}).get("page")
                }
            )

        except Exception as e:
            self._increment_error_count()
            logger.error(f"OpenAlex search error: {e}")
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
            paper_id: OpenAlex work ID or DOI

        Returns:
            ResearchPaper object or None
        """
        try:
            self._increment_request_count()

            # Handle both OpenAlex IDs and DOIs
            if paper_id.startswith("W"):
                url = f"{self.BASE_URL}/works/{paper_id}"
            elif paper_id.startswith("http"):
                url = f"{self.BASE_URL}/works/{paper_id}"
            else:
                # Assume DOI
                url = f"{self.BASE_URL}/works/doi:{paper_id}"

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            return self._parse_paper(data)

        except Exception as e:
            self._increment_error_count()
            logger.error(f"Error getting OpenAlex paper details: {e}")
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

            # OpenAlex doesn't have a direct "related papers" endpoint
            # We'll get papers that cite this paper
            params = {
                "filter": f"cites:{paper_id}",
                "per-page": max_results,
                "sort": "cited_by_count:desc"
            }

            response = self.session.get(
                f"{self.BASE_URL}/works",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get("results", []):
                try:
                    paper = self._parse_paper(item)
                    papers.append(paper)
                except:
                    continue

            return papers

        except Exception as e:
            logger.error(f"Error getting related papers: {e}")
            return []

    def _parse_paper(self, data: Dict[str, Any]) -> ResearchPaper:
        """
        Parse OpenAlex paper data into ResearchPaper object

        Args:
            data: Raw paper data from API

        Returns:
            ResearchPaper object
        """
        # Title
        title = data.get("title") or data.get("display_name", "Untitled")

        # Authors
        authors = []
        for authorship in data.get("authorships", []):
            author = authorship.get("author", {})
            name = author.get("display_name")
            if name:
                authors.append(name)

        # Abstract - OpenAlex uses inverted index
        abstract = self._reconstruct_abstract(data.get("abstract_inverted_index"))

        # Year
        pub_date = data.get("publication_date")
        year = self._extract_year(pub_date)

        # DOI
        doi = data.get("doi", "").replace("https://doi.org/", "")

        # URL
        url = data.get("id") or (f"https://doi.org/{doi}" if doi else None)

        # Citation count
        citation_count = data.get("cited_by_count", 0)

        # Publication venue
        primary_location = data.get("primary_location") or {}
        source_info = primary_location.get("source") or {}
        publication = source_info.get("display_name", "Unknown")

        # Open access
        is_oa = data.get("is_oa", False)
        open_access_info = data.get("open_access") or {}
        oa_url = open_access_info.get("oa_url")

        # Type
        work_type = data.get("type", "")
        peer_reviewed = work_type in ["journal-article", "proceedings-article"]

        # Biblio info
        biblio = data.get("biblio") or {}

        return ResearchPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            year=year,
            source=self.name,
            url=url,
            doi=doi if doi else None,
            citation_count=citation_count,
            publication=publication,
            keywords=[],  # OpenAlex concepts could be mapped here
            references=[],
            pdf_url=oa_url if is_oa else None,
            peer_reviewed=peer_reviewed,
            open_access=is_oa,
            metadata={
                "openalex_id": data.get("id"),
                "type": work_type,
                "volume": biblio.get("volume"),
                "issue": biblio.get("issue"),
                "first_page": biblio.get("first_page"),
                "last_page": biblio.get("last_page")
            }
        )

    def _reconstruct_abstract(self, inverted_index: Optional[Dict[str, List[int]]]) -> str:
        """
        Reconstruct abstract from OpenAlex's inverted index format

        Args:
            inverted_index: Dictionary mapping words to positions

        Returns:
            Reconstructed abstract string
        """
        if not inverted_index:
            return "No abstract available"

        try:
            # Create list of (position, word) tuples
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))

            # Sort by position and join
            word_positions.sort(key=lambda x: x[0])
            abstract = " ".join(word for _, word in word_positions)

            return abstract if abstract else "No abstract available"

        except Exception as e:
            logger.warning(f"Error reconstructing abstract: {e}")
            return "No abstract available"

    def requires_api_key(self) -> bool:
        """OpenAlex doesn't require API key but benefits from email"""
        return False

    def get_priority(self) -> int:
        """Medium priority"""
        return 6

    def supports_advanced_search(self) -> bool:
        """Supports advanced filtering"""
        return True

    def get_rate_limit(self) -> Optional[int]:
        """
        Polite pool (with email): 100,000 requests per day
        Without email: 10 requests per second (burst), then throttled
        """
        return 600 if self.email else 100  # requests per minute
