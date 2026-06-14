"""Graph query endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from sovereign_memory_bank.models.enums import GraphNodeType, NodeEdgeType
from sovereign_memory_bank.graph.graph_store import GraphNode, GraphEdge

router = APIRouter()


class AddNodeRequest(BaseModel):
    id: str
    node_type: GraphNodeType
    label: str = ""


class AddEdgeRequest(BaseModel):
    source: str
    target: str
    edge_type: NodeEdgeType
    weight: float = 1.0


@router.get("/stats")
async def graph_stats(request: Request):
    graph = request.app.state.knowledge_graph
    return graph.stats()


@router.get("/nodes/{node_id}")
async def get_node(request: Request, node_id: str):
    graph = request.app.state.knowledge_graph
    node = graph.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return {"id": node.id, "node_type": node.node_type.value, "label": node.label, "metadata": node.metadata}


@router.get("/neighbors/{node_id}")
async def get_neighbors(
    request: Request,
    node_id: str,
    edge_type: Optional[NodeEdgeType] = None,
):
    graph = request.app.state.knowledge_graph
    neighbors = graph.get_neighbors(node_id, edge_type)
    return [{"id": n.id, "node_type": n.node_type.value, "label": n.label} for n in neighbors]


@router.get("/multi-hop/{start_id}")
async def multi_hop_query(
    request: Request,
    start_id: str,
    max_hops: int = 3,
    edge_type: Optional[NodeEdgeType] = None,
):
    graph = request.app.state.knowledge_graph
    paths = graph.multi_hop_query(start_id, max_hops, edge_type)
    return [
        {"nodes": p.nodes, "edges": [e.value for e in p.edges]}
        for p in paths
    ]


@router.get("/path/{start_id}/{end_id}")
async def find_path(request: Request, start_id: str, end_id: str, max_hops: int = 5):
    graph = request.app.state.knowledge_graph
    path = graph.find_path(start_id, end_id, max_hops)
    if not path:
        raise HTTPException(status_code=404, detail="No path found")
    return {"nodes": path.nodes, "edges": [e.value for e in path.edges]}


@router.post("/nodes")
async def add_node(request: Request, req: AddNodeRequest):
    graph = request.app.state.knowledge_graph
    node = GraphNode(id=req.id, node_type=req.node_type, label=req.label)
    graph.add_node(node)
    graph.save()
    return {"id": node.id, "node_type": node.node_type.value, "label": node.label}


@router.post("/edges")
async def add_edge(request: Request, req: AddEdgeRequest):
    graph = request.app.state.knowledge_graph
    edge = GraphEdge(
        source=req.source,
        target=req.target,
        edge_type=req.edge_type,
        weight=req.weight,
    )
    graph.add_edge(edge)
    graph.save()
    return {"source": edge.source, "target": edge.target, "edge_type": edge.edge_type.value}


@router.get("/type/{node_type}")
async def nodes_by_type(request: Request, node_type: GraphNodeType):
    graph = request.app.state.knowledge_graph
    nodes = graph.nodes_by_type(node_type)
    return [{"id": n.id, "label": n.label, "metadata": n.metadata} for n in nodes]
