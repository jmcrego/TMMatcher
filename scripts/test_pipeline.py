#!/usr/bin/env python3
"""
End-to-end pipeline demonstration of TMMatcher functionality.

This script demonstrates:
1. Health check
2. Upload sample translation memories
3. Perform matching queries
4. View cache statistics
5. Clean up (optional)

Usage:
    python test_pipeline.py [--host HOST:PORT] [--cleanup]

Examples:
    python test_pipeline.py                    # Full demo, no cleanup
    python test_pipeline.py --cleanup          # Full demo with cleanup
    python test_pipeline.py --host localhost:8000
"""

import sys
import os
import argparse
import requests
import time


class TMMatcherDemo:
    def __init__(self, host: str = "127.0.0.1", port: int = 8002):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def check_health(self) -> bool:
        """Step 1: Check service health."""
        self.print_header("Step 1: Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✓ Service is healthy\n")
                
                indices = data.get("indices", [])
                print(f"  Loaded indices: {len(indices)}")
                for idx in indices:
                    print(f"    - {idx['name']}: {idx['size']} terms")
                
                stats = data.get("statistics", {})
                print(f"\n  Service statistics:")
                print(f"    Total requests: {stats.get('total_requests', 0)}")
                print(f"    Cache hits: {stats.get('cache_hits', 0)}")
                print(f"    Cache hit rate: {stats.get('cache_hit_rate_percent', 0):.2f}%")
                
                return True
            else:
                print(f"✗ Service unhealthy (HTTP {response.status_code})")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def upload_sample_tm(self) -> bool:
        """Step 2: Upload sample translation memory."""
        self.print_header("Step 2: Upload Sample Translation Memory")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "sample_tm.tsv")
        
        if not os.path.exists(file_path):
            print(f"✗ Sample file not found: {file_path}")
            return False
        
        print(f"Uploading: {file_path}")
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                data = {"name": "sample_tm"}
                response = requests.post(
                    f"{self.base_url}/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Upload successful\n")
                print(f"  Index: {result.get('index')}")
                print(f"  Size: {result.get('size')} terms")
                return True
            else:
                print(f"✗ Upload failed (HTTP {response.status_code})")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def perform_matches(self) -> bool:
        """Step 3: Perform matching queries."""
        self.print_header("Step 3: Perform Matching Queries")
        
        queries = [
            "hello world",
            "good morning",
            "thank you",
            "weather beach",
        ]
        
        try:
            for i, query in enumerate(queries, 1):
                print(f"\n  Query {i}: '{query}'")
                payload = {"sentence": query, "indices": ["sample_tm"]}
                response = requests.post(
                    f"{self.base_url}/match",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    matches = result.get("matches", [])
                    runtime = result.get("runtime_ms", 0)
                    cached = result.get("cached", False)
                    
                    if matches:
                        print(f"    ✓ Found {len(matches)} match(es)")
                        print(f"      Best match: '{matches[0]['source']}' → '{matches[0]['target']}'")
                        print(f"      Score: {matches[0]['score']:.4f}")
                    else:
                        print(f"    ✗ No matches found")
                    
                    print(f"    Runtime: {runtime:.2f} ms | Cached: {cached}")
                else:
                    print(f"    ✗ Match failed (HTTP {response.status_code})")
            
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def test_cache(self) -> bool:
        """Step 4: Test cache functionality."""
        self.print_header("Step 4: Test Cache Functionality")
        
        query = "hello world"
        print(f"Testing cache with repeated query: '{query}'\n")
        
        try:
            # First query (not cached)
            print("  1st query (should not be cached):")
            payload = {"sentence": query, "indices": ["sample_tm"]}
            response = requests.post(f"{self.base_url}/match", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                runtime1 = result.get("runtime_ms", 0)
                cached1 = result.get("cached", False)
                print(f"     Runtime: {runtime1:.2f} ms | Cached: {cached1}")
            else:
                print(f"     ✗ Error (HTTP {response.status_code})")
                return False
            
            time.sleep(0.1)
            
            # Second query (should be cached)
            print("\n  2nd query (should be cached):")
            response = requests.post(f"{self.base_url}/match", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                runtime2 = result.get("runtime_ms", 0)
                cached2 = result.get("cached", False)
                print(f"     Runtime: {runtime2:.2f} ms | Cached: {cached2}")
                
                if cached2:
                    print(f"\n  ✓ Cache is working!")
                    speedup = runtime1 / runtime2 if runtime2 > 0 else 0
                    if speedup > 1:
                        print(f"    Speedup: {speedup:.1f}x faster")
                else:
                    print(f"\n  ⚠ Cache not used (check if cache is enabled)")
            else:
                print(f"     ✗ Error (HTTP {response.status_code})")
                return False
            
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def view_statistics(self) -> bool:
        """Step 5: View final statistics."""
        self.print_header("Step 5: Final Statistics")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                stats = data.get("statistics", {})
                cache = data.get("cache", {})
                
                print("Service Statistics:")
                print(f"  Total requests: {stats.get('total_requests', 0)}")
                print(f"  Successful: {stats.get('successful_requests', 0)}")
                print(f"  Errors: {stats.get('total_errors', 0)}")
                print(f"  Cache hits: {stats.get('cache_hits', 0)}")
                print(f"  Cache misses: {stats.get('cache_misses', 0)}")
                print(f"  Cache hit rate: {stats.get('cache_hit_rate_percent', 0):.2f}%")
                print(f"  Avg runtime: {stats.get('average_runtime_ms', 0):.2f} ms")
                
                print(f"\nCache Status:")
                print(f"  Enabled: {cache.get('enabled', 'N/A')}")
                print(f"  Type: {cache.get('type', 'N/A')}")
                print(f"  Current size: {cache.get('size', 'N/A')}")
                print(f"  Max size: {cache.get('max_size', 'N/A')}")
                
                return True
            else:
                print(f"✗ Failed to get statistics (HTTP {response.status_code})")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Step 6 (optional): Clean up by removing the sample index."""
        self.print_header("Step 6: Cleanup")
        
        try:
            payload = {"index": "sample_tm"}
            response = requests.post(f"{self.base_url}/remove", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Cleanup successful")
                print(f"  Removed index: {result.get('index')}")
                return True
            else:
                print(f"✗ Cleanup failed (HTTP {response.status_code})")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def run(self, cleanup: bool = False):
        """Run the full demonstration pipeline."""
        print("\n" + "🎬 TMMatcher End-to-End Demo")
        print(f"Target: {self.base_url}")
        
        steps = [
            ("Health Check", self.check_health),
            ("Upload Sample TM", self.upload_sample_tm),
            ("Perform Matches", self.perform_matches),
            ("Test Cache", self.test_cache),
            ("View Statistics", self.view_statistics),
        ]
        
        passed = 0
        failed = 0
        
        for step_name, step_func in steps:
            try:
                if step_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"\n✗ Unexpected error in {step_name}: {e}")
                failed += 1
        
        if cleanup:
            print("\n")
            if self.cleanup():
                passed += 1
            else:
                failed += 1
        
        # Summary
        print("\n" + "=" * 70)
        print("  Demo Summary")
        print("=" * 70)
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print("=" * 70 + "\n")
        
        return failed == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="End-to-end TMMatcher demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_pipeline.py                    # Full demo
  python test_pipeline.py --cleanup          # Demo with cleanup
  python test_pipeline.py --host localhost:8000
        """
    )
    
    parser.add_argument("--host", "-H",
                       default="127.0.0.1:8002",
                       help="Server address (default: 127.0.0.1:8002)")
    parser.add_argument("--cleanup", "-c",
                       action="store_true",
                       help="Remove sample index after demo")
    
    args = parser.parse_args()
    
    # Parse host:port
    try:
        host, port_str = args.host.rsplit(":", 1)
        port = int(port_str)
    except (ValueError, IndexError):
        print(f"Invalid host format: {args.host}")
        print("Use: host:port (e.g., localhost:8000)")
        sys.exit(1)
    
    demo = TMMatcherDemo(host, port)
    success = demo.run(cleanup=args.cleanup)
    
    sys.exit(0 if success else 1)
