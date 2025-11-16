"""
arXiv and PubMed Integration
arXiv: Preprints in physics, math, CS, etc.
PubMed: Life sciences and biomedical literature
"""

import requests
import time
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import logging
from .base_source import BaseResearchSource, ResearchPaper, SearchResult

logger = logging.getLogger(__name__)


class ArXivSource(BaseResearchSource):
    """
    arXiv research source
    Free preprint repository for physics, mathematics, CS, and more
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, timeout: int = 30, max_results: int = 50):
        """
        Initialize arXiv source

        Args:
            timeout: Request timeout
            max_results: Maximum results per query
        """
        super().__init__(
            name="arXiv",
            api_key=None,  # No API key needed
            timeout=timeout,
            max_results=max_results
        )
        self.session = requests.Session()

    def search(self, query: str, max_results: Optional[int] = None,
               year_from: Optional[int] = None, year_to: Optional[int] = None,
               **kwargs) -> SearchResult:
        """
        Search arXiv for papers

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

            # Build query
            search_query = f"all:{query}"

            # arXiv doesn't support year filtering in query, we'll filter results
            params = {
                "search_query": search_query,
                "start": 0,
                "max_results": min(max_results * 2, 200),  # Get extra for filtering
                "sortBy": "relevance",
                "sortOrder": "descending"
            }

            # Make request
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom',
                        'arxiv': 'http://arxiv.org/schemas/atom'}

            papers = []
            for entry in root.findall('atom:entry', namespace):
                try:
                    paper = self._parse_paper(entry, namespace)

                    # Filter by year if specified
                    if year_from and paper.year and paper.year < year_from:
                        continue
                    if year_to and paper.year and paper.year > year_to:
                        continue

                    papers.append(paper)

                    if len(papers) >= max_results:
                        break

                except Exception as e:
                    logger.warning(f"Error parsing arXiv paper: {e}")
                    continue

            search_time = time.time() - start_time
            total_results_elem = root.find('opensearch:totalResults',
                                          {'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'})
            total_results = int(total_results_elem.text) if total_results_elem is not None else len(papers)

            logger.info(f"arXiv: Found {len(papers)} papers in {search_time:.2f}s")

            return SearchResult(
                papers=papers,
                total_results=total_results,
                query=query,
                source=self.name,
                search_time=search_time
            )

        except Exception as e:
            self._increment_error_count()
            logger.error(f"arXiv search error: {e}")
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
            paper_id: arXiv ID (e.g., "2101.12345" or "arxiv:2101.12345")

        Returns:
            ResearchPaper object or None
        """
        try:
            # Clean arXiv ID
            arxiv_id = paper_id.replace("arxiv:", "").replace("arXiv:", "")

            result = self.search(f"id:{arxiv_id}", max_results=1)
            if result.papers:
                return result.papers[0]
            return None

        except Exception as e:
            logger.error(f"Error getting arXiv paper details: {e}")
            return None

    def _parse_paper(self, entry: ET.Element, namespace: Dict[str, str]) -> ResearchPaper:
        """Parse arXiv XML entry into ResearchPaper"""
        title = entry.find('atom:title', namespace).text.strip()
        abstract = entry.find('atom:summary', namespace).text.strip()

        # Authors
        authors = []
        for author in entry.findall('atom:author', namespace):
            name = author.find('atom:name', namespace)
            if name is not None:
                authors.append(name.text)

        # Extract arXiv ID and year
        id_url = entry.find('atom:id', namespace).text
        arxiv_id = id_url.split('/')[-1]

        published = entry.find('atom:published', namespace).text
        year = self._extract_year(published)

        # Categories
        categories = []
        for category in entry.findall('atom:category', namespace):
            term = category.get('term')
            if term:
                categories.append(term)

        # PDF URL
        pdf_url = None
        for link in entry.findall('atom:link', namespace):
            if link.get('title') == 'pdf':
                pdf_url = link.get('href')
                break

        return ResearchPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            year=year,
            source=self.name,
            url=id_url,
            doi=None,
            citation_count=0,
            publication="arXiv",
            keywords=categories,
            references=[],
            pdf_url=pdf_url,
            peer_reviewed=False,  # Preprints are not peer-reviewed
            open_access=True,
            metadata={
                "arxiv_id": arxiv_id,
                "categories": categories,
                "published_date": published
            }
        )

    def requires_api_key(self) -> bool:
        return False

    def get_priority(self) -> int:
        return 7

    def get_rate_limit(self) -> Optional[int]:
        """arXiv allows ~1 request per 3 seconds"""
        return 20  # requests per minute


class PubMedSource(BaseResearchSource):
    """
    PubMed research source
    Free access to MEDLINE database of life sciences and biomedical literature
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None,
                 timeout: int = 30, max_results: int = 50):
        """
        Initialize PubMed source

        Args:
            api_key: Optional API key for higher rate limits
            email: Email for API usage tracking
            timeout: Request timeout
            max_results: Maximum results per query
        """
        super().__init__(
            name="PubMed",
            api_key=api_key,
            timeout=timeout,
            max_results=max_results
        )
        self.email = email
        self.session = requests.Session()

    def search(self, query: str, max_results: Optional[int] = None,
               year_from: Optional[int] = None, year_to: Optional[int] = None,
               **kwargs) -> SearchResult:
        """
        Search PubMed for papers

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

            # Build search query
            search_term = query
            if year_from or year_to:
                year_filter = f"{year_from or 1800}:{year_to or 2100}[dp]"
                search_term = f"({query}) AND {year_filter}"

            # Step 1: Search for PMIDs
            search_params = {
                "db": "pubmed",
                "term": search_term,
                "retmax": min(max_results, 200),
                "retmode": "json"
            }
            if self.api_key:
                search_params["api_key"] = self.api_key
            if self.email:
                search_params["email"] = self.email

            search_response = self.session.get(
                f"{self.BASE_URL}/esearch.fcgi",
                params=search_params,
                timeout=self.timeout
            )
            search_response.raise_for_status()
            search_data = search_response.json()

            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            total_results = int(search_data.get("esearchresult", {}).get("count", 0))

            if not pmids:
                return SearchResult(
                    papers=[],
                    total_results=0,
                    query=query,
                    source=self.name,
                    search_time=time.time() - start_time
                )

            # Step 2: Fetch details for PMIDs
            time.sleep(0.4)  # Rate limiting
            self._increment_request_count()

            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml"
            }
            if self.api_key:
                fetch_params["api_key"] = self.api_key

            fetch_response = self.session.get(
                f"{self.BASE_URL}/efetch.fcgi",
                params=fetch_params,
                timeout=self.timeout
            )
            fetch_response.raise_for_status()

            # Parse XML
            root = ET.fromstring(fetch_response.content)
            papers = []

            for article in root.findall('.//PubmedArticle'):
                try:
                    paper = self._parse_paper(article)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing PubMed paper: {e}")
                    continue

            search_time = time.time() - start_time
            logger.info(f"PubMed: Found {len(papers)} papers in {search_time:.2f}s")

            return SearchResult(
                papers=papers,
                total_results=total_results,
                query=query,
                source=self.name,
                search_time=search_time
            )

        except Exception as e:
            self._increment_error_count()
            logger.error(f"PubMed search error: {e}")
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
            paper_id: PubMed ID (PMID)

        Returns:
            ResearchPaper object or None
        """
        try:
            self._increment_request_count()

            params = {
                "db": "pubmed",
                "id": paper_id,
                "retmode": "xml"
            }
            if self.api_key:
                params["api_key"] = self.api_key

            response = self.session.get(
                f"{self.BASE_URL}/efetch.fcgi",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)
            article = root.find('.//PubmedArticle')

            if article is not None:
                return self._parse_paper(article)
            return None

        except Exception as e:
            logger.error(f"Error getting PubMed paper details: {e}")
            return None

    def _parse_paper(self, article: ET.Element) -> ResearchPaper:
        """Parse PubMed XML article into ResearchPaper"""
        medline_citation = article.find('.//MedlineCitation')
        article_elem = medline_citation.find('.//Article')

        # Title
        title_elem = article_elem.find('.//ArticleTitle')
        title = title_elem.text if title_elem is not None else "Untitled"

        # Abstract
        abstract_elem = article_elem.find('.//Abstract/AbstractText')
        abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"

        # Authors
        authors = []
        author_list = article_elem.find('.//AuthorList')
        if author_list is not None:
            for author in author_list.findall('.//Author'):
                last_name = author.find('.//LastName')
                first_name = author.find('.//ForeName')
                if last_name is not None and first_name is not None:
                    authors.append(f"{first_name.text} {last_name.text}")
                elif last_name is not None:
                    authors.append(last_name.text)

        # Year
        pub_date = article_elem.find('.//PubDate')
        year = None
        if pub_date is not None:
            year_elem = pub_date.find('.//Year')
            year = int(year_elem.text) if year_elem is not None else None

        # PMID
        pmid_elem = medline_citation.find('.//PMID')
        pmid = pmid_elem.text if pmid_elem is not None else None

        # DOI
        doi = None
        article_id_list = article.find('.//PubmedData/ArticleIdList')
        if article_id_list is not None:
            for article_id in article_id_list.findall('.//ArticleId'):
                if article_id.get('IdType') == 'doi':
                    doi = article_id.text
                    break

        # Journal
        journal = article_elem.find('.//Journal/Title')
        publication = journal.text if journal is not None else "Unknown"

        # Keywords/MeSH terms
        keywords = []
        mesh_list = medline_citation.find('.//MeshHeadingList')
        if mesh_list is not None:
            for mesh in mesh_list.findall('.//MeshHeading/DescriptorName'):
                if mesh.text:
                    keywords.append(mesh.text)

        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None

        return ResearchPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            year=year,
            source=self.name,
            url=url,
            doi=doi,
            citation_count=0,
            publication=publication,
            keywords=keywords,
            references=[],
            pdf_url=None,
            peer_reviewed=True,  # PubMed primarily indexes peer-reviewed journals
            open_access=False,
            metadata={
                "pmid": pmid
            }
        )

    def requires_api_key(self) -> bool:
        return False

    def get_priority(self) -> int:
        return 7

    def get_rate_limit(self) -> Optional[int]:
        """With API key: 10/sec, without: 3/sec"""
        return 600 if self.api_key else 180  # requests per minute
