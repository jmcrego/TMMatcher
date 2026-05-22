#!/usr/bin/env python3
"""
Cache statistics and management utility for TMMatcher.

Usage:
    python cache_stats.py [stats|clear]

Examples:
    python cache_stats.py stats     # Show cache statistics
    python cache_stats.py clear     # Clear cache
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import shared
from app.cache import get_cache_backend


def show_stats():
    """Display cache statistics."""
    if not shared.CACHE_ENABLED:
        print("Cache is disabled (TM_CACHE_ENABLED=false)")
        return
    
    cache = get_cache_backend(shared.CACHE_TYPE)
    
    print("=" * 50)
    print("TMMatcher Cache Statistics")
    print("=" * 50)
    print()
    print(f"Cache Backend: {shared.CACHE_TYPE}")
    print(f"Cache Enabled: {shared.CACHE_ENABLED}")
    print(f"Max Cache Size: {shared.CACHE_MAX_SIZE} entries")
    print()
    
    if hasattr(cache, 'stats'):
        cache_stats = cache.stats()
        print("Cache Status:")
        print(f"  Current entries: {cache_stats.get('size', 'N/A')}")
        print(f"  Max entries: {cache_stats.get('max_size', 'N/A')}")
        
        if 'memory_usage_mb' in cache_stats:
            print(f"  Memory usage: {cache_stats.get('memory_usage_mb', 'N/A')} MB")
    else:
        print("Cache stats not available for this backend")
    
    print()
    print("Service Statistics:")
    stats_dict = shared.stats.get_stats()
    print(f"  Total requests: {stats_dict['total_requests']}")
    print(f"  Successful requests: {stats_dict['successful_requests']}")
    print(f"  Errors: {stats_dict['total_errors']}")
    print(f"  Cache hits: {stats_dict['cache_hits']}")
    print(f"  Cache misses: {stats_dict['cache_misses']}")
    print(f"  Cache hit rate: {stats_dict['cache_hit_rate_percent']:.2f}%")
    print(f"  Average runtime: {stats_dict['average_runtime_ms']:.2f} ms")
    print(f"  Min runtime: {stats_dict['min_runtime_ms']:.2f} ms")
    print(f"  Max runtime: {stats_dict['max_runtime_ms']:.2f} ms")
    print()


def clear_cache():
    """Clear all cache entries."""
    if not shared.CACHE_ENABLED:
        print("Cache is disabled (TM_CACHE_ENABLED=false)")
        return
    
    cache = get_cache_backend(shared.CACHE_TYPE)
    cache.clear()
    print(f"✓ Cache cleared ({shared.CACHE_TYPE})")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        show_stats()
    elif command == "clear":
        clear_cache()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
