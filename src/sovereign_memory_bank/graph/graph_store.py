"""Knowledge graph with typed nodes and edges, supporting multi-hop reasoning."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

from sovereign_memory_bank.models.enums import GraphNodeType, NodeEdgeType


@dataclass
class GraphNode:
    id: str
    node_type: GraphNodeType
    label: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    source: str
    target: str
    edge_type: NodeEdgeType
    weight: float = 1.0
    metadata: dict = field(default_factory=dict)


@dataclass
class GraphPath:
    nodes: list[str]
    edges: list[NodeEdgeType]


class KnowledgeGraph:
    """In-memory knowledge graph persisted as JSON."""

    def __init__(self, graph_path: Path) -> None:
        self.path = graph_path
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self._adjacency: dict[str, list[GraphEdge]] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text())
            for n in data.get("nodes", []):
                node = GraphNode(
                    id=n["id"],
                    node_type=GraphNodeType(n["node_type"]),
                    label=n.get("label", ""),
                    metadata=n.get("metadata", {}),
                )
                self.nodes[node.id] = node
            for e in data.get("edges", []):
                edge = GraphEdge(
                    source=e["source"],
                    target=e["target"],
                    edge_type=NodeEdgeType(e["edge_type"]),
                    weight=e.get("weight", 1.0),
                    metadata=e.get("metadata", {}),
                )
                self.edges.append(edge)
                self._adjacency.setdefault(edge.source, []).append(edge)
                self._adjacency.setdefault(edge.target, []).append(edge)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "nodes": [
                {"id": n.id, "node_type": n.node_type.value, "label": n.label, "metadata": n.metadata}
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "edge_type": e.edge_type.value,
                    "weight": e.weight,
                    "metadata": e.metadata,
                }
                for e in self.edges
            ],
        }
        self.path.write_text(json.dumps(data, indent=2))

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)
        self._adjacency.setdefault(edge.source, []).append(edge)
        self._adjacency.setdefault(edge.target, []).append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str, edge_type: Optional[NodeEdgeType] = None) -> list[GraphNode]:
        neighbors = []
        for edge in self._adjacency.get(node_id, []):
            if edge_type and edge.edge_type != edge_type:
                continue
            other_id = edge.target if edge.source == node_id else edge.source
            if other_id in self.nodes:
                neighbors.append(self.nodes[other_id])
        return neighbors

    def get_edges_from(self, node_id: str) -> list[GraphEdge]:
        return [e for e in self._adjacency.get(node_id, []) if e.source == node_id]

    def get_edges_to(self, node_id: str) -> list[GraphEdge]:
        return [e for e in self._adjacency.get(node_id, []) if e.target == node_id]

    def multi_hop_query(
        self,
        start_id: str,
        max_hops: int = 3,
        edge_type_filter: Optional[NodeEdgeType] = None,
    ) -> list[GraphPath]:
        """BFS multi-hop query returning all paths up to max_hops."""
        results: list[GraphPath] = []
        queue: list[tuple[str, list[str], list[NodeEdgeType]]] = [(start_id, [start_id], [])]

        while queue:
            current, path_nodes, path_edges = queue.pop(0)
            if len(path_nodes) > 1:
                results.append(GraphPath(nodes=list(path_nodes), edges=list(path_edges)))
            if len(path_nodes) > max_hops:
                continue
            for edge in self._adjacency.get(current, []):
                if edge_type_filter and edge.edge_type != edge_type_filter:
                    continue
                next_id = edge.target if edge.source == current else edge.source
                if next_id not in path_nodes:
                    queue.append(
                        (next_id, path_nodes + [next_id], path_edges + [edge.edge_type])
                    )
        return results

    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_hops: int = 5,
    ) -> Optional[GraphPath]:
        """Find shortest path between two nodes."""
        paths = self.multi_hop_query(start_id, max_hops)
        for p in paths:
            if p.nodes[-1] == end_id:
                return p
        return None

    def nodes_by_type(self, node_type: GraphNodeType) -> list[GraphNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def edges_by_type(self, edge_type: NodeEdgeType) -> list[GraphEdge]:
        return [e for e in self.edges if e.edge_type == edge_type]

    def remove_node(self, node_id: str) -> None:
        self.nodes.pop(node_id, None)
        self.edges = [e for e in self.edges if e.source != node_id and e.target != node_id]
        self._adjacency.pop(node_id, None)
        for adj_list in self._adjacency.values():
            adj_list[:] = [e for e in adj_list if e.source != node_id and e.target != node_id]

    def stats(self) -> dict:
        type_counts = {}
        for n in self.nodes.values():
            type_counts[n.node_type.value] = type_counts.get(n.node_type.value, 0) + 1
        edge_counts = {}
        for e in self.edges:
            edge_counts[e.edge_type.value] = edge_counts.get(e.edge_type.value, 0) + 1
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": type_counts,
            "edge_types": edge_counts,
        }
