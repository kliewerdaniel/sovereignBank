"""Abstraction promotion - creates higher-order abstractions from patterns."""

from __future__ import annotations

from collections import Counter

from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph
from sovereign_memory_bank.models.enums import MemoryType, GraphNodeType, NodeEdgeType
from sovereign_memory_bank.models.memory_object import Concept, Abstraction
from sovereign_memory_bank.graph.graph_store import GraphNode, GraphEdge


class AbstractionPromoter:
    """Promotes recurring patterns into higher-order abstractions."""

    MIN_SUPPORT = 3  # Minimum concepts to form an abstraction

    def __init__(self, store: MarkdownStore, graph: KnowledgeGraph) -> None:
        self.store = store
        self.graph = graph

    async def promote(self) -> dict:
        """Find common patterns and create abstractions."""
        concepts = self.store.list_objects(MemoryType.CONCEPT)
        if len(concepts) < self.MIN_SUPPORT:
            return {"abstractions_created": 0}

        # Find frequently co-occurring tags
        tag_cooccurrence: dict[tuple[str, str], int] = Counter()
        for concept in concepts:
            for i, t1 in enumerate(concept.tags):
                for t2 in concept.tags[i + 1:]:
                    pair = tuple(sorted([t1, t2]))
                    tag_cooccurrence[pair] += 1

        abstractions_created = 0
        for (tag1, tag2), count in tag_cooccurrence.most_common(5):
            if count < self.MIN_SUPPORT:
                break

            # Find concepts with both tags
            related = [
                c for c in concepts
                if tag1 in c.tags and tag2 in c.tags
            ]

            if len(related) >= self.MIN_SUPPORT:
                abstraction = Abstraction(
                    title=f"Abstraction: {tag1} + {tag2}",
                    description=f"Higher-order abstraction emerging from {count} concepts combining {tag1} and {tag2}",
                    confidence=min(0.9, 0.5 + (count * 0.05)),
                    abstraction_text=f"Pattern: {tag1} and {tag2} co-occur in {count} concepts",
                    derived_from=[c.id for c in related[:10]],
                    level=1,
                    tags=[tag1, tag2, "abstraction"],
                )
                self.store.save(abstraction)

                # Add to graph
                node = GraphNode(
                    id=f"mem-{abstraction.id}",
                    node_type=GraphNodeType.ABSTRACTION,
                    label=abstraction.title,
                )
                self.graph.add_node(node)

                # Connect to source concepts
                for c in related[:10]:
                    self.graph.add_edge(
                        GraphEdge(
                            source=f"mem-{c.id}",
                            target=f"mem-{abstraction.id}",
                            edge_type=NodeEdgeType.DERIVES_FROM,
                        )
                    )

                abstractions_created += 1

        return {"abstractions_created": abstractions_created}
