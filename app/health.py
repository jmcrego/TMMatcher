from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .shared import indices, indices_lock, CACHE_ENABLED, CACHE_BACKEND, CACHE_TYPE, stats

class TMHealthIndex(BaseModel):
    name: str
    size: int

class CacheStats(BaseModel):
    enabled: bool
    type: str
    size: Optional[int] = None
    max_size: Optional[int] = None

class ServiceStats(BaseModel):
    total_requests: int
    total_errors: int
    successful_requests: int
    cache_hits: int
    cache_misses: int
    cache_hit_rate_percent: float
    average_runtime_ms: float
    min_runtime_ms: float
    max_runtime_ms: float

class TMHealthResponse(BaseModel):
    indices: List[TMHealthIndex]
    cache: CacheStats
    statistics: ServiceStats

def health_endpoint() -> TMHealthResponse:
    """Return health status including indices, cache stats, and service statistics."""
    with indices_lock:
        indices_list = [TMHealthIndex(name=k, size=v["size"]) for k, v in indices.items()]
    
    # Get cache stats
    cache_size = None
    cache_max_size = None
    if CACHE_BACKEND and hasattr(CACHE_BACKEND, 'stats'):
        cache_stats_dict = CACHE_BACKEND.stats()
        cache_size = cache_stats_dict.get('size')
        cache_max_size = cache_stats_dict.get('max_size')
    
    cache_info = CacheStats(
        enabled=CACHE_ENABLED,
        type=CACHE_TYPE,
        size=cache_size,
        max_size=cache_max_size,
    )
    
    # Get service statistics
    stats_dict = stats.get_stats()
    service_stats = ServiceStats(**stats_dict)
    
    return TMHealthResponse(
        indices=indices_list,
        cache=cache_info,
        statistics=service_stats,
    )
