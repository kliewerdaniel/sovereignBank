"""Pydantic models for memory objects."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from sovereign_memory_bank.models.enums import MemoryStatus, MemoryType


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return uuid4().hex[:12]


class MemoryObject(BaseModel):
    """Base memory object with standard fields."""

    id: str = Field(default_factory=_uuid)
    type: MemoryType
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    created: datetime = Field(default_factory=_now)
    modified: datetime = Field(default_factory=_now)
    status: MemoryStatus = MemoryStatus.ACTIVE
    embedding_id: Optional[str] = None
    graph_node_id: Optional[str] = None
    title: str = ""
    description: str = ""
    source_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    def to_yaml_header(self) -> str:
        """Serialize to YAML frontmatter for markdown storage."""
        lines = [
            "---",
            f"id: {self.id}",
            f"type: {self.type.value}",
            f"confidence: {self.confidence}",
            f"created: {self.created.isoformat()}",
            f"modified: {self.modified.isoformat()}",
            f"status: {self.status.value}",
        ]
        if self.embedding_id:
            lines.append(f"embedding_id: {self.embedding_id}")
        if self.graph_node_id:
            lines.append(f"graph_node_id: {self.graph_node_id}")
        if self.title:
            lines.append(f"title: \"{self.title}\"")
        if self.source_ids:
            lines.append("source_ids:")
            for sid in self.source_ids:
                lines.append(f"  - {sid}")
        if self.tags:
            lines.append("tags:")
            for tag in self.tags:
                lines.append(f"  - {tag}")
        lines.append("---")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Full markdown representation."""
        header = self.to_yaml_header()
        body = f"\n\n{self.title}\n\n{self.description}\n" if self.description else f"\n\n{self.title}\n"
        return header + body

    @classmethod
    def from_yaml_header(cls, data: dict, body: str = "") -> "MemoryObject":
        """Create from parsed YAML header data."""
        kwargs = {
            "id": data.get("id", _uuid()),
            "type": MemoryType(data.get("type", "concept")),
            "confidence": float(data.get("confidence", 0.5)),
            "status": MemoryStatus(data.get("status", "active")),
            "embedding_id": data.get("embedding_id"),
            "graph_node_id": data.get("graph_node_id"),
            "title": data.get("title", ""),
            "description": body.strip(),
            "source_ids": data.get("source_ids", []),
            "tags": data.get("tags", []),
        }
        if "created" in data:
            created = data["created"]
            if isinstance(created, str):
                kwargs["created"] = datetime.fromisoformat(created)
            elif isinstance(created, datetime):
                kwargs["created"] = created
        if "modified" in data:
            modified = data["modified"]
            if isinstance(modified, str):
                kwargs["modified"] = datetime.fromisoformat(modified)
            elif isinstance(modified, datetime):
                kwargs["modified"] = modified
        return cls(**kwargs)


class Concept(MemoryObject):
    """A concept extracted from source material."""

    type: MemoryType = MemoryType.CONCEPT
    related_concepts: list[str] = Field(default_factory=list)
    associated_claims: list[str] = Field(default_factory=list)


class Claim(MemoryObject):
    """A factual or opinion claim."""

    type: MemoryType = MemoryType.CLAIM
    claim_text: str = ""
    supports: list[str] = Field(default_factory=list)
    contradicts: list[str] = Field(default_factory=list)


class Entity(MemoryObject):
    """A named entity (person, org, place, etc.)."""

    type: MemoryType = MemoryType.ENTITY
    entity_type: str = ""  # person, organization, location, etc.
    aliases: list[str] = Field(default_factory=list)


class Relationship(MemoryObject):
    """A typed relationship between two memory objects."""

    type: MemoryType = MemoryType.RELATIONSHIP
    source_id: str = ""
    target_id: str = ""
    edge_type: str = "related_to"
    strength: float = Field(ge=0.0, le=1.0, default=0.5)


class Insight(MemoryObject):
    """A reflective insight derived from multiple sources."""

    type: MemoryType = MemoryType.INSIGHT
    insight_text: str = ""
    derived_from: list[str] = Field(default_factory=list)


class Contradiction(MemoryObject):
    """A detected contradiction between claims."""

    type: MemoryType = MemoryType.CONTRADICTION
    claim_a_id: str = ""
    claim_b_id: str = ""
    research_question: str = ""


class Question(MemoryObject):
    """A research question generated from gaps or contradictions."""

    type: MemoryType = MemoryType.QUESTION
    question_text: str = ""
    generated_from: list[str] = Field(default_factory=list)


class Synthesis(MemoryObject):
    """A novel synthesis combining multiple knowledge sources."""

    type: MemoryType = MemoryType.SYNTHESIS
    synthesis_text: str = ""
    source_concepts: list[str] = Field(default_factory=list)
    source_claims: list[str] = Field(default_factory=list)
    source_insights: list[str] = Field(default_factory=list)


class Abstraction(MemoryObject):
    """A higher-order abstraction derived from patterns."""

    type: MemoryType = MemoryType.ABSTRACTION
    abstraction_text: str = ""
    derived_from: list[str] = Field(default_factory=list)
    level: int = 1  # abstraction hierarchy level


class Narrative(MemoryObject):
    """A narrative connecting ideas over time."""

    type: MemoryType = MemoryType.NARRATIVE
    narrative_text: str = ""
    timeline: list[dict] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)


# Registry for dynamic deserialization
MEMORY_TYPE_REGISTRY: dict[MemoryType, type[MemoryObject]] = {
    MemoryType.CONCEPT: Concept,
    MemoryType.CLAIM: Claim,
    MemoryType.ENTITY: Entity,
    MemoryType.RELATIONSHIP: Relationship,
    MemoryType.INSIGHT: Insight,
    MemoryType.CONTRADICTION: Contradiction,
    MemoryType.QUESTION: Question,
    MemoryType.SYNTHESIS: Synthesis,
    MemoryType.ABSTRACTION: Abstraction,
    MemoryType.NARRATIVE: Narrative,
}


def deserialize_memory(data: dict, body: str = "") -> MemoryObject:
    """Deserialize a memory object from dict + body."""
    mem_type = MemoryType(data.get("type", "concept"))
    cls = MEMORY_TYPE_REGISTRY.get(mem_type, MemoryObject)
    return cls.from_yaml_header(data, body)
