#!/usr/bin/env python3
"""
Test translation memory matching with queries.

Usage:
    python test_match.py [--query TEXT] [--indices NAMES] [--host HOST:PORT]

Examples:
    python test_match.py                                    # Use default query
    python test_match.py --query "hello world"              # Custom query
    python test_match.py --indices tm_enfr,tm_esen          # Specific indices
    python test_match.py --query "good morning" --indices sample_tm
    python test_match.py --host localhost:8000
"""

import sys
import argparse
import requests
from typing import List


def match_query(query: str, indices: List[str], host: str = "127.0.0.1", port: int = 8002):
    """Test matching query against indices."""
    
    endpoint = f"http://{host}:{port}/match"
    
    print("=" * 60)
    print("TMMatcher Match Query")
    print("=" * 60)
    print(f"Query: {query}")
    print(f"Indices: {', '.join(indices)}")
    print(f"Endpoint: {endpoint}\n")
    print("Searching...")
    
    try:
        payload = {
            "sentence": query,
            "indices": indices
        }
        
        response = requests.post(endpoint, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✓ Match successful (HTTP 200)\n")
            
            matches = result.get("matches", [])
            if matches:
                print("Results:")
                for i, match in enumerate(matches, 1):
                    print(f"\n  {i}. Index: {match['index']}")
                    print(f"     Source: {match['source']}")
                    print(f"     Target: {match['target']}")
                    print(f"     Score: {match['score']:.4f}")
            else:
                print("No matches found")
            
            cached = result.get("cached", False)
            runtime = result.get("runtime_ms", 0)
            print(f"\nRuntime: {runtime:.2f} ms")
            print(f"Cached: {cached}")
            print()
            
        else:
            print(f"\n✗ Match failed (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Cannot connect to {endpoint}")
        print("Make sure the service is running:")
        print(f"  uvicorn app.main:app --host {host} --port {port}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test matching queries in TMMatcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_match.py                                    # Default query
  python test_match.py --query "hello world"              # Custom query
  python test_match.py --indices sample_tm                # Specific index
  python test_match.py --query "good morning" --indices enfr,esen
  python test_match.py --host localhost:8000              # Custom server
        """
    )
    
    parser.add_argument("--query", "-q",
                       default="hello world",
                       help="Query string (default: 'hello world')")
    parser.add_argument("--indices", "-i",
                       default="sample_tm",
                       help="Comma-separated index names (default: sample_tm)")
    parser.add_argument("--host", "-H",
                       default="127.0.0.1:8002",
                       help="Server address (default: 127.0.0.1:8002)")
    
    args = parser.parse_args()
    
    # Parse indices
    indices_list = [idx.strip() for idx in args.indices.split(",")]
    
    # Parse host:port
    try:
        host, port_str = args.host.rsplit(":", 1)
        port = int(port_str)
    except (ValueError, IndexError):
        print(f"Invalid host format: {args.host}")
        print("Use: host:port (e.g., localhost:8000)")
        sys.exit(1)
    
    match_query(args.query, indices_list, host, port)
