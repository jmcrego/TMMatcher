
# FastAPI BM25s Matcher

A FastAPI application for high-speed fuzzy matching using multiple <b>BM25s</b> indices. Supports concurrent requests, index upload, and health monitoring.

## Features
- Loads all `bm25s` indices from the `resources/` directory at startup
- `/health`: Lists available indices and their sizes
- `/upload`: Upload a TSV translation memory file and specify the index name to create and load
- `/match`: Query one or more indices for fuzzy sentence matches, returning an n-best list containing the fuzzy match and score

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
uvicorn app:main --reload --port 8002
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
