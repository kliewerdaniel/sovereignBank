"""Tests for contradiction detection."""

import pytest

from sovereign_memory_bank.evolution.contradiction_detector import ContradictionDetector
from sovereign_memory_bank.models.memory_object import Claim


class MockStore:
    def __init__(self):
        self.claims = []
        self.saved = []

    def list_objects(self, mem_type):
        return self.claims

    def save(self, obj):
        self.saved.append(obj)


class MockGraph:
    def __init__(self):
        self.edges = []
        self.nodes = {}
        self.added_nodes = []
        self.added_edges = []

    def add_node(self, node):
        self.nodes[node.id] = node
        self.added_nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)
        self.added_edges.append(edge)


def test_detect_contradiction_with_negation():
    store = MockStore()
    graph = MockGraph()
    detector = ContradictionDetector(store, graph)

    c1 = Claim(id="c1", title="AI is safe and beneficial", claim_text="AI is safe")
    c2 = Claim(id="c2", title="AI is not safe for society", claim_text="AI is not safe")
    store.claims = [c1, c2]

    import asyncio
    result = asyncio.run(detector.detect())

    assert result["contradictions_detected"] >= 1
    assert len(store.saved) >= 2  # contradiction + question


def test_no_contradiction_similar():
    store = MockStore()
    graph = MockGraph()
    detector = ContradictionDetector(store, graph)

    c1 = Claim(id="c1", title="Python is great for data science", claim_text="Python is great")
    c2 = Claim(id="c2", title="Python is great for web development", claim_text="Python is great")
    store.claims = [c1, c2]

    import asyncio
    result = asyncio.run(detector.detect())

    # These shouldn't be contradictory
    assert result["contradictions_detected"] == 0
