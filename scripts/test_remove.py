#!/usr/bin/env python3
"""
Remove a translation memory index.

Usage:
    python test_remove.py [--index NAME] [--host HOST:PORT]

Examples:
    python test_remove.py                          # Default: sample_tm
    python test_remove.py --index tm_enfr
    python test_remove.py --index tm_esen --host localhost:8000
"""

import sys
import argparse
import requests


def remove_index(index_name: str, host: str = "127.0.0.1", port: int = 8002):
    """Remove an index from the service."""
    
    endpoint = f"http://{host}:{port}/remove"
    
    print("=" * 60)
    print("TMMatcher Remove Index")
    print("=" * 60)
    print(f"Index: {index_name}")
    print(f"Endpoint: {endpoint}\n")
    print("Removing...")
    
    try:
        payload = {"index": index_name}
        response = requests.post(endpoint, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Remove successful (HTTP 200)")
            print(f"  Status: {result.get('status')}")
            print(f"  Index: {result.get('index')}")
            print()
        else:
            print(f"\n✗ Remove failed (HTTP {response.status_code})")
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
        description="Remove an index from TMMatcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_remove.py                              # Default: sample_tm
  python test_remove.py --index tm_enfr              # Specific index
  python test_remove.py --index sample_tm --host localhost:8000
        """
    )
    
    parser.add_argument("--index", "-i",
                       default="sample_tm",
                       help="Index name to remove (default: sample_tm)")
    parser.add_argument("--host", "-H",
                       default="127.0.0.1:8002",
                       help="Server address (default: 127.0.0.1:8002)")
    
    args = parser.parse_args()
    
    # Parse host:port
    try:
        host, port_str = args.host.rsplit(":", 1)
        port = int(port_str)
    except (ValueError, IndexError):
        print(f"Invalid host format: {args.host}")
        print("Use: host:port (e.g., localhost:8000)")
        sys.exit(1)
    
    remove_index(args.index, host, port)
