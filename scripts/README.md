# TMMatcher Test Scripts

Utility scripts for testing and demonstrating TMMatcher functionality.

## Quick Start

```bash
# Start the server in one terminal
cd /path/to/TMMatcher
uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload

# In another terminal, run tests
cd scripts

# Check service health
python test_health.py

# Upload sample translation memory
python test_upload.py

# Search with queries
python test_match.py

# Remove an index
python test_remove.py

# Run full end-to-end demo
python test_pipeline.py
```

## Available Scripts

### 1. `test_health.py` - Health Check

Verify service availability and view current status including indices, cache stats, and service statistics.

**Usage:**
```bash
python test_health.py [HOST:PORT]
```

**Examples:**
```bash
python test_health.py                      # Default: localhost:8002
python test_health.py localhost:8000       # Custom port
python test_health.py 192.168.1.100:8002  # Remote host
```

**Output shows:**
- Service status
- Loaded indices and their sizes
- Cache configuration and current usage
- Request statistics (total, cache hits/misses, average runtime)

---

### 2. `test_upload.py` - Upload Translation Memory

Upload a TSV translation memory file to create or update an index.

**File Format:**
Two-column TSV with tab-separated values:
```
source sentence    target sentence
hello world        bonjour le monde
how are you        comment allez-vous
```

**Usage:**
```bash
python test_upload.py [--file FILE] [--name NAME] [--host HOST:PORT]
```

**Examples:**
```bash
python test_upload.py                                # Use sample_tm.tsv
python test_upload.py --file /path/to/tm.tsv        # Custom file
python test_upload.py --file tm.tsv --name enfr     # Custom index name
python test_upload.py --host localhost:8000         # Custom server
```

**Output shows:**
- Upload status
- Index name
- Number of terms indexed

---

### 3. `test_match.py` - Search Queries

Test translation memory matching with queries.

**Usage:**
```bash
python test_match.py [--query TEXT] [--indices NAMES] [--host HOST:PORT]
```

**Examples:**
```bash
python test_match.py                                      # Default query
python test_match.py --query "hello world"                # Custom query
python test_match.py --indices sample_tm                  # Specific index
python test_match.py --query "good morning" --indices enfr,esen
python test_match.py --host localhost:8000                # Custom server
```

**Output shows:**
- Matching results with scores
- Source and target sentences
- Runtime and cache status
- Number of matches found

---

### 4. `test_remove.py` - Remove Index

Remove a translation memory index from the service.

**Usage:**
```bash
python test_remove.py [--index NAME] [--host HOST:PORT]
```

**Examples:**
```bash
python test_remove.py                               # Default: sample_tm
python test_remove.py --index tm_enfr               # Specific index
python test_remove.py --index tm_esen --host localhost:8000
```

**Output shows:**
- Removal status
- Removed index name

---

### 5. `test_pipeline.py` - End-to-End Demo

Comprehensive demonstration of all TMMatcher features in sequence.

**Steps:**
1. Health check
2. Upload sample translation memory
3. Perform multiple matching queries
4. Test cache functionality
5. View final statistics
6. Optional: Clean up (remove sample index)

**Usage:**
```bash
python test_pipeline.py [--host HOST:PORT] [--cleanup]
```

**Examples:**
```bash
python test_pipeline.py                    # Full demo without cleanup
python test_pipeline.py --cleanup          # Demo with cleanup
python test_pipeline.py --host localhost:8000
```

**Output shows:**
- Step-by-step progress
- Query results
- Cache efficiency (speedup measurement)
- Service statistics
- Demo summary

---

### 6. `cache_stats.py` - Cache Management

View and manage cache statistics and settings.

**Usage:**
```bash
python cache_stats.py [stats|clear|reset]
```

**Commands:**
- `stats` - Display cache and service statistics
- `clear` - Clear all cache entries
- `reset` - Reset service statistics

**Examples:**
```bash
python cache_stats.py stats    # View cache stats
python cache_stats.py clear    # Clear cache
python cache_stats.py reset    # Reset statistics
```

**Output shows:**
- Cache backend type (memory or redis)
- Current cache size and max size
- Service statistics (requests, hits, misses, runtime)

---

### 7. `sample_tm.tsv` - Sample Translation Memory

Sample TSV file with English-French translation pairs for testing.

Contains 10 common phrases for quick testing and demonstration.

---

## Configuration

### Server Connection

All scripts support custom server addresses via `--host` parameter:

```bash
python test_health.py --host localhost:8000       # Custom port
python test_health.py --host 192.168.1.100:8002   # Remote server
```

### Cache Configuration

Set environment variables before starting the server:

```bash
# Enable/disable cache (default: true)
export TM_CACHE_ENABLED=true

# Cache backend: 'memory' (default) or 'redis'
export TM_CACHE_TYPE=memory

# Maximum cache entries (default: 1000)
export TM_CACHE_MAX_SIZE=5000
```

### Resources Directory

Configure where translation memories are stored:

```bash
# Default: ~/.tm_resources
export TM_RESOURCES_PATH=/path/to/resources
```

---

## Typical Workflow

```bash
# 1. Start the server
uvicorn app.main:app --reload

# 2. Check health
python test_health.py

# 3. Upload translation memories
python test_upload.py --file my_tm.tsv --name my_index

# 4. Test queries
python test_match.py --query "test phrase" --indices my_index

# 5. View cache performance
python cache_stats.py stats

# 6. Clean up when done
python test_remove.py --index my_index
```

---

## Performance Testing

### Cache Effectiveness

Run the pipeline script to see cache speedup:

```bash
python test_pipeline.py
```

Look for the cache speedup measurement in the "Test Cache" step.

### Stress Testing

Test with many queries:

```bash
for i in {1..100}; do
  python test_match.py --query "test query $i" &
done
wait

python cache_stats.py stats
```

---

## Troubleshooting

**"Cannot connect to..." error:**
- Make sure the server is running: `uvicorn app.main:app --reload`
- Check the host and port: `python test_health.py --host localhost:8000`

**"File not found" error:**
- Make sure the TSV file exists in the current directory or provide full path
- Use `--file /path/to/file.tsv` with absolute path

**"Index not found" error:**
- Upload the index first: `python test_upload.py`
- Check existing indices with health check: `python test_health.py`

**No cache hits:**
- Check if cache is enabled: `python cache_stats.py stats`
- Enable cache: `export TM_CACHE_ENABLED=true`

---

## Examples

### Complete Demo Session

```bash
# Terminal 1: Start server
cd /path/to/TMMatcher
export TM_CACHE_MAX_SIZE=5000
uvicorn app.main:app --port 8002 --reload

# Terminal 2: Run tests
cd scripts

# 1. Check health
python test_health.py

# 2. Upload translations
python test_upload.py --file sample_tm.tsv --name english_french

# 3. Search
python test_match.py --query "hello world" --indices english_french

# 4. Run full pipeline
python test_pipeline.py

# 5. Check cache performance
python cache_stats.py stats
```

### Multiple Translation Memories

```bash
# Upload multiple TMs
python test_upload.py --file enfr.tsv --name enfr
python test_upload.py --file esen.tsv --name esen

# Search across all
python test_match.py --query "hello" --indices enfr,esen

# View all loaded indices
python test_health.py

# Clean up
python test_remove.py --index enfr
python test_remove.py --index esen
```

---

## Dependencies

The scripts require:
- `requests` - For HTTP communication with the service

Install with:
```bash
pip install requests
```

This is already included in `requirements.txt`.

---

## License

MIT
