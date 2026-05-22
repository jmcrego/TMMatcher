
import time
import numpy as np
from pydantic import BaseModel
from typing import List
from .shared import indices, indices_lock, tokenize, CACHE_ENABLED, CACHE_BACKEND, stats

#from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein


class TMMatchRequest(BaseModel):
    sentence: str
    indices: List[str]

class TMMatchResult(BaseModel):
    index: str
    source: str
    target: str
    score: float

class TMMatchResponse(BaseModel):
    matches: List[TMMatchResult]
    runtime_ms: float = 0
    cached: bool = False

def rescore(query_tokens, results, scores, k=5):
    # replace the score by a fuzzy match score for all retrieved documents, 
    # FMS = 1 - edit_distance(query, source) / max(len(query), len(source)) # normalized edit distance
    for b in range(results.shape[0]):
        for i in range(results.shape[1]):
            doc = results[b, i]
            source_tokens = tokenize(doc['source'])
            score = Levenshtein.distance(query_tokens, source_tokens)
            scores[b, i] = 1 - score / max(len(query_tokens), len(source_tokens)) # normalized edit distance
    # Get the indices of the top-k scores over each row (query), sort descending and take top k
    top_k_indices = scores.argsort(axis=1)[:, ::-1][:, :k] # sort descending and take top k shape is (n_queries, k)
    results = np.take_along_axis(results, top_k_indices, axis=1)
    scores = np.take_along_axis(scores, top_k_indices, axis=1)
    return results, scores

def match_endpoint(request: TMMatchRequest) -> TMMatchResponse:
    """Match endpoint with caching support."""
    tic = time.perf_counter()
    indices_str = ",".join(request.indices)
    cached = False
    
    try:
        # Check cache first
        if CACHE_ENABLED and CACHE_BACKEND:
            cached_result = CACHE_BACKEND.get(request.sentence, indices_str)
            if cached_result:
                runtime_ms = (time.perf_counter() - tic) * 1000
                cached_result.runtime_ms = runtime_ms
                cached_result.cached = True
                stats.record_request(runtime_ms, cached=True)
                return cached_result
        
        # Perform matching
        res = []
        query_tokens = tokenize(request.sentence)
        with indices_lock:
            for idx in request.indices:
                entry = indices.get(idx)
                print(f"entry for index '{idx}': {entry}")
                if not entry:
                    continue
                automaton = entry["automaton"]
                results, scores = automaton.retrieve([query_tokens], k=50)
                results, scores = rescore(query_tokens, results, scores, k=5)
                for i in range(results.shape[1]):
                    doc, score = results[0, i], scores[0, i]
                    res.append(TMMatchResult(
                        index=idx,
                        source=doc['source'],
                        target=doc['target'],
                        score=score
                    ))
        
        runtime_ms = (time.perf_counter() - tic) * 1000
        response = TMMatchResponse(matches=res, runtime_ms=runtime_ms, cached=False)
        
        # Cache the result
        if CACHE_ENABLED and CACHE_BACKEND:
            CACHE_BACKEND.set(request.sentence, indices_str, response)
        
        # Record statistics
        stats.record_request(runtime_ms, cached=False)
        
        return response
    
    except Exception as e:
        runtime_ms = (time.perf_counter() - tic) * 1000
        stats.record_request(runtime_ms, cached=False, error=True)
        raise
