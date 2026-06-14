"""Tests for evolution engine components."""

import pytest
import tempfile
from pathlib import Path

from sovereign_memory_bank.evolution.dedup import DuplicateDetector
from sovereign_memory_bank.evolution.splitter import ConceptSplitter
from sovereign_memory_bank.evolution.abstraction import AbstractionPromoter
from sovereign_memory_bank.layers.layer_manager import LayerManager
from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph, GraphNode, GraphEdge
from sovereign_memory_bank.models.enums import MemoryType, GraphNodeType, NodeEdgeType
from sovereign_memory_bank.models.memory_object import Concept


class MockStore:
    def __init__(self):
        self.concepts = []
        self.saved = []

    def list_objects(self, mem_type):
        return self.concepts

    def save(self, obj):
        self.saved.append(obj)


class MockGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.added_edges = []

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, edge):
        self.edges.append(edge)
        self.added_edges.append(edge)

    def get_edges_from(self, node_id):
        return [e for e in self.edges if e.source == node_id]

    def get_edges_to(self, node_id):
        return [e for e in self.edges if e.target == node_id]

    def remove_node(self, node_id):
        self.nodes.pop(node_id, None)
        self.edges = [e for e in self.edges if e.source != node_id and e.target != node_id]


def test_duplicate_detection():
    store = MockStore()
    graph = MockGraph()
    detector = DuplicateDetector(store, graph)

    c1 = Concept(id="c1", title="Machine Learning Fundamentals", description="ML basics")
    c2 = Concept(id="c2", title="Machine Learning Fundamentals", description="ML basics repeated")
    c3 = Concept(id="c3", title="Deep Learning Networks", description="Neural nets")
    store.concepts = [c1, c2, c3]

    import asyncio
    result = asyncio.run(detector.detect_and_merge())

    assert result["merged"] >= 1
    # c2 should be marked as merged
    merged = [s for s in store.saved if hasattr(s, 'status') and s.status.value == "merged"]
    assert len(merged) >= 1


def test_abstraction_promotion():
    store = MockStore()
    graph = MockGraph()
    promoter = AbstractionPromoter(store, graph)

    # Create concepts with shared tags
    for i in range(5):
        c = Concept(
            id=f"c{i}",
            title=f"Concept {i}",
            tags=["ai", "machine-learning"],
        )
        store.concepts.append(c)
        graph.add_node(GraphNode(id=f"mem-c{i}", node_type=GraphNodeType.CONCEPT, label=f"C{i}"))

    import asyncio
    result = asyncio.run(promoter.promote())

    assert result["abstractions_created"] >= 1
    assert len(store.saved) >= 1
