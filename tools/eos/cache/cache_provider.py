"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Cache Provider - Institutional In-Memory Cache Backing Store (FG164).
    Provides thread-safe, high-performance in-memory caching with Time-To-Live (TTL)
    and capacity eviction policies for cross-engine operations.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional storage and retrieval. Preserving resources.
    John 6:12 - "And when they had eaten their fill, he told his disciples, 'Gather up the leftover fragments, that nothing may be lost.'"

Collaboration & Maintenance:
    - [Architecture]: Thread-safe in-memory cache backend with expiration and statistics.
    - [Compliance]: Safe multi-threaded concurrency and clean resource management.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("WilsyOS.CacheProvider")


class CacheEntry:
    """Represents a cached value with expiration tracking."""
    def __init__(self, value: Any, ttl_seconds: Optional[float] = None) -> None:
        self.value = value
        self.created_at = time.time()
        self.expires_at = (self.created_at + ttl_seconds) if ttl_seconds is not None else None

    def is_expired(self) -> bool:
        """Returns True if the cache entry has exceeded its TTL."""
        if self.expires_at is None:
            return False
        return time.time() >= self.expires_at


class CacheProvider:
    """
    Institutional thread-safe cache provider managing in-memory key-value storage
    with expiration (TTL) and telemetry hits/misses.
    """

    def __init__(self, max_capacity: int = 10000) -> None:
        """Initializes the cache provider with capacity limits and thread locking."""
        self._cache: Dict[str, CacheEntry] = {}
        self._max_capacity = max_capacity
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    # [FUNCTION EXPLANATION]: Stores a value in the cache with an optional TTL.
    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """
        Sets a key-value pair in the cache.

        Args:
            key (str): The cache key.
            value (Any): The data to cache.
            ttl_seconds (Optional[float]): Time-to-live in seconds before expiration.
        """
        with self._lock:
            # Evict oldest or check capacity if full
            if len(self._cache) >= self._max_capacity and key not in self._cache:
                # Evict first expired or arbitrary item
                expired_keys = [k for k, entry in self._cache.items() if entry.is_expired()]
                if expired_keys:
                    for ek in expired_keys:
                        del self._cache[ek]
                elif self._cache:
                    # Pop first key inserted (approximate FIFO eviction)
                    first_key = next(iter(self._cache))
                    del self._cache[first_key]

            self._cache[key] = CacheEntry(value, ttl_seconds)
        logger.debug(f"Cache SET: [{key}]")

    # [FUNCTION EXPLANATION]: Retrieves a cached value by key, validating expiration.
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a cached value, returning None if missing or expired.

        Args:
            key (str): The cache key.

        Returns:
            Optional[Any]: The cached value or None.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache EXPIRED & EVICTED: [{key}]")
                return None

            self._hits += 1
            logger.debug(f"Cache HIT: [{key}]")
            return entry.value

    # [FUNCTION EXPLANATION]: Invalidates and removes a cache entry.
    def invalidate(self, key: str) -> None:
        """Removes a key from the cache if present."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache INVALIDATED: [{key}]")

    # [FUNCTION EXPLANATION]: Clears the entire cache store.
    def clear(self) -> None:
        """Clears all cached items and resets metrics."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
        logger.info("Cache provider cleared.")

    # [FUNCTION EXPLANATION]: Returns cache performance statistics and hit rates.
    def get_stats(self) -> Dict[str, Any]:
        """Returns diagnostic metrics including hits, misses, and hit ratio."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_ratio = (self._hits / total_requests * 100.0) if total_requests > 0 else 0.0
            return {
                "total_items": len(self._cache),
                "max_capacity": self._max_capacity,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio_percent": round(hit_ratio, 2),
            }
