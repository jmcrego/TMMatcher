
import time
from pydantic import BaseModel
from typing import List
from .shared import indices, indices_lock, tokenize

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


def match_endpoint(request: TMMatchRequest) -> TMMatchResponse:
    results = []
    tic = time.perf_counter()
    query_tokens = tokenize(request.sentence)  # or use your custom tokenizer
    with indices_lock:
        for idx in request.indices:
            entry = indices.get(idx)
            if not entry:
                continue
            automaton = entry["automaton"]
            results, scores = automaton.retrieve([query_tokens], k=2)
            for i in range(results.shape[1]):
                doc, score = results[0, i], scores[0, i]
                results.append(TMMatchResult(
                    index=idx,
                    source=doc['source'],
                    target=doc['target'],
                    score=score
                ))
    runtime_s = time.perf_counter() - tic
    return TMMatchResponse(matches=results, runtime_ms=runtime_s * 1000)
