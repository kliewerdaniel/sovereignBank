"""Enumerations for memory objects, graph nodes, and edges."""

from enum import StrEnum


class MemoryType(StrEnum):
    """Types of memory objects."""

    CONCEPT = "concept"
    CLAIM = "claim"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    INSIGHT = "insight"
    CONTRADICTION = "contradiction"
    QUESTION = "question"
    SYNTHESIS = "synthesis"
    ABSTRACTION = "abstraction"
    NARRATIVE = "narrative"


class MemoryStatus(StrEnum):
    """Lifecycle status of a memory object."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REVISED = "revised"
    MERGED = "merged"
    SPLIT = "split"


class GraphNodeType(StrEnum):
    """Valid node types in the knowledge graph."""

    CONCEPT = "concept"
    ENTITY = "entity"
    CLAIM = "claim"
    INSIGHT = "insight"
    NARRATIVE = "narrative"
    ABSTRACTION = "abstraction"


class NodeEdgeType(StrEnum):
    """Valid edge types in the knowledge graph."""

    REFERENCES = "references"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    DERIVES_FROM = "derives_from"
    INSPIRED_BY = "inspired_by"
    EVOLVES_INTO = "evolves_into"
    RELATED_TO = "related_to"
    CONTAINS = "contains"
    EXPLAINS = "explains"


class LayerIndex(StrEnum):
    """Memory layer indices (0-6)."""

    SOURCE = "0"
    EXTRACTED = "1"
    SEMANTIC = "2"
    REFLECTIVE = "3"
    SYNTHETIC = "4"
    NARRATIVE = "5"
    EXECUTIVE = "6"
