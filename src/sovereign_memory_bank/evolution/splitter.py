"""Concept splitting for overloaded concepts."""

from __future__ import annotations

from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph
from sovereign_memory_bank.models.enums import MemoryType
from sovereign_memory_bank.models.memory_object import Concept


class ConceptSplitter:
    """Splits overloaded concepts into focused sub-concepts."""

    MAX_EDGES = 15  # Threshold for "overloaded"

    def __init__(self, store: MarkdownStore, graph: KnowledgeGraph) -> None:
        self.store = store
        self.graph = graph

    async def split_overloaded(self) -> dict:
        """Find and split overloaded concepts."""
        concepts = self.store.list_objects(MemoryType.CONCEPT)
        split_count = 0

        for concept in concepts:
            node_id = f"mem-{concept.id}"
            edges = self.graph.get_edges_from(node_id) + self.graph.get_edges_to(node_id)

            if len(edges) > self.MAX_EDGES:
                sub_concepts = self._split(concept, edges)
                if sub_concepts:
                    split_count += 1

        return {"split": split_count}

    def _split(self, concept: Concept, edges) -> list[Concept]:
        """Split a concept into focused sub-concepts."""
        # Group related nodes by their edge type
        groups: dict[str, list[str]] = {}
        for edge in edges:
            other_id = edge.target if edge.source == f"mem-{concept.id}" else edge.source
            edge_key = edge.edge_type.value
            groups.setdefault(edge_key, []).append(other_id)

        if len(groups) < 2:
            return []

        sub_concepts = []
        for edge_type, node_ids in groups.items():
            sub = Concept(
                title=f"{concept.title} ({edge_type})",
                description=f"Sub-concept of {concept.title}, focused on {edge_type} relationships",
                confidence=concept.confidence * 0.9,
                source_ids=list(concept.source_ids),
                tags=concept.tags + [edge_type],
            )
            self.store.save(sub)
            sub_concepts.append(sub)

            # Connect sub-concept to related nodes
            from sovereign_memory_bank.graph.graph_store import GraphNode, GraphEdge
            from sovereign_memory_bank.models.enums import GraphNodeType, NodeEdgeType

            sub_node = GraphNode(
                id=f"mem-{sub.id}",
                node_type=GraphNodeType.CONCEPT,
                label=sub.title,
            )
            self.graph.add_node(sub_node)

            for nid in node_ids[:5]:  # Limit connections
                self.graph.add_edge(
                    GraphEdge(
                        source=f"mem-{sub.id}",
                        target=nid,
                        edge_type=NodeEdgeType(edge_type) if edge_type in [e.value for e in NodeEdgeType] else NodeEdgeType.RELATED_TO,
                    )
                )

        # Mark original as split
        from sovereign_memory_bank.models.enums import MemoryStatus
        concept.status = MemoryStatus.SPLIT
        self.store.save(concept)

        return sub_concepts
