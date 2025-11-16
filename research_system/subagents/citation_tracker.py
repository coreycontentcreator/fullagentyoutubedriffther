"""
Citation Tracker Subagent
Tracks and validates all research sources and citations
"""

from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..sources.base_source import ResearchPaper

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """Represents a single citation"""
    paper_id: str
    title: str
    authors: List[str]
    year: Optional[int]
    source: str
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_context: Optional[str] = None  # Where/how it's cited
    accessed_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'year': self.year,
            'source': self.source,
            'doi': self.doi,
            'url': self.url,
            'citation_context': self.citation_context,
            'accessed_date': self.accessed_date.isoformat()
        }

    def format_apa(self) -> str:
        """Format citation in APA style"""
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."

        year_str = f"({self.year})" if self.year else "(n.d.)"

        return f"{authors_str} {year_str}. {self.title}. {self.source}."

    def format_mla(self) -> str:
        """Format citation in MLA style"""
        if not self.authors:
            return f'"{self.title}." {self.source}, {self.year or "n.d."}.'

        authors_str = self.authors[0]
        if len(self.authors) > 1:
            authors_str += ", et al."

        return f'{authors_str}. "{self.title}." {self.source}, {self.year or "n.d."}.'


class CitationTracker:
    """
    Citation Tracker Subagent
    Manages all citations and references used in research
    """

    def __init__(self):
        """Initialize citation tracker"""
        self.citations: Dict[str, Citation] = {}
        self.citation_network: Dict[str, Set[str]] = {}  # paper_id -> set of cited paper_ids
        self.paper_to_citations: Dict[str, List[str]] = {}  # Maps papers to their citations

        logger.info("Citation Tracker initialized")

    def add_paper_citations(self, paper: ResearchPaper) -> None:
        """
        Track all citations from a research paper

        Args:
            paper: Research paper to track citations from
        """
        paper_id = self._get_paper_id(paper)

        # Create citation for the paper itself
        citation = Citation(
            paper_id=paper_id,
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            source=paper.source,
            doi=paper.doi,
            url=paper.url
        )

        self.citations[paper_id] = citation

        # Track references if available
        if paper.references:
            if paper_id not in self.citation_network:
                self.citation_network[paper_id] = set()
            self.citation_network[paper_id].update(paper.references)

        logger.debug(f"Added citation: {paper.title[:50]}...")

    def add_papers_bulk(self, papers: List[ResearchPaper]) -> None:
        """
        Add multiple papers at once

        Args:
            papers: List of research papers
        """
        for paper in papers:
            self.add_paper_citations(paper)

        logger.info(f"Added {len(papers)} papers to citation tracker")

    def get_citation(self, paper_id: str) -> Optional[Citation]:
        """
        Get citation by paper ID

        Args:
            paper_id: Paper identifier

        Returns:
            Citation or None
        """
        return self.citations.get(paper_id)

    def get_all_citations(self) -> List[Citation]:
        """
        Get all tracked citations

        Returns:
            List of all citations
        """
        return list(self.citations.values())

    def get_citations_by_source(self, source: str) -> List[Citation]:
        """
        Get citations from a specific source

        Args:
            source: Source name

        Returns:
            List of citations from that source
        """
        return [c for c in self.citations.values()
                if c.source.lower() == source.lower()]

    def get_citations_by_year(self, year_from: Optional[int] = None,
                            year_to: Optional[int] = None) -> List[Citation]:
        """
        Get citations within a year range

        Args:
            year_from: Start year (inclusive)
            year_to: End year (inclusive)

        Returns:
            List of citations in range
        """
        citations = []
        for citation in self.citations.values():
            if citation.year is None:
                continue

            if year_from and citation.year < year_from:
                continue
            if year_to and citation.year > year_to:
                continue

            citations.append(citation)

        return citations

    def get_citation_network(self, paper_id: str, depth: int = 1) -> Set[str]:
        """
        Get citation network for a paper

        Args:
            paper_id: Paper identifier
            depth: Network depth to retrieve

        Returns:
            Set of related paper IDs
        """
        if depth == 0 or paper_id not in self.citation_network:
            return set()

        network = set(self.citation_network[paper_id])

        if depth > 1:
            for cited_id in list(network):
                network.update(self.get_citation_network(cited_id, depth - 1))

        return network

    def validate_citations(self) -> Dict[str, Any]:
        """
        Validate all citations for completeness and accuracy

        Returns:
            Validation report
        """
        total = len(self.citations)
        complete = 0
        missing_doi = 0
        missing_year = 0
        missing_authors = 0

        for citation in self.citations.values():
            is_complete = True

            if not citation.doi:
                missing_doi += 1
                is_complete = False

            if not citation.year:
                missing_year += 1
                is_complete = False

            if not citation.authors:
                missing_authors += 1
                is_complete = False

            if is_complete:
                complete += 1

        return {
            'total_citations': total,
            'complete_citations': complete,
            'completeness_rate': complete / max(total, 1),
            'missing_doi': missing_doi,
            'missing_year': missing_year,
            'missing_authors': missing_authors
        }

    def generate_bibliography(self, format: str = "apa") -> List[str]:
        """
        Generate formatted bibliography

        Args:
            format: Citation format ("apa", "mla", "chicago")

        Returns:
            List of formatted citations
        """
        citations = sorted(
            self.citations.values(),
            key=lambda c: (c.authors[0] if c.authors else "", c.year or 0)
        )

        if format.lower() == "apa":
            return [c.format_apa() for c in citations]
        elif format.lower() == "mla":
            return [c.format_mla() for c in citations]
        else:
            return [c.format_apa() for c in citations]  # Default to APA

    def get_source_distribution(self) -> Dict[str, int]:
        """
        Get distribution of citations by source

        Returns:
            Dictionary mapping sources to citation counts
        """
        distribution = {}
        for citation in self.citations.values():
            source = citation.source
            distribution[source] = distribution.get(source, 0) + 1

        return distribution

    def get_temporal_distribution(self) -> Dict[int, int]:
        """
        Get distribution of citations by year

        Returns:
            Dictionary mapping years to citation counts
        """
        distribution = {}
        for citation in self.citations.values():
            if citation.year:
                distribution[citation.year] = distribution.get(citation.year, 0) + 1

        return distribution

    def export_citations(self, format: str = "bibtex") -> str:
        """
        Export citations in specified format

        Args:
            format: Export format ("bibtex", "json", "csv")

        Returns:
            Formatted citation data
        """
        if format == "json":
            import json
            return json.dumps([c.to_dict() for c in self.citations.values()], indent=2)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            if self.citations:
                fieldnames = list(list(self.citations.values())[0].to_dict().keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for citation in self.citations.values():
                    writer.writerow(citation.to_dict())
            return output.getvalue()
        else:  # bibtex
            return self._export_bibtex()

    def _export_bibtex(self) -> str:
        """Export citations in BibTeX format"""
        entries = []
        for i, citation in enumerate(self.citations.values(), 1):
            authors = " and ".join(citation.authors)
            entry = f"""@article{{ref{i},
  title={{{citation.title}}},
  author={{{authors}}},
  year={{{citation.year or ""}}}"""

            if citation.doi:
                entry += f",\n  doi={{{citation.doi}}}"
            if citation.url:
                entry += f",\n  url={{{citation.url}}}"

            entry += "\n}"
            entries.append(entry)

        return "\n\n".join(entries)

    def _get_paper_id(self, paper: ResearchPaper) -> str:
        """Generate unique paper ID"""
        if paper.doi:
            return f"doi:{paper.doi}"
        elif paper.metadata.get('arxiv_id'):
            return f"arxiv:{paper.metadata['arxiv_id']}"
        elif paper.metadata.get('pmid'):
            return f"pmid:{paper.metadata['pmid']}"
        else:
            # Fallback to title-based ID
            import hashlib
            title_hash = hashlib.md5(paper.title.encode()).hexdigest()[:8]
            return f"paper:{title_hash}"

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics

        Returns:
            Statistics dictionary
        """
        return {
            'total_citations': len(self.citations),
            'source_distribution': self.get_source_distribution(),
            'temporal_distribution': self.get_temporal_distribution(),
            'validation': self.validate_citations(),
            'citation_network_size': len(self.citation_network)
        }

    def __len__(self) -> int:
        """Get number of tracked citations"""
        return len(self.citations)

    def __repr__(self) -> str:
        """String representation"""
        return f"CitationTracker({len(self.citations)} citations tracked)"
