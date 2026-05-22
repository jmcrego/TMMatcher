"""Service statistics tracking for match requests."""

import threading
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Statistics:
    """Service statistics tracker for match requests."""
    
    # Request tracking
    total_requests: int = 0
    total_cache_hits: int = 0
    total_cache_misses: int = 0
    total_errors: int = 0
    
    # Performance tracking (in milliseconds)
    total_runtime_ms: float = 0.0
    min_runtime_ms: float = float('inf')
    max_runtime_ms: float = 0.0
    
    # Lock for thread-safe updates
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_request(self, runtime_ms: float, cached: bool, error: bool = False) -> None:
        """Record a request with its metrics."""
        with self._lock:
            self.total_requests += 1
            
            if error:
                self.total_errors += 1
            else:
                if cached:
                    self.total_cache_hits += 1
                else:
                    self.total_cache_misses += 1
                
                self.total_runtime_ms += runtime_ms
                self.min_runtime_ms = min(self.min_runtime_ms, runtime_ms)
                self.max_runtime_ms = max(self.max_runtime_ms, runtime_ms)

    def get_stats(self) -> dict:
        """Return current statistics as dict."""
        with self._lock:
            total_success = self.total_requests - self.total_errors
            cache_hit_rate = 0.0
            avg_runtime_ms = 0.0
            
            if total_success > 0:
                cache_hit_rate = (self.total_cache_hits / total_success) * 100
                avg_runtime_ms = self.total_runtime_ms / total_success
            
            return {
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "successful_requests": total_success,
                "cache_hits": self.total_cache_hits,
                "cache_misses": self.total_cache_misses,
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "average_runtime_ms": round(avg_runtime_ms, 2),
                "min_runtime_ms": round(self.min_runtime_ms, 2) if self.min_runtime_ms != float('inf') else 0.0,
                "max_runtime_ms": round(self.max_runtime_ms, 2),
            }

    def reset(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self.total_requests = 0
            self.total_cache_hits = 0
            self.total_cache_misses = 0
            self.total_errors = 0
            self.total_runtime_ms = 0.0
            self.min_runtime_ms = float('inf')
            self.max_runtime_ms = 0.0
