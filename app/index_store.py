
import os
import bm25s
from .shared import indices, indices_lock, RESOURCES_DIR

def load_index(name: str):
    # Ensure resources directory exists
    os.makedirs(RESOURCES_DIR, exist_ok=True)

    # ... load the model when you need it

    index_path = os.path.join(RESOURCES_DIR, f"{name}")

    if not os.path.exists(index_path):
        return False
    automaton = bm25s.BM25.load("ECB_index", load_corpus=False)
    with indices_lock:
        indices[name] = {"automaton": automaton, "size": len(automaton)}
    return True

def load_all_indices():
    for fname in os.listdir(RESOURCES_DIR):
        if os.path.isdir(os.path.join(RESOURCES_DIR, fname)):
            name = fname
            load_index(name)
