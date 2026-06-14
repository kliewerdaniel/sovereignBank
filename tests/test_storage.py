"""Tests for storage layer."""

import pytest
import tempfile
from pathlib import Path

from sovereign_memory_bank.layers.layer_manager import LayerManager
from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.models.enums import MemoryType
from sovereign_memory_bank.models.memory_object import Concept, Claim


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def layer_manager(temp_dir):
    lm = LayerManager(temp_dir / "memory-bank")
    lm.initialize()
    return lm


@pytest.fixture
def markdown_store(layer_manager):
    return MarkdownStore(layer_manager)


def test_layer_manager_initialize(temp_dir):
    lm = LayerManager(temp_dir / "memory-bank")
    lm.initialize()
    assert (temp_dir / "memory-bank" / "layer-0").is_dir()
    assert (temp_dir / "memory-bank" / "layer-1").is_dir()
    assert (temp_dir / "memory-bank" / "layer-1" / "concepts").is_dir()
    assert (temp_dir / "memory-bank" / "layer-1" / "claims").is_dir()
    assert (temp_dir / "memory-bank" / "layer-3" / "contradictions").is_dir()
    assert (temp_dir / "memory-bank" / "layer-4" / "syntheses").is_dir()


def test_markdown_store_save_and_load(markdown_store):
    concept = Concept(
        title="Test Concept",
        description="A concept for testing",
        confidence=0.8,
    )
    path = markdown_store.save(concept)
    assert path.exists()

    loaded = markdown_store.load(MemoryType.CONCEPT, concept.id)
    assert loaded is not None
    assert loaded.title == "Test Concept"
    assert loaded.confidence == 0.8


def test_markdown_store_list(markdown_store):
    for i in range(3):
        concept = Concept(title=f"Concept {i}", description=f"Description {i}")
        markdown_store.save(concept)

    concepts = markdown_store.list_objects(MemoryType.CONCEPT)
    assert len(concepts) == 3


def test_markdown_store_delete(markdown_store):
    concept = Concept(title="To Delete")
    markdown_store.save(concept)
    assert markdown_store.exists(MemoryType.CONCEPT, concept.id)

    deleted = markdown_store.delete(MemoryType.CONCEPT, concept.id)
    assert deleted
    assert not markdown_store.exists(MemoryType.CONCEPT, concept.id)


def test_markdown_store_count(markdown_store):
    for i in range(5):
        markdown_store.save(Concept(title=f"C{i}"))
    for i in range(3):
        markdown_store.save(Claim(title=f"Cl{i}"))

    assert markdown_store.count(MemoryType.CONCEPT) == 5
    assert markdown_store.count(MemoryType.CLAIM) == 3
    assert markdown_store.count() == 8


def test_markdown_store_load_nonexistent(markdown_store):
    result = markdown_store.load(MemoryType.CONCEPT, "nonexistent-id")
    assert result is None
