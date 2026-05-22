"""Cache backend implementations for search results."""

from abc import ABC, abstractmethod
from collections import OrderedDict
import hashlib
import threading
import json
from typing import Any, Optional

from . import shared


class CacheBackend(ABC):
    """Abstract cache backend interface."""

    @abstractmethod
    def get(self, sentence: str, indices: str) -> Optional[Any]:
        """Get cached result for sentence and indices."""
        pass

    @abstractmethod
    def set(self, sentence: str, indices: str, value: Any) -> None:
        """Store result in cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass

    @abstractmethod
    def stats(self) -> dict:
        """Return cache statistics."""
        pass


class LocalMemoryCache(CacheBackend):
    """In-memory LRU cache implementation for match results."""

    def __init__(self, max_size: int = 1000):
        """Initialize LRU cache with max size."""
        self.max_size = max_size
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.lock = threading.Lock()

    def _make_key(self, sentence: str, indices: str) -> str:
        """Create cache key from sentence and indices."""
        # Normalize indices list (sort for consistent keys)
        indices_list = sorted([i.strip() for i in indices.split(",")])
        indices_normalized = ",".join(indices_list)
        
        # Create hash of sentence and indices for key
        key_str = f"{sentence}:{indices_normalized}"
        text_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        return text_hash

    def get(self, sentence: str, indices: str) -> Optional[Any]:
        """Get cached result for sentence and indices."""
        key = self._make_key(sentence, indices)
        with self.lock:
            if key in self.cache:
                # Move to end (mark as recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
        return None

    def set(self, sentence: str, indices: str, value: Any) -> None:
        """Cache result with LRU eviction."""
        key = self._make_key(sentence, indices)
        with self.lock:
            if key in self.cache:
                # Update existing entry and mark as recently used
                self.cache.move_to_end(key)
                self.cache[key] = value
            else:
                # Add new entry
                self.cache[key] = value
                # Evict oldest entry if max size exceeded
                if len(self.cache) > self.max_size:
                    self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()

    def stats(self) -> dict:
        """Return cache statistics."""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
            }


class RedisCache(CacheBackend):
    """Redis-based cache implementation for distributed caching."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 3600):
        """Initialize Redis cache with TTL."""
        try:
            import redis
        except ImportError:
            raise ImportError("redis package required for RedisCache. Install with: pip install redis")

        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = ttl

    def _make_key(self, sentence: str, indices: str) -> str:
        """Create cache key from sentence and indices."""
        # Normalize indices list (sort for consistent keys)
        indices_list = sorted([i.strip() for i in indices.split(",")])
        indices_normalized = ",".join(indices_list)
        
        # Create hash of sentence and indices for key
        key_str = f"{sentence}:{indices_normalized}"
        text_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        return f"tm_match:{text_hash}"

    def get(self, sentence: str, indices: str) -> Optional[Any]:
        """Get cached result from Redis."""
        key = self._make_key(sentence, indices)
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    def set(self, sentence: str, indices: str, value: Any) -> None:
        """Cache result in Redis with TTL."""
        key = self._make_key(sentence, indices)
        try:
            self.client.setex(key, self.ttl, json.dumps(value, default=str))
        except Exception as e:
            print(f"Warning: Failed to cache in Redis: {e}")

    def clear(self) -> None:
        """Clear all cache entries."""
        self.client.flushdb()

    def stats(self) -> dict:
        """Return cache statistics."""
        try:
            info = self.client.info("memory")
            keys = self.client.dbsize()
            return {
                "size": keys,
                "max_size": "unlimited",
                "memory_usage_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2),
            }
        except Exception:
            return {
                "size": 0,
                "max_size": "unknown",
            }


def get_cache_backend(backend_type: str = "memory") -> CacheBackend:
    """Factory function to create cache backend."""
    if backend_type == "redis":
        return RedisCache()
    elif backend_type == "memory":
        return LocalMemoryCache(max_size=shared.CACHE_MAX_SIZE)
    else:
        raise ValueError(f"Unknown cache backend: {backend_type}")
