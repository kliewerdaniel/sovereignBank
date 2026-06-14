"""Knowledge synthesis generation."""

from __future__ import annotations

from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph
from sovereign_memory_bank.models.enums import MemoryType, GraphNodeType, NodeEdgeType
from sovereign_memory_bank.models.memory_object import Concept, Insight, Synthesis
from sovereign_memory_bank.graph.graph_store import GraphNode, GraphEdge


class SynthesisGenerator:
    """Generates novel syntheses from multiple knowledge sources."""

    MIN_SOURCES = 3

    def __init__(self, store: MarkdownStore, graph: KnowledgeGraph) -> None:
        self.store = store
        self.graph = graph

    async def generate(self) -> dict:
        """Generate syntheses from related concepts and insights."""
        concepts = self.store.list_objects(MemoryType.CONCEPT)
        insights = self.store.list_objects(MemoryType.INSIGHT)

        syntheses_created = 0

        # Find clusters of related concepts via graph
        visited = set()
        for concept in concepts:
            if concept.id in visited:
                continue

            node_id = f"mem-{concept.id}"
            neighbors = self.graph.get_neighbors(node_id)

            if len(neighbors) < self.MIN_SOURCES:
                continue

            # Collect related concepts
            related_concepts = []
            for n in neighbors:
                if n.id.startswith("mem-"):
                    cid = n.id[4:]
                    related_concepts.append(cid)
                    visited.add(cid)

            if len(related_concepts) < self.MIN_SOURCES:
                continue

            # Create synthesis
            titles = []
            for cid in related_concepts[:5]:
                c = next((x for x in concepts if x.id == cid), None)
                if c:
                    titles.append(c.title)

            synthesis = Synthesis(
                title=f"Synthesis: {', '.join(titles[:3])}...",
                description=f"Novel synthesis combining {len(related_concepts)} related concepts",
                synthesis_text=self._build_synthesis_text(titles, related_concepts),
                source_concepts=related_concepts[:10],
                confidence=0.6,
                tags=["synthesis"],
            )
            self.store.save(synthesis)

            # Add to graph
            node = GraphNode(
                id=f"mem-{synthesis.id}",
                node_type=GraphNodeType.INSIGHT,
                label=synthesis.title,
            )
            self.graph.add_node(node)

            for cid in related_concepts[:10]:
                self.graph.add_edge(
                    GraphEdge(
                        source=f"mem-{cid}",
                        target=f"mem-{synthesis.id}",
                        edge_type=NodeEdgeType.SUPPORTS,
                    )
                )

            syntheses_created += 1

        return {"syntheses_created": syntheses_created}

    def _build_synthesis_text(self, titles: list[str], concept_ids: list[str]) -> str:
        """Build a synthesis description from source concepts."""
        parts = [f"Synthesis connecting: {', '.join(titles[:5])}"]
        parts.append(f"\nThis synthesis integrates {len(concept_ids)} related concepts "
                     "to reveal emergent patterns not explicitly stated in any single source.")
        return "\n".join(parts)
