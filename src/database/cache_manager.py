"""
Cache Manager - Caches API responses and computations
"""

import logging
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entry in the cache"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    hits: int
    metadata: Dict[str, Any]


class CacheManager:
    """
    Manages caching of API responses and expensive computations
    """

    def __init__(
        self,
        storage_path: str = "data/cache",
        default_ttl: int = 3600,  # 1 hour
        max_size: int = 1000
    ):
        """
        Initialize cache manager

        Args:
            storage_path: Path to store cache
            default_ttl: Default time-to-live in seconds
            max_size: Maximum cache entries
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.default_ttl = default_ttl
        self.max_size = max_size

        self.cache: Dict[str, CacheEntry] = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }

        self._load_from_disk()

        logger.info(f"Cache Manager initialized: {len(self.cache)} entries")

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.stats['misses'] += 1
            return None

        entry = self.cache[key]

        # Check expiration
        if entry.expires_at and time.time() > entry.expires_at:
            del self.cache[key]
            self.stats['misses'] += 1
            return None

        # Update hits
        entry.hits += 1
        self.stats['hits'] += 1

        logger.debug(f"Cache hit: {key}")
        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiration)
            metadata: Optional metadata

        Returns:
            True if set successfully
        """
        try:
            # Check if we need to evict
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()

            now = time.time()
            expires_at = now + (ttl or self.default_ttl) if ttl is not None or self.default_ttl else None

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=expires_at,
                hits=0,
                metadata=metadata or {}
            )

            self.cache[key] = entry
            logger.debug(f"Cache set: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True
        return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        self.cache = {}
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
        logger.info("Cache cleared")
        return True

    def _evict_lru(self) -> bool:
        """Evict least recently used entry"""
        if not self.cache:
            return False

        # Find entry with lowest hits and oldest creation time
        lru_key = min(
            self.cache.keys(),
            key=lambda k: (self.cache[k].hits, self.cache[k].created_at)
        )

        del self.cache[lru_key]
        self.stats['evictions'] += 1
        logger.debug(f"Evicted LRU entry: {lru_key}")
        return True

    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        now = time.time()
        expired = [
            key for key, entry in self.cache.items()
            if entry.expires_at and entry.expires_at < now
        ]

        for key in expired:
            del self.cache[key]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired entries")

        return len(expired)

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get from cache or compute if not present

        Args:
            key: Cache key
            compute_fn: Function to compute value if not cached
            ttl: Time-to-live

        Returns:
            Cached or computed value
        """
        # Try cache first
        value = self.get(key)
        if value is not None:
            return value

        # Compute and cache
        value = compute_fn()
        self.set(key, value, ttl)
        return value

    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """
        Generate cache key from arguments

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Hash-based cache key
        """
        # Create a deterministic string from args
        key_str = json.dumps({
            'args': args,
            'kwargs': kwargs
        }, sort_keys=True)

        # Generate hash
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'entries': len(self.cache),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'evictions': self.stats['evictions'],
            'hit_rate': f"{hit_rate:.1f}%",
            'max_size': self.max_size,
            'default_ttl': self.default_ttl
        }

    def save_to_disk(self) -> bool:
        """Save cache to disk"""
        try:
            # Only save non-expired entries
            self.cleanup_expired()

            cache_file = self.storage_path / "cache.json"

            # Prepare serializable data
            data = {
                'entries': {
                    key: {
                        'value': entry.value,
                        'created_at': entry.created_at,
                        'expires_at': entry.expires_at,
                        'hits': entry.hits,
                        'metadata': entry.metadata
                    }
                    for key, entry in self.cache.items()
                },
                'stats': self.stats
            }

            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved cache: {len(self.cache)} entries")
            return True

        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            return False

    def _load_from_disk(self) -> bool:
        """Load cache from disk"""
        try:
            cache_file = self.storage_path / "cache.json"
            if not cache_file.exists():
                logger.info("No existing cache found")
                return False

            with open(cache_file, 'r') as f:
                data = json.load(f)

            # Reconstruct cache entries
            for key, entry_data in data.get('entries', {}).items():
                entry = CacheEntry(
                    key=key,
                    value=entry_data['value'],
                    created_at=entry_data['created_at'],
                    expires_at=entry_data.get('expires_at'),
                    hits=entry_data.get('hits', 0),
                    metadata=entry_data.get('metadata', {})
                )
                self.cache[key] = entry

            self.stats = data.get('stats', self.stats)

            # Cleanup expired
            self.cleanup_expired()

            logger.info(f"Loaded cache from disk")
            return True

        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return False
