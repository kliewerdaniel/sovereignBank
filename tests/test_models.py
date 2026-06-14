"""Tests for memory object data models."""

import pytest
from datetime import datetime, timezone

from sovereign_memory_bank.models.enums import MemoryType, MemoryStatus, GraphNodeType, NodeEdgeType
from sovereign_memory_bank.models.memory_object import (
    MemoryObject,
    Concept,
    Claim,
    Entity,
    Relationship,
    Insight,
    Contradiction,
    Question,
    Synthesis,
    Abstraction,
    Narrative,
    deserialize_memory,
)


def test_memory_object_creation():
    obj = MemoryObject(type=MemoryType.CONCEPT, title="Test Concept")
    assert obj.type == MemoryType.CONCEPT
    assert obj.title == "Test Concept"
    assert obj.confidence == 0.5
    assert obj.status == MemoryStatus.ACTIVE
    assert obj.id is not None
    assert obj.created is not None


def test_concept_creation():
    concept = Concept(
        title="Dynamic Persona Systems",
        description="A system for creating adaptive AI personas",
        confidence=0.85,
        tags=["ai", "personas"],
    )
    assert concept.type == MemoryType.CONCEPT
    assert concept.title == "Dynamic Persona Systems"
    assert concept.confidence == 0.85
    assert "ai" in concept.tags


def test_claim_creation():
    claim = Claim(
        title="LLMs can reason",
        claim_text="Large language models demonstrate reasoning capabilities",
        confidence=0.7,
    )
    assert claim.type == MemoryType.CLAIM
    assert claim.claim_text == "Large language models demonstrate reasoning capabilities"


def test_entity_creation():
    entity = Entity(
        title="OpenAI",
        entity_type="organization",
        aliases=["Open AI", "OpenAI Inc"],
    )
    assert entity.entity_type == "organization"
    assert "Open AI" in entity.aliases


def test_relationship_creation():
    rel = Relationship(
        title="A relates to B",
        source_id="concept-a",
        target_id="concept-b",
        edge_type="related_to",
        strength=0.75,
    )
    assert rel.edge_type == "related_to"
    assert rel.strength == 0.75


def test_contradiction_creation():
    cont = Contradiction(
        title="Contradiction found",
        claim_a_id="claim-1",
        claim_b_id="claim-2",
        research_question="Which is correct?",
    )
    assert cont.claim_a_id == "claim-1"
    assert cont.research_question == "Which is correct?"


def test_to_yaml_header():
    obj = MemoryObject(type=MemoryType.CONCEPT, title="Test")
    header = obj.to_yaml_header()
    assert "---" in header
    assert "id:" in header
    assert "type: concept" in header
    assert "title:" in header


def test_to_markdown():
    obj = MemoryObject(type=MemoryType.CONCEPT, title="Test Concept", description="A test")
    md = obj.to_markdown()
    assert md.startswith("---")
    assert "Test Concept" in md
    assert "A test" in md


def test_deserialize_memory():
    data = {
        "id": "test-123",
        "type": "concept",
        "confidence": 0.9,
        "status": "active",
        "title": "Deserialized Concept",
    }
    obj = deserialize_memory(data, "Body text here")
    assert obj.id == "test-123"
    assert obj.type == MemoryType.CONCEPT
    assert obj.confidence == 0.9
    assert obj.description == "Body text here"


def test_confidence_bounds():
    with pytest.raises(Exception):
        MemoryObject(type=MemoryType.CONCEPT, confidence=1.5)
    with pytest.raises(Exception):
        MemoryObject(type=MemoryType.CONCEPT, confidence=-0.1)


def test_enum_values():
    assert MemoryType.CONCEPT.value == "concept"
    assert NodeEdgeType.CONTRADICTS.value == "contradicts"
    assert GraphNodeType.INSIGHT.value == "insight"
