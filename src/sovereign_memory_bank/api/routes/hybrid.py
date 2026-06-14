"""Hybrid recall: combines vector search with graph traversal."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional

from sovereign_memory_bank.models.enums import NodeEdgeType

router = APIRouter()


class HybridQueryRequest(BaseModel):
    query: str
    n_results: int = 10
    max_hops: int = 2
    edge_type: Optional[NodeEdgeType] = None


@router.post("/")
async def hybrid_search(request: Request, req: HybridQueryRequest):
    vector_store = request.app.state.vector_store
    graph = request.app.state.knowledge_graph

    # Step 1: Semantic search
    semantic_results = vector_store.query(text=req.query, n_results=req.n_results)

    # Step 2: Graph expansion from semantic results
    expanded_nodes = {}
    for result in semantic_results:
        node_id = f"mem-{result['id']}"
        if node_id in graph.nodes:
            # Get neighbors up to max_hops
            paths = graph.multi_hop_query(node_id, req.max_hops, req.edge_type)
            for path in paths:
                for nid in path.nodes:
                    if nid not in expanded_nodes and nid in graph.nodes:
                        n = graph.nodes[nid]
                        expanded_nodes[nid] = {
                            "id": n.id,
                            "node_type": n.node_type.value,
                            "label": n.label,
                            "source": "graph_traversal",
                        }

    return {
        "query": req.query,
        "semantic_results": semantic_results,
        "graph_expanded": list(expanded_nodes.values()),
        "total_results": len(semantic_results) + len(expanded_nodes),
    }
