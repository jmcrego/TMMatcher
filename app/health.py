from pydantic import BaseModel
from typing import List
from .shared import indices, indices_lock

class TMHealthIndex(BaseModel):
    name: str
    size: int

class TMHealthResponse(BaseModel):
    indices: List[TMHealthIndex]

def health_endpoint() -> TMHealthResponse:
    with indices_lock:
        return TMHealthResponse(indices=[TMHealthIndex(name=k, size=v["size"]) for k, v in indices.items()])
