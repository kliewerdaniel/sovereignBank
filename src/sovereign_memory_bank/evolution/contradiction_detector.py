"""Contradiction detection between claims."""

from __future__ import annotations

from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph
from sovereign_memory_bank.models.enums import MemoryType
from sovereign_memory_bank.models.memory_object import Claim, Contradiction, Question


class ContradictionDetector:
    """Detects contradictions between claims and generates research questions."""

    def __init__(self, store: MarkdownStore, graph: KnowledgeGraph) -> None:
        self.store = store
        self.graph = graph

    async def detect(self) -> dict:
        """Scan claims for contradictions."""
        claims = self.store.list_objects(MemoryType.CLAIM)
        contradictions_found = 0

        for i, c1 in enumerate(claims):
            for c2 in claims[i + 1 :]:
                if self._are_contradictory(c1, c2):
                    self._create_contradiction(c1, c2)
                    contradictions_found += 1

        return {"contradictions_detected": contradictions_found}

    def _are_contradictory(self, c1: Claim, c2: Claim) -> bool:
        """Simple heuristic contradiction detection."""
        # Check if claims reference similar topics but have opposing sentiment
        t1 = c1.title.lower()
        t2 = c2.title.lower()

        # Simple negation detection
        negations = ["not", "no", "never", "neither", "nor", "cannot", "can't", "won't", "don't"]
        has_negation_1 = any(neg in t1 for neg in negations)
        has_negation_2 = any(neg in t2 for neg in negations)

        # If one has negation and they share significant words, might be contradictory
        if has_negation_1 != has_negation_2:
            words1 = set(t1.split())
            words2 = set(t2.split())
            overlap = words1 & words2
            if len(overlap) >= 2:
                return True

        # Check if claims contradict each other via graph edges
        c1_node = f"mem-{c1.id}"
        c2_node = f"mem-{c2.id}"
        for edge in self.graph.edges:
            if (edge.source == c1_node and edge.target == c2_node) or \
               (edge.source == c2_node and edge.target == c1_node):
                if edge.edge_type.value == "contradicts":
                    return True

        return False

    def _create_contradiction(self, c1: Claim, c2: Claim) -> None:
        """Create a contradiction object and research question."""
        contradiction = Contradiction(
            title=f"Contradiction: {c1.title[:40]} vs {c2.title[:40]}",
            description=f"Contradiction detected between:\n- {c1.title}\n- {c2.title}",
            claim_a_id=c1.id,
            claim_b_id=c2.id,
            source_ids=list(set(c1.source_ids + c2.source_ids)),
        )
        self.store.save(contradiction)

        # Generate research question
        question = Question(
            title=f"Why do {c1.title[:30]} and {c2.title[:30]} contradict?",
            description=f"Research question to resolve contradiction between claims",
            question_text=f"What is the relationship between: {c1.title} and {c2.title}?",
            generated_from=[c1.id, c2.id],
        )
        self.store.save(question)

        # Add graph nodes and edges
        from sovereign_memory_bank.graph.graph_store import GraphNode, GraphEdge
        from sovereign_memory_bank.models.enums import GraphNodeType, NodeEdgeType

        cont_node = GraphNode(
            id=f"mem-{contradiction.id}",
            node_type=GraphNodeType.INSIGHT,
            label=contradiction.title,
        )
        self.graph.add_node(cont_node)

        self.graph.add_edge(
            GraphEdge(
                source=f"mem-{c1.id}",
                target=f"mem-{contradiction.id}",
                edge_type=NodeEdgeType.CONTRADICTS,
            )
        )
        self.graph.add_edge(
            GraphEdge(
                source=f"mem-{c2.id}",
                target=f"mem-{contradiction.id}",
                edge_type=NodeEdgeType.CONTRADICTS,
            )
        )
