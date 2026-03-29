

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from pydantic import BaseModel
from typing import List

from .index_store import load_all_indices
from .upload import upload_endpoint, TMUploadResponse
from .match import match_endpoint, TMMatchRequest, TMMatchResponse

from .health import health_endpoint, TMHealthResponse
from .remove import remove_endpoint, TMRemoveRequest, TMRemoveResponse

# Load existing indices on startup (this will be done in the lifespan context manager, when the app starts)
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_all_indices()
    yield # marks the point where the app starts accepting requests
 
# FastAPI app
app = FastAPI(lifespan=lifespan)

# Health check endpoint, returns list of loaded indices and their sizes
@app.get("/health", response_model=TMHealthResponse)
def health():
    return health_endpoint()

# Upload endpoint, allows uploading files to create or update indices
@app.post("/upload", response_model=TMUploadResponse)
def upload(file: UploadFile = File(...), name: str = Form(...)):
    return upload_endpoint(file, name)


# Match endpoint, performs matching against the loaded indices (POST, JSON body)
@app.post("/match", response_model=TMMatchResponse)
def match(request: TMMatchRequest):
    return match_endpoint(request)

# Match2 endpoint, performs matching using GET with query parameters
# @app.get("/match2", response_model=TMMatchResponse)
# def match2(sentence: str, indices: str):
#     # indices is a comma-separated string
#     indices_list = [i.strip() for i in indices.split(",") if i.strip()]
#     return match_endpoint(TMMatchRequest(sentence=sentence, indices=indices_list))

# Remove endpoint, deletes an index and its .pkl file
@app.post("/remove", response_model=TMRemoveResponse)
def remove(request: TMRemoveRequest):
    return remove_endpoint(request)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
