
import os
import bm25s

from fastapi import UploadFile
from pydantic import BaseModel
from .shared import indices, indices_lock, RESOURCES_DIR, tokenize

class TMUploadResponse(BaseModel):
    status: str
    index: str
    size: int

def upload_endpoint(file: UploadFile, name: str) -> TMUploadResponse:
    tsv_path = os.path.join(RESOURCES_DIR, f"{name}.tsv")
    with open(tsv_path, "wb") as out:
        out.write(file.file.read())

    with open(tsv_path, "r", encoding="utf-8") as f:
        corpus_json = [
            {"source": source, "target": target} for source, target in (line.strip().split("\t") for line in f)
        ]

    # Extract the source sentences for indexing
    corpus_source = [doc["source"] for doc in corpus_json]
    # tokenize the source sentences (you can use your custom tokenizer here)
    corpus_tokens = [tokenize(s) for s in corpus_source]

    # Create the BM25 retriever and attach the corpus_json to it (optional, but allows you to get the original sentences back)
    automaton = bm25s.BM25()
    # Add corpus_tokens to the index
    automaton.index(corpus_tokens, corpus=corpus_json) # corpus_json is the original documents, which will be returned in the results

    # Save the index, and the corpus 
    path = os.path.join(RESOURCES_DIR, name)
    automaton.save(path, corpus=corpus_json)

    with indices_lock:
        indices[name] = {"automaton": automaton, "size": len(corpus_json)}
    return TMUploadResponse(status="ok", index=name, size=len(corpus_json))
