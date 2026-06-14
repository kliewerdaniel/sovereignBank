"""FastAPI application for the Sovereign Memory Bank agent interface."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from sovereign_memory_bank.config import settings
from sovereign_memory_bank.layers.layer_manager import LayerManager
from sovereign_memory_bank.storage.sqlite_store import SQLiteStore
from sovereign_memory_bank.storage.vector_store import VectorStore
from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph
from sovereign_memory_bank.api.routes import memory, graph, search, hybrid


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize stores on startup, close on shutdown."""
    lm = LayerManager(settings.memory_bank_dir)
    lm.initialize()

    sqlite_store = SQLiteStore(settings.sqlite_db_path)
    await sqlite_store.initialize()

    vector_store = VectorStore(settings.chroma_persist_dir, settings.chroma_collection)
    vector_store.initialize()

    markdown_store = MarkdownStore(lm)
    knowledge_graph = KnowledgeGraph(settings.memory_bank_dir / "graph.json")

    app.state.sqlite_store = sqlite_store
    app.state.vector_store = vector_store
    app.state.markdown_store = markdown_store
    app.state.knowledge_graph = knowledge_graph
    app.state.layer_manager = lm

    yield

    await sqlite_store.close()


app = FastAPI(
    title="Sovereign Memory Bank",
    description="Agent interface for autonomous cognitive memory system",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(hybrid.router, prefix="/api/hybrid", tags=["hybrid"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
