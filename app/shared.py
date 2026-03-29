import threading
from pathlib import Path
import re

TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE) # Find continuous sequences of word characters (words and numbers)

def tokenize(text):
    return TOKEN_PATTERN.findall(text.lower())

# Shared resources for the app
indices = {}
indices_lock = threading.Lock()
RESOURCES_DIR = Path(__file__).parent.parent / "resources"

