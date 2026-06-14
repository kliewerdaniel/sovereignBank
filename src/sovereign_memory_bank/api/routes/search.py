"""Semantic search endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    n_results: int = 10
    type_filter: Optional[str] = None


@router.post("/")
async def semantic_search(request: Request, req: SearchRequest):
    vector_store = request.app.state.vector_store

    where = None
    if req.type_filter:
        where = {"type": req.type_filter}

    results = vector_store.query(text=req.query, n_results=req.n_results, where=where)
    return {"results": results, "query": req.query}


@router.get("/stats")
async def vector_stats(request: Request):
    vector_store = request.app.state.vector_store
    return {"total_embeddings": vector_store.count()}
