#!/usr/bin/env python3
"""
Cache statistics and management utility for TMMatcher.

Usage:
    python scripts/cache_stats.py stats       - Show cache statistics (requires running server)
    python scripts/cache_stats.py clear       - Clear cache via API (requires running server)
    python scripts/cache_stats.py health      - Get full health check including stats

Examples:
    python scripts/cache_stats.py stats
    python scripts/cache_stats.py health
    python scripts/cache_stats.py clear
"""

import sys
import json
import requests
from typing import Optional


# Configuration
DEFAULT_HOST = "http://localhost:8002"


def get_health_stats(host: str = DEFAULT_HOST) -> Optional[dict]:
    """Fetch health stats from running server."""
    try:
        response = requests.get(f"{host}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to server at {host}")
        print("Make sure the server is running: uvicorn app.main:app --reload --port 8002")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching health stats: {e}")
        return None


def show_stats(host: str = DEFAULT_HOST) -> None:
    """Display cache and service statistics."""
    data = get_health_stats(host)
    if not data:
        return
    
    print("\n" + "=" * 70)
    print("SERVICE STATISTICS")
    print("=" * 70)
    
    if "statistics" in data:
        stats = data["statistics"]
        print(f"Total Requests:      {stats.get('total_requests', 0)}")
        print(f"Successful Requests: {stats.get('successful_requests', 0)}")
        print(f"Total Errors:        {stats.get('total_errors', 0)}")
        print(f"\nCache Performance:")
        print(f"  Cache Hits:        {stats.get('cache_hits', 0)}")
        print(f"  Cache Misses:      {stats.get('cache_misses', 0)}")
        print(f"  Hit Rate:          {stats.get('cache_hit_rate_percent', 0):.2f}%")
        print(f"\nRuntime Metrics (ms):")
        print(f"  Average:           {stats.get('average_runtime_ms', 0):.2f}")
        print(f"  Min:               {stats.get('min_runtime_ms', 0):.2f}")
        print(f"  Max:               {stats.get('max_runtime_ms', 0):.2f}")
    
    if "cache" in data:
        cache = data["cache"]
        print(f"\nCache Configuration:")
        print(f"  Enabled:           {cache.get('enabled', False)}")
        print(f"  Type:              {cache.get('type', 'N/A')}")
        print(f"  Current Size:      {cache.get('size', 0)}")
        print(f"  Max Size:          {cache.get('max_size', 0)}")
    
    if "indices" in data:
        print(f"\nLoaded Indices: {len(data['indices'])}")
        for idx in data["indices"]:
            print(f"  - {idx['name']}: {idx['size']} terms")
    
    print("=" * 70 + "\n")


def show_full_health(host: str = DEFAULT_HOST) -> None:
    """Display full health check response as JSON."""
    data = get_health_stats(host)
    if data:
        print(json.dumps(data, indent=2))


def clear_cache(host: str = DEFAULT_HOST) -> None:
    """Clear the cache by requesting cache clear (if implemented)."""
    print("Cache will be automatically cleared when indices are uploaded or removed.")
    print("To manually clear cache, restart the server.")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        show_stats()
    elif command == "health":
        show_full_health()
    elif command == "clear":
        clear_cache()
    elif command in ["-h", "--help", "help"]:
        print(__doc__)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
