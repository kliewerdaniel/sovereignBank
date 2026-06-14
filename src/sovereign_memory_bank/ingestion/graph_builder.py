"""Graph builder - adds memory objects as nodes and creates edges."""

from __future__ import annotations

from sovereign_memory_bank.graph.graph_store import KnowledgeGraph, GraphNode, GraphEdge
from sovereign_memory_bank.models.enums import MemoryType, GraphNodeType, NodeEdgeType
from sovereign_memory_bank.models.memory_object import MemoryObject, Relationship


# Mapping from memory type to graph node type
MEMORY_TO_GRAPH_NODE: dict[MemoryType, GraphNodeType] = {
    MemoryType.CONCEPT: GraphNodeType.CONCEPT,
    MemoryType.CLAIM: GraphNodeType.CLAIM,
    MemoryType.ENTITY: GraphNodeType.ENTITY,
    MemoryType.INSIGHT: GraphNodeType.INSIGHT,
    MemoryType.NARRATIVE: GraphNodeType.NARRATIVE,
    MemoryType.ABSTRACTION: GraphNodeType.ABSTRACTION,
}


class GraphBuilder:
    """Builds knowledge graph from memory objects."""

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph

    def add_memory_node(self, obj: MemoryObject) -> GraphNode:
        """Add a memory object as a graph node."""
        node_type = MEMORY_TO_GRAPH_NODE.get(obj.type, GraphNodeType.CONCEPT)
        node = GraphNode(
            id=f"mem-{obj.id}",
            node_type=node_type,
            label=obj.title,
            metadata={
                "memory_type": obj.type.value,
                "confidence": obj.confidence,
                "status": obj.status.value,
            },
        )
        self.graph.add_node(node)
        return node

    def add_relationship_edge(self, rel: Relationship) -> GraphEdge:
        """Add a relationship as a graph edge."""
        edge_type_map = {
            "references": NodeEdgeType.REFERENCES,
            "supports": NodeEdgeType.SUPPORTS,
            "contradicts": NodeEdgeType.CONTRADICTS,
            "extends": NodeEdgeType.EXTENDS,
            "derives_from": NodeEdgeType.DERIVES_FROM,
            "inspired_by": NodeEdgeType.INSPIRED_BY,
            "evolves_into": NodeEdgeType.EVOLVES_INTO,
            "related_to": NodeEdgeType.RELATED_TO,
            "contains": NodeEdgeType.CONTAINS,
            "explains": NodeEdgeType.EXPLAINS,
        }
        edge_type = edge_type_map.get(rel.edge_type, NodeEdgeType.RELATED_TO)
        edge = GraphEdge(
            source=f"mem-{rel.source_id}",
            target=f"mem-{rel.target_id}",
            edge_type=edge_type,
            weight=rel.strength,
        )
        self.graph.add_edge(edge)
        return edge

    def connect_concepts(self, concept_ids: list[str], edge_type: NodeEdgeType) -> None:
        """Create edges between a list of concepts."""
        for i, c1 in enumerate(concept_ids):
            for c2 in concept_ids[i + 1 :]:
                self.graph.add_edge(
                    GraphEdge(
                        source=f"mem-{c1}",
                        target=f"mem-{c2}",
                        edge_type=edge_type,
                    )
                )

    def add_source_connection(
        self, source_id: str, memory_id: str, edge_type: NodeEdgeType = NodeEdgeType.REFERENCES
    ) -> None:
        """Connect a source document to a memory object."""
        self.graph.add_edge(
            GraphEdge(
                source=f"source-{source_id}",
                target=f"mem-{memory_id}",
                edge_type=edge_type,
            )
        )
