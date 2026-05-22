#!/usr/bin/env python3
"""
Upload a translation memory file to create/update an index.

Usage:
    python test_upload.py [--file FILE] [--name NAME] [--host HOST:PORT]

Examples:
    python test_upload.py                                    # Use sample_tm.tsv, name=sample_tm
    python test_upload.py --file /path/to/tm.tsv --name tm_enfr
    python test_upload.py --host localhost:8000
"""

import sys
import os
import argparse
import requests

def upload_tm(file_path: str, index_name: str, host: str = "127.0.0.1", port: int = 8002):
    """Upload a translation memory file to create an index."""
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        sys.exit(1)
    
    endpoint = f"http://{host}:{port}/upload"
    
    print("=" * 60)
    print("TMMatcher Upload")
    print("=" * 60)
    print(f"File: {file_path}")
    print(f"Index name: {index_name}")
    print(f"Endpoint: {endpoint}\n")
    print("Uploading...")
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {"name": index_name}
            response = requests.post(endpoint, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Upload successful (HTTP 200)")
            print(f"  Index: {result.get('index')}")
            print(f"  Status: {result.get('status')}")
            print(f"  Size: {result.get('size')} terms")
            print()
        else:
            print(f"\n✗ Upload failed (HTTP {response.status_code})")
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
        description="Upload a translation memory file to TMMatcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_upload.py                              # Use sample_tm.tsv
  python test_upload.py --file /path/to/tm.tsv      # Custom file
  python test_upload.py --name enfr                  # Custom index name
  python test_upload.py --host localhost:8000        # Custom server
        """
    )
    
    parser.add_argument("--file", "-f", 
                       default="sample_tm.tsv",
                       help="Path to TSV file (default: sample_tm.tsv)")
    parser.add_argument("--name", "-n",
                       help="Index name (default: filename without extension)")
    parser.add_argument("--host", "-H",
                       default="127.0.0.1:8002",
                       help="Server address (default: 127.0.0.1:8002)")
    
    args = parser.parse_args()
    
    # Default name to filename without extension
    if not args.name:
        args.name = os.path.splitext(os.path.basename(args.file))[0]
    
    # Parse host:port
    try:
        host, port_str = args.host.rsplit(":", 1)
        port = int(port_str)
    except (ValueError, IndexError):
        print(f"Invalid host format: {args.host}")
        print("Use: host:port (e.g., localhost:8000)")
        sys.exit(1)
    
    upload_tm(args.file, args.name, host, port)
