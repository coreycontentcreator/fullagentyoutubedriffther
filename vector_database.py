"""
Vector Database for Viral YouTube Synthesis System
Stores research data, viral strategies, output data, and video analysis using OpenAI embeddings
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

try:
    from openai import OpenAI
except ImportError:
    print("Warning: OpenAI library not installed. Run: pip install openai")


class ContentType(Enum):
    """Types of content stored in the vector database"""
    RESEARCH = "research"
    VIRAL_STRATEGY = "viral_strategy"
    VIDEO_ANALYSIS = "video_analysis"
    OUTPUT_DATA = "output_data"
    HOOK = "hook"
    PSYCHOLOGY_TRIGGER = "psychology_trigger"
    SCRIPT = "script"
    PATTERN = "pattern"


class ViralTier(Enum):
    """Viral performance tiers based on engagement metrics"""
    GOLD = "gold"      # 1M+ views, 10%+ engagement, 60%+ retention
    SILVER = "silver"  # 500K+ views, 7%+ engagement, 50%+ retention
    BRONZE = "bronze"  # 100K+ views, 5%+ engagement, 40%+ retention
    PENDING = "pending"  # Not yet classified


@dataclass
class VectorEntry:
    """Single entry in the vector database"""
    id: str
    content: str
    content_type: ContentType
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: str
    viral_tier: Optional[ViralTier] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'content': self.content,
            'content_type': self.content_type.value,
            'embedding': self.embedding,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'viral_tier': self.viral_tier.value if self.viral_tier else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorEntry':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            content=data['content'],
            content_type=ContentType(data['content_type']),
            embedding=data['embedding'],
            metadata=data['metadata'],
            timestamp=data['timestamp'],
            viral_tier=ViralTier(data['viral_tier']) if data.get('viral_tier') else None
        )


class VectorDatabase:
    """
    Vector database for storing and retrieving viral content data using OpenAI embeddings.

    Stores:
    - Research data and citations
    - Viral strategies and patterns
    - YouTube video analysis
    - Output data (scripts, hooks, etc.)
    - Psychology trigger effectiveness
    - Retention patterns and engagement metrics
    """

    def __init__(self,
                 storage_path: str = "./data/vector_db",
                 openai_api_key: Optional[str] = None,
                 embedding_model: str = "text-embedding-3-large"):
        """
        Initialize the vector database.

        Args:
            storage_path: Directory to store database files
            openai_api_key: OpenAI API key for embeddings
            embedding_model: OpenAI embedding model to use
        """
        self.storage_path = storage_path
        self.embedding_model = embedding_model
        self.entries: List[VectorEntry] = []

        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            print("Warning: No OpenAI API key provided. Embeddings will not work.")

        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)

        # Load existing database
        self._load_database()

        print(f"✅ Vector Database initialized with {len(self.entries)} entries")

    def _generate_id(self, content: str, content_type: ContentType) -> str:
        """Generate unique ID for content"""
        hash_input = f"{content}{content_type.value}{datetime.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI API.

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide API key.")

        try:
            # Truncate text if too long (OpenAI has token limits)
            max_chars = 8000
            if len(text) > max_chars:
                text = text[:max_chars]

            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )

            return response.data[0].embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def add_entry(self,
                  content: str,
                  content_type: ContentType,
                  metadata: Dict[str, Any],
                  viral_tier: Optional[ViralTier] = None) -> str:
        """
        Add a new entry to the vector database.

        Args:
            content: The text content to store
            content_type: Type of content (research, viral strategy, etc.)
            metadata: Additional metadata about the content
            viral_tier: Optional viral performance tier

        Returns:
            ID of the created entry
        """
        # Generate embedding
        embedding = self._get_embedding(content)

        # Create entry
        entry = VectorEntry(
            id=self._generate_id(content, content_type),
            content=content,
            content_type=content_type,
            embedding=embedding,
            metadata=metadata,
            timestamp=datetime.now().isoformat(),
            viral_tier=viral_tier
        )

        # Add to database
        self.entries.append(entry)

        # Save database
        self._save_database()

        print(f"✅ Added {content_type.value} entry: {entry.id}")
        return entry.id

    def add_research_data(self,
                         research_content: str,
                         topic: str,
                         sources: List[str],
                         key_insights: List[str],
                         citations: List[Dict[str, str]]) -> str:
        """
        Add research data to the database.

        Args:
            research_content: The research text
            topic: Research topic
            sources: List of data sources (JSTOR, Semantic Scholar, etc.)
            key_insights: Key findings from research
            citations: List of citation information

        Returns:
            Entry ID
        """
        metadata = {
            'topic': topic,
            'sources': sources,
            'key_insights': key_insights,
            'citations': citations,
            'num_sources': len(sources),
            'num_citations': len(citations)
        }

        return self.add_entry(
            content=research_content,
            content_type=ContentType.RESEARCH,
            metadata=metadata
        )

    def add_viral_strategy(self,
                          strategy_content: str,
                          topic: str,
                          hooks: List[str],
                          psychology_triggers: List[str],
                          retention_strategy: str,
                          viral_score: float,
                          viral_tier: Optional[ViralTier] = None) -> str:
        """
        Add viral strategy to the database.

        Args:
            strategy_content: The strategy description
            topic: Strategy topic
            hooks: List of hook variations
            psychology_triggers: List of triggers used
            retention_strategy: Retention optimization approach
            viral_score: Predicted viral score (0-10)
            viral_tier: Performance tier

        Returns:
            Entry ID
        """
        metadata = {
            'topic': topic,
            'hooks': hooks,
            'num_hooks': len(hooks),
            'psychology_triggers': psychology_triggers,
            'num_triggers': len(psychology_triggers),
            'retention_strategy': retention_strategy,
            'viral_score': viral_score
        }

        return self.add_entry(
            content=strategy_content,
            content_type=ContentType.VIRAL_STRATEGY,
            metadata=metadata,
            viral_tier=viral_tier
        )

    def add_video_analysis(self,
                          analysis_content: str,
                          video_id: str,
                          video_url: str,
                          metrics: Dict[str, Any],
                          identified_triggers: List[str],
                          structure: Dict[str, Any],
                          viral_tier: ViralTier) -> str:
        """
        Add YouTube video analysis to the database.

        Args:
            analysis_content: Analysis text
            video_id: YouTube video ID
            video_url: Full video URL
            metrics: Video metrics (views, engagement, retention, etc.)
            identified_triggers: Psychology triggers found in video
            structure: Video structure breakdown
            viral_tier: Performance tier classification

        Returns:
            Entry ID
        """
        metadata = {
            'video_id': video_id,
            'video_url': video_url,
            'metrics': metrics,
            'views': metrics.get('views', 0),
            'engagement_rate': metrics.get('engagement_rate', 0),
            'retention_rate': metrics.get('retention_rate', 0),
            'identified_triggers': identified_triggers,
            'num_triggers': len(identified_triggers),
            'structure': structure
        }

        return self.add_entry(
            content=analysis_content,
            content_type=ContentType.VIDEO_ANALYSIS,
            metadata=metadata,
            viral_tier=viral_tier
        )

    def add_output_data(self,
                       output_content: str,
                       output_type: str,
                       topic: str,
                       quality_score: float,
                       production_ready: bool = True) -> str:
        """
        Add output data (scripts, final content) to the database.

        Args:
            output_content: The output content
            output_type: Type of output (script, visual_scenes, etc.)
            topic: Content topic
            quality_score: Quality score (0-10)
            production_ready: Whether content is production ready

        Returns:
            Entry ID
        """
        metadata = {
            'output_type': output_type,
            'topic': topic,
            'quality_score': quality_score,
            'production_ready': production_ready,
            'word_count': len(output_content.split())
        }

        return self.add_entry(
            content=output_content,
            content_type=ContentType.OUTPUT_DATA,
            metadata=metadata
        )

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        magnitude1 = np.linalg.norm(vec1_np)
        magnitude2 = np.linalg.norm(vec2_np)

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def search(self,
               query: str,
               content_type: Optional[ContentType] = None,
               viral_tier: Optional[ViralTier] = None,
               top_k: int = 10,
               min_similarity: float = 0.5) -> List[Tuple[VectorEntry, float]]:
        """
        Search for similar content in the database.

        Args:
            query: Search query text
            content_type: Filter by content type
            viral_tier: Filter by viral tier
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of (entry, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self._get_embedding(query)

        # Filter entries
        filtered_entries = self.entries
        if content_type:
            filtered_entries = [e for e in filtered_entries if e.content_type == content_type]
        if viral_tier:
            filtered_entries = [e for e in filtered_entries if e.viral_tier == viral_tier]

        # Calculate similarities
        results = []
        for entry in filtered_entries:
            similarity = self._cosine_similarity(query_embedding, entry.embedding)
            if similarity >= min_similarity:
                results.append((entry, similarity))

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def get_by_id(self, entry_id: str) -> Optional[VectorEntry]:
        """Get entry by ID"""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def get_by_tier(self, viral_tier: ViralTier) -> List[VectorEntry]:
        """Get all entries of a specific viral tier"""
        return [e for e in self.entries if e.viral_tier == viral_tier]

    def get_by_content_type(self, content_type: ContentType) -> List[VectorEntry]:
        """Get all entries of a specific content type"""
        return [e for e in self.entries if e.content_type == content_type]

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'total_entries': len(self.entries),
            'by_content_type': {},
            'by_viral_tier': {},
            'avg_viral_scores': []
        }

        # Count by content type
        for content_type in ContentType:
            count = len([e for e in self.entries if e.content_type == content_type])
            stats['by_content_type'][content_type.value] = count

        # Count by viral tier
        for tier in ViralTier:
            count = len([e for e in self.entries if e.viral_tier == tier])
            stats['by_viral_tier'][tier.value] = count

        # Average viral scores
        viral_strategies = self.get_by_content_type(ContentType.VIRAL_STRATEGY)
        if viral_strategies:
            scores = [e.metadata.get('viral_score', 0) for e in viral_strategies]
            stats['avg_viral_score'] = sum(scores) / len(scores) if scores else 0

        return stats

    def _save_database(self):
        """Save database to disk"""
        db_file = os.path.join(self.storage_path, "vector_db.json")

        data = {
            'version': '1.0',
            'embedding_model': self.embedding_model,
            'last_updated': datetime.now().isoformat(),
            'entries': [entry.to_dict() for entry in self.entries]
        }

        with open(db_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_database(self):
        """Load database from disk"""
        db_file = os.path.join(self.storage_path, "vector_db.json")

        if not os.path.exists(db_file):
            print("No existing database found. Starting fresh.")
            return

        try:
            with open(db_file, 'r') as f:
                data = json.load(f)

            self.entries = [VectorEntry.from_dict(e) for e in data.get('entries', [])]
            print(f"✅ Loaded {len(self.entries)} entries from database")

        except Exception as e:
            print(f"Error loading database: {e}")
            self.entries = []

    def delete_entry(self, entry_id: str) -> bool:
        """
        Delete an entry from the database.

        Args:
            entry_id: ID of entry to delete

        Returns:
            True if deleted, False if not found
        """
        for i, entry in enumerate(self.entries):
            if entry.id == entry_id:
                self.entries.pop(i)
                self._save_database()
                print(f"✅ Deleted entry: {entry_id}")
                return True

        print(f"❌ Entry not found: {entry_id}")
        return False

    def update_entry_metadata(self, entry_id: str, metadata_updates: Dict[str, Any]) -> bool:
        """
        Update metadata for an existing entry.

        Args:
            entry_id: ID of entry to update
            metadata_updates: Dictionary of metadata fields to update

        Returns:
            True if updated, False if not found
        """
        entry = self.get_by_id(entry_id)
        if entry:
            entry.metadata.update(metadata_updates)
            self._save_database()
            print(f"✅ Updated metadata for entry: {entry_id}")
            return True

        print(f"❌ Entry not found: {entry_id}")
        return False


if __name__ == "__main__":
    # Example usage
    print("Vector Database - Example Usage")
    print("=" * 50)

    # Initialize database
    db = VectorDatabase()

    # Example: Add research data
    research_id = db.add_research_data(
        research_content="Quantum computing represents a paradigm shift in computational power...",
        topic="Quantum Computing",
        sources=["JSTOR", "Semantic Scholar", "arXiv"],
        key_insights=["Quantum supremacy achieved", "New error correction methods"],
        citations=[{"title": "Quantum Computing Advances", "author": "Smith et al."}]
    )

    # Example: Add viral strategy
    strategy_id = db.add_viral_strategy(
        strategy_content="Hook: 'What if I told you computers could break all encryption in seconds?'",
        topic="Quantum Computing",
        hooks=["The encryption killer", "Breaking the unbreakable"],
        psychology_triggers=["Curiosity Gap", "Fear/Urgency", "Authority"],
        retention_strategy="Pattern interruption every 2 minutes",
        viral_score=9.2,
        viral_tier=ViralTier.GOLD
    )

    # Example: Search
    results = db.search("quantum computing encryption", top_k=5)
    print(f"\nSearch results: {len(results)} found")

    # Show statistics
    stats = db.get_statistics()
    print(f"\nDatabase statistics:")
    print(json.dumps(stats, indent=2))
