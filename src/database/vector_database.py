"""
Vector Database - Stores embeddings for viral strategies and patterns
Uses in-memory vectors with persistent storage
"""

import logging
import json
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ViralTier(Enum):
    """Viral content tier classification"""
    GOLD = "gold"        # 1M+ views, 10%+ engagement
    SILVER = "silver"    # 500K+ views, 7%+ engagement
    BRONZE = "bronze"    # 100K+ views, 5%+ engagement
    PROMISING = "promising"  # Potential but unproven


@dataclass
class VectorEntry:
    """Entry in the vector database"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    tier: ViralTier
    created_at: str
    updated_at: str
    tags: List[str]
    category: str


class VectorDatabase:
    """
    Vector database for storing and retrieving patterns, strategies, and insights
    Uses cosine similarity for retrieval
    """

    def __init__(self, storage_path: str = "data/vector_store"):
        """
        Initialize vector database

        Args:
            storage_path: Path to store vector data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.vectors: List[VectorEntry] = []
        self.index = {}  # id -> index mapping

        self._load_from_disk()

        logger.info(f"Vector Database initialized with {len(self.vectors)} entries")

    def add_entry(
        self,
        id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        tier: ViralTier = ViralTier.PROMISING,
        tags: Optional[List[str]] = None,
        category: str = "general"
    ) -> bool:
        """
        Add entry to vector database

        Args:
            id: Unique identifier
            content: Text content
            embedding: Vector embedding
            metadata: Additional metadata
            tier: Viral tier classification
            tags: Tags for categorization
            category: Content category

        Returns:
            True if added successfully
        """
        try:
            now = datetime.now().isoformat()

            # Check if exists
            if id in self.index:
                logger.warning(f"Entry {id} already exists, updating...")
                return self.update_entry(id, content, embedding, metadata, tier, tags)

            entry = VectorEntry(
                id=id,
                content=content,
                embedding=embedding,
                metadata=metadata,
                tier=tier,
                created_at=now,
                updated_at=now,
                tags=tags or [],
                category=category
            )

            self.vectors.append(entry)
            self.index[id] = len(self.vectors) - 1

            logger.info(f"Added entry {id} (tier: {tier.value}, category: {category})")
            return True

        except Exception as e:
            logger.error(f"Failed to add entry: {e}")
            return False

    def update_entry(
        self,
        id: str,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tier: Optional[ViralTier] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Update existing entry"""
        try:
            if id not in self.index:
                logger.error(f"Entry {id} not found")
                return False

            idx = self.index[id]
            entry = self.vectors[idx]

            if content:
                entry.content = content
            if embedding:
                entry.embedding = embedding
            if metadata:
                entry.metadata.update(metadata)
            if tier:
                entry.tier = tier
            if tags:
                entry.tags = tags

            entry.updated_at = datetime.now().isoformat()

            logger.info(f"Updated entry {id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update entry: {e}")
            return False

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        tier_filter: Optional[List[ViralTier]] = None,
        category_filter: Optional[str] = None,
        tag_filter: Optional[List[str]] = None,
        min_similarity: float = 0.0
    ) -> List[Tuple[VectorEntry, float]]:
        """
        Search for similar entries using cosine similarity

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            tier_filter: Filter by viral tier
            category_filter: Filter by category
            tag_filter: Filter by tags
            min_similarity: Minimum similarity threshold

        Returns:
            List of (entry, similarity_score) tuples
        """
        try:
            if not self.vectors:
                return []

            query_vec = np.array(query_embedding)
            results = []

            for entry in self.vectors:
                # Apply filters
                if tier_filter and entry.tier not in tier_filter:
                    continue
                if category_filter and entry.category != category_filter:
                    continue
                if tag_filter and not any(tag in entry.tags for tag in tag_filter):
                    continue

                # Calculate similarity
                entry_vec = np.array(entry.embedding)
                similarity = self._cosine_similarity(query_vec, entry_vec)

                if similarity >= min_similarity:
                    results.append((entry, similarity))

            # Sort by similarity and return top k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))
        except:
            return 0.0

    def get_by_id(self, id: str) -> Optional[VectorEntry]:
        """Get entry by ID"""
        if id in self.index:
            return self.vectors[self.index[id]]
        return None

    def get_by_tier(self, tier: ViralTier) -> List[VectorEntry]:
        """Get all entries of a specific tier"""
        return [entry for entry in self.vectors if entry.tier == tier]

    def get_by_category(self, category: str) -> List[VectorEntry]:
        """Get all entries in a category"""
        return [entry for entry in self.vectors if entry.category == category]

    def get_by_tags(self, tags: List[str], match_all: bool = False) -> List[VectorEntry]:
        """
        Get entries matching tags

        Args:
            tags: Tags to match
            match_all: If True, entry must have all tags; if False, any tag

        Returns:
            List of matching entries
        """
        results = []
        for entry in self.vectors:
            if match_all:
                if all(tag in entry.tags for tag in tags):
                    results.append(entry)
            else:
                if any(tag in entry.tags for tag in tags):
                    results.append(entry)
        return results

    def delete_entry(self, id: str) -> bool:
        """Delete entry by ID"""
        try:
            if id not in self.index:
                return False

            idx = self.index[id]
            del self.vectors[idx]

            # Rebuild index
            self.index = {
                entry.id: i
                for i, entry in enumerate(self.vectors)
            }

            logger.info(f"Deleted entry {id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete entry: {e}")
            return False

    def save_to_disk(self) -> bool:
        """Save vector database to disk"""
        try:
            # Save as pickle for efficient storage
            db_file = self.storage_path / "vectors.pkl"
            with open(db_file, 'wb') as f:
                pickle.dump({
                    'vectors': self.vectors,
                    'index': self.index
                }, f)

            # Also save as JSON for human readability (metadata only)
            metadata_file = self.storage_path / "metadata.json"
            metadata = {
                'count': len(self.vectors),
                'tiers': {
                    tier.value: len(self.get_by_tier(tier))
                    for tier in ViralTier
                },
                'categories': list(set(entry.category for entry in self.vectors)),
                'last_saved': datetime.now().isoformat()
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Saved {len(self.vectors)} entries to disk")
            return True

        except Exception as e:
            logger.error(f"Failed to save to disk: {e}")
            return False

    def _load_from_disk(self) -> bool:
        """Load vector database from disk"""
        try:
            db_file = self.storage_path / "vectors.pkl"
            if not db_file.exists():
                logger.info("No existing database found, starting fresh")
                return False

            with open(db_file, 'rb') as f:
                data = pickle.load(f)
                self.vectors = data.get('vectors', [])
                self.index = data.get('index', {})

            logger.info(f"Loaded {len(self.vectors)} entries from disk")
            return True

        except Exception as e:
            logger.error(f"Failed to load from disk: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        tier_counts = {
            tier.value: len(self.get_by_tier(tier))
            for tier in ViralTier
        }

        categories = {}
        for entry in self.vectors:
            categories[entry.category] = categories.get(entry.category, 0) + 1

        all_tags = []
        for entry in self.vectors:
            all_tags.extend(entry.tags)
        tag_counts = {tag: all_tags.count(tag) for tag in set(all_tags)}

        return {
            'total_entries': len(self.vectors),
            'tier_distribution': tier_counts,
            'category_distribution': categories,
            'tag_distribution': tag_counts,
            'storage_path': str(self.storage_path)
        }

    def clear(self) -> bool:
        """Clear all entries"""
        self.vectors = []
        self.index = {}
        logger.info("Database cleared")
        return True

    def export_to_json(self, output_path: str) -> bool:
        """Export database to JSON"""
        try:
            data = []
            for entry in self.vectors:
                entry_dict = {
                    'id': entry.id,
                    'content': entry.content,
                    'metadata': entry.metadata,
                    'tier': entry.tier.value,
                    'created_at': entry.created_at,
                    'updated_at': entry.updated_at,
                    'tags': entry.tags,
                    'category': entry.category,
                    # Exclude embedding for size
                    'embedding_size': len(entry.embedding)
                }
                data.append(entry_dict)

            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Exported {len(data)} entries to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
