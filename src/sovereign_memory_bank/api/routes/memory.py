"""Memory object CRUD endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from sovereign_memory_bank.models.enums import MemoryType, MemoryStatus
from sovereign_memory_bank.models.memory_object import MemoryObject, deserialize_memory

router = APIRouter()


class CreateMemoryRequest(BaseModel):
    type: MemoryType
    title: str = ""
    description: str = ""
    confidence: float = 0.5
    tags: list[str] = []


class UpdateMemoryRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    confidence: Optional[float] = None
    status: Optional[MemoryStatus] = None
    tags: Optional[list[str]] = None


@router.get("/{obj_id}")
async def get_memory(request: Request, obj_id: str):
    store = request.app.state.markdown_store
    # Search across all types
    for mem_type in MemoryType:
        obj = store.load(mem_type, obj_id)
        if obj:
            return obj.model_dump(mode="json")
    raise HTTPException(status_code=404, detail=f"Memory object {obj_id} not found")


@router.post("/")
async def create_memory(request: Request, req: CreateMemoryRequest):
    from sovereign_memory_bank.models.memory_object import MEMORY_TYPE_REGISTRY

    cls = MEMORY_TYPE_REGISTRY.get(req.type, MemoryObject)
    obj = cls(type=req.type, title=req.title, description=req.description, confidence=req.confidence, tags=req.tags)

    store = request.app.state.markdown_store
    sqlite = request.app.state.sqlite_store

    store.save(obj)
    await sqlite.save(obj)

    return obj.model_dump(mode="json")


@router.put("/{obj_id}")
async def update_memory(request: Request, obj_id: str, req: UpdateMemoryRequest):
    store = request.app.state.markdown_store
    sqlite = request.app.state.sqlite_store

    for mem_type in MemoryType:
        obj = store.load(mem_type, obj_id)
        if obj:
            if req.title is not None:
                obj.title = req.title
            if req.description is not None:
                obj.description = req.description
            if req.confidence is not None:
                obj.confidence = req.confidence
            if req.status is not None:
                obj.status = req.status
            if req.tags is not None:
                obj.tags = req.tags

            from datetime import datetime, timezone

            obj.modified = datetime.now(timezone.utc)

            store.save(obj)
            await sqlite.save(obj)
            return obj.model_dump(mode="json")

    raise HTTPException(status_code=404, detail=f"Memory object {obj_id} not found")


@router.delete("/{obj_id}")
async def delete_memory(request: Request, obj_id: str):
    store = request.app.state.markdown_store
    sqlite = request.app.state.sqlite_store
    vector = request.app.state.vector_store
    graph = request.app.state.knowledge_graph

    for mem_type in MemoryType:
        if store.exists(mem_type, obj_id):
            store.delete(mem_type, obj_id)
            await sqlite.delete(obj_id)
            vector.delete(obj_id)
            graph.remove_node(f"mem-{obj_id}")
            graph.save()
            return {"deleted": obj_id}

    raise HTTPException(status_code=404, detail=f"Memory object {obj_id} not found")


@router.get("/")
async def list_memory(request: Request, type: Optional[MemoryType] = None, limit: int = 100):
    store = request.app.state.markdown_store
    if type:
        objects = store.list_objects(type)
    else:
        objects = store.list_all()
    return [obj.model_dump(mode="json") for obj in objects[:limit]]
