#!/usr/bin/env python3
"""
Health check script - verifies service availability and displays status.

Usage:
    python test_health.py [HOST:PORT]

Examples:
    python test_health.py                      # Default: localhost:8002
    python test_health.py localhost:8000
    python test_health.py 127.0.0.1:8002
"""

import sys
import requests
import json

def check_health(host: str = "127.0.0.1", port: int = 8002):
    """Check service health status."""
    endpoint = f"http://{host}:{port}/health"
    
    print("=" * 60)
    print("TMMatcher Health Check")
    print("=" * 60)
    print(f"Endpoint: {endpoint}\n")
    
    try:
        response = requests.get(endpoint, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✓ Service is healthy (HTTP 200)\n")
            
            # Indices
            print("Loaded Indices:")
            if data.get("indices"):
                for idx in data["indices"]:
                    print(f"  - {idx['name']}: {idx['size']} terms")
            else:
                print("  (none)")
            
            # Cache status
            cache = data.get("cache", {})
            print(f"\nCache Status:")
            print(f"  Enabled: {cache.get('enabled', 'N/A')}")
            print(f"  Type: {cache.get('type', 'N/A')}")
            print(f"  Current size: {cache.get('size', 'N/A')}")
            print(f"  Max size: {cache.get('max_size', 'N/A')}")
            
            # Statistics
            stats = data.get("statistics", {})
            print(f"\nService Statistics:")
            print(f"  Total requests: {stats.get('total_requests', 0)}")
            print(f"  Successful: {stats.get('successful_requests', 0)}")
            print(f"  Errors: {stats.get('total_errors', 0)}")
            print(f"  Cache hits: {stats.get('cache_hits', 0)}")
            print(f"  Cache misses: {stats.get('cache_misses', 0)}")
            print(f"  Cache hit rate: {stats.get('cache_hit_rate_percent', 0):.2f}%")
            print(f"  Avg runtime: {stats.get('average_runtime_ms', 0):.2f} ms")
            
            print()
            
        else:
            print(f"✗ Service unhealthy (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {endpoint}")
        print("Make sure the service is running:")
        print(f"  uvicorn app.main:app --host {host} --port {port}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8002
    
    if len(sys.argv) > 1:
        try:
            host, port_str = sys.argv[1].rsplit(":", 1)
            port = int(port_str)
        except (ValueError, IndexError):
            print(f"Invalid format: {sys.argv[1]}")
            print("Use: host:port (e.g., localhost:8000)")
            sys.exit(1)
    
    check_health(host, port)
