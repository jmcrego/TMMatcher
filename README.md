
# FastAPI bm25s Matcher

A FastAPI application for high-speed fuzzy matching using multiple <b>bm25s</b> indices. Supports concurrent requests, index upload, and health monitoring.

## Preprocessing TMs and Queries

Translation memory entries (TM first column) and queries are preprocessed before matching. This ensures consistent tokenization and scoring across different queries and indices.

### Preprocessing Steps

- All text is converted to lowercase.
- Sentences are tokenized using the following regular expression pattern:

  ```python
  TOKEN_PATTERN = re.compile(r"\\w+", re.UNICODE)
  ```

  This pattern extracts contiguous sequences of Unicode word characters (letters, digits, and underscores), effectively splitting text into tokens such as words and numbers while discarding punctuation.

- The resulting list of tokens is used consistently for both indexing and querying.

This approach ensures that punctuation and case do not affect the matching process, and that only meaningful word units are compared.

## Features
- Loads all `bm25s` indices from the `resources/` directory at startup
- `/health`: Lists available indices and their sizes
- `/upload`: Upload a TSV translation memory file and specify the index name to create and load
- `/match`: Query one or more indices for fuzzy sentence matches, returning an n-best list containing the fuzzy match and score
- **Caching System**: In-memory LRU cache (or Redis) to speed up repeated queries
- **Statistics Tracking**: Comprehensive request tracking, cache performance metrics, and runtime analysis

## Caching

TMMatcher includes an intelligent caching system to improve performance for repeated searches. The cache stores previous match results to serve identical queries instantly.

### Cache Backends

- **Memory (default)**: Fast in-memory LRU cache, perfect for single-server deployments
- **Redis**: Distributed cache backend for multi-server setups

### Cache Configuration

All cache settings are configured via environment variables:

```bash
# Enable cache (default: true)
export TM_CACHE_ENABLED=true

# Cache backend: 'memory' (default) or 'redis'
export TM_CACHE_TYPE=memory

# Maximum cache entries in memory (default: 1000)
# Older entries are evicted using LRU when limit is reached
export TM_CACHE_MAX_SIZE=1000
```

### Cache Management

View cache statistics:
```bash
python scripts/cache_stats.py stats
```

Clear cache:
```bash
python scripts/cache_stats.py clear
```

Reset statistics:
```bash
python scripts/cache_stats.py reset
```

### Performance Monitoring

The `/health` endpoint provides comprehensive cache and service statistics:

```bash
curl http://localhost:8002/health | python -m json.tool
```

Response includes:
- **Cache Status**: Current entries, max size, cache type
- **Service Statistics**: Total requests, cache hits/misses, hit rate percentage, min/max/average runtime

Example:
```json
{
  "indices": [...],
  "cache": {
    "enabled": true,
    "type": "memory",
    "size": 245,
    "max_size": 1000
  },
  "statistics": {
    "total_requests": 1250,
    "successful_requests": 1247,
    "total_errors": 3,
    "cache_hits": 892,
    "cache_misses": 355,
    "cache_hit_rate_percent": 71.53,
    "average_runtime_ms": 4.23,
    "min_runtime_ms": 0.12,
    "max_runtime_ms": 45.67
  }
}
```

## Endpoints

### `GET /health`
Returns a list of loaded indices and their sizes (number of terms).

### `POST /upload`
Upload a TSV file (two columns: `<source sentence>\t<target sentence>`) and specify the index name. The server saves the file as `resources/NAME.tsv`, builds the index `resources/NAME/`, and loads it into memory.

**Request (multipart/form-data):**
- `file`: The TSV translation memory file
- `name`: The desired index name (used for .tsv and .pkl files)

### `POST /match`
Query one or more indices for exact term matches in a sentence.

## Setup

### Installation

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install requirements:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running the Server

Start the FastAPI server (default port 8000, or use --port 8001 if needed):
```bash
uvicorn app.main:app --reload --port 8002
```

## Example Requests

### Health Check
```bash
curl http://localhost:8002/health
```

### Upload a TM Index
```bash
curl -X POST "http://localhost:8002/upload" \
  -F "file=@/path/to/your_translation_memory.tsv" \
  -F "name=tm_enfr"
```

### Match a Sentence
```bash
curl -X POST "http://localhost:8002/match" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "your sentence here", "indices": ["tm_enfr"]}'
```

### Remove an Index
```bash
curl -X POST "http://localhost:8002/remove" \
  -H "Content-Type: application/json" \
  -d '{"index": "tm_enfr"}'
```

## Directory Structure
- `app.py` — Main FastAPI application
- `resources/` — Directory for .tsv files and index dirs

## License
MIT
