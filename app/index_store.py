
import os
import bm25s
from .shared import indices, indices_lock, RESOURCES_PATH

def load_index(name):
    path_name = os.path.join(RESOURCES_PATH, name)
    automaton = bm25s.BM25.load(path_name, load_corpus=True)
    with indices_lock:
        indices[name] = {"automaton": automaton, "size": len(automaton.corpus)}
    return True

def load_all_indices():
    if not RESOURCES_PATH.exists():
        return
    for name in os.listdir(RESOURCES_PATH):
        if os.path.isdir(os.path.join(RESOURCES_PATH, name)):
            load_index(name)
