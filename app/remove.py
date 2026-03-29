from fastapi import HTTPException
from pydantic import BaseModel
from .shared import indices, indices_lock, RESOURCES_DIR
import os


class TMRemoveRequest(BaseModel):
    index: str

class TMRemoveResponse(BaseModel):
    status: str
    index: str


def remove_endpoint(request: TMRemoveRequest) -> TMRemoveResponse:
    name = request.index
    with indices_lock:
        if name not in indices:
            raise HTTPException(status_code=404, detail=f"Index '{name}' not found.")
        # Remove from memory
        del indices[name]
    # Remove directory
    index_dir = os.path.join(RESOURCES_DIR, name)
    if os.path.exists(index_dir):
        os.rmdir(index_dir)
    # Remove .tsv file
    tsv_path = os.path.join(RESOURCES_DIR, f"{name}.tsv")
    if os.path.exists(tsv_path):
        os.remove(tsv_path)
    return TMRemoveResponse(status="removed", index=name)

