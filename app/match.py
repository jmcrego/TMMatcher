
import time
import numpy as np
from pydantic import BaseModel
from typing import List
from .shared import indices, indices_lock, tokenize

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
    res = []
    tic = time.perf_counter()
    query_tokens = tokenize(request.sentence)  # or use your custom tokenizer
    with indices_lock:
        for idx in request.indices:
            entry = indices.get(idx)
            print(f"entry for index '{idx}': {entry}")
            if not entry:
                continue
            automaton = entry["automaton"]
            results, scores = automaton.retrieve([query_tokens], k=10)
            results, scores = rescore(query_tokens, results, scores, k=5)
            for i in range(results.shape[1]):
                doc, score = results[0, i], scores[0, i]
                res.append(TMMatchResult(
                    index=idx,
                    source=doc['source'],
                    target=doc['target'],
                    score=score
                ))
    runtime_s = time.perf_counter() - tic
    return TMMatchResponse(matches=res, runtime_ms=runtime_s * 1000)
