"""Tests for knowledge graph."""

import pytest
import tempfile
from pathlib import Path

from sovereign_memory_bank.graph.graph_store import KnowledgeGraph, GraphNode, GraphEdge
from sovereign_memory_bank.models.enums import GraphNodeType, NodeEdgeType


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def graph(temp_dir):
    return KnowledgeGraph(temp_dir / "graph.json")


def test_add_node(graph):
    node = GraphNode(id="n1", node_type=GraphNodeType.CONCEPT, label="Test")
    graph.add_node(node)
    assert "n1" in graph.nodes
    assert graph.nodes["n1"].label == "Test"


def test_add_edge(graph):
    n1 = GraphNode(id="n1", node_type=GraphNodeType.CONCEPT, label="A")
    n2 = GraphNode(id="n2", node_type=GraphNodeType.CONCEPT, label="B")
    graph.add_node(n1)
    graph.add_node(n2)

    edge = GraphEdge(source="n1", target="n2", edge_type=NodeEdgeType.RELATED_TO)
    graph.add_edge(edge)
    assert len(graph.edges) == 1


def test_get_neighbors(graph):
    n1 = GraphNode(id="n1", node_type=GraphNodeType.CONCEPT, label="A")
    n2 = GraphNode(id="n2", node_type=GraphNodeType.CONCEPT, label="B")
    n3 = GraphNode(id="n3", node_type=GraphNodeType.CLAIM, label="C")
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    graph.add_edge(GraphEdge(source="n1", target="n2", edge_type=NodeEdgeType.RELATED_TO))
    graph.add_edge(GraphEdge(source="n1", target="n3", edge_type=NodeEdgeType.SUPPORTS))

    neighbors = graph.get_neighbors("n1")
    assert len(neighbors) == 2

    # Filter by edge type
    supports_only = graph.get_neighbors("n1", edge_type=NodeEdgeType.SUPPORTS)
    assert len(supports_only) == 1
    assert supports_only[0].id == "n3"


def test_multi_hop_query(graph):
    # Create chain: n1 -> n2 -> n3 -> n4
    for i in range(1, 5):
        graph.add_node(GraphNode(id=f"n{i}", node_type=GraphNodeType.CONCEPT, label=f"Node {i}"))

    graph.add_edge(GraphEdge(source="n1", target="n2", edge_type=NodeEdgeType.RELATED_TO))
    graph.add_edge(GraphEdge(source="n2", target="n3", edge_type=NodeEdgeType.RELATED_TO))
    graph.add_edge(GraphEdge(source="n3", target="n4", edge_type=NodeEdgeType.RELATED_TO))

    paths = graph.multi_hop_query("n1", max_hops=3)
    assert len(paths) >= 3  # n1->n2, n1->n2->n3, n1->n2->n3->n4

    # Check that we can reach n4
    reachable = [p.nodes[-1] for p in paths]
    assert "n4" in reachable


def test_find_path(graph):
    for i in range(1, 4):
        graph.add_node(GraphNode(id=f"n{i}", node_type=GraphNodeType.CONCEPT, label=f"Node {i}"))

    graph.add_edge(GraphEdge(source="n1", target="n2", edge_type=NodeEdgeType.RELATED_TO))
    graph.add_edge(GraphEdge(source="n2", target="n3", edge_type=NodeEdgeType.RELATED_TO))

    path = graph.find_path("n1", "n3")
    assert path is not None
    assert path.nodes[0] == "n1"
    assert path.nodes[-1] == "n3"


def test_remove_node(graph):
    graph.add_node(GraphNode(id="n1", node_type=GraphNodeType.CONCEPT, label="A"))
    graph.add_node(GraphNode(id="n2", node_type=GraphNodeType.CONCEPT, label="B"))
    graph.add_edge(GraphEdge(source="n1", target="n2", edge_type=NodeEdgeType.RELATED_TO))

    graph.remove_node("n1")
    assert "n1" not in graph.nodes
    assert len(graph.edges) == 0


def test_save_and_load(temp_dir):
    graph = KnowledgeGraph(temp_dir / "graph.json")
    graph.add_node(GraphNode(id="n1", node_type=GraphNodeType.CONCEPT, label="Persisted"))
    graph.add_edge(GraphEdge(source="n1", target="n2", edge_type=NodeEdgeType.RELATED_TO))
    graph.save()

    graph2 = KnowledgeGraph(temp_dir / "graph.json")
    assert "n1" in graph2.nodes
    assert graph2.nodes["n1"].label == "Persisted"


def test_stats(graph):
    graph.add_node(GraphNode(id="n1", node_type=GraphNodeType.CONCEPT, label="A"))
    graph.add_node(GraphNode(id="n2", node_type=GraphNodeType.CLAIM, label="B"))
    graph.add_edge(GraphEdge(source="n1", target="n2", edge_type=NodeEdgeType.SUPPORTS))

    stats = graph.stats()
    assert stats["total_nodes"] == 2
    assert stats["total_edges"] == 1
    assert stats["node_types"]["concept"] == 1
    assert stats["node_types"]["claim"] == 1
