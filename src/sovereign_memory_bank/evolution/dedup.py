"""Duplicate detection and merging."""

from __future__ import annotations

from difflib import SequenceMatcher

from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph
from sovereign_memory_bank.models.enums import MemoryType, MemoryStatus
from sovereign_memory_bank.models.memory_object import Concept


class DuplicateDetector:
    """Detects and merges duplicate concepts."""

    SIMILARITY_THRESHOLD = 0.85

    def __init__(self, store: MarkdownStore, graph: KnowledgeGraph) -> None:
        self.store = store
        self.graph = graph

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    async def detect_and_merge(self) -> dict:
        """Find and merge duplicate concepts."""
        concepts = self.store.list_objects(MemoryType.CONCEPT)
        merged_count = 0
        pairs_found = []

        seen = set()
        for i, c1 in enumerate(concepts):
            if c1.id in seen:
                continue
            for c2 in concepts[i + 1 :]:
                if c2.id in seen:
                    continue
                sim = self._similarity(c1.title, c2.title)
                if sim >= self.SIMILARITY_THRESHOLD:
                    # Merge c2 into c1
                    self._merge(c1, c2)
                    seen.add(c2.id)
                    pairs_found.append((c1.id, c2.id, sim))
                    merged_count += 1

        return {"merged": merged_count, "pairs": pairs_found}

    def _merge(self, target: Concept, source: Concept) -> None:
        """Merge source into target."""
        # Combine descriptions
        if source.description and source.description not in target.description:
            target.description = f"{target.description}\n\n{source.description}".strip()

        # Combine source IDs
        for sid in source.source_ids:
            if sid not in target.source_ids:
                target.source_ids.append(sid)

        # Combine tags
        for tag in source.tags:
            if tag not in target.tags:
                target.tags.append(tag)

        # Mark source as merged
        source.status = MemoryStatus.MERGED
        self.store.save(source)

        # Save merged target
        self.store.save(target)

        # Update graph: redirect edges from source to target
        from sovereign_memory_bank.graph.graph_store import GraphEdge
        from sovereign_memory_bank.models.enums import NodeEdgeType

        source_node_id = f"mem-{source.id}"
        target_node_id = f"mem-{target.id}"

        for edge in list(self.graph.edges):
            if edge.source == source_node_id:
                edge.source = target_node_id
            elif edge.target == source_node_id:
                edge.target = target_node_id

        self.graph.remove_node(source_node_id)
