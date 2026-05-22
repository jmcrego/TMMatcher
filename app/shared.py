import threading
from pathlib import Path
import re
import os

from .statistics import Statistics

TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE) # Find continuous sequences of word characters (words and numbers)

def tokenize(text):
    return TOKEN_PATTERN.findall(text.lower())

# Shared resources for the app
indices = {}
indices_lock = threading.Lock()

# Use environment variable TM_RESOURCES_PATH, default to ~/.tm_resources
RESOURCES_PATH = Path(os.getenv("TM_RESOURCES_PATH", str(Path.home() / ".tm_resources"))).expanduser()
RESOURCES_PATH.mkdir(parents=True, exist_ok=True)

# Service statistics
stats = Statistics()

# Cache configuration from environment variables
CACHE_BACKEND = None  # Will be initialized in main.py
CACHE_ENABLED = os.getenv("TM_CACHE_ENABLED", "true").lower() == "true"
CACHE_TYPE = os.getenv("TM_CACHE_TYPE", "memory")
CACHE_MAX_SIZE = int(os.getenv("TM_CACHE_MAX_SIZE", "1000"))

